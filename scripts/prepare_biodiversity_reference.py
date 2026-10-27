"""Build an attributed national taxonomy reference from the public IEPNB API.

Requires Python 3; standard library only. Run from any directory:
  python web/scripts/prepare_biodiversity_reference.py
  python web/scripts/prepare_biodiversity_reference.py --offline

Raw official responses and checksums stay in web/tmp/biodiversidad. Public
reference JSON goes into web/dist/data/biodiversity. The curated catalogue,
photographs and application code are never modified.

The API is the public integration route explicitly documented by IEPNB. This
script does not submit or circumvent the CAPTCHA-protected website downloads.
TLS certificate validation stays enabled; system-trusted CAs are loaded.
"""

import argparse
import collections
import datetime as dt
import hashlib
import json
import re
import ssl
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'tmp/biodiversidad'
OUT = ROOT / 'dist/data/biodiversity'
API = 'https://iepnb.gob.es/api/catalogo/v_listapatronespecie'
SOURCE_PAGE = 'https://pro.iepnb.gob.es/recursos/listas-controladas'
API_DOCUMENTATION = 'https://pro.iepnb.gob.es/recursos/servicios-interoperables/api-catalogo'
LICENCE_PAGE = 'https://pro.iepnb.gob.es/aviso-legal'
SOURCE_ID = 'miteco-iepnb-lista-patron'
DATE = dt.datetime.now(dt.timezone.utc).date().isoformat()
SELECT = ','.join([
    'id:idtaxon', 'concept:taxonConceptID', 'scientific:WithoutAutorship',
    'full:ScientificName', 'author:ScientificNameAuthorship', 'kingdom', 'phylum',
    'class', 'order', 'family', 'genus', 'rank:taxonRank',
    'common:"Vernacular Name"', 'origin:Origen', 'environment:Environment',
    'group:"Grupo taxonómico"', 'reference:nameAccordingto', 'remarks:taxonRemarks',
])
GROUPS = {
    'birds': ('Aves', 'Birds'),
    'mammals': ('Mamíferos', 'Mammals'),
    'reptiles': ('Reptiles', 'Reptiles'),
    'amphibians': ('Anfibios', 'Amphibians'),
    'fish': ('Peces', 'Fish'),
    'invertebrates': ('Invertebrados', 'Invertebrates'),
    'vascular-plants': ('Plantas vasculares', 'Vascular plants'),
    'bryophytes': ('Briófitos', 'Bryophytes'),
    'plants-other': ('Algas y otras plantas', 'Algae and other plants'),
    'fungi': ('Hongos y líquenes', 'Fungi and lichens'),
    'chromista': ('Cromistas', 'Chromists'),
    'protists': ('Protozoos y otros protistas', 'Protozoa and other protists'),
    'bacteria': ('Bacterias', 'Bacteria'),
    'archaea': ('Arqueas', 'Archaea'),
    'other': ('Otros taxones', 'Other taxa'),
}


def write_json(path, value, indent=None):
    path.parent.mkdir(parents=True, exist_ok=True)
    encoded = json.dumps(value, ensure_ascii=False, indent=indent,
        separators=(',', ':') if indent is None else None) + '\n'
    with path.open('w', encoding='utf-8', newline='\n') as handle:
        handle.write(encoded)
    return len(encoded.encode('utf-8'))


def text(value):
    return re.sub(r'\s+', ' ', str(value)).strip() if value is not None else None


