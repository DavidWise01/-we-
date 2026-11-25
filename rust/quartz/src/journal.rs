use crate::{recovery::Recovery, CELLS};
#[derive(Clone,Debug,PartialEq,Eq)]
pub enum Event { Shock(Vec<(usize,u8)>), Recover }
pub trait Transition { fn apply(&self, prior:&Recovery)->Option<Recovery>; }
impl Transition for Event {
 fn apply(&self, prior:&Recovery)->Option<Recovery>{
  match self {Self::Shock(d)=>prior.shock(d),Self::Recover=>prior.parallel_step()}
 }
}
#[derive(Clone,Copy,Debug,PartialEq,Eq)]
pub enum Policy { FixedV1, RotatingV2 }
impl Policy {
 fn apply(self,event:&Event,prior:&Recovery)->Option<Recovery>{
  match (self,event){(Self::RotatingV2,Event::Recover)=>prior.rotating_step(),_=>event.apply(prior)}
 }
 fn tag(self)->&'static str{match self{Self::FixedV1=>"QJ1",Self::RotatingV2=>"QJ2"}}
}
#[derive(Clone,Debug,PartialEq,Eq)]
pub struct Journal { initial:[u32;3], events:Vec<Event>, state:Recovery, policy:Policy }
impl Journal {
 pub fn new(initial:[u32;3])->Self {Self::with_policy(initial,Policy::FixedV1)}
 pub fn with_policy(initial:[u32;3],policy:Policy)->Self{Self{initial,events:Vec::new(),state:Recovery::new(initial),policy}}
 pub fn policy(&self)->Policy{self.policy}
 pub fn events(&self)->&[Event]{&self.events}
 pub fn state(&self)->&Recovery{&self.state}
 pub fn append(&self,event:Event)->Option<Self>{
  let state=self.policy.apply(&event,&self.state)?;
  let mut events=self.events.clone();events.push(event);
  Some(Self{initial:self.initial,events,state,policy:self.policy})
 }
 pub fn replay(initial:[u32;3],events:&[Event])->Option<Self>{
  Self::replay_with_policy(initial,Policy::FixedV1,events)
 }
 pub fn replay_with_policy(initial:[u32;3],policy:Policy,events:&[Event])->Option<Self>{
  let mut journal=Self::with_policy(initial,policy);
  for event in events {journal.state=policy.apply(event,&journal.state)?;journal.events.push(event.clone());}
  Some(journal)
 }
 /// Canonical text, versioned, portable across native and WASM.
 pub fn encode(&self)->String{
  let mut out=format!("{} {} {} {}\n",self.policy.tag(),self.initial[0],self.initial[1],self.initial[2]);
  for event in &self.events { match event {
   Event::Recover=>out.push_str("R\n"),
   Event::Shock(d)=>{out.push('S');for (i,v) in d {out.push_str(&format!(" {}:{}",i,v));}out.push('\n');}
  }}
  out
 }
 pub fn decode(input:&str)->Option<Self>{
  let mut lines=input.lines();let mut h=lines.next()?.split_whitespace();
  let policy=match h.next()?{"QJ1"=>Policy::FixedV1,"QJ2"=>Policy::RotatingV2,_=>return None};
  let initial=[h.next()?.parse().ok()?,h.next()?.parse().ok()?,h.next()?.parse().ok()?];
  if h.next().is_some(){return None;}
  let mut events=Vec::new();
  for line in lines {
   let mut parts=line.split_whitespace();
   match parts.next()?{
    "R"=>{if parts.next().is_some(){return None;}events.push(Event::Recover);}
    "S"=>{let mut damage=Vec::new();for p in parts {let (i,v)=p.split_once(':')?;let i:usize=i.parse().ok()?;if i>=CELLS{return None;}damage.push((i,v.parse().ok()?));}events.push(Event::Shock(damage));}
    _=>return None
   }
  }
  let journal=Self::replay_with_policy(initial,policy,&events)?;
  if journal.encode()!=input{return None;}Some(journal)
 }
}
