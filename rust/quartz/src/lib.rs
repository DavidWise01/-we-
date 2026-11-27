#![forbid(unsafe_code)]
pub const CELLS: usize = 125;
pub const PORTS: usize = 24;
pub const PUMPS: usize = 3;
pub const CENTER: usize = 62;
pub const CONSTANT: i32 = 1;
pub fn index(x:usize,y:usize,z:usize)->usize { x+5*y+25*z }
pub fn edges()->Vec<(usize,usize)> {
 let mut e=Vec::new();
 for z in 0..5 { for y in 0..5 { for x in 0..5 {
 let a=index(x,y,z);
 if x<4 {e.push((a,index(x+1,y,z)));}
 if y<4 {e.push((a,index(x,y+1,z)));}
 if z<4 {e.push((a,index(x,y,z+1)));}
 } } } e
}
pub fn generation_index(g:u64)->Option<u64> {g.checked_mul(144)?.checked_add(1560)}
#[derive(Clone,Debug,PartialEq,Eq)]
pub struct State { generation:u64, cells:[i32;CELLS] }
impl State {
 pub fn new()->Self {let mut cells=[0;CELLS];cells[CENTER]=CONSTANT;Self{generation:0,cells}}
 pub fn generation(&self)->u64 {self.generation}
 pub fn cells(&self)->&[i32;CELLS] {&self.cells}
 pub fn successor(&self, updates:&[(usize,i32)])->Option<Self>{
 let mut next=self.clone(); next.generation=self.generation.checked_add(1)?;
 generation_index(next.generation)?;
 for &(i,v) in updates {if i>=CELLS || i==CENTER {return None;} next.cells[i]=v;}
 Some(next)
 }
}
#[cfg(test)]
mod tests {
 use super::*;
 #[test] fn geometry(){let e=edges();assert_eq!(e.len(),300);assert_eq!(e.iter().collect::<std::collections::HashSet<_>>().len(),300);assert_eq!(index(2,2,2),CENTER);assert_eq!(PORTS/PUMPS,8);}
 #[test] fn progression(){assert_eq!((0..=5).map(|g|generation_index(g).unwrap()).collect::<Vec<_>>(),vec![1560,1704,1848,1992,2136,2280]);}
 #[test] fn inheritance(){let a=State::new();let b=a.successor(&[(0,9)]).unwrap();assert_eq!(a.cells()[0],0);assert_eq!(b.cells()[0],9);assert_eq!(b.cells()[CENTER],CONSTANT);assert_eq!(b.generation(),1);assert!(b.successor(&[(CENTER,0)]).is_none());assert!(b.successor(&[(125,0)]).is_none());}
}

pub mod recovery;

pub mod journal;

#[cfg(target_arch = "wasm32")]
pub mod browser;

pub mod observation;

pub mod bit_geometry;

pub mod pump_memory;

pub mod adaptive;

pub mod selection;

pub mod cortex;

pub mod witness;

pub mod homeostasis;

pub mod mesh;

pub mod silo_memory;

pub mod diode;

pub mod coupling;

pub mod temporal;

pub mod provenance;

pub mod distributed;

pub mod evidence_gate;

pub mod canonical;

pub mod integrity;

pub mod containment;

pub mod inheritance;

pub mod specialization;

pub mod parity;

pub mod decoding;

pub mod quarantine_chain;

pub mod authentication;

pub mod epochs;

pub mod interruption;

#[cfg(not(target_arch = "wasm32"))]
pub mod filesystem;

#[cfg(unix)]
pub mod publication;

pub mod roster_binding;

pub mod signed_evidence;

pub mod custody;

#[cfg(unix)]
pub mod cross_ledger;

pub mod state_commitment;

pub mod transition_binding;

pub mod transition_containment;

pub mod specialization_binding;

#[cfg(unix)]
pub mod sovereign_checkpoint;

#[cfg(unix)]
pub mod incremental;

#[cfg(unix)]
pub mod temporal_chain;

#[cfg(unix)]
pub mod checkpoint_frame;
