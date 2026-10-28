import test from 'node:test';
import assert from 'node:assert/strict';
import {mapInsets,boundsPitch,terrainPitch,REGIONAL_BOUNDS} from '../dist/map-layout.js';

test('desktop list and detail panels leave their actual occupied region outside the camera',()=>{
 const list=mapInsets({width:1280,height:800,top:148,panel:{left:24,right:360,top:152}});
 assert.ok(list.left>360);assert.ok(1280-list.left-list.right>500);
 const detail=mapInsets({width:1280,height:800,top:148,panel:{left:828,right:1188,top:152},side:'right'});
 assert.ok(1280-detail.right<828);assert.ok(1280-detail.left-detail.right>700);
});
test('mobile camera leaves room above the bottom sheet and below search controls',()=>{
 for(const width of [375,390]){
  const p=mapInsets({width,height:844,top:180,panel:{left:12,right:width-12,top:506}});
  assert.equal(p.top,180);assert.ok(844-p.bottom<506);
  assert.ok(844-p.top-p.bottom>250);assert.ok(width-p.left-p.right>=150);
 }
});
test('short landscape and expanded panels never produce invalid native padding',()=>{
 for(const [width,height,top,panel]of [[844,390,120,{left:24,right:324,top:124}],[390,640,180,{left:12,right:378,top:180}]]){
  const p=mapInsets({width,height,top,panel});
  assert.ok(Object.values(p).every(Number.isFinite));assert.ok(Object.values(p).every(n=>n>=0));
  assert.ok(width-p.left-p.right>=149.99);assert.ok(height-p.top-p.bottom>=139.99);
 }
});
test('broad geographic views use a shallower camera while local terrain retains depth',()=>{
 assert.ok(boundsPitch(REGIONAL_BOUNDS)<boundsPitch([[-4.01,40.78],[-3.99,40.80]]));
 assert.ok(terrainPitch(8)<terrainPitch(14));
 assert.equal(boundsPitch(REGIONAL_BOUNDS,false),0);assert.equal(terrainPitch(14,false),0);
});
