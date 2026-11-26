use std::io::Write;
fn main(){std::io::stdout().write_all(&quartz_kernel::parity::fixture().expect("G39 fixture failed")).unwrap();}
