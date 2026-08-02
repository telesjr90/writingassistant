import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { readFile } from 'node:fs/promises';
import { after, test } from 'node:test';
import { createServer } from 'vite';

import {
  buildFinalChallengeRequest,
  buildReferenceOnlyApplyPromotionRequest,
  canonicalizeFinalChallengeValue,
  classifyApplyPromotionFailure,
  computeFinalChallengeResponse,
  getFinalChallengeTemporalState,
} from '../src/api.js';


const HASH_A = 'a'.repeat(64);
const HASH_B = 'b'.repeat(64);
const CHALLENGE_ID = `challenge_0123456789abcdef_${'c'.repeat(64)}`;
const UUID_A = '11111111-1111-4111-8111-111111111111';
const UUID_B = '22222222-2222-4222-8222-222222222222';

const frontendRoot = new URL('..', import.meta.url).pathname;
const confirmationPath = new URL('../src/components/ApplyPromotionConfirmation.jsx', import.meta.url);
const viteServer = await createServer({
  root: frontendRoot,
  appType: 'custom',
  logLevel: 'silent',
  server: { middlewareMode: true },
});
const confirmationModule = await viteServer.ssrLoadModule('/src/components/ApplyPromotionConfirmation.jsx');
const {
  appendDependencyInputEntry,
  buildDependencyResolutionInput,
  createEmptyDependencyInputEntry,
  getDependencyResolutionBlockers,
  normalizeDependencyInputEntry,
  removeDependencyInputEntry,
  updateDependencyInputEntry,
} = confirmationModule;

after(async () => {
  await viteServer.close();
});

function completeDependency(status = 'blocked') {
  return {
    dependency_id: 'dependency_one',
    kind: 'approved_record',
    required: true,
    status,
    target_mode: 'record',
    target: {
      destination_type: 'approved_character',
      destination_key: 'character_one',
      record_version: '2',
      content_hash: HASH_A,
    },
    rationale: 'The owner recorded the bounded dependency outcome.',
    evidence_ref_ids: ['evidence_1'],
    provenance_ref_ids: ['provenance_1'],
    applicability_rule: 'Applies to this approved character record.',
  };
}

function challengeFixture() {
  const nonceBytes = Uint8Array.from({ length: 32 }, (_, index) => index);
  const challengeScope = {
    protocol: 'apply-promotion-final-challenge.v1',
    project_id: 'project_a',
    promotion_id: 'promotion_a',
    revision: 3,
    sealed_contract_hash: HASH_A,
    before_state_snapshot_token: HASH_B,
    operation: 'update',
    destination_path: 'writer_assistant/approved_memory/approved_character/character_a.json',
    authoritative_owner_actor: {
      actor_type: 'owner',
      owner_id: 'owner_a',
      display_name: 'Local Owner',
      identity_source: 'project_local_owner_config',
      config_version: 2,
      config_hash: 'd'.repeat(64),
    },
    challenge_id: CHALLENGE_ID,
    issued_at: '2026-08-01T00:00:00Z',
    expires_at: '2026-08-01T00:02:00Z',
  };
  return {
    challenge_id: CHALLENGE_ID,
    challenge_nonce: Buffer.from(nonceBytes).toString('base64url'),
    response_algorithm: 'sha256-canonical-final-confirmation-v1',
    challenge_scope: challengeScope,
    replayed: false,
    nonceBytes,
  };
}

test('challenge request is closed and reference-only', () => {
  assert.deepEqual(buildFinalChallengeRequest({
    revision: 3,
    sealedContractHash: HASH_A,
    beforeStateSnapshotToken: HASH_B,
    idempotencyKey: UUID_A,
  }), {
    revision: 3,
    sealed_contract_hash: HASH_A,
    before_state_snapshot_token: HASH_B,
    idempotency_key: UUID_A,
  });
});

test('canonical challenge JSON sorts nested keys and preserves Unicode', () => {
  assert.equal(
    canonicalizeFinalChallengeValue({ z: 1, a: { y: 'é', b: true } }),
    '{"a":{"b":true,"y":"é"},"z":1}',
  );
});

