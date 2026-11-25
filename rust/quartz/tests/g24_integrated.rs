use quartz_kernel::{journal::{Journal,Event,Policy},pump_memory::derive,cortex::{regulate,Decision},witness::inspect,homeostasis::{run,reconcile},CENTER};
#[test]fn integrated_phase_three(){
 for policy in [Policy::FixedV1,Policy::RotatingV2]{
  for seed in 0..16u32{
   let mut j=Journal::with_policy([100+seed,80,60],policy);
   for t in 0..12{
    j=j.append(Event::Shock(vec![(0,(t*3+1) as u8),(124,7)])).unwrap().append(Event::Recover).unwrap();
    assert_eq!(Journal::decode(&j.encode()),Some(j.clone()));
    assert!(derive(&j).is_some());
    let before=j.clone();
    if let Some(Decision::Trial(order))=regulate(&j){let b=j.state().ordered_step(order).unwrap();assert!(inspect(&j,order,&b).consistent());}
    let s=run(j.state(),16).unwrap();assert!(reconcile(j.state(),16,&s));assert_eq!(s.state.health()[CENTER],100);assert_eq!(j,before);
   }
  }
 }
}
