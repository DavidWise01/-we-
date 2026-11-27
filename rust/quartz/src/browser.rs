use crate::{journal::{Event,Journal}, CELLS};
use wasm_bindgen::prelude::*;
#[wasm_bindgen]
pub struct Quartz { journal:Journal }
#[wasm_bindgen]
impl Quartz {
 #[wasm_bindgen(constructor)]
 pub fn new(r:u32,b:u32,g:u32)->Self{Self{journal:Journal::new([r,b,g])}}
 pub fn shock(&mut self,cell:u32,damage:u32)->bool{
  if cell>=CELLS as u32 || damage>100{return false;}
  self.append(Event::Shock(vec![(cell as usize,damage as u8)]))
 }
 pub fn recover(&mut self)->bool{self.append(Event::Recover)}
 pub fn observation(&self)->Vec<u8>{crate::observation::frame(self.journal.state()).to_vec()}
 pub fn health(&self)->Vec<u8>{self.journal.state().health().to_vec()}
 pub fn energy(&self)->Vec<u32>{self.journal.state().energy().to_vec()}
 pub fn journal(&self)->String{self.journal.encode()}
 pub fn replay(&mut self,input:&str)->bool{
  if input.len()>65536{return false;}
  if let Some(j)=Journal::decode(input){if j.events().len()>2048{return false;}self.journal=j;true}else{false}
 }
}
impl Quartz {
 fn append(&mut self,event:Event)->bool{
  if self.journal.events().len()>=2048{return false;}
  if let Some(j)=self.journal.append(event){self.journal=j;true}else{false}
 }
}

#[wasm_bindgen]
pub fn g39_fixture()->Vec<u8>{crate::parity::fixture().expect("G39 fixture failed")}

#[wasm_bindgen]
pub fn g75_fixture()->Vec<u8>{crate::portable_parity::fixture().expect("G75 fixture failed")}
