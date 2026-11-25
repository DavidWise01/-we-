use crate::{journal::{Journal,Event}, recovery::Recovery};
pub const WINDOW:usize=32;
#[derive(Clone,Copy,Debug,Default,PartialEq,Eq)]
pub struct Sample {pub spent:u8,pub unused:u8,pub pressure:u16}
#[derive(Clone,Debug,PartialEq,Eq)]
pub struct PumpMemory {samples:[Sample;WINDOW],next:usize,len:usize}
impl Default for PumpMemory {fn default()->Self{Self{samples:[Sample::default();WINDOW],next:0,len:0}}}
impl PumpMemory {
 pub(crate) fn record(&mut self,s:Sample){self.samples[self.next]=s;self.next=(self.next+1)%WINDOW;self.len=(self.len+1).min(WINDOW);}
 pub fn samples(&self)->impl Iterator<Item=&Sample>{(0..self.len).map(move |i|&self.samples[(self.next+WINDOW-self.len+i)%WINDOW])}
 pub fn spent(&self)->u32{self.samples().map(|s|u32::from(s.spent)).sum()}
}
fn pressure(s:&Recovery)->u16{s.health().iter().map(|&h|100u16-u16::from(h)).sum()}
/// Observational projection only; no policy or energy mutation.
pub fn derive(j:&Journal)->Option<[PumpMemory;3]>{
 let header=j.encode();let mut fields=header.lines().next()?.split_whitespace();fields.next()?;
 let initial=[fields.next()?.parse().ok()?,fields.next()?.parse().ok()?,fields.next()?.parse().ok()?];
 let mut prior=Journal::with_policy(initial,j.policy());
 let mut memory:[PumpMemory;3]=std::array::from_fn(|_|PumpMemory::default());
 for e in j.events(){
  let next=prior.append(e.clone())?;
  if matches!(e,Event::Recover){
   let a=prior.state().energy();let b=next.state().energy();
   for p in 0..3{let spent=u8::try_from(a[p].checked_sub(b[p])?).ok()?;let unused=8u8.checked_sub(spent)?;
    memory[p].record(Sample{spent,unused,pressure:pressure(prior.state())});}
  }prior=next;
 }
 if &prior!=j{return None;}Some(memory)
}
#[cfg(test)]
mod tests{
 use super::*;use crate::journal::Policy;
 #[test]fn rotation_and_replay(){
 let mut j=Journal::with_policy([100;3],Policy::RotatingV2);
 for _ in 0..39{j=j.append(Event::Shock(vec![(0,1)])).unwrap().append(Event::Recover).unwrap();}
 let m=derive(&j).unwrap();assert_eq!(m.iter().map(PumpMemory::spent).sum::<u32>(),32);
 for p in &m{assert_eq!(p.samples().count(),32);for s in p.samples(){assert_eq!(s.spent+s.unused,8);assert_eq!(s.pressure,1);}}
 assert_eq!(derive(&Journal::decode(&j.encode()).unwrap()),Some(m));
 }
 #[test]fn fixed_and_empty(){let j=Journal::new([10;3]);assert_eq!(derive(&j).unwrap()[0].samples().count(),0);
 let j=j.append(Event::Shock(vec![(0,1)])).unwrap().append(Event::Recover).unwrap();
 let m=derive(&j).unwrap();assert_eq!([m[0].spent(),m[1].spent(),m[2].spent()],[1,0,0]);}
}
