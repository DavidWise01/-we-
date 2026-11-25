use crate::{edges, CELLS, CENTER};
pub const OUTER: usize = 98;
pub const PORTS_PER_PUMP: usize = 8;
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct Recovery { health: [u8; CELLS], energy: [u32; 3], tick: u64 }
impl Recovery {
 pub fn new(energy: [u32;3]) -> Self { Self { health: [100;CELLS], energy, tick:0 } }
 pub fn health(&self)->&[u8;CELLS] {&self.health}
 pub fn energy(&self)->[u32;3] {self.energy}
 pub fn tick(&self)->u64 {self.tick}
 pub fn outer(i:usize)->bool { if i>=CELLS{return false;} let (x,y,z)=(i%5,(i/5)%5,i/25); [x,y,z].iter().any(|&v|v==0||v==4) }
 pub fn shock(&self, damage:&[(usize,u8)])->Option<Self> {
 let mut n=self.clone(); for &(i,d) in damage { if !Self::outer(i){return None;} n.health[i]=n.health[i].saturating_sub(d); } Some(n)
 }
 pub fn step(&self)->Option<Self> {
 let mut n=self.clone(); n.tick=self.tick.checked_add(1)?;
 let mut reachable=[false;CELLS];
 for (a,b) in edges(){if self.health[a]==100 && self.health[b]<100 {reachable[b]=true;} if self.health[b]==100 && self.health[a]<100 {reachable[a]=true;}}
 for pump in 0..3 { for port in 0..PORTS_PER_PUMP {
 let start=(self.tick%125) as usize;
 if n.energy[pump]==0 {break;}
 if let Some(i)=(0..CELLS).map(|k|(start+k+8*pump+port)%CELLS).find(|&i|i!=CENTER && reachable[i] && n.health[i]<100) {n.health[i]+=1;n.energy[pump]-=1;}
 } } Some(n)
 }
}
#[test] fn shell(){assert_eq!((0..CELLS).filter(|&i|Recovery::outer(i)).count(),OUTER);}
#[test] fn conservation(){let a=Recovery::new([100;3]);let b=a.shock(&[(0,40)]).unwrap();let c=b.step().unwrap(); assert_eq!(a.health()[0],100);assert_eq!(b.health()[0],60);assert_eq!(c.health()[0],84);assert_eq!(c.energy().iter().sum::<u32>(),276);assert_eq!(c.health()[CENTER],100);assert!(a.shock(&[(CENTER,1)]).is_none());}
#[test] fn exhaustion(){let a=Recovery::new([0;3]).shock(&[(0,40)]).unwrap();assert_eq!(a.step().unwrap().health(),a.health());}
#[test] fn deterministic(){let a=Recovery::new([100;3]).shock(&[(0,40),(124,50)]).unwrap();assert_eq!(a.step(),a.step());}