def browse_group(row):
    kingdom = (row.get('kingdom') or '').casefold()
    taxon_class = (row.get('class') or '').casefold()
    phylum = (row.get('phylum') or '').casefold()
    source_group = (row.get('group') or '').casefold()
    if kingdom in {'animalia', 'metazoa'}:
        if taxon_class == 'aves': return 'birds'
        if taxon_class == 'mammalia': return 'mammals'
        if taxon_class in {'reptilia', 'sauropsida'}: return 'reptiles'
        if taxon_class == 'amphibia': return 'amphibians'
        if taxon_class in {'actinopterygii', 'actinopteri', 'chondrichthyes', 'elasmobranchii', 'holocephali', 'sarcopterygii', 'myxini', 'petromyzonti', 'cephalaspidomorphi', 'petromyzontida'} or 'peces' in source_group: return 'fish'
        return 'invertebrates'
    if kingdom == 'plantae':
        if phylum == 'tracheophyta' or 'vasculares' in source_group and 'no vasculares' not in source_group: return 'vascular-plants'
        if phylum in {'bryophyta', 'marchantiophyta', 'anthocerotophyta'} or 'briófit' in source_group or 'briofit' in source_group: return 'bryophytes'
        return 'plants-other'
    if kingdom == 'fungi': return 'fungi'
    if kingdom == 'chromista': return 'chromista'
    if kingdom in {'protozoa', 'protista'}: return 'protists'
    if kingdom in {'bacteria', 'eubacteria'}: return 'bacteria'
    if kingdom == 'archaea': return 'archaea'
    return 'other'


def download_pages(page_size, offline=False, refresh=False):
    RAW.mkdir(parents=True, exist_ok=True)
    manifest_path = RAW / 'source-pages.json'
    previous = json.loads(manifest_path.read_text(encoding='utf-8')) if manifest_path.exists() and not refresh else {}
    cache = {page['offset']: page for page in previous.get('pages', [])}
    manifest = {'api': API, 'select': SELECT, 'order': 'idtaxon.asc', 'snapshot_date': previous.get('snapshot_date') or DATE,
        'retrieved_at': previous.get('retrieved_at') or dt.datetime.now(dt.timezone.utc).isoformat(),
        'pages': [], 'complete': False}
    context = ssl.create_default_context()
    context.load_default_certs()
    records, offset, expected = [], 0, previous.get('expected_total')
    while expected is None or offset < expected:
        cached = cache.get(offset)
        if cached and (RAW / cached['file']).is_file():
            content = (RAW / cached['file']).read_bytes()
            if hashlib.sha256(content).hexdigest() != cached['sha256']:
                raise RuntimeError('Raw source checksum mismatch: ' + cached['file'])
            page_meta = cached
        else:
            if offline: raise RuntimeError('Offline cache is incomplete at offset ' + str(offset))
            query = urllib.parse.urlencode({'select': SELECT, 'order': 'idtaxon.asc', 'limit': page_size, 'offset': offset})
            url = API + '?' + query
            request = urllib.request.Request(url, headers={'User-Agent': 'DrNatureWiki/1.2 (attributed public taxonomy reference)', 'Accept': 'application/json', 'Prefer': 'count=exact'})
            for attempt in range(4):
                try:
                    with urllib.request.urlopen(request, context=context, timeout=60) as response:
                        content = response.read(24_000_001)
                        if len(content) > 24_000_000: raise RuntimeError('Official response exceeds the per-page limit')
                        content_range = response.headers.get('Content-Range', '')
                        match = re.search(r'/([0-9]+)$', content_range)
                        if match:
                            total = int(match.group(1))
                            if expected is not None and expected != total: raise RuntimeError('Official list changed during import; restart with --refresh')
                            expected = total
                        page_meta = {'offset': offset, 'file': 'taxa-' + str(offset).zfill(6) + '.json',
                            'url': url, 'content_range': content_range, 'server_date': response.headers.get('Date'),
                            'sha256': hashlib.sha256(content).hexdigest(), 'bytes': len(content)}
                        (RAW / page_meta['file']).write_bytes(content)
                    break
                except urllib.error.HTTPError as error:
                    if error.code not in {429, 500, 502, 503, 504} or attempt == 3: raise
                    delay = min(60, max(2, int(error.headers.get('Retry-After', 2 ** (attempt + 1)))))
                    print('Official API temporarily unavailable; waiting ' + str(delay) + ' seconds', flush=True)
                    time.sleep(delay)
            time.sleep(0.4)
        rows = json.loads(content.decode('utf-8-sig'))
        if not isinstance(rows, list): raise RuntimeError('Official API did not return a record array')
        if not rows:
            if expected is not None and offset != expected: raise RuntimeError('Official list ended before its declared count')
            break
        page_meta['count'] = len(rows)
        manifest['pages'].append(page_meta)
        manifest['expected_total'] = expected
        records.extend(rows)
        offset += len(rows)
        write_json(manifest_path, manifest, indent=2)
        print('Official taxon records: ' + str(offset) + '/' + str(expected or '?'), flush=True)
    if expected is not None and len(records) != expected: raise RuntimeError('Downloaded count differs from official count')
    ids = [str(row['id']) for row in records]
    manifest['complete'] = True
    manifest['downloaded_total'] = len(records)
    manifest['unique_taxon_ids'] = len(set(ids))
    manifest['duplicate_source_rows'] = len(ids) - len(set(ids))
    write_json(manifest_path, manifest, indent=2)
    return records, manifest


