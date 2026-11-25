use crate::{CELLS,CENTER};
pub const VALID:u128=(1u128<<125)-1;
pub const CENTER_BIT:u128=1u128<<CENTER;
const fn boundary(axis:usize, high:bool)->u128{
 let mut mask=0;let mut i=0;
 while i<CELLS{let c=(i/axis)%5;if c==if high{4}else{0}{mask|=1u128<<i;}i+=1;}mask
}
pub fn neighbors(bits:u128)->u128{
 let b=bits&VALID;let mut out=0;
 for d in [1usize,5,25]{out|=((b&!boundary(d,true))<<d)|((b&!boundary(d,false))>>d);}
 out&VALID
}
pub fn reachable(health:&[u8;CELLS])->u128{
 let mut healthy=0;let mut damaged=0;
 for (i,&h) in health.iter().enumerate(){if h==100{healthy|=1u128<<i;}else{damaged|=1u128<<i;}}
 neighbors(healthy)&damaged&!CENTER_BIT
}
#[cfg(test)]
mod tests{
 use super::*;
 #[test] fn every_cell(){for i in 0..CELLS{let mut want=0;for(a,b)in crate::edges(){if a==i{want|=1u128<<b;}if b==i{want|=1u128<<a;}}assert_eq!(neighbors(1u128<<i),want);}}
 #[test] fn masks(){assert_eq!(neighbors(!VALID),0);assert_eq!(neighbors(VALID),VALID);for seed in 0..256usize{let mut h=[100;CELLS];for(i,v)in h.iter_mut().enumerate(){if (i*17+seed)%11<seed%11{*v=50;}}let mut want=0;for(a,b)in crate::edges(){if h[a]==100&&h[b]<100{want|=1u128<<b;}if h[b]==100&&h[a]<100{want|=1u128<<a;}}assert_eq!(reachable(&h),want&!CENTER_BIT);}}
}
