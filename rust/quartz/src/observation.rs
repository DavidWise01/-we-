use crate::{recovery::Recovery,CELLS};
pub const FRAME_BYTES:usize=CELLS+3*4+8;
/// Owned, little-endian observation; no mutable alias to engine memory.
pub fn frame(state:&Recovery)->[u8;FRAME_BYTES]{
 let mut out=[0;FRAME_BYTES];
 out[..CELLS].copy_from_slice(state.health());
 for (p,e) in state.energy().iter().enumerate(){
  let offset=CELLS+4*p;out[offset..offset+4].copy_from_slice(&e.to_le_bytes());
 }
 out[CELLS+12..].copy_from_slice(&state.tick().to_le_bytes());
 out
}
#[cfg(test)]
mod tests{
 use super::*;
 #[test] fn layout_and_isolation(){
  let s=Recovery::new([1,256,u32::MAX]).shock(&[(0,40)]).unwrap();
  let mut f=frame(&s);assert_eq!(f.len(),145);assert_eq!(f[0],60);
  assert_eq!(&f[125..137],&[1,0,0,0,0,1,0,0,255,255,255,255]);
  assert_eq!(&f[137..],&[0;8]);f[62]=0;assert_eq!(s.health()[62],100);
  let n=s.step().unwrap();assert_eq!(&frame(&n)[137..],&1u64.to_le_bytes());
 }
}
