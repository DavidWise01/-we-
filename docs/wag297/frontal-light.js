/* WAG-297 · frontal shadow / nested illumination · .dlw
 Canonical 1³ is one ADDRESS holding three distinguished unit forms:
 box [1], brace {1}, toroid (1). They are NOT three separate silos.
 All three are initially shadowed. {[()]} is the illumination geometry:
 brace envelope -> box aperture -> toroidal focus.
 This is a purely visual interpretive readout; no photons are simulated.
*/
const WAG297=Object.freeze({frontalAddress:62,volume:'{{1x1}}^{{1}}',
 units:Object.freeze(['[1]','{1}','(1)']),shadow:true,
 illumination:'{[()]}',physicalActions:0});
function wag297Light(level=0){
 if(!Number.isFinite(level)||level<0||level>1)throw Error('illumination outside [0,1]');
 const shadows=WAG297.units.map((form,i)=>Object.freeze({
  form,illumination:level,visible:level>0,
  contribution:level*([.8,.9,1][i])
 }));
 return Object.freeze({address:WAG297.frontalAddress,
  geometry:WAG297.illumination,units:Object.freeze(shadows),
  status:level===0?'SHADOW':level===1?'ILLUMINATED':'EMERGING',
  authority:'VISUALIZATION_ONLY'});
}
function wag297Audit(){
 const original=wag288Initial(),before=JSON.stringify(original);
 const dark=wag297Light(0),lit=wag297Light(1),half=wag297Light(.5);
 const checks={
  exactlyThreeUnitForms:WAG297.units.length===3&&new Set(WAG297.units).size===3,
  exactShadowSyntax:WAG297.units.join('|')==='[1]|{1}|(1)',
  exactIllumination:WAG297.illumination==='{[()]}',
  centerRemainsOneAddress:WAG297.frontalAddress===62&&wag289Groups().frontal.length===1,
  darkness:dark.units.every(x=>!x.visible&&x.contribution===0),
  illuminated:lit.units.every(x=>x.visible&&x.contribution>0),
  intermediate:half.units.every(x=>x.visible&&x.contribution>0&&x.contribution<1),
  validBounds:(()=>{try{wag297Light(2);return false}catch(e){return true}})(),
  noStateMutation:JSON.stringify(original)===before,
  objectImmutable:Object.isFrozen(lit)&&Object.isFrozen(lit.units)&&Object.isFrozen(lit.units[0]),
  independentSilos:new Set(original.nodes).size===125,
  priorLearningValid:wag296Audit().pass,
  noActuation:WAG297.physicalActions===0
 };
 return {bound:'WAG-297',pass:Object.values(checks).every(Boolean),
  checks,scope:'front-lobe shadow/illumination visualization, not physical optics'};
}
if(typeof module!=='undefined')module.exports={WAG297,wag297Light,wag297Audit};
