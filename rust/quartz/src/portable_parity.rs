use crate::{mesh::mesh,journal::{Policy,Event},state_commitment,authentication::Witness,roster_binding::Binding,signed_evidence::{self,Evidence},temporal::{Clock,TimedObservation},rolling_evidence::Rolling,transition_binding::{self,Transition}};
use ed25519_dalek::{SigningKey,Signer};
/// Synthetic deterministic keys are fixtures only. No production authority.
pub fn fixture()->Option<Vec<u8>>{
 let mut out=b"G75\0".to_vec();
 for policy in [Policy::FixedV1,Policy::RotatingV2]{for seed in 0..4u8{let a=mesh([100+u32::from(seed);3],policy);for i in 0..5{
 let prior=a[i].successor(Event::Shock(vec![(0,40+seed)]))?;let next=prior.successor(Event::Recover)?;let source=a[if i==4{0}else{4}].successor(Event::Shock(vec![(124,20+seed)]))?;
 let keys:[SigningKey;3]=std::array::from_fn(|j|SigningKey::from_bytes(&[(i*3+j+1)as u8;32]));
 let binding=Binding::genesis(prior.observation().source,std::array::from_fn(|j|Witness{key:keys[j].verifying_key().to_bytes(),root:[(i*3+j+1)as u8;32]}))?;
 let sign=|j:usize,b:&[u8]|keys.iter().find(|k|k.verifying_key().to_bytes()==binding.members()[j].key).unwrap().sign(b).to_bytes();
 let now=Clock::new(359+u64::from(seed));let message=TimedObservation{observed:now,observation:source.observation()};
 let signatures=std::array::from_fn(|j|sign(j,&signed_evidence::signing_bytes(&binding,&message,binding.members()[j].root)));
 let e=Evidence{recipient:binding.owner(),roster:binding.digest(),message,signatures};
 let claim=transition_binding::Claim::prepare(&binding,now,&prior,&next,&source,&e)?;
 let signatures=std::array::from_fn(|j|sign(j,&claim.signing_bytes(binding.members()[j].root)));let t=Transition{claim,signatures};
 if !t.verify(&binding,&prior,&next,&source,&e,t.digest()){return None;}
 let rolling=Rolling::genesis(&binding)?.advance(&binding,&e)?;
 for s in [&prior,&next,&source]{let bytes=state_commitment::encode(s)?;let hash=state_commitment::digest(&bytes);if state_commitment::restore(s.observation().source,&bytes,hash).as_ref()!=Some(s){return None;}out.extend_from_slice(&(bytes.len()as u32).to_be_bytes());out.extend_from_slice(&bytes);out.extend_from_slice(&hash);}
 out.extend_from_slice(&binding.encode());out.extend_from_slice(&e.encode());out.extend_from_slice(&t.encode());out.extend_from_slice(&rolling.encode());
 }}}
 Some(out)
}
#[cfg(test)]mod tests{#[test]fn deterministic(){let a=super::fixture().unwrap();assert!(a.starts_with(b"G75\0"));assert_eq!(Some(a),super::fixture());}}
