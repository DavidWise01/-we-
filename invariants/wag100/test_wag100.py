import os,tempfile,unittest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding,PublicFormat
from wag100 import Identity,Succession,sign,check,demo

class Tests(unittest.TestCase):
    def setUp(self):
        self.d=tempfile.TemporaryDirectory();self.addCleanup(self.d.cleanup)
        self.path=os.path.join(self.d.name,'x.sqlite')
        self.keys={w:Ed25519PrivateKey.generate() for w in ('W1','W2','W3','W4','W5')}
        self.ids=[Identity(w,'ancestry-'+w,'controller-'+w,'domain-'+w,self.keys[w].public_key().public_bytes(Encoding.Raw,PublicFormat.Raw)) for w in self.keys]
        self.a=Succession(self.path,self.ids)
    def proposal(self,new='W4',root='root-100'):
        s=self.a.state();return {'operation':'rotate','old':'W1','new':new,'epoch':s['epoch'],'prior_root':s['root'],'next_root':root,'challenge':s['challenge']}
    def reviews(self,p=None):
        p=p or self.proposal();return {w:sign(self.keys[w],p) for w in ('W2','W3')}
    def rotate(self):
        self.a.revoke('W1','signed-conflict')
        p=self.proposal();return self.a.rotate('W1','W4',self.reviews(p),'root-100')
    def attest(self):
        s=self.a.state();p={'operation':'attest','epoch':s['epoch'],'root':s['root'],'challenge':s['challenge'],'roster':sorted(s['roster'])}
        return {w:sign(self.keys[w],p) for w in s['roster']}
    def test_01_initial_epoch(self):self.assertEqual(self.a.state()['epoch'],99)
    def test_02_initial_roster(self):self.assertEqual(self.a.state()['roster'],('W1','W2','W3'))
    def test_03_initial_audit(self):self.assertTrue(self.a.audit())
    def test_04_revocation_persistent(self):self.a.revoke('W1','proof');self.assertEqual(self.a.historic('W1'),(99,'proof'))
    def test_05_revocation_holds(self):self.a.revoke('W1','proof');self.assertEqual(self.a.state()['quarantined'],'W1')
    def test_06_no_empty_evidence(self):
        with self.assertRaises(ValueError):self.a.revoke('W1','')
    def test_07_unknown_revoke(self):
        with self.assertRaises(ValueError):self.a.revoke('W4','proof')
    def test_08_duplicate_revocation(self):
        self.a.revoke('W1','proof')
        with self.assertRaises(ValueError):self.a.revoke('W1','again')
    def test_09_rotate_ok(self):self.rotate();self.assertEqual(self.a.state()['roster'],('W2','W3','W4'))
    def test_10_epoch_increment(self):self.rotate();self.assertEqual(self.a.state()['epoch'],100)
    def test_11_challenge_rotation(self):self.rotate();self.assertEqual(self.a.state()['challenge'],'challenge-100')
    def test_12_evidence_still_present(self):self.rotate();self.assertEqual(self.a.historic('W1'),(99,'signed-conflict'))
    def test_13_no_rotate_without_revoke(self):
        with self.assertRaises(ValueError):self.a.rotate('W1','W4',self.reviews(),'root-100')
    def test_14_missing_review(self):
        self.a.revoke('W1','proof')
        with self.assertRaises(ValueError):self.a.rotate('W1','W4',{'W2':self.reviews()['W2']},'root-100')
    def test_15_forged_review(self):
        self.a.revoke('W1','proof');x=self.reviews();x['W2']=sign(self.keys['W4'],self.proposal())
        with self.assertRaises(ValueError):self.a.rotate('W1','W4',x,'root-100')
    def test_16_wrong_proposal(self):
        self.a.revoke('W1','proof')
        with self.assertRaises(ValueError):self.a.rotate('W1','W4',self.reviews(self.proposal(root='wrong')),'root-100')
    def test_17_new_root_required(self):
        self.a.revoke('W1','proof')
        with self.assertRaises(ValueError):self.a.rotate('W1','W4',self.reviews(),'root-99')
    def test_18_unknown_candidate(self):
        self.a.revoke('W1','proof')
        with self.assertRaises(ValueError):self.a.rotate('W1','W9',self.reviews(),'root-100')
    def test_19_new_identity_current(self):
        self.a.revoke('W1','proof')
        with self.assertRaises(ValueError):self.a.rotate('W1','W2',self.reviews(),'root-100')
    def test_20_old_key_reuse(self):
        bad=list(self.ids);old=self.a.ids['W1'];new=self.a.ids['W4']
        bad=[Identity('W4',new.ancestor,new.controller,new.domain,old.public_key) if i.name=='W4' else i for i in bad]
        b=Succession(os.path.join(self.d.name,'bad.db'),bad);b.revoke('W1','proof')
        s=b.state();p={'operation':'rotate','old':'W1','new':'W4','epoch':s['epoch'],'prior_root':s['root'],'next_root':'root-100','challenge':s['challenge']}
        with self.assertRaises(ValueError):b.rotate('W1','W4',self.reviews(p),'root-100')
    def test_21_shared_controller(self):
        old=self.a.ids['W1'];new=self.a.ids['W4']
        ids=[Identity('W4',new.ancestor,old.controller,new.domain,new.public_key) if i.name=='W4' else i for i in self.ids]
        b=Succession(os.path.join(self.d.name,'bad.db'),ids);b.revoke('W1','proof')
        with self.assertRaises(ValueError):b.rotate('W1','W4',self.reviews(),'root-100')
    def test_22_shared_ancestry(self):
        old=self.a.ids['W1'];new=self.a.ids['W4']
        ids=[Identity('W4',old.ancestor,new.controller,new.domain,new.public_key) if i.name=='W4' else i for i in self.ids]
        b=Succession(os.path.join(self.d.name,'bad.db'),ids);b.revoke('W1','proof')
        with self.assertRaises(ValueError):b.rotate('W1','W4',self.reviews(),'root-100')
    def test_23_new_ring_controller_collision(self):
        other=self.a.ids['W2'];new=self.a.ids['W4']
        ids=[Identity('W4',new.ancestor,other.controller,new.domain,new.public_key) if i.name=='W4' else i for i in self.ids]
        b=Succession(os.path.join(self.d.name,'bad.db'),ids);b.revoke('W1','proof')
        with self.assertRaises(ValueError):b.rotate('W1','W4',self.reviews(),'root-100')
    def test_24_certify(self):self.rotate();self.assertEqual(self.a.certify(self.attest()),'LOCAL_RECONSTITUTED_QUORUM')
    def test_25_old_witness_cert_cannot_reenter(self):
        self.rotate();x=self.attest();x.pop('W4');x['W1']=b'invalid'
        with self.assertRaises(ValueError):self.a.certify(x)
    def test_26_no_certification_during_quarantine(self):
        self.a.revoke('W1','proof')
        with self.assertRaises(ValueError):self.a.certify({})
    def test_27_missing_signature(self):
        self.rotate();x=self.attest();x.pop('W3')
        with self.assertRaises(ValueError):self.a.certify(x)
    def test_28_forged_attestation(self):
        self.rotate();x=self.attest();x['W4']=sign(self.keys['W1'],{'operation':'wrong'})
        with self.assertRaises(ValueError):self.a.certify(x)
    def test_29_replay_attestation(self):
        self.rotate();x=self.attest();self.a.certify(x)
        with self.assertRaises(ValueError):self.a.certify(x)
    def test_30_audit_history(self):self.rotate();self.a.certify(self.attest());self.assertTrue(self.a.audit())
    def test_31_audit_tamper(self):
        self.rotate()
        c=self.a._connect();c.execute("UPDATE events SET kind='FORGED' WHERE n=1");c.commit();c.close()
        self.assertFalse(self.a.audit())
    def test_32_rollback_after_failure(self):
        self.a.revoke('W1','proof')
        with self.assertRaises(ValueError):self.a.rotate('W1','W4',{'W2':b'bad','W3':b'bad'},'root-100')
        self.assertEqual(self.a.state()['roster'],('W1','W2','W3'))
    def test_33_restart_preservation(self):
        self.rotate();b=Succession(self.path,self.ids)
        self.assertEqual(b.state()['roster'],('W2','W3','W4'))
        self.assertEqual(b.historic('W1'),(99,'signed-conflict'))
    def test_34_replay_after_restart(self):
        self.rotate();x=self.attest();self.a.certify(x);b=Succession(self.path,self.ids)
        with self.assertRaises(ValueError):b.certify(x)
    def test_35_no_partial_events(self):
        self.a.revoke('W1','proof');n=len(self.a.events())
        with self.assertRaises(ValueError):self.a.rotate('W1','W4',{'W2':b'bad','W3':b'bad'},'root-100')
        self.assertEqual(len(self.a.events()),n)
    def test_36_demo(self):
        a,_,report=demo(os.path.join(self.d.name,'demo.db'))
        self.assertEqual(report['status'],'LOCAL_RECONSTITUTED_QUORUM')
        self.assertEqual(report['records'],4)
        self.assertTrue(a.audit())
    def test_37_invalid_roster(self):
        with self.assertRaises(ValueError):Succession(os.path.join(self.d.name,'new.db'),self.ids,active=('W1','W1','W3'))
    def test_38_invalid_identity(self):
        with self.assertRaises(ValueError):Identity('W6','','c','d',b'0'*32)
    def test_39_bad_signature(self):self.assertFalse(check(self.a.ids['W1'].public_key,{'a':1},b'\x00'*64))
    def test_40_replay_old_review(self):
        self.rotate();s=self.a.state()
        with self.assertRaises(ValueError):self.a.rotate('W1','W4',self.reviews(self.proposal()),'root-100')

if __name__=='__main__':unittest.main()