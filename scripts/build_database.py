"""Crea una base SQLite real del catálogo. La web sirve JSON; esta BD es exportable."""
import json
import sqlite3
from pathlib import Path
root=Path(__file__).resolve().parents[1]
d=json.loads((root/'dist/data/catalogue.json').read_text(encoding='utf-8'))
target=root/'data/catalogue.sqlite'
target.parent.mkdir(exist_ok=True)
if target.exists():target.unlink()
db=sqlite3.connect(target)
db.execute('PRAGMA foreign_keys=ON')
db.executescript('''
CREATE TABLE sources(id TEXT PRIMARY KEY,title TEXT NOT NULL,url TEXT NOT NULL,checked_at TEXT NOT NULL,metadata_json TEXT NOT NULL);
CREATE TABLE places(id TEXT PRIMARY KEY,name TEXT NOT NULL,name_en TEXT NOT NULL,longitude REAL NOT NULL,latitude REAL NOT NULL,summary_es TEXT,summary_en TEXT,metadata_json TEXT NOT NULL);
CREATE TABLE species(id TEXT PRIMARY KEY,name_es TEXT,name_en TEXT,scientific_name TEXT NOT NULL,taxon_group TEXT,summary_es TEXT,summary_en TEXT,metadata_json TEXT NOT NULL);
CREATE TABLE routes(id TEXT PRIMARY KEY,place_id TEXT REFERENCES places(id),name TEXT NOT NULL,distance_km REAL,duration_minutes INTEGER,ascent_m REAL,geometry_status TEXT,geojson TEXT,metadata_json TEXT NOT NULL);
CREATE TABLE place_species(place_id TEXT REFERENCES places(id),species_id TEXT REFERENCES species(id),PRIMARY KEY(place_id,species_id));
CREATE TABLE habitats(place_id TEXT REFERENCES places(id),habitat TEXT,PRIMARY KEY(place_id,habitat));
CREATE TABLE water_features(place_id TEXT REFERENCES places(id),name TEXT,PRIMARY KEY(place_id,name));
CREATE TABLE evidence(entity_type TEXT,entity_id TEXT,source_id TEXT REFERENCES sources(id),PRIMARY KEY(entity_type,entity_id,source_id));
CREATE TABLE media(file TEXT PRIMARY KEY,author TEXT,license TEXT,source_url TEXT,metadata_json TEXT);
''')
dump=lambda x:json.dumps(x,ensure_ascii=False)
for i,s in d['sources'].items():db.execute('INSERT INTO sources VALUES(?,?,?,?,?)',(i,s['title'],s['url'],s['checked_at'],dump(s)))
for p in d['places']:
    db.execute('INSERT INTO places VALUES(?,?,?,?,?,?,?,?)',(p['id'],p['name'],p['name_en'],*p['coordinates'],p['summary']['es'],p['summary']['en'],dump(p)))
    db.executemany('INSERT INTO habitats VALUES(?,?)',[(p['id'],x) for x in p['habitats']])
    db.executemany('INSERT INTO water_features VALUES(?,?)',[(p['id'],x) for x in p['water']])
for s in d['species']:db.execute('INSERT INTO species VALUES(?,?,?,?,?,?,?,?)',(s['id'],s['name']['es'],s['name']['en'],s['scientific_name'],s['group'],s['summary']['es'],s['summary']['en'],dump(s)))
for p in d['places']:db.executemany('INSERT INTO place_species VALUES(?,?)',[(p['id'],s) for s in p['species_ids']])
for r in d['routes']:
    f=root/f"dist/data/tracks/{r['id']}.geojson";g=f.read_text(encoding='utf-8') if f.exists() else None
    db.execute('INSERT INTO routes VALUES(?,?,?,?,?,?,?,?,?)',(r['id'],r['place_id'],r['name'],r['distance_km'],r['duration_minutes'],r['ascent_m'],r['geometry_status'],g,dump(r)))
for kind,key in [('place','places'),('route','routes'),('species','species')]:
    for item in d[key]:db.executemany('INSERT OR IGNORE INTO evidence VALUES(?,?,?)',[(kind,item['id'],source) for source in item.get('sources',item.get('source_ids',[]))])
for m in json.loads((root/'dist/data/attribution.json').read_text(encoding='utf-8')):db.execute('INSERT INTO media VALUES(?,?,?,?,?)',(m['file'],m['author'],m['license'],m['source_url'],dump(m)))
db.commit();assert db.execute('PRAGMA integrity_check').fetchone()[0]=='ok';assert not db.execute('PRAGMA foreign_key_check').fetchall();db.close()
print(f'Created {target.name}: {target.stat().st_size} bytes; integrity and foreign keys OK.')
