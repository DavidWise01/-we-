use quartz_kernel::{mesh::mesh,journal::{Event,Policy},temporal::{Clock,TimedObservation},evidence_gate::{Packet,Outcome},integrity::{self,Link},provenance::Report,containment::{Gate,Fault},coupling::Coupling,specialization::specialize,CENTER};
#[test]fn phase_v_matrix(){
 for policy in [Policy::FixedV1,Policy::RotatingV2]{
 for lambda in [0,500,1000]{
 for delay in [0,32,33]{
 let mut a=mesh([100;3],policy);
 a[0]=a[0].successor(Event::Shock(vec![(0,20)])).unwrap();
 a[4]=a[4].successor(Event::Shock(vec![(124,100)])).unwrap();
 let before=a.clone();let observed=Clock::new(359);let now=Clock::new(359+delay);
 let message=TimedObservation{observed,observation:a[4].observation()};
 let reports=(1..=3).map(|n|Report{root:[n;32],relay:n,observed,subject:integrity::observation_id(&message),value:100}).collect();
 let packet=Packet{message,reports};let mut packets=std::array::from_fn(|_|Vec::new());packets[0].push(packet.clone());
 let digest=integrity::checkpoint(&a,now,lambda,&packets).unwrap();
 let link=Link::new(0,[0;32],digest);assert!(integrity::verify(&[link],link.digest));
 let mut gate=Gate::new(a[0].observation().source);let c=Coupling::new(lambda).unwrap();
 let result=gate.trial(&a[0],now,c,&[packet.clone()]);
 if delay<=32{
 let Ok(Outcome::Trial{state,advice})=result else{panic!("expected trial")};
 assert_eq!(state.health()[CENTER],100);assert_eq!(advice.shift,8*lambda/1000);
 assert_eq!(gate.trial(&a[0],now,c,&[packet.clone()]),Err(Fault::Replay));
 let mut altered=packet.clone();altered.message.observation.energy-=1;
 assert_eq!(gate.trial(&a[0],now,c,&[altered]),Err(Fault::Equivocation));
 assert!(gate.quarantined(a[4].observation().source));
 }else{assert_eq!(result,Err(Fault::Evidence));}
 let training=vec![vec![vec![(0,1)];9]];let challenge=vec![vec![vec![(124,1)];12]];
 assert!(specialize(&a[0],&training,&challenge).is_some());
 assert!(specialize(&a[0],&training,&training).is_none());
 assert_eq!(a,before);
 }
 }
 }
}
