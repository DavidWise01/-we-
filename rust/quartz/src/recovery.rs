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

type Plan = Vec<Vec<usize>>;
fn plan(pump: usize, tick:u64, reachable:&[bool;CELLS])->Plan {
 (0..PORTS_PER_PUMP).map(|port| (0..CELLS)
 .map(|k|((tick%125) as usize+k+8*pump+port)%CELLS)
 .filter(|&i|i!=CENTER && reachable[i]).collect()).collect()
}
impl Recovery {
 /// Native workers observe one immutable snapshot; WASM uses identical serial plans.
 pub fn parallel_step(&self)->Option<Self> {
  let mut n=self.clone(); n.tick=self.tick.checked_add(1)?;
  let mut reachable=[false;CELLS];
  for (a,b) in edges(){
   if self.health[a]==100 && self.health[b]<100 {reachable[b]=true;}
   if self.health[b]==100 && self.health[a]<100 {reachable[a]=true;}
  }
  #[cfg(not(target_arch="wasm32"))]
  let plans:Vec<Plan>=std::thread::scope(|s| {
   let handles:Vec<_>=(0..3).map(|p| {let r=&reachable; let t=self.tick; s.spawn(move ||plan(p,t,r))}).collect();
   handles.into_iter().map(|h|h.join().ok()).collect::<Option<Vec<_>>>()
  })?;
  #[cfg(target_arch="wasm32")]
  let plans:Vec<Plan>=(0..3).map(|p|plan(p,self.tick,&reachable)).collect();
  for (p,ports) in plans.iter().enumerate(){
   for candidates in ports {
    if n.energy[p]==0 {break;}
    if let Some(&i)=candidates.iter().find(|&&i|n.health[i]<100){
     n.health[i]+=1;n.energy[p]-=1;
    }
   }
  }
  Some(n)
 }
}

struct FixedPlan<const N:usize,const P:usize>{cells:[[u8;N];P],lengths:[usize;P]}
impl<const N:usize,const P:usize> FixedPlan<N,P>{
 fn build(pump:usize,tick:u64,reachable:&[bool;N])->Self{
  assert!(N>0 && N<=256);
  let mut out=Self{cells:[[0;N];P],lengths:[0;P]};
  for port in 0..P {for k in 0..N {
   let i=((tick%N as u64) as usize+k+P*pump+port)%N;
   if i!=CENTER && reachable[i]{let n=out.lengths[port];out.cells[port][n]=i as u8;out.lengths[port]+=1;}
  }}out
 }
}
impl Recovery{
 pub fn fixed_step(&self)->Option<Self>{
  let mut n=self.clone();n.tick=self.tick.checked_add(1)?;
  let mut reachable=[false;CELLS];
  for i in 0..CELLS {for d in [1usize,5,25] {
    if (d==1 && i%5<4)||(d==5 && (i/5)%5<4)||(d==25 && i<100){
     let b=i+d;
     if self.health[i]==100 && self.health[b]<100{reachable[b]=true;}
     if self.health[b]==100 && self.health[i]<100{reachable[i]=true;}
    }
  }}
  for p in 0..3 {
   let plan=FixedPlan::<CELLS,PORTS_PER_PUMP>::build(p,self.tick,&reachable);
   for port in 0..PORTS_PER_PUMP{
    if n.energy[p]==0{break;}
    if let Some(i)=plan.cells[port][..plan.lengths[port]].iter().map(|&i|usize::from(i)).find(|&i|n.health[i]<100){
     n.health[i]+=1;n.energy[p]-=1;
    }
   }
  }
  Some(n)
 }
}
