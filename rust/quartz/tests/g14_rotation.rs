use quartz_kernel::{CELLS,CENTER,recovery::Recovery};
#[test] fn equal_priority(){
 let mut a=Recovery::new([10;3]);
 for t in 0..9 {let prior=a.shock(&[(0,1)]).unwrap();let b=prior.rotating_step().unwrap();let mut expected=prior.energy();expected[t%3]-=1;assert_eq!(b.energy(),expected);assert_eq!(b.health()[0],100);a=b;}
 assert_eq!(a.energy(),[7;3]);
}
#[test] fn conservation(){
 for seed in 0..32usize{
 let d:Vec<_>=(0..CELLS).filter(|&i|Recovery::outer(i)&&(i+seed)%3==0).map(|i|(i,40)).collect();
 let mut a=Recovery::new([seed as u32,40,90]).shock(&d).unwrap();
 for _ in 0..32{let b=a.rotating_step().unwrap();assert_eq!(Some(b.clone()),a.rotating_step());let gain:u32=b.health().iter().zip(a.health()).map(|(&x,&y)|u32::from(x-y)).sum();assert_eq!(gain,a.energy().iter().sum::<u32>()-b.energy().iter().sum::<u32>());assert!(gain<=24);assert_eq!(b.health()[CENTER],100);for p in 0..3{assert!(a.energy()[p]-b.energy()[p]<=8);}a=b;}
 }
}
