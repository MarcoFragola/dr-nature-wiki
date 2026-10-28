import {spawnSync} from 'node:child_process';
import {existsSync} from 'node:fs';
import {homedir} from 'node:os';
import path from 'node:path';

// Runs with an ordinary Node installation or the desktop app's bundled runtimes.
export function runPython(script){
  const bundled=path.join(homedir(),'.cache/codex-runtimes/codex-primary-runtime/dependencies/python',process.platform==='win32'?'python.exe':'bin/python3');
  const candidates=[process.env.DRNATURE_PYTHON,existsSync(bundled)?bundled:null,'python3','python'].filter(Boolean);
  for(const candidate of candidates){
    const result=spawnSync(candidate,[script],{stdio:'inherit'});
    if(result.error?.code==='ENOENT')continue;
    process.exit(result.status??1);
  }
  console.error('Python 3 is required for catalogue validation and SQLite export.');process.exit(1);
}

if(process.argv.includes('--database'))runPython('scripts/build_database.py');
else{
  for(const file of ['dist/app.js','dist/bootstrap.js','dist/map-markers.js','dist/map-layout.js','dist/album.js','dist/search.js','dist/right-drag.js','dist/entry-route.js','dist/geography.js','dist/i18n.js','dist/cover.js','dist/journey.js','dist/terrain-intro.js','dist/boundaries.js','dist/cinematic-cover.js','dist/terrain-fallback.js']){
    const result=spawnSync(process.execPath,['--check',file],{stdio:'inherit'});
    if(result.status!==0)process.exit(result.status??1);
  }
  runPython('scripts/validate_data.py');
}
