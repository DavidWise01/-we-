use crate::{mesh::{Silo,SiloId,Observation,route},silo_memory::MemoryBank};
use std::{cell::RefCell,rc::Rc,collections::VecDeque};
pub const CAPACITY:usize=32;
#[derive(Clone,Copy,Debug,PartialEq,Eq)]
pub enum SendError{WrongSource,Full}
pub struct Transmit{source:SiloId,queue:Rc<RefCell<VecDeque<Observation>>>}
pub struct Receive{destination:SiloId,queue:Rc<RefCell<VecDeque<Observation>>>}
pub fn channel(source:SiloId,destination:SiloId)->Option<(Transmit,Receive)>{
 if !route(source,destination){return None;}
 let queue=Rc::new(RefCell::new(VecDeque::with_capacity(CAPACITY)));
 Some((Transmit{source,queue:queue.clone()},Receive{destination,queue}))
}
impl Transmit{
 pub fn send(&self,silo:&Silo)->Result<(),SendError>{
  let msg=silo.observation();if msg.source!=self.source{return Err(SendError::WrongSource);}
  let mut q=self.queue.borrow_mut();if q.len()>=CAPACITY{return Err(SendError::Full);}
  q.push_back(msg);Ok(())
 }
}
impl Receive{
 pub fn drain(&self,bank:&mut MemoryBank)->Option<(usize,usize)>{
  if bank.owner()!=self.destination{return None;}
  let mut accepted=0;let mut rejected=0;
  for msg in self.queue.borrow_mut().drain(..){if bank.receive(msg){accepted+=1;}else{rejected+=1;}}
  Some((accepted,rejected))
 }
}
#[cfg(test)]mod tests{
 use super::*;use crate::{mesh::mesh,journal::{Event,Policy}};
 #[test]fn boundaries(){
 let a=mesh([100;3],Policy::FixedV1);let id=|i|SiloId::new(i).unwrap();
 let(tx,rx)=channel(id(0),id(4)).unwrap();let mut bank=MemoryBank::new(id(4));let mut wrong=MemoryBank::new(id(1));
 assert_eq!(tx.send(&a[1]),Err(SendError::WrongSource));assert!(channel(id(0),id(1)).is_none());
 let mut s=a[0].clone();for _ in 0..CAPACITY{s=s.successor(Event::Shock(vec![(0,1)])).unwrap();tx.send(&s).unwrap();}
 assert_eq!(tx.send(&s),Err(SendError::Full));assert_eq!(rx.drain(&mut wrong),None);
 assert_eq!(rx.drain(&mut bank),Some((32,0)));assert_eq!(bank.external(id(0)).len(),32);
 tx.send(&s).unwrap();assert_eq!(rx.drain(&mut bank),Some((0,1)));assert_eq!(a[4].observation().deficit,0);
 }
}
