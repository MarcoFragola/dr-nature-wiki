"""Lossless geographic delivery, preserving every original JSON byte by hash."""
from pathlib import Path
import gzip, hashlib, json, shutil

ROOT=Path(__file__).resolve().parents[1]
DIST=(ROOT/'dist').resolve()
DATA=DIST/'data/geography'
BACKUP=(ROOT/'tmp/geography-uncompressed').resolve()

def sha(raw):return hashlib.sha256(raw).hexdigest()
def write(path,data):path.write_text(json.dumps(data,ensure_ascii=False,separators=(',',':'))+'\n',encoding='utf-8')

index=json.loads((DATA/'index.json').read_text(encoding='utf-8'))
original=compressed=0
for chunk in index['chunks']+index['overview_chunks']:
    path=(DIST/chunk['file']).resolve()
    assert path.is_relative_to(DATA.resolve())
    if path.suffix=='.gz':
        payload=path.read_bytes(); raw=gzip.decompress(payload)
        assert sha(raw)==chunk['uncompressed_sha256']
    else:
        raw=path.read_bytes()
        assert sha(raw)==chunk['sha256']
        payload=gzip.compress(raw,compresslevel=9,mtime=0)
        packed=path.with_name(path.name+'.gz')
        assert not packed.exists()
        packed.write_bytes(payload)
        assert gzip.decompress(packed.read_bytes())==raw
        backup=BACKUP/path.relative_to(DATA.resolve())
        assert backup.resolve().is_relative_to(BACKUP)
        backup.parent.mkdir(parents=True,exist_ok=True)
        assert not backup.exists()
        shutil.move(str(path),str(backup))
        chunk.update(file=str(packed.relative_to(DIST)).replace('\\','/'),bytes=len(payload),sha256=sha(payload),
                     encoding='gzip',uncompressed_bytes=len(raw),uncompressed_sha256=sha(raw))
    original+=len(raw);compressed+=len(payload)
write(DATA/'index.json',index)
metadata=json.loads((DATA/'metadata.json').read_text(encoding='utf-8'))
metadata['delivery']={'encoding':'gzip','lossless':True,'chunks':len(index['chunks'])+len(index['overview_chunks']),
 'original_geometry_chunk_bytes':original,'compressed_geometry_chunk_bytes':compressed,
 'verification':'SHA-256 of every decompressed payload equals the original JSON. Features, properties, coordinate precision and geometry remain unchanged.',
 'decode':'Native browser DecompressionStream; the geographic index stays plain JSON. Only requested geographic chunks are decompressed.',
 'rebuild':'After prepare_geography.py and derive_geography_regions.py, run python scripts/compress_geography.py, then the normal validation.'}
write(DATA/'metadata.json',metadata)
print(json.dumps(metadata['delivery'],ensure_ascii=False))
