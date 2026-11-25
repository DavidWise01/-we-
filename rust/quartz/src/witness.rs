use crate::{CELLS,CENTER,recovery::Recovery,journal::{Journal,Event},cortex::{regulate,Decision}};
#[derive(Clone,Copy,Debug,PartialEq,Eq)]
pub struct Evidence{pub geometry:bool,pub conservation:bool,pub ancestry:bool}
impl Evidence{pub fn consistent(self)->bool{self.geometry&&self.conservation&&self.ancestry}}
/// Separate checks on shared software ancestry; not independent external witnesses.
pub fn geometry(a:&Recovery,b:&Recovery)->bool{
 for i in 0..CELLS{
  let h=a.health()[i];let n=b.health()[i];
  if n<h||n>100{return false;}
  let x=i%5;let y=i/5%5;let z=i/25;
  if x>0&&x<4&&y>0&&y<4&&z>0&&z<4{if h!=100||n!=100{return false;}}
  if n>h{
   let mut adjacent=false;
   for j in 0..CELLS{let d=x.abs_diff(j%5)+y.abs_diff(j/5%5)+z.abs_diff(j/25);if d==1&&a.health()[j]==100{adjacent=true;break;}}
   if !adjacent{return false;}
  }
 } b.health()[CENTER]==100
}
pub fn conservation(a:&Recovery,b:&Recovery)->bool{
 if a.tick().checked_add(1)!=Some(b.tick()){return false;}
 let mut spent=0i64;
 for (x,y) in a.energy().into_iter().zip(b.energy()){let d=i64::from(x)-i64::from(y);if !(0..=8).contains(&d){return false;}spent+=d;}
 let gain:i64=b.health().iter().zip(a.health()).map(|(&x,&y)|i64::from(x)-i64::from(y)).sum();
 gain==spent
}
pub fn ancestry(j:&Journal,order:[usize;3],candidate:&Recovery)->bool{
 let Some(replayed)=Journal::decode(&j.encode())else{return false;};
 if &replayed!=j{return false;}
 if regulate(&replayed)!=Some(Decision::Trial(order)){return false;}
 replayed.state().ordered_step(order).as_ref()==Some(candidate)
}
pub fn inspect(j:&Journal,order:[usize;3],candidate:&Recovery)->Evidence{
 Evidence{geometry:geometry(j.state(),candidate),conservation:conservation(j.state(),candidate),ancestry:ancestry(j,order,candidate)}
}
#[cfg(test)]mod tests{
 use super::*;
 #[test]fn valid_and_stale(){
 let j=Journal::new([10,40,90]).append(Event::Shock(vec![(0,40)])).unwrap();
 let Decision::Trial(order)=regulate(&j).unwrap()else{panic!("expected trial")};
 let b=j.state().ordered_step(order).unwrap();
 assert!(inspect(&j,order,&b).consistent());
 assert!(!inspect(&j,order,j.state()).consistent());
 assert!(!inspect(&j,[0,0,2],&b).ancestry);
 let wrong=Journal::new([10,40,91]).append(Event::Shock(vec![(0,40)])).unwrap();
 assert!(!inspect(&wrong,order,&b).ancestry);
 }
 #[test]fn shock_is_not_recovery(){let a=Recovery::new([100;3]);let b=a.shock(&[(0,1)]).unwrap();assert!(!geometry(&a,&b));assert!(!conservation(&a,&b));}
}
