use quartz_kernel::recovery::Recovery;
use std::{hint::black_box,time::Instant};
fn main(){
 let initial=Recovery::new([100;3]).shock(&[(0,40),(124,70)]).unwrap();
 let methods:[(&str,fn(&Recovery)->Option<Recovery>);3]=[("serial",Recovery::step),("parallel",Recovery::parallel_step),("fixed",Recovery::fixed_step)];
 let reference=initial.step().unwrap();
 for (name,f) in methods {assert_eq!(f(&initial).unwrap(),reference);for _ in 0..100{black_box(f(black_box(&initial)));}for sample in 0..5{let start=Instant::now();for _ in 0..1000{black_box(f(black_box(&initial)));}println!("{name},{sample},1000,{}",start.elapsed().as_nanos());}}
}
