import assert from 'node:assert/strict';
import test from 'node:test';

import {
  describeNcpInterfaceState,
  validateNcpDestinationIdentifier,
} from '../src/omiAnalysisRunWorkflow.js';

test('NCP destination validation accepts only new opaque identifiers', () => {
  assert.deepEqual(validateNcpDestinationIdentifier('owner-export.2026_01'), {
    valid: true,
    code: 'operator_selected_new_target',
    message: 'Safe opaque identifier selected for a new target. No path or write is authorized.',
  });

  for (const unsafe of [
    '../escape',
    '/absolute/path',
    'folder/name',
    'folder\\name',
    '.',
    '..',
    '',
  ]) {
    assert.equal(validateNcpDestinationIdentifier(unsafe).valid, false, unsafe);
  }
});

test('NCP destination validation blocks destructive target semantics', () => {
  for (const destructive of [
    'overwrite-target',
    'overwriteExisting',
    'replace_existing',
    'delete.artifact',
    'purge-retained-data',
  ]) {
    const result = validateNcpDestinationIdentifier(destructive);
    assert.equal(result.valid, false, destructive);
    assert.equal(result.code, 'destructive_destination_semantics');
  }
});

test('NCP interface states distinguish loading, empty, invalid, unavailable, failure, and success', () => {
  for (const state of ['loading', 'empty', 'invalid', 'unavailable', 'request_failure']) {
    assert.equal(describeNcpInterfaceState(state).operable, false, state);
  }

  assert.deepEqual(describeNcpInterfaceState('success'), {
    tone: 'is-success',
    label: 'Diagnostics available',
    operable: true,
  });
  assert.equal(describeNcpInterfaceState('unknown').label, 'Interface unavailable');
});
