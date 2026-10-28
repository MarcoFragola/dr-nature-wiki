import test from 'node:test';
import assert from 'node:assert/strict';
import {NatureAlbum} from '../dist/album.js';

function album(query,group='all'){
  const search=[['a','Quercus pyrenaica','Roble melojo','plant'],['b','Quercus ilex','Encina','plant'],['c','Quercuz exactus','Fixture','fungus']];
  return {scope:'national',query,group,index:{search},searchTexts:search.map(r=>(r[1]+' '+r[2]).toLowerCase()),nationalCache:new Map()};
}
test('national atlas prefers exact names over approximate matches',()=>{
  const a=album('quercuz');assert.deepEqual(NatureAlbum.prototype.entries.call(a).map(r=>r[0]),['c']);assert.equal(a.approximate,false);
});
test('typo fallback retains the selected taxonomic group and cache status',()=>{
  const a=album('quercuz','plant');assert.deepEqual(NatureAlbum.prototype.entries.call(a).map(r=>r[0]),['a','b']);assert.equal(a.approximate,true);
  assert.equal(NatureAlbum.prototype.entries.call(a).length,2);assert.equal(a.approximate,true);
});
test('empty national query remains bounded by the group, without fuzzy results',()=>{
  const a=album('','fungus');assert.deepEqual(NatureAlbum.prototype.entries.call(a).map(r=>r[0]),['c']);assert.equal(a.approximate,false);
});
