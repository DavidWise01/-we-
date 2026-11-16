import unittest
from dataclasses import replace
from hashlib import sha256
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from wag079 import (Block,ConsistencyProof,Observer,PrefixGate,Vote,_cover,create_proof,demo,
                    leaf_hash,merkle_root,node_hash,sign_vote,verify_proof)


def fixture(n=5,m=3):
    leaves=tuple(f'event-{i}'.encode() for i in range(n))
    p=create_proof(leaves,m)
    old=merkle_root(leaves[:m]).hex();new=merkle_root(leaves).hex()
    priv=tuple(Ed25519PrivateKey.generate() for _ in range(3))
    obs=tuple(Observer('W'+str(i+1),'root'+str(i+1),'op'+str(i+1),'fd'+str(i+1),k.public_key().public_bytes(serialization.Encoding.Raw,serialization.PublicFormat.Raw)) for i,k in enumerate(priv))
    gate=PrefixGate(obs,m,old,12,'nonce-079')
    votes=tuple(sign_vote(o.identity,k,p,old,new,12,'nonce-079') for o,k in zip(obs,priv))
    return leaves,p,old,new,gate,votes,priv,obs

class TestMerkle(unittest.TestCase):
    def test_leaf_domain(self):self.assertEqual(leaf_hash(b'A'),sha256(b'\x00A').digest())
    def test_internal_domain(self):self.assertEqual(node_hash(b'x'*32,b'y'*32),sha256(b'\x01'+b'x'*32+b'y'*32).digest())
    def test_empty_root(self):self.assertEqual(merkle_root([]),sha256(b'').digest())
    def test_one_leaf(self):self.assertEqual(merkle_root([b'A']),leaf_hash(b'A'))
    def test_two_leaf(self):self.assertEqual(merkle_root([b'A',b'B']),node_hash(leaf_hash(b'A'),leaf_hash(b'B')))
    def test_three_leaf(self):self.assertEqual(merkle_root([b'A',b'B',b'C']),node_hash(merkle_root([b'A',b'B']),leaf_hash(b'C')))
    def test_full_range(self):
        for n in range(1,80):
            items=tuple(str(i).encode() for i in range(n))
            for m in range(1,n+1):
                with self.subTest(n=n,m=m):self.assertTrue(verify_proof(create_proof(items,m),merkle_root(items[:m]).hex(),merkle_root(items).hex()))
    def test_bad_old_size_zero(self):
        with self.assertRaises(ValueError):create_proof((b'A',),0)
    def test_bad_old_size_too_big(self):
        with self.assertRaises(ValueError):create_proof((b'A',),2)
    def test_same_size(self):
        x,p,o,n,*_=fixture(7,7);self.assertTrue(verify_proof(p,o,n));self.assertEqual(p.appended_blocks,())
    def test_compact(self):
        x,p,o,n,*_=fixture(1000,477)
        self.assertLessEqual(len(p.old_blocks)+len(p.appended_blocks),2*1000 .bit_length())
    def test_prefix_mutation(self):
        x,p,o,n,*_=fixture();altered=(b'altered',)+x[1:];self.assertFalse(verify_proof(create_proof(altered,3),o,merkle_root(altered).hex()))
    def test_suffix_mutation(self):
        x,p,o,n,*_=fixture();altered=x[:-1]+(b'altered',);self.assertFalse(verify_proof(p,o,merkle_root(altered).hex()))
    def test_wrong_old_root(self):
        _,p,o,n,*_=fixture();self.assertFalse(verify_proof(p,'00'*32,n))
    def test_wrong_new_root(self):
        _,p,o,n,*_=fixture();self.assertFalse(verify_proof(p,o,'ff'*32))
    def test_wrong_index(self):
        _,p,o,n,*_=fixture();self.assertFalse(verify_proof(replace(p,old_blocks=(replace(p.old_blocks[0],start=1),)+p.old_blocks[1:]),o,n))
    def test_wrong_block_len(self):
        _,p,o,n,*_=fixture();self.assertFalse(verify_proof(replace(p,old_blocks=(replace(p.old_blocks[0],length=1),)+p.old_blocks[1:]),o,n))
    def test_wrong_hash(self):
        _,p,o,n,*_=fixture();self.assertFalse(verify_proof(replace(p,appended_blocks=(replace(p.appended_blocks[0],hash_hex='ee'*32),)+p.appended_blocks[1:]),o,n))
    def test_malformed_hash(self):
        _,p,o,n,*_=fixture();self.assertFalse(verify_proof(replace(p,old_blocks=(replace(p.old_blocks[0],hash_hex='not-hex'),)+p.old_blocks[1:]),o,n))
    def test_duplicate_block(self):
        _,p,o,n,*_=fixture();self.assertFalse(verify_proof(replace(p,old_blocks=p.old_blocks+p.old_blocks[:1]),o,n))
    def test_missing_block(self):
        _,p,o,n,*_=fixture();self.assertFalse(verify_proof(replace(p,old_blocks=p.old_blocks[1:]),o,n))
    def test_swapped_blocks(self):
        _,p,o,n,*_=fixture();self.assertFalse(verify_proof(replace(p,old_blocks=p.old_blocks[::-1]),o,n))
    def test_negative_sizes(self):
        _,p,o,n,*_=fixture();self.assertFalse(verify_proof(replace(p,new_size=-1),o,n))
    def test_nonproof(self):self.assertFalse(verify_proof(None,'00'*32,'11'*32))
    def test_cover(self):self.assertEqual(_cover(3,8),((3,1),(4,4)))

