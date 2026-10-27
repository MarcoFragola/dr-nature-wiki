import assert from 'node:assert/strict';
import test from 'node:test';
import {parseEntryRoute} from '../dist/entry-route.js';

test('official natural-feature links retain complete decoded identifiers', () => {
  assert.deepEqual(parseEntryRoute('#natural/miteco%3Aenp%3AES416003%3AES10'), {
    type: 'natural', id: 'miteco:enp:ES416003:ES10', key: 'natural:miteco:enp:ES416003:ES10',
  });
  assert.equal(parseEntryRoute('#natural/ign:watercourse:123').id, 'ign:watercourse:123');
});
test('place and route links remain compatible, including accented names', () => {
  assert.equal(parseEntryRoute('#place/penalara').type, 'place');
  assert.equal(parseEntryRoute('#route/cotos-zabala').id, 'cotos-zabala');
  assert.equal(parseEntryRoute('#place/Pe%C3%B1alara').id, 'Peñalara');
});
test('chapter anchors and malformed entry URLs do not throw or open entries', () => {
  for (const hash of ['', '#atlas', '#como-funciona', '#natural/', '#natural/%E0%A4', '#place/a%00b', '#unknown/test']) {
    assert.equal(parseEntryRoute(hash), null);
  }
});
