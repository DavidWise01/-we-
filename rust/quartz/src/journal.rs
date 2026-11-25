use crate::{recovery::Recovery, CELLS};
#[derive(Clone,Debug,PartialEq,Eq)]
pub enum Event { Shock(Vec<(usize,u8)>), Recover }
pub trait Transition { fn apply(&self, prior:&Recovery)->Option<Recovery>; }
impl Transition for Event {
 fn apply(&self, prior:&Recovery)->Option<Recovery>{
  match self {Self::Shock(d)=>prior.shock(d),Self::Recover=>prior.parallel_step()}
 }
}
#[derive(Clone,Debug,PartialEq,Eq)]
pub struct Journal { initial:[u32;3], events:Vec<Event>, state:Recovery }
impl Journal {
 pub fn new(initial:[u32;3])->Self {Self{initial,events:Vec::new(),state:Recovery::new(initial)}}
 pub fn events(&self)->&[Event]{&self.events}
 pub fn state(&self)->&Recovery{&self.state}
 pub fn append(&self,event:Event)->Option<Self>{
  let state=event.apply(&self.state)?;
  let mut events=self.events.clone();events.push(event);
  Some(Self{initial:self.initial,events,state})
 }
 pub fn replay(initial:[u32;3],events:&[Event])->Option<Self>{
  let mut journal=Self::new(initial);
  for event in events {journal.state=event.apply(&journal.state)?;journal.events.push(event.clone());}
  Some(journal)
 }
 /// Canonical text, versioned, portable across native and WASM.
 pub fn encode(&self)->String{
  let mut out=format!("QJ1 {} {} {}\n",self.initial[0],self.initial[1],self.initial[2]);
  for event in &self.events { match event {
   Event::Recover=>out.push_str("R\n"),
   Event::Shock(d)=>{out.push('S');for (i,v) in d {out.push_str(&format!(" {}:{}",i,v));}out.push('\n');}
  }}
  out
 }
 pub fn decode(input:&str)->Option<Self>{
  let mut lines=input.lines();let mut h=lines.next()?.split_whitespace();
  if h.next()? != "QJ1"{return None;}
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
  let journal=Self::replay(initial,&events)?;
  if journal.encode()!=input{return None;}Some(journal)
 }
}
