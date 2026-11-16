import unittest,tempfile,json
from pathlib import Path
from hashlib import sha256
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from wag083 import AnchorHost,AnchorGate,write_anchor,demo

def h(b):return sha256(b.encode()).hexdigest()
class TestAnchorGate(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.base=Path(self.tmp.name)
        self.keys=[Ed25519PrivateKey.generate() for _ in range(3)]
        self.hosts=[AnchorHost(f'W{i+1}',f'domain-{i+1}',f'root-{i+1}',self.keys[i].public_key(),self.base/f'host{i}'/'anchor.json') for i in range(3)]
        self.gate=AnchorGate(self.hosts,self.base/'local.db',7,h('A'))
        for i in range(3):self.write(i)
    def write(self,i,epoch=7,root=None,challenge='round-7'):
        write_anchor(self.hosts[i],self.keys[i],epoch,h('A') if root is None else root,challenge)
    def state(self):return self.gate.evaluate('round-7').status
    def test_01_clean(self):self.assertEqual(self.state(),'LOCAL_RECOVERY_ELIGIBLE')
    def test_02_initial_audit(self):self.assertTrue(self.gate.verify_audit())
    def test_03_audit_growth(self):self.state();self.assertEqual(len(self.gate.audit),2)
    def test_04_missing_one(self):self.hosts[0].path.unlink();self.assertEqual(self.state(),'HOLD_ANCHOR_INCOMPLETE')
    def test_05_missing_two(self):
        for i in (0,1):self.hosts[i].path.unlink()
        self.assertEqual(self.state(),'HOLD_ANCHOR_INCOMPLETE')
    def test_06_missing_all(self):
        for host in self.hosts:host.path.unlink()
        self.assertEqual(self.state(),'HOLD_ANCHOR_INCOMPLETE')
    def test_07_restore_file(self):self.hosts[0].path.unlink();self.write(0);self.assertEqual(self.state(),'LOCAL_RECOVERY_ELIGIBLE')
    def test_08_different_root(self):self.write(2,root=h('fork'));self.assertEqual(self.state(),'QUARANTINE_CONFLICT')
    def test_09_different_epoch(self):self.write(1,epoch=8);self.assertEqual(self.state(),'QUARANTINE_CONFLICT')
    def test_10_all_anchor_ahead(self):
        for i in range(3):self.write(i,epoch=8)
        self.assertEqual(self.state(),'HOLD_ANCHOR_AHEAD')
    def test_11_all_local_ahead(self):
        for i in range(3):self.write(i,epoch=6)
        self.assertEqual(self.state(),'HOLD_LOCAL_AHEAD')
    def test_12_all_root_fork(self):
        for i in range(3):self.write(i,root=h('fork'))
        self.assertEqual(self.state(),'QUARANTINE_ROOT_FORK')
    def test_13_one_stale_nonce(self):self.write(1,challenge='old');self.assertEqual(self.state(),'HOLD_STALE_CHALLENGE')
    def test_14_all_stale_nonce(self):
        for i in range(3):self.write(i,challenge='old')
        self.assertEqual(self.state(),'HOLD_STALE_CHALLENGE')
    def test_15_recovery_from_fork(self):self.write(2,root=h('fork'));self.state();self.write(2);self.assertEqual(self.state(),'LOCAL_RECOVERY_ELIGIBLE')
    def test_16_bad_signature(self):
        obj=json.loads(self.hosts[0].path.read_text());obj['signature']='00'*64;self.hosts[0].path.write_text(json.dumps(obj))
        self.assertEqual(self.state(),'HOLD_ANCHOR_INCOMPLETE')
    def test_17_signed_identity_mismatch(self):
        obj=json.loads(self.hosts[0].path.read_text());obj['record']['host']='W9';self.hosts[0].path.write_text(json.dumps(obj))
        self.assertEqual(self.state(),'HOLD_ANCHOR_INCOMPLETE')
    def test_18_unknown_json(self):self.hosts[0].path.write_text('broken');self.assertEqual(self.state(),'HOLD_ANCHOR_INCOMPLETE')
    def test_19_extra_field(self):
        obj=json.loads(self.hosts[0].path.read_text());obj['extra']=1;self.hosts[0].path.write_text(json.dumps(obj));self.assertEqual(self.state(),'HOLD_ANCHOR_INCOMPLETE')
    def test_20_empty_signature(self):
        obj=json.loads(self.hosts[0].path.read_text());obj['signature']='';self.hosts[0].path.write_text(json.dumps(obj));self.assertEqual(self.state(),'HOLD_ANCHOR_INCOMPLETE')
    def test_21_invalid_epoch(self):
        with self.assertRaises(ValueError):AnchorGate(self.hosts,self.base/'local',-1,h('A'))
    def test_22_invalid_root(self):
        with self.assertRaises(ValueError):AnchorGate(self.hosts,self.base/'local',7,'bad')
    def test_23_duplicate_domain(self):
        x=[self.hosts[0],AnchorHost('W2',self.hosts[0].domain,'r2',self.keys[1].public_key(),self.hosts[1].path),self.hosts[2]]
        with self.assertRaises(ValueError):AnchorGate(x,self.base/'local',7,h('A'))
    def test_24_duplicate_ancestor(self):
        x=[self.hosts[0],AnchorHost('W2','d2',self.hosts[0].ancestor,self.keys[1].public_key(),self.hosts[1].path),self.hosts[2]]
        with self.assertRaises(ValueError):AnchorGate(x,self.base/'local',7,h('A'))
    def test_25_duplicate_name(self):
        x=[self.hosts[0],AnchorHost('W1','d2','r2',self.keys[1].public_key(),self.hosts[1].path),self.hosts[2]]
        with self.assertRaises(ValueError):AnchorGate(x,self.base/'local',7,h('A'))
    def test_26_duplicate_path(self):
        x=[self.hosts[0],AnchorHost('W2','d2','r2',self.keys[1].public_key(),self.hosts[0].path),self.hosts[2]]
        with self.assertRaises(ValueError):AnchorGate(x,self.base/'local',7,h('A'))
    def test_27_fewer_than_three(self):
        with self.assertRaises(ValueError):AnchorGate(self.hosts[:2],self.base/'local',7,h('A'))
    def test_28_no_challenge(self):
        with self.assertRaises(ValueError):self.gate.evaluate('')
    def test_29_tamper_ledger(self):self.state();self.gate.audit[1]['details']['decision']='fake';self.assertFalse(self.gate.verify_audit())
    def test_30_audit_after_conflict(self):self.write(2,root=h('fork'));self.state();self.assertTrue(self.gate.verify_audit())
    def test_31_signature_binds_challenge(self):
        obj=json.loads(self.hosts[2].path.read_text());obj['record']['challenge']='other';self.hosts[2].path.write_text(json.dumps(obj));self.assertEqual(self.state(),'HOLD_ANCHOR_INCOMPLETE')
    def test_32_immutable_domains(self):self.assertEqual(len({x.domain for x in self.hosts}),3)
    def test_33_root_normalization(self):self.assertEqual(len(self.gate.root),64)
    def test_34_valid_signature_bytes(self):self.assertEqual(len(bytes.fromhex(json.loads(self.hosts[0].path.read_text())['signature'])),64)
    def test_35_replay_round_hold(self):self.assertEqual(self.gate.evaluate('round-8').status,'HOLD_STALE_CHALLENGE')
    def test_36_demo(self):
        with tempfile.TemporaryDirectory() as d:
            gate,a,b,c=demo(d)
            self.assertEqual([a.status,b.status,c.status],['LOCAL_RECOVERY_ELIGIBLE','QUARANTINE_CONFLICT','LOCAL_RECOVERY_ELIGIBLE']);self.assertTrue(gate.verify_audit())
if __name__=='__main__':unittest.main()
