import unittest,tempfile,sqlite3
from dataclasses import replace
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from wag092 import Gate,sign_beacon,sign_receipt,sample,demo
class WAG092(unittest.TestCase):
    def setUp(self):
        self.t=tempfile.TemporaryDirectory();self.addCleanup(self.t.cleanup)
        self.path=Path(self.t.name)/'gate.db'
        self.bs=Ed25519PrivateKey.generate()
        self.hs={w:Ed25519PrivateKey.generate() for w in ('W1','W2','W3')}
        self.g=Gate(self.path,self.bs.public_key(),{w:k.public_key() for w,k in self.hs.items()})
        self.b=sign_beacon(self.bs,'cp',92,b'fixed beacon signed output')
    def freeze(self):return self.g.freeze(self.b,17,3,'root')
    def proofs(self):
        ix=self.g.state('cp',92)[0]
        return [sign_receipt(sk,w,'cp',92,ix,'root','id-'+w) for w,sk in self.hs.items()]
    def test_demo(self):self.assertTrue(demo(Path(self.t.name)/'other.db')['audit'])
    def test_positions(self):self.assertEqual(len(set(self.freeze())),3)
    def test_bound(self):self.assertTrue(all(0<=i<17 for i in self.freeze()))
    def test_deterministic(self):self.assertEqual(sample('cp',92,b'x'*32,17,3),sample('cp',92,b'x'*32,17,3))
    def test_epoch_domain(self):self.assertNotEqual(sample('cp',92,b'x'*32,257,10),sample('cp',93,b'x'*32,257,10))
    def test_all_positions(self):self.assertEqual(set(sample('cp',92,b'x'*32,4,4)),set(range(4)))
    def test_invalid_n(self):
        with self.assertRaises(ValueError):sample('cp',92,b'x'*32,0,1)
    def test_invalid_k(self):
        with self.assertRaises(ValueError):sample('cp',92,b'x'*32,4,5)
    def test_invalid_beacon(self):
        with self.assertRaises(Exception):self.g.freeze(replace(self.b,sig=b'0'*64),17,3,'root')
    def test_no_redraw(self):
        self.freeze()
        with self.assertRaises(Exception):self.g.freeze(sign_beacon(self.bs,'cp',92,b'another signed beacon output'),17,3,'root')
    def test_restart(self):
        ix=self.freeze()
        self.g=Gate(self.path,self.bs.public_key(),{w:k.public_key() for w,k in self.hs.items()})
        self.assertEqual(self.g.state('cp',92)[0],ix)
    def test_abort(self):self.freeze();self.g.abort('cp',92);self.assertEqual(self.g.state('cp',92)[1],'HOLD_ABORT')
    def test_abort_twice(self):
        self.freeze();self.g.abort('cp',92)
        with self.assertRaises(ValueError):self.g.abort('cp',92)
    def test_same_sample(self):
        ix=self.freeze();self.g.abort('cp',92);self.assertEqual(self.g.recover_same_sample('cp',92),ix)
    def test_no_unconditional_recovery(self):
        self.freeze()
        with self.assertRaises(ValueError):self.g.recover_same_sample('cp',92)
    def test_accept(self):self.freeze();self.assertEqual(self.g.accept('cp',92,self.proofs()),'LOCAL_ELIGIBLE')
    def test_replay(self):
        self.freeze();r=self.proofs();self.g.accept('cp',92,r)
        with self.assertRaises(ValueError):self.g.accept('cp',92,r)
    def test_missing_host(self):
        self.freeze()
        with self.assertRaises(ValueError):self.g.accept('cp',92,self.proofs()[:2])
    def test_duplicate_host(self):
        self.freeze();r=self.proofs()
        with self.assertRaises(ValueError):self.g.accept('cp',92,[r[0],r[0],r[2]])
    def test_bad_root(self):
        self.freeze();r=self.proofs();r[0]=replace(r[0],root='wrong')
        with self.assertRaises(ValueError):self.g.accept('cp',92,r)
    def test_wrong_sample(self):
        self.freeze();r=self.proofs();r[0]=replace(r[0],indices=(1,2,3))
        with self.assertRaises(ValueError):self.g.accept('cp',92,r)
    def test_signature_forged(self):
        self.freeze();r=self.proofs();r[0]=replace(r[0],sig=b'0'*64)
        with self.assertRaises(Exception):self.g.accept('cp',92,r)
    def test_audit_tamper(self):
        self.freeze()
        with sqlite3.connect(self.path) as db:db.execute("UPDATE audit SET kind='FAKE' WHERE seq=1")
        self.assertFalse(self.g.verify_audit())
    def test_audit_valid(self):
        self.freeze();self.g.abort('cp',92);self.g.recover_same_sample('cp',92);self.g.accept('cp',92,self.proofs())
        self.assertTrue(self.g.verify_audit())
if __name__=='__main__':unittest.main()