def normalize(row):
    source_id = int(row['id'])
    scientific = text(row.get('scientific')) or text(row.get('full'))
    if not scientific: raise RuntimeError('Official taxon has no scientific name: ' + str(source_id))
    return {
        'id': 'miteco:lp:' + str(source_id), 'source_taxon_id': source_id,
        'taxon_concept_id': text(row.get('concept')), 'scientific_name': scientific,
        'scientific_name_with_author': text(row.get('full')), 'authorship': text(row.get('author')),
        'common_name': text(row.get('common')) or None,
        'common_name_language': None,  # API supplies no per-name language field.
        'kingdom': text(row.get('kingdom')), 'phylum': text(row.get('phylum')),
        'class': text(row.get('class')), 'order': text(row.get('order')),
        'family': text(row.get('family')), 'genus': text(row.get('genus')),
        'rank': text(row.get('rank')), 'group': browse_group(row),
        'source_group': text(row.get('group')), 'environment': text(row.get('environment')),
        'origin': text(row.get('origin')), 'source_id': SOURCE_ID,
        'source_url': API + '?idtaxon=eq.' + str(source_id), 'scope': 'ES',
        'name_according_to': text(row.get('reference')), 'taxon_remarks': text(row.get('remarks')) or None,
    }


def consolidate(rows):
    """The API view repeats a few IDs for alternative vernaculars/authorships."""
    by_id = collections.defaultdict(list)
    for row in rows: by_id[int(row['id'])].append(row)
    records, changes = [], []
    for taxon_id, variants in by_id.items():
        record = normalize(variants[0])
        if len(variants) > 1:
            differing = [key for key in variants[0] if len({json.dumps(value.get(key), ensure_ascii=False) for value in variants}) > 1]
            if set(differing) - {'common', 'author'}:
                raise RuntimeError('Conflicting official taxonomy for taxon ID ' + str(taxon_id) + ': ' + ','.join(differing))
            common = sorted({text(value.get('common')) for value in variants if text(value.get('common'))}, key=str.casefold)
            authors = sorted({text(value.get('author')) for value in variants if text(value.get('author'))}, key=str.casefold)
            record['common_names'] = common
            record['common_name'] = common[0] if common else None
            record['authorship_variants'] = authors
            if len(authors) > 1: record['authorship'] = None
            record['source_row_count'] = len(variants)
            changes.append({'id': record['id'], 'rows': len(variants), 'differing_fields': differing,
                'common_names': common, 'authorship_variants': authors})
        records.append(record)
    return records, changes


