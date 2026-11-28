"""Compare six submitted G75 streams; never certify execution. .dlw"""
import hashlib, json, re
REV='8b7bca2810ca1fa6901c7120ac0cd4d41e91aaa0'
TARGETS=('native','native-repeat','node','node-repeat','chromium','chromium-repeat')
LIMIT=32*1024*1024

def reconcile(revision, lock, expected_lock, outputs, exits):
    result={'authority':'HOLD','authenticated':False}
    def finish(state): return dict(result,state=state)
    if revision!=REV: return finish('SOURCE_MISMATCH')
    if not isinstance(expected_lock,str) or not re.fullmatch('[0-9a-f]{64}',expected_lock): return finish('MISSING_LOCK_PIN')
    if not isinstance(lock,bytes) or len(lock)>LIMIT or hashlib.sha256(lock).hexdigest()!=expected_lock: return finish('LOCK_MISMATCH')
    if set(outputs)!=set(TARGETS) or set(exits)!=set(TARGETS): return finish('INCOMPLETE')
    if any(type(v) is not int or not 0<=v<=255 for v in exits.values()): return finish('INVALID_EXIT')
    if any(exits.values()): return finish('EXECUTION_FAILURE_DECLARED')
    if any(not isinstance(b,bytes) or not 4<len(b)<=LIMIT or not b.startswith(b'G75\0') for b in outputs.values()): return finish('INVALID_OUTPUT')
    result['sha256']={k:hashlib.sha256(outputs[k]).hexdigest() for k in TARGETS}
    result['different']=[k for k in TARGETS if outputs[k]!=outputs['native']]
    return finish('CONTRADICTORY' if result['different'] else 'CONSISTENT_SUBMISSION')
