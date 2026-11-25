use quartz_kernel::{CENTER,CELLS,recovery::{Recovery,OUTER}};
#[test] fn shell(){assert_eq!((0..CELLS).filter(|&i|Recovery::outer(i)).count(),OUTER);}
#[test] fn conservation(){let a=Recovery::new([100;3]);let b=a.shock(&[(0,40)]).unwrap();let c=b.step().unwrap(); assert_eq!(a.health()[0],100);assert_eq!(b.health()[0],60);assert_eq!(c.health()[0],84);assert_eq!(c.energy().iter().sum::<u32>(),276);assert_eq!(c.health()[CENTER],100);assert!(a.shock(&[(CENTER,1)]).is_none());}
#[test] fn exhaustion(){let a=Recovery::new([0;3]).shock(&[(0,40)]).unwrap();assert_eq!(a.step().unwrap().health(),a.health());}
#[test] fn deterministic(){let a=Recovery::new([100;3]).shock(&[(0,40),(124,50)]).unwrap();assert_eq!(a.step(),a.step());}
