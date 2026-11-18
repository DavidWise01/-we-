import unittest,tempfile,copy,sqlite3
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey as K
from cryptography.exceptions import InvalidSignature
from wag129 import *
class Tests(unittest.TestCase):
 def setUp(self):
  t=tempfile.TemporaryDirectory();self.addCleanup(t.cleanup);self.path=Path(t.name)/'db';self.k=K.generate();self.ks={n:K.generate() for n in 'HON'};self.keys={n:k.public_key() for n,k in self.ks.items()};self.a=Gate(self.path,'mesh',self.k,self.keys)
  for o in [{'kind':'send','src':0,'dst':1,'q':26,'id':'p'},{'kind':'graduate'},{'kind':'receive','id':'p'}]:
   p=self.a.proposal(o);self.a.commit(p,{n:k.sign(enc(p)).hex() for n,k in self.ks.items()})
  self.e,self.h=self.a.export()
 def audit(self,e,h=None):return replay('mesh',self.keys,self.k.public_key(),e,h)
 def test_replay(self):self.assertEqual(self.audit(self.e,self.h),self.a.head())
 def test_missing_middle(self):self.assertRaises(ValueError,self.audit,[self.e[0],self.e[2]])
 def test_reorder(self):self.assertRaises(ValueError,self.audit,self.e[::-1])
 def test_duplicate(self):self.assertRaises(ValueError,self.audit,self.e+self.e[-1:])
 def test_modified_operation(self):self.e[0][0][4]['q']=1;self.assertRaises(InvalidSignature,self.audit,self.e)
 def test_forged_witness(self):self.e[0][1]['H']='00'*64;self.assertRaises(InvalidSignature,self.audit,self.e)
 def test_forged_receipt(self):self.e[0][2][1]='00'*64;self.assertRaises(InvalidSignature,self.audit,self.e)
 def test_tail_with_floor(self):self.assertRaises(ValueError,self.audit,self.e[:-1],self.h)
 def test_tail_without_floor(self):self.assertEqual(self.audit(self.e[:-1])['g'],2)
 def test_restart(self):self.assertEqual(Gate(self.path,'mesh',self.k,self.keys).export(),(self.e,self.h))
 def test_missing_db_evidence(self):
  with sqlite3.connect(self.path) as c:c.execute('DELETE FROM evidence WHERE g=3')
  self.assertRaises(ValueError,self.a.export)
if __name__=='__main__':unittest.main(verbosity=2)
