"""Export explicit provenance for existing editorial species/place links.

No observations or coordinates are inferred. Shared official area sources may
support regional distribution; all remaining editorial links stay habitat context.
"""
import json
from pathlib import Path
root = Path(__file__).resolve().parents[1]
catalogue = json.loads((root/'dist/data/catalogue.json').read_text(encoding='utf-8'))
species = {s['id']: s for s in catalogue['species']}
records = []
for place in catalogue['places']:
    for identifier in place['species_ids']:
        taxon = species[identifier]
        shared = [s for s in taxon['sources'] if s in place['sources'] and catalogue['sources'][s].get('type') == 'official']
        managed = place['id'] == 'centro-lobo-iberico' and identifier == 'lobo-iberico'
        kind = 'managed_collection' if managed else 'regional_distribution' if shared and taxon.get('observation_status') == 'regional_documented_presence_not_live_sighting' else 'habitat_context'
        records.append({
            'id': f"{place['id']}:{identifier}", 'place_id': place['id'], 'species_id': identifier,
            'relation_type': kind, 'source_ids': shared or list(dict.fromkeys(place['sources'] + taxon['sources'])),
            'geographic_scope': taxon.get('documented_area'), 'verified_at': place.get('verified_at'),
            'observation_id': None, 'local_presence_confirmed': False,
        })
result = {
    'schema': 'dr-nature-species-relations-v1', 'generated_at': '2026-10-27',
    'observations': [], 'records': records,
    'method': 'Existing editorial links classified conservatively. Regional distribution requires a shared official area source and an existing regional distribution status. Other links remain habitat context. Managed animals are separate from wildlife observations.',
    'limitation': 'No point observation or guaranteed local presence is established by these relations. No occurrence coordinates are published.',
}
target = root/'dist/data/species-relations.json'
target.write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
print(f'Exported {len(records)} sourced contextual relations; 0 point observations inferred.')