class TestSignedGate(unittest.TestCase):
    def setUp(self):self.leaves,self.p,self.old,self.new,self.gate,self.votes,self.keys,self.obs=fixture()
    def test_accept(self):self.assertEqual(self.gate.certify(self.p,self.new,self.votes),'LOCAL_PREFIX_CERTIFIED')
    def test_ledger(self):self.gate.certify(self.p,self.new,self.votes);self.assertTrue(self.gate.ledger_valid())
    def test_reject_prefix(self):
        x=list(self.leaves);x[0]=b'X';bad=create_proof(tuple(x),3)
        self.assertEqual(self.gate.certify(bad,merkle_root(x).hex(),self.votes),'QUARANTINE_PREFIX')
    def test_missing_votes(self):self.assertEqual(self.gate.certify(self.p,self.new,self.votes[:2]),'HOLD_QUORUM')
    def test_duplicate_identity(self):self.assertEqual(self.gate.certify(self.p,self.new,(self.votes[0],self.votes[0],self.votes[2])),'HOLD_QUORUM')
    def test_old_challenge(self):self.assertEqual(self.gate.certify(self.p,self.new,(replace(self.votes[0],challenge='old'),)+self.votes[1:]),'HOLD_STALE_OR_SPLIT')
    def test_old_epoch(self):self.assertEqual(self.gate.certify(self.p,self.new,(replace(self.votes[0],epoch=11),)+self.votes[1:]),'HOLD_STALE_OR_SPLIT')
    def test_other_root(self):self.assertEqual(self.gate.certify(self.p,self.new,(replace(self.votes[0],new_root='01'*32),)+self.votes[1:]),'HOLD_STALE_OR_SPLIT')
    def test_other_size(self):self.assertEqual(self.gate.certify(self.p,self.new,(replace(self.votes[0],new_size=6),)+self.votes[1:]),'HOLD_STALE_OR_SPLIT')
    def test_bad_sig(self):self.assertEqual(self.gate.certify(self.p,self.new,(replace(self.votes[0],signature=b'\x00'*64),)+self.votes[1:]),'HOLD_BAD_SIGNATURE')
    def test_wrong_key(self):
        fake=sign_vote('W1',self.keys[1],self.p,self.old,self.new,12,'nonce-079')
        self.assertEqual(self.gate.certify(self.p,self.new,(fake,)+self.votes[1:]),'HOLD_BAD_SIGNATURE')
    def test_disjoint_roots(self):self.assertEqual({o.ancestor for o in self.obs},{'root1','root2','root3'})
    def test_duplicate_ancestors(self):
        with self.assertRaises(ValueError):PrefixGate((replace(self.obs[0],ancestor='root2'),)+self.obs[1:],3,self.old,12,'nonce-079')
    def test_duplicate_domain(self):
        with self.assertRaises(ValueError):PrefixGate((replace(self.obs[0],domain='fd2'),)+self.obs[1:],3,self.old,12,'nonce-079')
    def test_duplicate_operator(self):
        with self.assertRaises(ValueError):PrefixGate((replace(self.obs[0],operator='op2'),)+self.obs[1:],3,self.old,12,'nonce-079')
    def test_duplicate_key(self):
        with self.assertRaises(ValueError):PrefixGate((replace(self.obs[0],public_key=self.obs[1].public_key),)+self.obs[1:],3,self.old,12,'nonce-079')
    def test_two_observers(self):
        with self.assertRaises(ValueError):PrefixGate(self.obs[:2],3,self.old,12,'nonce-079')
    def test_empty_challenge(self):
        with self.assertRaises(ValueError):PrefixGate(self.obs,3,self.old,12,'')
    def test_ledger_tamper(self):
        self.gate.certify(self.p,self.new,self.votes);self.gate.entries[0]['data']['challenge']='wrong';self.assertFalse(self.gate.ledger_valid())
    def test_preserve_rejection(self):
        self.gate.certify(self.p,'ff'*32,self.votes)
        self.assertEqual(self.gate.entries[1]['data']['decision'],'QUARANTINE_PREFIX')
    def test_demo(self):
        d=demo();self.assertEqual(d['accepted'],'LOCAL_PREFIX_CERTIFIED');self.assertEqual(d['rewritten'],'QUARANTINE_PREFIX');self.assertTrue(d['ledger_valid'])
    def test_three_entries(self):self.assertEqual(demo()['ledger_records'],3)
    def test_vote_message_scope(self):
        from wag079 import vote_message
        self.assertNotEqual(vote_message(self.votes[0]),vote_message(replace(self.votes[0],challenge='different')))

if __name__=='__main__':unittest.main()