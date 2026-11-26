use crate::{canonical::{encode,MAX_JOURNAL_BYTES},mesh::{Silo,SiloId,Observation,SILOS},journal::Journal,temporal::{Clock,TimedObservation},evidence_gate::Packet,provenance::{Report,MAX_REPORTS}};
pub const MAX_FRAME:usize=14+SILOS*(14+MAX_JOURNAL_BYTES+SILOS*(36+75*MAX_REPORTS));
pub const MAX_EVENTS:usize=4096;
#[derive(Clone,Debug,PartialEq,Eq)]
pub struct Decoded{pub silos:[Silo;SILOS],pub now:Clock,pub lambda:u16,pub packets:[Vec<Packet>;SILOS]}
struct Reader<'a>{rest:&'a [u8]}
impl<'a> Reader<'a>{
 fn take(&mut self,n:usize)->Option<&'a [u8]>{if n>self.rest.len(){return None;}let (a,b)=self.rest.split_at(n);self.rest=b;Some(a)}
 fn arr<const N:usize>(&mut self)->Option<[u8;N]>{self.take(N)?.try_into().ok()}
 fn u8(&mut self)->Option<u8>{Some(self.arr::<1>()?[0])}
 fn u16(&mut self)->Option<u16>{Some(u16::from_be_bytes(self.arr()?))}
 fn u32(&mut self)->Option<u32>{Some(u32::from_be_bytes(self.arr()?))}
 fn u64(&mut self)->Option<u64>{Some(u64::from_be_bytes(self.arr()?))}
 fn clock(&mut self)->Option<Clock>{Some(Clock::new(self.u64()?))}
}
/// Bounded reconstruction, not authorization. Re-encoding rejects noncanonical report order.
pub fn decode(bytes:&[u8])->Option<Decoded>{
 if bytes.len()>MAX_FRAME{return None;}
 let mut r=Reader{rest:bytes};if r.take(4)?!=b"QD1\0"{return None;}
 let now=r.clock()?;let lambda=r.u16()?;if lambda>1000{return None;}
 let mut silos=Vec::with_capacity(SILOS);let mut packets:[Vec<Packet>;SILOS]=std::array::from_fn(|_|Vec::new());
 for i in 0..SILOS{
  if usize::from(r.u8()?)!=i{return None;}
  let sequence=r.u64()?;let len=r.u32()? as usize;if len>MAX_JOURNAL_BYTES{return None;}
  let raw=r.take(len)?;if raw.iter().filter(|&&b|b==b'\n').count()>MAX_EVENTS+1{return None;}
  let journal=Journal::decode(std::str::from_utf8(raw).ok()?)?;
  silos.push(Silo::from_journal(SiloId::new(i as u8)?,journal,sequence)?);
  let count=usize::from(r.u8()?);if count>SILOS{return None;}
  for _ in 0..count{
   let observed=r.clock()?;let source=SiloId::new(r.u8()?)?;
   let observation=Observation{source,sequence:r.u64()?,recovery_tick:r.u64()?,deficit:r.u16()?,energy:r.u64()?};
   let n=usize::from(r.u8()?);if n>MAX_REPORTS{return None;}
   let mut reports=Vec::with_capacity(n);
   for _ in 0..n{reports.push(Report{root:r.arr()?,relay:r.u8()?,observed:r.clock()?,subject:r.arr()?,value:r.u16()?});}
   packets[i].push(Packet{message:TimedObservation{observed,observation},reports});
  }
 }
 if !r.rest.is_empty(){return None;}
 let silos:[Silo;SILOS]=silos.try_into().ok()?;
 if encode(&silos,now,lambda,&packets)?.as_slice()!=bytes{return None;}
 Some(Decoded{silos,now,lambda,packets})
}
#[cfg(test)]mod tests{
 use super::*;use crate::{mesh::mesh,journal::{Policy,Event},integrity::observation_id};
 #[test]fn roundtrip_and_malformed(){
 let mut a=mesh([10,40,90],Policy::RotatingV2);a[0]=a[0].successor(Event::Shock(vec![(0,20)])).unwrap();
 let now=Clock::new(360);let m=TimedObservation{observed:now,observation:a[4].observation()};
 let reports=(1..=3).rev().map(|n|Report{root:[n;32],relay:n,observed:now,subject:observation_id(&m),value:0}).collect();
 let mut p:[Vec<Packet>;SILOS]=std::array::from_fn(|_|Vec::new());p[0].push(Packet{message:m,reports});
 let b=encode(&a,now,500,&p).unwrap();let d=decode(&b).unwrap();assert_eq!(d.silos,a);assert_eq!(d.now,now);assert_eq!(encode(&d.silos,d.now,d.lambda,&d.packets),Some(b.clone()));
 for n in 0..b.len(){assert!(decode(&b[..n]).is_none());}
 let mut bad=b.clone();bad.push(0);assert!(decode(&bad).is_none());
 let mut bad=b.clone();bad[0]=0;assert!(decode(&bad).is_none());
 let mut bad=b.clone();bad[22]^=1;assert!(decode(&bad).is_none());
 let mut bad=b.clone();let len=u32::from_be_bytes(bad[23..27].try_into().unwrap())as usize;let start=27+len+1+36;for i in 0..75{bad.swap(start+i,start+75+i);}assert!(decode(&bad).is_none());
 }
}
