import assert from 'node:assert/strict';
import test from 'node:test';
import {gzipSync} from 'node:zlib';
import {readGeographicResponse} from '../dist/geography.js';

const feature={type:'FeatureCollection',features:[{id:'miteco:enp:ES416003:ES10',type:'Feature',
 properties:{name:'Sierra Norte de Guadarrama',regionMask:3},geometry:{type:'LineString',coordinates:[[-4.123456,40.765432],[-3.987654,41.123456]]}}]};
test('compressed geographic delivery retains exact identifiers, properties and coordinates',async()=>{
 assert.deepEqual(await readGeographicResponse(new Response(gzipSync(JSON.stringify(feature))),'part.geojson.gz'),feature);
});
test('plain JSON and automatically decoded gzip responses remain compatible',async()=>{
 for(const file of ['part.geojson','part.geojson.gz'])assert.deepEqual(await readGeographicResponse(new Response(JSON.stringify(feature)),file),feature);
});
test('failed downloads and corrupt compressed payloads reject instead of returning empty features',async()=>{
 await assert.rejects(()=>readGeographicResponse(new Response('missing',{status:404}),'part.geojson.gz'));
 const bytes=gzipSync(JSON.stringify(feature)).subarray(0,10);
 await assert.rejects(()=>readGeographicResponse(new Response(bytes),'part.geojson.gz'));
});
