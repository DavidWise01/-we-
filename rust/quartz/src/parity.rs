use crate::{mesh::{mesh,SILOS},journal::{Policy,Event},temporal::Clock,integrity,distributed::simulate};
/// Deterministic native/WASM fixture; includes canonical input digest and resulting state bytes.
pub fn fixture()->Option<Vec<u8>>{
 let mut out=b"G39\0".to_vec();
 for policy in [Policy::FixedV1,Policy::RotatingV2]{
 for seed in 0..8u32{
 let mut a=mesh([10+seed,40,90],policy);
 for i in 0..SILOS{a[i]=a[i].successor(Event::Shock(vec![(0,((seed as usize*7+i*13)%100+1)as u8)]))?;}
 let packets=std::array::from_fn(|_|Vec::new());
 let states=std::array::from_fn(|i|a[i].journal().state().clone());
 for lambda in [0,500,1000]{
 out.extend_from_slice(&integrity::checkpoint(&a,Clock::new(359+u64::from(seed)),lambda,&packets)?);
 let result=simulate(&states,lambda,16)?;
 out.extend_from_slice(&(result.rounds.len() as u16).to_be_bytes());
 for s in &result.states{out.extend_from_slice(s.health());for e in s.energy(){out.extend_from_slice(&e.to_be_bytes());}out.extend_from_slice(&s.tick().to_be_bytes());}
 }
 }
 }
 Some(out)
}
#[cfg(test)]mod tests{use super::*;#[test]fn fixture_shape(){let a=fixture().unwrap();assert_eq!(a.len(),4+48*(32+2+5*145));assert_eq!(Some(a),fixture());}}