test('challenge response matches the independent accepted preimage hash', async () => {
  const challenge = challengeFixture();
  const canonical = canonicalizeFinalChallengeValue({
    challenge_scope: challenge.challenge_scope,
    final_confirmation: {
      confirmed: true,
      method: 'explicit_final_apply_confirmation',
    },
  });
  const expected = createHash('sha256')
    .update(Buffer.from('apply-promotion-final-confirmation-v1\0', 'utf8'))
    .update(Buffer.from(challenge.nonceBytes))
    .update(Buffer.from([0]))
    .update(Buffer.from(canonical, 'utf8'))
    .digest('hex');

  assert.equal(await computeFinalChallengeResponse(challenge), expected);
});

test('final apply request contains exactly the eight accepted fields', () => {
  const request = buildReferenceOnlyApplyPromotionRequest({
    promotionId: 'promotion_a',
    revision: 3,
    sealedContractHash: HASH_A,
    beforeStateSnapshotToken: HASH_B,
    challengeId: CHALLENGE_ID,
    challengeResponse: 'e'.repeat(64),
    idempotencyKey: UUID_B,
  });
  assert.deepEqual(Object.keys(request).sort(), [
    'before_state_snapshot_token',
    'challenge_id',
    'challenge_response',
    'final_confirmation',
    'idempotency_key',
    'promotion_id',
    'revision',
    'sealed_contract_hash',
  ]);
  assert.deepEqual(request.final_confirmation, {
    confirmed: true,
    method: 'explicit_final_apply_confirmation',
  });
  for (const forbidden of [
    'owner_actor',
    'destination_path',
    'approved_payload',
    'evidence_refs',
    'provenance_refs',
    'source_locator_refs',
  ]) {
    assert.equal(Object.hasOwn(request, forbidden), false);
  }
});

test('challenge timing is explicit at active and expired boundaries', () => {
  const challenge = challengeFixture();
  assert.deepEqual(
    getFinalChallengeTemporalState(challenge, Date.parse('2026-08-01T00:01:00Z')),
    { state: 'active', secondsRemaining: 60 },
  );
  assert.deepEqual(
    getFinalChallengeTemporalState(challenge, Date.parse('2026-08-01T00:02:00Z')),
    { state: 'expired', secondsRemaining: 0 },
  );
});

test('backend errors map to distinct challenge and recovery states', () => {
  assert.deepEqual(classifyApplyPromotionFailure('FINAL_CHALLENGE_EXPIRED'), {
    challengeState: 'expired',
    applyState: 'not_started',
  });
  assert.deepEqual(classifyApplyPromotionFailure('FINAL_CHALLENGE_REPLACED'), {
    challengeState: 'replaced',
    applyState: 'not_started',
  });
  assert.deepEqual(classifyApplyPromotionFailure('FINAL_CHALLENGE_REQUIRED_AFTER_RESTART'), {
    challengeState: 'restart_invalidated',
    applyState: 'not_started',
  });
  assert.deepEqual(classifyApplyPromotionFailure('RECOVERY_REQUIRED'), {
    challengeState: 'consumed',
    applyState: 'recovery_required',
  });
  assert.deepEqual(classifyApplyPromotionFailure('APPLY_FAILED_BEFORE_COMMIT'), {
    challengeState: 'consumed',
    applyState: 'not_committed',
  });
  assert.deepEqual(classifyApplyPromotionFailure('APPLY_CONTRACT_BEFORE_STATE_CHANGED'), {
    challengeState: null,
    applyState: 'blocked',
  });
  assert.deepEqual(classifyApplyPromotionFailure(null), {
    challengeState: null,
    applyState: 'failed',
  });
});

test('dependency resolution cardinality blocks zero-entry blocked and satisfied states', () => {
  for (const state of ['blocked', 'satisfied']) {
    assert.deepEqual(getDependencyResolutionBlockers({
      state,
      dependencies: [],
      rationale: 'Owner-entered resolution rationale.',
      evidenceRefIds: ['evidence_1'],
    }), [`Dependency decision "${state}" requires at least one dependency entry.`]);
  }
});

test('none_declared remains valid with exactly zero dependency entries', () => {
  assert.deepEqual(getDependencyResolutionBlockers({
    state: 'none_declared',
    dependencies: [],
    rationale: 'The owner found no dependencies in the reviewed scope.',
    evidenceRefIds: ['evidence_1'],
  }), []);
  assert.deepEqual(buildDependencyResolutionInput({
    state: 'none_declared',
    dependencies: [],
    rationale: '  The owner found no dependencies in the reviewed scope.  ',
    evidenceRefIds: ['evidence_1'],
  }), {
    state: 'none_declared',
    dependencies: [],
    rationale: 'The owner found no dependencies in the reviewed scope.',
    evidence_ref_ids: ['evidence_1'],
  });
});

