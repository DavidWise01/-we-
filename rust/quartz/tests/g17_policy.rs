use quartz_kernel::{journal::{Journal,Event,Policy},CENTER};
#[test] fn versioned_inheritance(){
 let mut a=Journal::new([10;3]);let mut b=Journal::with_policy([10;3],Policy::RotatingV2);
 for _ in 0..9{for e in [Event::Shock(vec![(0,1)]),Event::Recover]{a=a.append(e.clone()).unwrap();b=b.append(e).unwrap();assert_eq!(Journal::decode(&a.encode()),Some(a.clone()));assert_eq!(Journal::decode(&b.encode()),Some(b.clone()));}}
 assert_eq!(a.state().energy(),[1,10,10]);assert_eq!(b.state().energy(),[7;3]);assert_eq!(a.state().health(),b.state().health());assert_eq!(b.state().health()[CENTER],100);
 assert_eq!(a.policy(),Policy::FixedV1);assert_eq!(b.policy(),Policy::RotatingV2);
 assert_eq!(Journal::replay([10;3],a.events()),Some(a.clone()));
 assert_eq!(Journal::replay_with_policy([10;3],Policy::RotatingV2,b.events()),Some(b.clone()));
 assert!(Journal::decode("QJ3 10 10 10\n").is_none());
}