def build(rows, source_manifest, chunk_size):
    OUT.mkdir(parents=True, exist_ok=True)
    records, consolidated = consolidate(rows)
    snapshot_date = source_manifest['snapshot_date']
    grouped = collections.defaultdict(list)
    for record in records: grouped[record['group']].append(record)
    source = {
        'id': SOURCE_ID, 'title': 'Lista Patrón de las especies silvestres presentes en España',
        'publisher': 'Ministerio para la Transición Ecológica y el Reto Demográfico · IEPNB',
        'page_url': SOURCE_PAGE, 'api_url': API, 'api_documentation_url': API_DOCUMENTATION,
        'retrieved_at': source_manifest['retrieved_at'], 'snapshot_date': snapshot_date,
        'source_update_date': None, 'source_update_date_note': 'The API does not supply a dataset-wide last-update timestamp in these responses.',
        'licence': 'CC BY 4.0 (portal default unless a dataset states otherwise)',
        'licence_url': 'https://creativecommons.org/licenses/by/4.0/', 'licence_evidence_url': LICENCE_PAGE,
        'attribution': 'MITECO / Inventario Español del Patrimonio Natural y de la Biodiversidad, Lista Patrón de las especies silvestres presentes en España; snapshot ' + snapshot_date + '. Normalized for Dr Nature wiki.',
    }
    index = {
        'schema': 'dr-nature-biodiversity-reference-v1', 'generated_at': dt.datetime.now(dt.timezone.utc).isoformat(),
        'source': source, 'total_taxa': len(records), 'official_declared_rows': source_manifest['expected_total'],
        'consolidated_duplicate_rows': len(rows) - len(records),
        'scope': {'id': 'ES', 'name': {'es': 'España', 'en': 'Spain'},
            'definition': {'es': 'Referencia taxonómica de ámbito nacional, terrestre y marino. La pertenencia a la Lista Patrón no acredita presencia en Madrid, en una ruta o en un punto concreto.',
                'en': 'National terrestrial and marine taxonomy reference. Membership of the master list does not establish presence in Madrid, on a trail or at an individual location.'}},
        'groups': [], 'chunks': [],
        'search_columns': ['id', 'scientific_name', 'common_name', 'group', 'chunk'], 'search': [],
        'ranks': dict(sorted(collections.Counter(record['rank'] or 'Unspecified' for record in records).items())),
        'kingdoms': dict(sorted(collections.Counter(record['kingdom'] or 'Unspecified' for record in records).items())),
        'records_with_common_name': sum(bool(record['common_name']) for record in records),
        'limitations': {
            'es': ['Taxones de distintos rangos: no todos los registros equivalen a especies.',
                'Ámbito España; no se añaden coordenadas, avistamientos ni relaciones locales inferidas.',
                'Sin fotografías o descripciones añadidas a partir de semejanzas; las fichas curadas se mantienen aparte.',
                'Los nombres comunes se conservan cuando los facilita la fuente; el API no declara el idioma de cada nombre.',
                'Los grandes grupos son una ayuda de navegación derivada de la taxonomía oficial, que se conserva íntegra.',
                'La instantánea no implica sincronización automática con cambios posteriores.'],
            'en': ['Taxa at several ranks; the record count is not a species count.',
                'Spain-wide scope; no coordinates, sightings or inferred local associations are added.',
                'No photographs or descriptions inferred by similarity; curated cards remain separate.',
                'Common names are preserved when supplied; the API does not declare each name’s language.',
                'Broad groups help navigation and are derived from, without replacing, official taxonomy.',
                'This snapshot does not automatically synchronize later changes.']},
    }
    for group in GROUPS:
        values = grouped.get(group, [])
        if not values: continue
        values.sort(key=lambda record: (record['scientific_name'].casefold(), record['source_taxon_id']))
        label_es, label_en = GROUPS[group]
        group_meta = {'id': group, 'label': {'es': label_es, 'en': label_en}, 'count': len(values), 'chunks': []}
        for offset in range(0, len(values), chunk_size):
            chunk = values[offset:offset + chunk_size]
            number = offset // chunk_size + 1
            filename = f'chunks/{group}-{number:03}.json'
            count_bytes = write_json(OUT / filename, {'schema': 'dr-nature-biodiversity-chunk-v1',
                'source_id': SOURCE_ID, 'scope': 'ES', 'group': group, 'records': chunk})
            chunk_index = len(index['chunks'])
            index['chunks'].append({'file': 'data/biodiversity/' + filename, 'group': group,
                'label': {'es': label_es, 'en': label_en}, 'count': len(chunk), 'bytes': count_bytes,
                'first_name': chunk[0]['scientific_name'], 'last_name': chunk[-1]['scientific_name']})
            group_meta['chunks'].append(chunk_index)
            for record in chunk:
                common_search = ' · '.join(record.get('common_names', [])) or record['common_name']
                index['search'].append([record['id'], record['scientific_name'], common_search, group, chunk_index])
        index['groups'].append(group_meta)
    index_bytes = write_json(OUT / 'index.json', index)
    if index_bytes >= 10_000_000: raise RuntimeError('Search index exceeds the 10 MB integration budget')
    metadata = {key: index[key] for key in ('schema', 'generated_at', 'source', 'total_taxa',
        'official_declared_rows', 'consolidated_duplicate_rows', 'scope', 'groups',
        'ranks', 'kingdoms', 'records_with_common_name', 'limitations')}
    metadata.update({'index_file': 'data/biodiversity/index.json', 'index_bytes': index_bytes,
        'chunk_count': len(index['chunks']), 'chunk_bytes': sum(item['bytes'] for item in index['chunks'])})
    write_json(OUT / 'metadata.json', metadata, indent=2)

    by_name = collections.defaultdict(list)
    for record in records: by_name[record['scientific_name'].strip().casefold()].append(record['id'])
    catalogue = ROOT / 'dist/data/catalogue.json'
    links = []
    if catalogue.is_file():
        curated = json.loads(catalogue.read_text(encoding='utf-8')).get('species', [])
        for record in curated:
            match = by_name.get(record['scientific_name'].strip().casefold(), [])
            if match: links.append({'curated_id': record['id'], 'reference_ids': match, 'match': 'exact_scientific_name'})
    write_json(OUT / 'curated-links.json', {'schema': 'dr-nature-curated-reference-links-v1', 'source_id': SOURCE_ID,
        'method': 'Exact scientific-name equality only; no inferred synonymy or local presence.', 'matches': links}, indent=2)
    write_json(OUT / 'source-consolidation.json', {'source_rows': len(rows), 'unique_taxa': len(records),
        'method': 'Consolidate repeated official taxon IDs only when other taxonomy fields agree; preserve alternative vernacular names and authorships.',
        'records': consolidated}, indent=2)
    summary = {'total_taxa': len(records), 'index_bytes': index_bytes, 'chunks': len(index['chunks']),
        'chunk_bytes': sum(item['bytes'] for item in index['chunks']), 'with_common_names': index['records_with_common_name'],
        'curated_exact_matches': len(links), 'groups': {group['id']: group['count'] for group in index['groups']},
        'ranks': index['ranks'], 'source_pages': len(source_manifest['pages'])}
    write_json(OUT / 'import-report.json', summary, indent=2)
    print(json.dumps(summary, ensure_ascii=True, indent=2), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--offline', action='store_true', help='Rebuild only from verified raw cached responses.')
    parser.add_argument('--refresh', action='store_true', help='Fetch a new official snapshot instead of the existing raw cache.')
    parser.add_argument('--page-size', type=int, default=5000)
    parser.add_argument('--chunk-size', type=int, default=1000)
    args = parser.parse_args()
    if not 1 <= args.page_size <= 10000 or not 100 <= args.chunk_size <= 5000: parser.error('Unsupported batch size')
    if args.offline and args.refresh: parser.error('--offline and --refresh are mutually exclusive')
    rows, manifest = download_pages(args.page_size, args.offline, args.refresh)
    build(rows, manifest, args.chunk_size)


if __name__ == '__main__': main()
