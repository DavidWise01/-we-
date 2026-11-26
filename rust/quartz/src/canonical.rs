use crate::{mesh::{Silo,SILOS},temporal::Clock,evidence_gate::Packet,provenance::MAX_REPORTS};
pub const MAX_JOURNAL_BYTES:usize=1_048_576;
fn clock(t:Clock)->[u8;8]{(t.cycle()*360+t.phase()).to_be_bytes()}
fn framed(out:&mut Vec<u8>,bytes:&[u8])->Option<()>{
 out.extend_from_slice(&u32::try_from(bytes.len()).ok()?.to_be_bytes());out.extend_from_slice(bytes);Some(())
}
/// QD1 encodes ordered silo journals and observation evidence, not inbox high-water marks.
pub fn encode(silos:&[Silo;SILOS],now:Clock,lambda:u16,packets:&[Vec<Packet>;SILOS])->Option<Vec<u8>>{
 if lambda>1000{return None;}
 let mut out=b"QD1\0".to_vec();out.extend_from_slice(&clock(now));out.extend_from_slice(&lambda.to_be_bytes());
 for i in 0..SILOS{
  let s=&silos[i];let o=s.observation();if o.source.index()!=i||packets[i].len()>SILOS{return None;}
  out.push(i as u8);out.extend_from_slice(&o.sequence.to_be_bytes());
  let journal=s.journal().encode();if journal.len()>MAX_JOURNAL_BYTES{return None;}
  framed(&mut out,journal.as_bytes())?;
  out.push(packets[i].len() as u8);
  // Packet order is preserved: admission is sequence-sensitive.
  for p in &packets[i]{
   let m=&p.message;let o=&m.observation;
   out.extend_from_slice(&clock(m.observed));out.push(o.source.index() as u8);
   out.extend_from_slice(&o.sequence.to_be_bytes());out.extend_from_slice(&o.recovery_tick.to_be_bytes());
   out.extend_from_slice(&o.deficit.to_be_bytes());out.extend_from_slice(&o.energy.to_be_bytes());
   if p.reports.len()>MAX_REPORTS{return None;}
   let mut reports:Vec<Vec<u8>>=p.reports.iter().map(|r|{
    let mut b=Vec::with_capacity(75);b.extend_from_slice(&r.root);b.push(r.relay);b.extend_from_slice(&clock(r.observed));b.extend_from_slice(&r.subject);b.extend_from_slice(&r.value.to_be_bytes());b
   }).collect();
   reports.sort();out.push(reports.len() as u8);for b in reports{out.extend_from_slice(&b);}
  }
 }
 Some(out)
}
#[cfg(test)]mod tests{
 use super::*;use crate::{mesh::mesh,journal::{Policy,Event},temporal::TimedObservation,provenance::Report,evidence_gate::subject};
 #[test]fn stable_and_sensitive(){
 let a=mesh([10,40,90],Policy::FixedV1);let now=Clock::new(360);let mut p:[Vec<Packet>;SILOS]=std::array::from_fn(|_|Vec::new());
 let m=TimedObservation{observed:now,observation:a[4].observation()};
 let reports=(1..=3).map(|n|Report{root:[n;32],relay:0,observed:now,subject:subject(&m),value:0}).collect();
 p[0].push(Packet{message:m,reports});
 let b=encode(&a,now,500,&p).unwrap();assert_eq!(&b[..4],b"QD1\0");
 p[0][0].reports.reverse();assert_eq!(encode(&a,now,500,&p),Some(b.clone()));
 assert_ne!(encode(&a,Clock::new(361),500,&p),Some(b.clone()));
 assert_ne!(encode(&a,now,501,&p),Some(b.clone()));
 let mut c=a.clone();c[0]=c[0].successor(Event::Shock(vec![(0,1)])).unwrap();assert_ne!(encode(&c,now,500,&p),Some(b.clone()));
 p[0][0].message.observed=Clock::new(359);assert_ne!(encode(&a,now,500,&p),Some(b));
 assert!(encode(&a,now,1001,&p).is_none());c.swap(0,1);assert!(encode(&c,now,500,&p).is_none());
 }
}
