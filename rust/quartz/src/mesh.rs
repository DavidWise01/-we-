use crate::{journal::{Journal,Event,Policy},cortex::observe};
pub const SILOS:usize=5;
#[derive(Clone,Copy,Debug,PartialEq,Eq)]
pub struct SiloId(u8);
impl SiloId{pub fn new(i:u8)->Option<Self>{if i<5{Some(Self(i))}else{None}} pub fn index(self)->usize{usize::from(self.0)}}
#[derive(Clone,Debug,PartialEq,Eq)]
pub struct Observation{pub source:SiloId,pub sequence:u64,pub recovery_tick:u64,pub deficit:u16,pub energy:u64}
#[derive(Clone,Debug,PartialEq,Eq)]
pub struct Silo{id:SiloId,journal:Journal,sequence:u64}
impl Silo{
 pub fn new(id:SiloId,energy:[u32;3],policy:Policy)->Self{Self{id,journal:Journal::with_policy(energy,policy),sequence:0}}
 pub fn journal(&self)->&Journal{&self.journal}
 pub fn successor(&self,event:Event)->Option<Self>{Some(Self{id:self.id,journal:self.journal.append(event)?,sequence:self.sequence.checked_add(1)?})}
 pub fn observation(&self)->Observation{let o=observe(self.journal.state());Observation{source:self.id,sequence:self.sequence,recovery_tick:self.journal.state().tick(),deficit:o.shell_deficit,energy:o.energy}}
}
pub fn mesh(energy:[u32;3],policy:Policy)->[Silo;SILOS]{std::array::from_fn(|i|Silo::new(SiloId(i as u8),energy,policy))}
/// Eight directed paths: four peripheral nodes each connected to the hub in both directions.
pub fn route(source:SiloId,dest:SiloId)->bool{source!=dest&&(source.index()==4||dest.index()==4)}
pub fn deliver(source:&Silo,dest:SiloId)->Option<Observation>{if route(source.id,dest){Some(source.observation())}else{None}}
#[cfg(test)]mod tests{
 use super::*;
 #[test]fn isolated(){let a=mesh([100;3],Policy::FixedV1);let before=a.clone();let b=a[0].successor(Event::Shock(vec![(0,40)])).unwrap();assert_eq!(b.observation().deficit,40);assert_eq!(b.observation().sequence,1);assert_eq!(a,before);let msg=deliver(&b,SiloId::new(4).unwrap()).unwrap();assert_eq!(msg.deficit,40);assert_eq!(a[4].observation().deficit,0);assert!(deliver(&b,SiloId::new(1).unwrap()).is_none());}
 #[test]fn topology(){let mut n=0;for a in 0..5{for b in 0..5{if route(SiloId(a),SiloId(b)){n+=1;}}}assert_eq!(n,8);assert!(SiloId::new(5).is_none());}
}
