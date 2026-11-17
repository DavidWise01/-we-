import json,tempfile,unittest
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from wag098 import Anchor,Recovery,snapshot,verify_receipt,digest

class Tests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
  p=Path(self.tmp.name)
  self.anchors=[Anchor(n,p/n,Ed25519PrivateKey.generate()) for n in 'XYZ']
  self.g=Recovery(p/'local.db',self.anchors)
  self.s=snapshot({n:[{'event':'genesis','log':n}] for n in 'ABC'},98)
 def publish(self,s=None):
  for a in self.anchors:a.publish(s or self.s)
 def test_recover_missing_local_db(self):
  self.publish();self.assertEqual('RECOVERED_AUTHENTICATED_SNAPSHOT',self.g.recover(98));self.assertEqual(self.s,self.g.local())
 def test_match_after_restart(self):
  self.publish();self.g.recover(98);h=Recovery(self.g.dbpath,self.anchors)
  self.assertEqual('MATCHED_AUTHENTICATED_SNAPSHOT',h.recover(98))
 def test_replaced_local_db(self):
  self.publish();self.g.recover(98)
  self.g.install(snapshot({n:[{'forged':n}] for n in 'ABC'},98))
  self.assertEqual('RECOVERED_AUTHENTICATED_SNAPSHOT',self.g.recover(98))
  self.assertEqual('LOCAL_REPLACEMENT_DETECTED',self.g.incidents[-1][0])
  self.assertEqual(self.s,self.g.local())
 def test_missing_anchor(self):
  self.anchors[0].publish(self.s)
  self.assertEqual('HOLD_MISSING_ANCHOR',self.g.recover(98))
 def test_bad_signature(self):
  self.publish();p=self.anchors[1].file(98);obj=json.loads(p.read_text());obj['signature']='00'*64;p.write_text(json.dumps(obj))
  self.assertEqual('QUARANTINE_INVALID_RECEIPT',self.g.recover(98))
 def test_changed_snapshot(self):
  self.publish();p=self.anchors[1].file(98);obj=json.loads(p.read_text());obj['snapshot']['logs']['A'][0]['event']='forged';p.write_text(json.dumps(obj))
  self.assertEqual('QUARANTINE_INVALID_RECEIPT',self.g.recover(98))
 def test_signed_anchor_disagreement(self):
  self.anchors[0].publish(self.s);self.anchors[1].publish(self.s)
  alt=snapshot({n:[{'another':n}] for n in 'ABC'},98);self.anchors[2].publish(alt)
  self.assertEqual('QUARANTINE_ANCHOR_DISAGREEMENT',self.g.recover(98))
 def test_immutable_anchor_receipt(self):
  self.anchors[0].publish(self.s)
  with self.assertRaises(ValueError):self.anchors[0].publish(self.s)
 def test_valid_append_only(self):
  self.publish();nxt=snapshot({n:self.s['logs'][n]+[{'next':1}] for n in 'ABC'},99)
  self.assertEqual('ELIGIBLE_TO_PUBLISH_NEW_ANCHORS',self.g.extend(nxt,98))
 def test_extended_fork(self):
  self.publish();nxt=snapshot({n:[{'rewritten':1},{'new':2}] for n in 'ABC'},99)
  self.assertEqual('QUARANTINE_FORK',self.g.extend(nxt,98))
  self.assertEqual('QUARANTINE_FORK',self.g.incidents[-1][0])
 def test_shorter_extension(self):
  self.publish();nxt={'tag':'WAG098-snapshot-v1','epoch':99,'logs':{n:[] for n in 'ABC'}}
  self.assertEqual('HOLD_INVALID_STATE',self.g.extend(nxt,98))
 def test_earlier_epoch(self):
  self.publish();self.assertEqual('HOLD_ROLLBACK',self.g.extend(self.s,98))
 def test_cross_anchor_replay(self):
  self.publish();self.anchors[2].file(98).write_bytes(self.anchors[0].file(98).read_bytes())
  self.assertEqual('QUARANTINE_INVALID_RECEIPT',self.g.recover(98))
 def test_wrong_epoch_receipt(self):
  self.publish();item=self.anchors[0].read(98)
  self.assertFalse(verify_receipt(item,'X',self.anchors[0].public,97))
 def test_corrupt_local_db(self):
  self.publish();self.g.dbpath.write_text('not sqlite')
  with self.assertRaises(Exception):self.g.recover(98)
 def test_published_digest(self):
  self.publish();self.assertEqual(self.anchors[0].read(98)['body']['state_digest'],digest(self.s))
 def test_no_approval_on_missing(self):
  self.assertEqual('HOLD_MISSING_ANCHOR',self.g.recover(98));self.assertIsNone(self.g.local())

if __name__=='__main__':unittest.main()
