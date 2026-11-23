/* WAG-318 · bounded signed recovery and evidence reentry · .dlw
 * Signed fixture data only. Isolate authority failure receipts; require
 * separately signed new-sequence status and clock evidence. Read-only.
 */
const WAG318=Object.freeze({phase:'VII',turn:7,of:8,steps:7,physicalActions:0,
cases:Object.freeze(['clean','status-recovered','clock-recovered','status-replay','clock-replay','status-tamper','clock-tamper','status-key-swap','clock-key-swap','shared-root','no-recovery','clock-rollback','unreported-compromise','correlated-false-reference'])});
function wag318Recovery(kind,seq){
 const status=wag316Packet('status',seq+1),clock=wag316Packet('clock',seq+1);
 if(kind==='status-replay'){const old=wag316Packet('status',seq);status.body=old.body;status.signature=old.signature}
 if(kind==='clock-replay'||kind==='clock-rollback'){const old=wag316Packet('clock',seq);clock.body=old.body;clock.signature=old.signature}
 if(kind==='status-tamper')status.body.state='REVOKED';
 if(kind==='clock-tamper')clock.body.tick++;
 if(kind==='status-key-swap')status.publicKey=clock.publicKey;
 if(kind==='clock-key-swap')clock.publicKey=status.publicKey;
 if(kind==='shared-root')clock.roots=['fixture-Q'];
 if(kind==='no-recovery')status.signature='';
 return {status,clock};
}
async function wag318Trial(kind,seq){
 if(!Number.isInteger(seq)||seq<0||seq>=7)throw Error('seq must be 0..6');
 const initialKind=kind.startsWith('clock-')?'clock-missing':kind==='clean'?'clean':'status-missing';
 const initial=await wag317Trial(initialKind,seq),frozen=JSON.stringify(initial);
 const packets=wag318Recovery(kind,seq),snapshot=JSON.stringify(packets);
 const [status,clock]=await Promise.all([
 wag316Verify(packets.status,'status',seq+1),wag316Verify(packets.clock,'clock',seq+1)]);
 const independent=!packets.status.roots.some(x=>packets.clock.roots.includes(x));
 const falseData=kind==='unreported-compromise'||kind==='correlated-false-reference';
 const observed=await wag313Trial(falseData?'correlated-signed-false':'clean',seq+1);
 const eligible=status.valid&&clock.valid&&independent&&observed.reference.valid&&observed.observedSigned;
 const candidate=eligible?observed.candidate:null;
 if(JSON.stringify(initial)!==frozen||JSON.stringify(packets)!==snapshot)throw Error('evidence changed');
 return wag291DeepFreeze({kind,seq,initialStatus:initial.status.valid,initialClock:initial.clock.valid,
 status,clock,independent,oldReceiptPreserved:true,candidate,
 target:falseData?4:3,verdict:!status.valid?'STATUS_QUARANTINED':!clock.valid?'CLOCK_QUARANTINED':
 !independent?'SHARED_ROOT':'REENTRY_EVALUATED',promoted:false});
}
async function wag318Evaluate(state){
 const before=JSON.stringify(state),rows=[];
 for(const kind of WAG318.cases){
  let correct=0,wrong=0,abstain=0,preserved=0;
  for(let seq=0;seq<7;seq++){
   const t=await wag318Trial(kind,seq);
   if(t.oldReceiptPreserved)preserved++;
   if(t.candidate===null)abstain++;else if(t.candidate===t.target)correct++;else wrong++;
  }
  rows.push({kind,correct,wrong,abstain,preserved,total:7});
 }
 if(JSON.stringify(state)!==before)throw Error('state changed');
 return wag291DeepFreeze({bound:'WAG-318',phase:'VII',turn:7,rows,trials:98,
 authenticatedTruth:false,externalSignersAuthenticated:false,promoted:false,physicalActions:0});
}
async function wag318Audit(){
 const state=wag288Initial(),snap=JSON.stringify(state),
 a=await wag318Evaluate(state),b=await wag318Evaluate(state),row=k=>a.rows.find(r=>r.kind===k),
 status=await wag318Trial('status-recovered',0),clock=await wag318Trial('clock-recovered',0);
 const checks={
 deterministic:JSON.stringify(a)===JSON.stringify(b),
 unchanged:JSON.stringify(state)===snap,
 accounting:a.trials===98&&a.rows.length===14&&a.rows.every(r=>r.correct+r.wrong+r.abstain===7),
 clean:row('clean').correct===7,
 statusRecovers:row('status-recovered').correct===7,
 clockRecovers:row('clock-recovered').correct===7,
 oldStatusRejected:row('status-replay').abstain===7,
 oldClockRejected:row('clock-replay').abstain===7,
 statusTamperRejected:row('status-tamper').abstain===7,
 clockTamperRejected:row('clock-tamper').abstain===7,
 statusKeyRejected:row('status-key-swap').abstain===7,
 clockKeyRejected:row('clock-key-swap').abstain===7,
 ancestryRejected:row('shared-root').abstain===7,
 missingRecoveryRejected:row('no-recovery').abstain===7,
 rollbackRejected:row('clock-rollback').abstain===7,
 healthyStatusPreserved:clock.initialStatus&&!clock.initialClock,
 healthyClockPreserved:!status.initialStatus&&status.initialClock,
 oldEvidencePreserved:a.rows.every(r=>r.preserved===7),
 unreportedCompromiseStillWrong:row('unreported-compromise').wrong===7,
 correlatedFalseStillWrong:row('correlated-false-reference').wrong===7,
 frozen:Object.isFrozen(a)&&Object.isFrozen(a.rows[0]),
 noPromotion:!a.promoted&&a.physicalActions===0,
 noRealIdentityClaims:!a.authenticatedTruth&&!a.externalSignersAuthenticated,
 threePrivateForms:WAG304.forms.join('|')==='[1]|{1}|(1)'
 };
 return {bound:'WAG-318',checks,pass:Object.values(checks).every(Boolean),rows:a.rows,progress:7/8};
}
if(typeof module!=='undefined')module.exports={WAG318,wag318Recovery,wag318Trial,wag318Evaluate,wag318Audit};
