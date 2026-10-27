"""Validate official reference ingestion and settlement points shipped with the atlas."""
import json
from pathlib import Path

dist = Path(__file__).resolve().parents[1] / 'dist'
index = json.loads((dist / 'data/biodiversity/index.json').read_text(encoding='utf-8'))
metadata = json.loads((dist / 'data/biodiversity/metadata.json').read_text(encoding='utf-8'))
assert index['source']['api_url'].startswith('https://iepnb.gob.es/api/')
assert index['scope']['id'] == 'ES'
assert index['total_taxa'] == len(index['search'])
assert index['official_declared_rows'] - index['consolidated_duplicate_rows'] == index['total_taxa']
seen = {}
for i, chunk in enumerate(index['chunks']):
    file = dist / chunk['file']
    assert file.resolve().is_relative_to(dist.resolve())
    records = json.loads(file.read_text(encoding='utf-8'))['records']
    assert len(records) == chunk['count']
    for record in records:
        assert record['id'] not in seen
        assert record['scientific_name'] and record['scope'] == 'ES'
        assert record['source_url'].startswith('https://iepnb.gob.es/')
        assert 'coordinates' not in record
        seen[record['id']] = (record['scientific_name'], record['group'], i)
for identifier, name, common, group, chunk in index['search']:
    assert seen[identifier] == (name, group, chunk)
assert len(seen) == index['total_taxa']

cities = json.loads((dist / 'data/cities.geojson').read_text(encoding='utf-8'))
assert cities['type'] == 'FeatureCollection'
assert len({f['properties']['id'] for f in cities['features']}) == len(cities['features'])
assert sum(f['properties']['rank'] == 'capital' for f in cities['features']) == 6
for feature in cities['features']:
    assert feature['geometry']['type'] == 'Point'
    longitude, latitude = feature['geometry']['coordinates']
    assert -6 < longitude < -1 and 39 < latitude < 42
    assert feature['properties']['minZoom'] >= 7
print(f"OK: {len(seen):,} official national taxa in {len(index['chunks'])} chunks; {len(cities['features'])} IGN settlement points.")
