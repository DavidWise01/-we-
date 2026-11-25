use quartz_kernel::{CELLS,CENTER,recovery::Recovery};
#[test]
fn serial_parallel_equivalence(){
 for seed in 0..32usize {
  let damage:Vec<_>=(0..CELLS).filter(|&i|Recovery::outer(i)&&(i+seed)%3==0).map(|i|(i,((i*7+seed)%100+1) as u8)).collect();
  let mut a=Recovery::new([seed as u32,40,90]).shock(&damage).unwrap();
  for _ in 0..16 {
   let b=a.parallel_step().unwrap();
   assert_eq!(a.step().unwrap(),b);
   let gain:u32=b.health().iter().zip(a.health()).map(|(&x,&y)|u32::from(x-y)).sum();
   assert_eq!(gain,a.energy().iter().sum::<u32>()-b.energy().iter().sum::<u32>());
   assert!(gain<=24);assert_eq!(b.health()[CENTER],100);
   a=b;
  }
 }
}
#[test]
fn contested_cell(){
 let a=Recovery::new([8;3]).shock(&[(0,1)]).unwrap();
 let b=a.parallel_step().unwrap();
 assert_eq!(b.health()[0],100);assert_eq!(b.energy(),[7,8,8]);assert_eq!(a.health()[0],99);
}
