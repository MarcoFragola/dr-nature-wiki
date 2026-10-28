import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {lessonRoute,lessonCamera} from '../dist/route-lesson-model.js';

const official=JSON.parse(fs.readFileSync(new URL('../dist/data/tracks/penalara-zabala.geojson',import.meta.url)));
test('the lesson retains every official GPX point, the start and a return destination',()=>{
  const route=lessonRoute(official),points=official.geometry.coordinates;
  assert.equal(route.segments[0],points);assert.deepEqual(route.start,points[0]);
  assert.ok(route.turn[1]>route.start[1]);assert.ok(points.includes(route.turn));
  assert.ok(route.length>4000&&route.length<5500);
  assert.ok(points.every(p=>p.length===2),'do not invent GPX elevation samples');
});
test('separate source segments are never connected by an invented line',()=>{
  const segments=[[[0,0],[0,.001]],[[30,30],[30,30.001]]];
  const route=lessonRoute({type:'MultiLineString',coordinates:segments});
  assert.equal(route.segments.length,2);assert.ok(route.length<250);
});
test('scroll camera is bounded and reduced motion has one stable pose',()=>{
  const base={center:[-3.955,40.831],zoom:14};
  for(const p of [-1,0,.25,.5,.9,1,2]){
    const camera=lessonCamera(base,p);assert.deepEqual(camera.center,base.center);
    assert.ok(camera.pitch>=34&&camera.pitch<=43);assert.ok(Number.isFinite(camera.zoom));
  }
  assert.deepEqual(lessonCamera(base,0,true),lessonCamera(base,1,true));
});
