import unittest
from hashlib import sha256
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from wag095 import Authority, ReceiptGate, sign, demo

class Tests(unittest.TestCase):
    def setUp(self):
        self.keys={n:Ed25519PrivateKey.generate() for n in ('A','B','C','beacon')}
        auth={n:Authority(n,'root-'+n,'owner-'+n,'zone-'+n,self.keys[n].public_key()) for n in ('A','B','C')}
        beacon=Authority('beacon','root-beacon','owner-beacon','zone-beacon',self.keys['beacon'].public_key())
        self.g=ReceiptGate(auth,beacon,95,sha256(b'archive').hexdigest(),7)
    def obs(self,n,slot=12, **overrides):
        s={**self.g.expected(),'slot':slot,**overrides}
        self.g.observe(n,s,sign(self.keys[n],s))
    def fill(self,slot=12):
        for n in ('A','B','C'):self.obs(n,slot)
    def rel(self,slot=13,**overrides):
        s={'kind':'beacon-released','epoch':95,'round':7,'root':self.g.checkpoint,
           'receipt_set':self.g.freeze_hash,'slot':slot,'entropy':sha256(b'beacon').hexdigest(),**overrides}
        return self.g.release_beacon(s,sign(self.keys['beacon'],s))
    def test_01_demo(self):self.assertTrue(demo()[1]['verified'])
    def test_02_genesis(self):self.assertEqual(len(self.g.history),1)
    def test_03_missing(self):self.assertEqual(self.g.decision(),'HOLD_OBSERVERS_MISSING')
    def test_04_one(self):self.obs('A');self.assertEqual(len(self.g.receipts),1)
    def test_05_three(self):self.fill();self.assertEqual(len(self.g.receipts),3)
    def test_06_freeze(self):self.fill();self.assertEqual(len(self.g.freeze()),64)
    def test_07_post_freeze(self):self.fill();self.g.freeze();self.assertEqual(self.g.decision(),'HOLD_BEACON_MISSING')
    def test_08_valid_release(self):self.fill();self.g.freeze();self.assertEqual(self.rel(),'LOCAL_DECLARED_ORDER_ACCEPTED')
    def test_09_history(self):self.fill();self.g.freeze();self.rel();self.assertEqual(len(self.g.history),6)
    def test_10_verify(self):self.fill();self.g.freeze();self.rel();self.assertTrue(self.g.audit_valid())
    def test_11_tamper(self):self.fill();self.g.history[1]['data']['name']='X';self.assertFalse(self.g.audit_valid())
    def test_12_duplicate_receipt(self):
        self.obs('A')
        with self.assertRaises(ValueError):self.obs('A')
    def test_13_unknown_receipt(self):
        with self.assertRaises(ValueError):self.g.observe('D',{**self.g.expected(),'slot':12},'bad')
    def test_14_wrong_root(self):
        with self.assertRaises(ValueError):self.obs('A',root='f'*64)
    def test_15_wrong_epoch(self):
        with self.assertRaises(ValueError):self.obs('A',epoch=96)
    def test_16_wrong_round(self):
        with self.assertRaises(ValueError):self.obs('A',round=9)
    def test_17_wrong_kind(self):
        with self.assertRaises(ValueError):self.obs('A',kind='irrelevant')
    def test_18_slot_negative(self):
        with self.assertRaises(ValueError):self.obs('A',slot=-1)
    def test_19_bad_sig(self):
        s={**self.g.expected(),'slot':12}
        with self.assertRaises(ValueError):self.g.observe('A',s,sign(self.keys['B'],s))
    def test_20_missing_receipt_freeze(self):
        self.obs('A')
        with self.assertRaises(ValueError):self.g.freeze()
    def test_21_disagree_slots(self):
        self.obs('A',12);self.obs('B',12);self.obs('C',13)
        with self.assertRaises(ValueError):self.g.freeze()
    def test_22_repeat_freeze(self):
        self.fill();self.g.freeze()
        with self.assertRaises(ValueError):self.g.freeze()
    def test_23_release_without_freeze(self):
        with self.assertRaises(ValueError):self.rel()
    def test_24_equal_slot(self):
        self.fill();self.g.freeze()
        with self.assertRaises(ValueError):self.rel(slot=12)
    def test_25_earlier_release(self):
        self.fill();self.g.freeze()
        with self.assertRaises(ValueError):self.rel(slot=11)
    def test_26_wrong_receiptset(self):
        self.fill();self.g.freeze()
        with self.assertRaises(ValueError):self.rel(receipt_set='f'*64)
    def test_27_wrong_release_epoch(self):
        self.fill();self.g.freeze()
        with self.assertRaises(ValueError):self.rel(epoch=2)
    def test_28_wrong_release_root(self):
        self.fill();self.g.freeze()
        with self.assertRaises(ValueError):self.rel(root='0'*64)
    def test_29_wrong_release_round(self):
        self.fill();self.g.freeze()
        with self.assertRaises(ValueError):self.rel(round=0)
    def test_30_invalid_entropy(self):
        self.fill();self.g.freeze()
        with self.assertRaises(ValueError):self.rel(entropy='wrong')
    def test_31_repeat_release(self):
        self.fill();self.g.freeze();self.rel()
        with self.assertRaises(ValueError):self.rel()
    def test_32_bad_beacon_sig(self):
        self.fill();self.g.freeze()
        s={'kind':'beacon-released','epoch':95,'round':7,'root':self.g.checkpoint,'receipt_set':self.g.freeze_hash,'slot':13,'entropy':'a'*64}
        with self.assertRaises(ValueError):self.g.release_beacon(s,sign(self.keys['A'],s))
    def test_33_no_mutation_bad_release(self):
        self.fill();self.g.freeze();n=len(self.g.history)
        with self.assertRaises(ValueError):self.rel(slot=11)
        self.assertEqual(len(self.g.history),n)
    def test_34_no_mutation_bad_observe(self):
        n=len(self.g.history)
        with self.assertRaises(ValueError):self.obs('A',root='a'*64)
        self.assertEqual(len(self.g.history),n)
    def test_35_duplicate_ancestry(self):
        a=dict(self.g.authorities);w=a['B'];a['B']=Authority('B',a['A'].ancestry,w.controller,w.domain,w.public_key)
        with self.assertRaises(ValueError):ReceiptGate(a,self.g.beacon,95,self.g.checkpoint,7)
    def test_36_duplicate_controller(self):
        a=dict(self.g.authorities);w=a['B'];a['B']=Authority('B',w.ancestry,a['A'].controller,w.domain,w.public_key)
        with self.assertRaises(ValueError):ReceiptGate(a,self.g.beacon,95,self.g.checkpoint,7)
    def test_37_duplicate_domain(self):
        a=dict(self.g.authorities);w=a['B'];a['B']=Authority('B',w.ancestry,w.controller,a['A'].domain,w.public_key)
        with self.assertRaises(ValueError):ReceiptGate(a,self.g.beacon,95,self.g.checkpoint,7)
    def test_38_beacon_overlap(self):
        b=Authority('beacon',self.g.authorities['A'].ancestry,'beaconowner','beacondomain',self.keys['beacon'].public_key())
        with self.assertRaises(ValueError):ReceiptGate(self.g.authorities,b,95,self.g.checkpoint,7)
    def test_39_bad_root(self):
        with self.assertRaises(ValueError):ReceiptGate(self.g.authorities,self.g.beacon,95,'bad',7)
    def test_40_bad_epoch(self):
        with self.assertRaises(ValueError):ReceiptGate(self.g.authorities,self.g.beacon,-1,self.g.checkpoint,7)
    def test_41_frozen_receipt(self):
        self.fill();self.g.freeze()
        with self.assertRaises(ValueError):self.obs('A')
    def test_42_preserve_failed_beacon(self):
        self.fill();self.g.freeze()
        with self.assertRaises(ValueError):self.rel(slot=12)
        self.assertIsNone(self.g.release)

if __name__=='__main__':unittest.main()