test('complete blocked and satisfied dependencies produce the exact accepted input shape', () => {
  for (const state of ['blocked', 'satisfied']) {
    const dependency = completeDependency(state);
    assert.deepEqual(buildDependencyResolutionInput({
      state,
      dependencies: [dependency],
      rationale: 'Owner-entered resolution rationale.',
      evidenceRefIds: ['evidence_1'],
    }), {
      state,
      dependencies: [{
        dependency_id: 'dependency_one',
        kind: 'approved_record',
        required: true,
        status: state,
        target: {
          destination_type: 'approved_character',
          destination_key: 'character_one',
          record_version: 2,
          content_hash: HASH_A,
        },
        rationale: 'The owner recorded the bounded dependency outcome.',
        evidence_ref_ids: ['evidence_1'],
        provenance_ref_ids: ['provenance_1'],
        applicability_rule: 'Applies to this approved character record.',
      }],
      rationale: 'Owner-entered resolution rationale.',
      evidence_ref_ids: ['evidence_1'],
    });
  }
});

test('incomplete nested dependency fields produce specific visible blockers', () => {
  const empty = createEmptyDependencyInputEntry();
  const blockers = getDependencyResolutionBlockers({
    state: 'blocked',
    dependencies: [empty],
    rationale: 'Owner-entered resolution rationale.',
    evidenceRefIds: ['evidence_1'],
  });
  for (const expected of [
    'Dependency 1: Enter a stable dependency ID.',
    'Dependency 1: Enter an accepted dependency kind.',
    'Dependency 1: Choose required or not required.',
    'Dependency 1: Choose a dependency status.',
    'Dependency 1: Choose whether this dependency has a target record.',
    'Dependency 1: Enter a dependency rationale.',
    'Dependency 1: Select at least one evidence reference.',
    'Dependency 1: Select at least one provenance reference.',
  ]) {
    assert.equal(blockers.includes(expected), true, expected);
  }
});

test('dependency entry add update and remove preserve owner-entered sibling values', () => {
  const first = { ...createEmptyDependencyInputEntry(), dependency_id: 'first_dependency' };
  const withSecond = appendDependencyInputEntry([first]);
  assert.equal(withSecond.length, 2);
  const updated = updateDependencyInputEntry(withSecond, 1, {
    dependency_id: 'second_dependency',
    rationale: 'Owner-entered second rationale.',
  });
  assert.equal(updated[0].dependency_id, 'first_dependency');
  assert.equal(updated[1].dependency_id, 'second_dependency');
  assert.equal(updated[1].rationale, 'Owner-entered second rationale.');
  assert.deepEqual(removeDependencyInputEntry(updated, 0), [updated[1]]);
});

test('empty and normalized entries do not manufacture authority or owner evidence', () => {
  const empty = createEmptyDependencyInputEntry();
  assert.deepEqual(empty, {
    dependency_id: '',
    kind: '',
    required: null,
    status: '',
    target_mode: '',
    target: {
      destination_type: '',
      destination_key: '',
      record_version: '',
      content_hash: '',
    },
    rationale: '',
    evidence_ref_ids: [],
    provenance_ref_ids: [],
    applicability_rule: '',
  });
  const normalized = normalizeDependencyInputEntry(completeDependency());
  for (const forbidden of ['resolved_by', 'resolved_at', 'owner_actor', 'actor', 'resolution_scope_hash']) {
    assert.equal(Object.hasOwn(normalized, forbidden), false);
  }
});

test('dependency controls retain retry semantics and introduce no authentication or canon claim', async () => {
  const source = await readFile(confirmationPath, 'utf8');
  assert.match(source, /const \[dependencyEntries, setDependencyEntries\] = useState\(\[\]\)/);
  assert.match(source, /const request = recoveryRequest \?\? buildPreparationRequest\(\)/);
  assert.match(source, /setRecoveryRequest\(request\)/);
  assert.match(source, /aria-describedby=\{entryBlockerId\}/);
  assert.doesNotMatch(source, /dependency[^\n]{0,80}(authenticates|authentication proof|becomes canon)/i);
});
