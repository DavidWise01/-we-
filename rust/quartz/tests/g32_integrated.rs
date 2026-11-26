use quartz_kernel::{mesh::{mesh,SiloId},journal::{Event,Policy},silo_memory::MemoryBank,diode::channel,temporal::{Clock,Inbox,TimedObservation},coupling::Coupling,provenance::{Report,Verdict,reconcile},distributed::simulate,CENTER};
#[test]fn integrated_mesh_matrix(){
 for policy in [Policy::FixedV1,Policy::RotatingV2]{
 for energy in [[0;3],[1;3],[10,40,90],[100;3]]{
 for lambda in [0,250,500,750,1000]{
 for delay in [0,32,33]{
 let mut a=mesh(energy,policy);
 a[0]=a[0].successor(Event::Shock(vec![(0,20)])).unwrap();
 a[4]=a[4].successor(Event::Shock(vec![(124,100)])).unwrap();
 let id=|n|SiloId::new(n).unwrap();
 let (tx,rx)=channel(id(4),id(0)).unwrap();
 let mut bank=MemoryBank::new(id(0));bank.refresh(&a[0]).unwrap();
 tx.send(&a[4]).unwrap();assert_eq!(rx.drain(&mut bank),Some((1,0)));
 let now=Clock::new(359+delay);let mut inbox=Inbox::new(id(0));
 let msg=TimedObservation{observed:Clock::new(359),observation:bank.external(id(4))[0].clone()};
 assert_eq!(inbox.receive(now,msg),delay<=32);
 let advice=inbox.advise(&a[0],now,Coupling::new(lambda).unwrap()).unwrap();
 assert_eq!(advice.shift,if delay<=32{(8*lambda/1000)as u16}else{0});
 let states=std::array::from_fn(|i|a[i].journal().state().clone());
 let result=simulate(&states,lambda,16).unwrap();
 assert_eq!(simulate(&states,lambda,16),Some(result.clone()));
 for i in 0..5{
 assert_eq!(result.states[i].health()[CENTER],100);
 let spent:u64=states[i].energy().iter().zip(result.states[i].energy()).map(|(&x,y)|u64::from(x.checked_sub(y).unwrap())).sum();
 let gain:u64=states[i].health().iter().zip(result.states[i].health()).map(|(&x,&y)|u64::from(y.checked_sub(x).unwrap())).sum();
 assert_eq!(spent,gain);
 }
 let report=|root,value|Report{root:[root;32],relay:0,observed:now,subject:[9;32],value};
 let reports=[report(1,20),report(2,20),report(3,20)];
 assert_eq!(reconcile(now,[9;32],&reports),Verdict::ConsistentDeclared);
 assert_eq!(reconcile(now,[9;32],&[reports[0],reports[0],reports[1]]),Verdict::Insufficient);
 assert_eq!(reconcile(now,[9;32],&[reports[0],reports[1],report(3,21)]),Verdict::Contradiction);
 }
 }
 }
 }
}
