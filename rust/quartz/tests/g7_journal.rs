use quartz_kernel::{journal::{Event,Journal},CENTER};
#[test] fn replay_roundtrip(){
 for seed in 0..32u32 {
  let mut j=Journal::new([seed,40,90]);
  for tick in 0..16 {
   let old=j.clone();
   let event=if tick%4==0 {Event::Shock(vec![(0,((seed+tick)%100+1) as u8),(124,20)])}else{Event::Recover};
   j=j.append(event).unwrap();
   assert_eq!(old.events(),&j.events()[..old.events().len()]);
   assert_eq!(Journal::decode(&j.encode()),Some(j.clone()));
   assert_eq!(Journal::replay([seed,40,90],j.events()),Some(j.clone()));
   assert_eq!(j.state().health()[CENTER],100);
  }
 }
}
#[test] fn reject_invalid(){
 let j=Journal::new([1,2,3]);
 assert!(j.append(Event::Shock(vec![(CENTER,1)])).is_none());
 for s in ["QJ2 1 2 3\n","QJ1 1 2 3\nR extra\n","QJ1 1 2 3\nS 62:1\n","QJ1 1 2 3\nS 125:1\n","QJ1 1 2 3\nS 0:256\n","QJ1 1 2 3\nR"] {assert!(Journal::decode(s).is_none());}
 assert!(j.events().is_empty());
}
