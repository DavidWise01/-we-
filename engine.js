(()=>{'use strict';const data=window.WE_RECORD;if(!data)throw Error('WE_RECORD missing');const q=id=>document.getElementById(id),canvas=q('screen'),g=canvas.getContext('2d',{alpha:false});canvas.width=960;canvas.height=540;g.imageSmoothingEnabled=false;let n=0,t=0,paused=false,heard=new Set(),answers={},sound=false;const storage='we.story.'+data.id;try{const s=JSON.parse(localStorage.getItem(storage)||'{}');n=Math.max(0,Math.min(6,s.scene||0));heard=new Set(s.heard||[]);answers=s.answers||{}}catch(e){}const R=(x,y,w,h,c)=>{g.fillStyle=c;g.fillRect(Math.round(x),Math.round(y),Math.ceil(w),Math.ceil(h))},T=(s,x,y,color='#fff0c8',size=8)=>{g.fillStyle=color;g.font='bold '+size+'px monospace';g.fillText(s,x,y)},L=(x,y,w,h,c)=>{R(x,y,w,2,c);R(x,y+h-2,w,2,c);R(x,y,2,h,c);R(x+w-2,y,2,h,c)};function person(x,y,coat,hair,phase=0){const b=Math.sin(t/18+phase)*1.4;R(x-6,y-21+b,12,11,'#e8bca0');R(x-7,y-26+b,14,7,hair);R(x-10,y-10+b,20,22,coat);R(x-8,y+12+b,6,13,'#203e57');R(x+2,y+12+b,6,13,'#203e57');R(x-12,y-7+b,3,17,'#cba68f');R(x+9,y-7+b,3,17,'#cba68f');R(x+2,y-17+b,2,2,'#30405b')};function city(){R(0,0,320,180,'#091a2d');for(let j=0;j<9;j++){let x=j*43-9;R(x,20,35,118,'#245575');R(x+4,26,27,103,'#43899b');R(x+7,31,21,94,'#142e4f');R(x+7,31,3,91,'#9be6e2');for(let y=38;y<122;y+=22)R(x+10,y,18,2,'#6598aa')}R(0,132,320,28,'#19394c');for(let x=0;x<320;x+=21)R(x,141,13,2,'#527f88');for(let j=0;j<10;j++){let x=j*39+((t/3)%39);R(x,110,3,15,'#75b4c1')}}
function w002(m){
 const d=(x,y)=>person(x,y,'#d5b6a2','#a67b5b',0);
 const o=(x,y)=>person(x,y,'#e5a5c7','#d4a57c',1);
 const i=(x,y)=>{person(x,y,'#a98cd9','#414059',2);R(x-8,y-16,4,2,'#fff3ef');R(x+4,y-16,4,2,'#fff3ef')};
 const title=s=>{R(18,24,284,19,'#152d46');L(18,24,284,19,'#8be8da');T(s,25,37,'#ffcb99',8)};
 if(m===0){R(0,22,320,107,'#275d77');R(0,99,320,30,'#2e936d');for(let j=0;j<15;j++){const x=(j*25+t/4)%320;R(x,54+j%5*11,3,3,'#f5d485')}d(240,116);title('SPRING CROSSES THE WALL')}
 if(m===1){R(36,49,250,81,'#2c5a74');for(let j=0;j<6;j++){let x=51+j*39;R(x,85,28,34,'#416d80');R(x+4,72,20,12,'#b9d6e1');R(x+13,61+Math.sin(t/12+j)*4,4,13,'#ffbd81')}d(39,116);title('THE INTEGRAL / MECHANICAL BALLET')}
 if(m===2){d(95,114);o(225,114);R(139,55,45,30,'#376c85');T('SPRING',143,74,'#ffe0b0',8);title('O-90 / TWO DIFFERENT THOUGHTS')}
 if(m===3){for(let j=0;j<8;j++)person(20+j*39,114,['#9fbfd0','#b9a5db'][j%2],'#7c768b',j);R(146,48,28,20,'#b49677');T('4x',153,61,'#fff0ca',9);title('FOUR ABREAST / THE MARCH')}
 if(m===4){d(78,114);i(240,113);R(130,56,65,51,'#513d70');L(130,56,65,51,'#e3a0e5');T('X',154,88,'#ffcfeb',20);title('I-330 / THE UNRESOLVED X')}
 if(m===5){o(55,115);d(160,113);i(269,114);R(146,55,28,31,'#e6baa6');for(let j=0;j<4;j++)R(149+j*6,61,2,17,'#88614f');title('INDIVIDUALS NOT IDENTICAL')}
 if(m===6){d(71,116);o(124,116);i(266,112);R(153,55,83,45,'#215673');L(153,55,83,45,'#9fe9d7');T('AUD. 112',162,82,'#ffdda9',11);title('INVITATION != ARRIVAL')}
}

function w003(m){
 const d=(x,y)=>person(x,y,'#d5b8a2','#a67959',1),s=(x,y)=>person(x,y,'#7883a2','#303747',2);
 const banner=msg=>{R(17,23,286,21,'#10273c');L(17,23,286,21,'#8fe4d7');T(msg,25,37,'#ffd3a3',8)};
 const coat=(x,y)=>{R(x,y,55,60,'#c7a77b');R(x+8,y-6,39,13,'#e6c9a2');R(x-12,y+13,18,39,'#967b70');R(x+49,y+13,18,39,'#967b70');R(x+24,y+4,7,45,'#6e6067')};
 const table=(x,y)=>{R(x,y,154,78,'#ab7b4f');R(x+5,y+5,144,68,'#e5b86f');for(let j=0;j<6;j++){R(x+12+j*22,y+13,14,13,'#724aa0');T(('0'+(j+1)).slice(-2),x+13+j*22,y+22,'#f0defb',8);R(x+12+j*22,y+37,14,13,'#724aa0');T(('0'+(j+7)).slice(-2),x+13+j*22,y+46,'#f0defb',8)}};
 if(m===0){d(75,114);R(117,54,151,69,'#1a3d5b');L(117,54,151,69,'#81d9de');T('DEAR FUTURE',142,77,'#ffd6a6',10);T('READER...',154,96,'#a0f5e4',10);banner('THE UNKNOWN READER')}
 if(m===1){coat(151,62);d(69,114);T('?',222,86,'#ffd69d',19);banner('THE COAT / THE CONVENTION')}
 if(m===2){R(0,55,320,75,'#266769');for(let j=0;j<18;j++){const x=j*20;R(x,64,4,64,'#68ae7e')}R(0,94,320,7,'#7dbe81');R(82,50,9,85,'#8fa5a4');R(229,50,9,85,'#8fa5a4');d(152,117);banner('TWO-HUNDRED-YEAR WAR / THE WALL')}
 if(m===3){table(101,52);d(54,117);banner('PURPLE NUMBERS / GOLDEN GROUND')}
 if(m===4){for(let j=0;j<10;j++)person(16+j*33,117,j%2?'#9ac1cd':'#baa5d9','#6f7791',j);R(105,51,110,36,'#244a62');T('ALL AT ONCE',119,76,'#ffdaae',10);banner('THE ONE STATE MOVES AS ONE')}
 if(m===5){table(102,50);d(67,117);R(267,65,27,52,'#514361');R(269,67,23,48,'#9ca6b9');T('16',275,81,'#251e45',9);T('21',275,99,'#251e45',9);banner('PERSONAL HOURS / 86,400 SEC')}
 if(m===6){d(59,117);s(262,114);R(127,58,65,51,'#1a3955');L(127,58,65,51,'#d8a8dd');T('S → ?',141,90,'#ffddb3',14);banner('A MEMORY / NOT YET A PROOF')}
}

function w004(m){
const d=(x,y)=>person(x,y,'#d5b5a0','#a67b58',1),o=(x,y)=>person(x,y,'#dda1c8','#d8a773',2),i=(x,y)=>person(x,y,'#322b42','#24243a',3);
const banner=s=>{R(16,21,288,21,'#112b43');L(16,21,288,21,'#8de7d9');T(s,24,35,'#ffd5a1',8)};
const seats=()=>{for(let j=0;j<9;j++){let x=18+j*37;R(x,98,24,26,'#29586c');R(x+6,92,12,10,'#bfbac7')}};
const piano=()=>{R(137,70,99,43,'#211d35');R(139,109,96,6,'#e4d7ce');for(let j=0;j<13;j++)R(145+j*7,108,5,8,'#f8ebe6');for(let j=0;j<6;j++)R(152+j*14,108,3,5,'#252536');R(145,114,7,20,'#302737');R(224,114,7,20,'#302737')};
if(m===0){d(63,116);R(120,53,147,73,'#23495d');L(120,53,147,73,'#70dccc');T('ASSIGNMENT',137,75,'#ffdcaa',10);T('AUDITORIUM 112',126,92,'#aeebe3',10);T('1 / 20,000',152,111,'#fbc39e',10);banner('PREDICTION / AN UNLIKELY ORDER')}
if(m===1){R(27,48,266,76,'#285977');for(let j=0;j<10;j++){let x=44+j*25;R(x,55,17,64,'#457c92');R(x+5,59,8,57,'#8bd9df')}seats();d(47,121);banner('GLASS HEMISPHERE / PUBLIC ANTHEM')}
if(m===2){R(85,47,152,82,'#294a60');R(116,56,95,54,'#f1cc9b');R(155,65,4,32,'#9a5764');R(149,87,18,5,'#4d6480');T('RAIN',132,110,'#573754',9);R(78,112,161,5,'#c5a07b');d(51,117);banner('BAROMETER READING IS NOT RAIN')}
if(m===3){R(39,50,246,82,'#173e59');for(let j=0;j<7;j++){let x=55+j*33;R(x,82,23,31,'#4d7992');R(x+9,60+(j%2)*8,5,22,'#d8a17f');R(x+11,58,12,3,'#d5f3ee')}d(270,116);T('MUSICOMETER',113,119,'#ffe3b4',10);banner('STATE APPROVED / FORMULA MUSIC')}
if(m===4){R(27,47,266,77,'#3a3053');piano();i(104,116);d(53,114);for(let j=0;j<6;j++){let x=176+j*17,y=50+Math.sin(t/15+j)*8;R(x,y,5,5,'#f2bddc')}banner('I-330 / OLD PIANO MUSIC')}
if(m===5){seats();d(163,114);R(111,51,99,35,'#453c68');T('...',147,70,'#d7addc',15);banner('LAUGHTER / PUBLIC VS PRIVATE')}
if(m===6){R(57,49,216,79,'#20475f');R(77,57,152,58,'#3d7390');R(75,60,5,61,'#8dd8e1');R(219,60,5,61,'#8dd8e1');d(115,115);o(203,115);R(133,55,48,16,'#cf91ba');T('TICKET',135,66,'#241f3b',9);R(205,89,3,8,'#9ee1ed');banner('O-90 / AUTHORIZED PRIVACY')}
}

function w005(m){
const d=(x,y)=>person(x,y,'#d3b4a1','#ab7b56',0);
const banner=s=>{R(15,22,290,21,'#102c43');L(15,22,290,21,'#81e4d4');T(s,23,36,'#ffe0a9',8)};
const diamond=(x,y)=>{R(x,y,75,70,'#3e4b76');L(x,y,75,70,'#d4b5ea');R(x+12,y+13,50,43,'#ba9acb');L(x+12,y+13,50,43,'#eed8fc')};
if(m===0){d(74,115);diamond(153,54);T('90',181,77,'#37294c',11);T('90',181,102,'#37294c',11);banner('A SQUARE EXPLAINS ITSELF')}
if(m===1){d(53,117);R(105,55,90,57,'#266075');R(208,55,90,57,'#54426c');T('HUNGER',123,81,'#fff0b8',10);T('LOVE',238,81,'#ffe1cf',10);T('2',157,101,'#aff0e0',11);banner('TWO RULERS / ONE STATE')}
if(m===2){R(0,54,320,73,'#5b5b64');for(let j=0;j<7;j++){let x=23+j*45;R(x,82,18,45,'#3c6570');R(x+7,69,6,13,'#e8a77d');R(x+13,94,11,4,'#c9997e')}R(107,66,33,9,'#f0b36e');R(176,59,47,8,'#8e94aa');d(278,118);banner('CITY / COUNTRYSIDE / WAR')}
if(m===3){R(38,51,244,76,'#1e475a');for(let j=0;j<6;j++){let x=55+j*38;R(x,78,24,38,'#40798a');R(x+5,61,14,18,'#ebbd87');R(x+9,90,7,15,'#d6f0df')}d(37,117);T('SYNTHETIC FOOD',122,123,'#ffe0aa',9);banner('FOOD FROM INDUSTRY')}
if(m===4){R(65,47,196,83,'#264960');L(65,47,196,83,'#70cbd1');T('BUREAU OF SEX',113,67,'#ffceae',11);R(96,77,143,32,'#e9be9a');R(105,83,125,20,'#d39fc0');T('PINK TICKET',122,96,'#2c2740',10);d(55,113);banner('OFFICIAL PERMISSION / CONSENT?')}
if(m===5){d(59,115);R(118,56,154,61,'#233f5c');L(118,56,154,61,'#87e0dc');T('LOVE = F(X)?',130,81,'#ffe0a4',11);T('HAPPINESS?',142,103,'#d6b5f9',9);banner('THE CALCULATION OF FEELING')}
if(m===6){d(64,114);R(123,52,151,79,'#253c57');L(123,52,151,79,'#adbbdc');R(145,78,91,31,'#e0b89c');for(let j=0;j<5;j++){R(153+j*17,63,8,36,'#e6bda8');R(156+j*17,67,2,25,'#6d5d58')}T('X',240,93,'#ffca9b',21);banner('THE UNERASED UNKNOWN X')}
}

function w006(m){
 const D=(x,y)=>person(x,y,'#ccb7ac','#a4785d',1),I=(x,y)=>person(x,y,'#b68ad2','#24283a',3);
 const B=s=>{R(12,21,296,22,'#102a43');L(12,21,296,22,'#91e2dc');T(s,21,36,'#ffd9a6',8)};
 const house=()=>{R(67,49,192,83,'#5e536b');R(79,62,169,69,'#302d49');R(99,70,37,61,'#8c6958');R(141,64,29,41,'#b38c68');R(178,66,55,44,'#434160');R(192,74,26,27,'#a7657d');R(148,114,61,9,'#ae7960')};
 const clock=(x,y)=>{R(x,y,57,43,'#e3c08b');R(x+5,y+5,47,33,'#325770');T('15:50',x+9,y+26,'#fce7bd',12)};
 if(m===0){R(34,51,251,81,'#23475b');L(34,51,251,81,'#75c5d0');T('JUSTICE / PLAZA OF CUBE',52,76,'#ffd6ae',10);T('STATE NOTICE',101,96,'#91e6d9',10);D(56,113);B('A CEREMONY / AN UNEXPECTED EVENT')}
 if(m===1){D(69,115);clock(113,51);R(225,64,36,42,'#d5bfa9');R(232,58,23,15,'#bfa8bf');R(238,90,10,22,'#243749');T('CALL',226,122,'#f1c99b',9);B('TELEPHONE / TEN TO SIXTEEN')}
 if(m===2){R(0,19,320,104,'#256d86');for(let j=0;j<8;j++){let x=(j*51+t/4)%330;R(x,41+j%3*21,27,5,'#b9d8e7')}R(67,81,191,35,'#325b7a');R(95,69,141,17,'#b8dde2');R(102,70,129,14,'#70a8b9');D(136,106);I(199,106);R(0,127,320,8,'#2d906c');B('AERO / SKY / GREEN WALL')}
 if(m===3){house();D(51,115);I(262,114);person(230,113,'#b2a08f','#f1e1bd',2);R(116,56,37,8,'#d8b49d');B('THE CARETAKER REMEMBERS')}
 if(m===4){house();I(206,115);D(82,116);R(133,59,30,42,'#d1bdad');R(136,62,24,36,'#1b3750');T('?',146,86,'#ffe1b9',14);B('OPAQUE WALLS / HIDDEN THOUGHT')}
 if(m===5){house();D(55,114);person(250,114,'#e6c35e','#26263b',2);R(117,53,95,47,'#4d4063');L(117,53,95,47,'#ebbf95');T('STAY?',142,79,'#ffe6b5',11);B('THE YELLOW DRESS / AN OFFER')}
 if(m===6){D(62,116);R(122,51,151,77,'#203c55');L(122,51,151,77,'#88d7dd');T('24 HOURS',139,83,'#ffdbb2',12);T('REPORT?',149,102,'#ccb9ef',10);B('DECLARED DUTY / DEFERRED ACTION')}
}

function w007(m){
const d=(x,y)=>person(x,y,'#d9b8a1','#a87752',1),o=(x,y)=>person(x,y,'#dfa3c6','#d8ab75',2),s=(x,y)=>{person(x,y,'#738aa0','#354052',3);R(x-11,y-30,22,3,'#6c89a6')};
const banner=msg=>{R(13,22,294,21,'#0d2a44');L(13,22,294,21,'#88e1d7');T(msg,21,36,'#ffe0a9',8)};
if(m===0){R(0,18,320,116,'#29274b');for(let j=0;j<9;j++){let x=(j*41+t/3)%320,y=46+j%3*21;R(x,y,23,7,['#aa6ed0','#4aa4ba','#dd9465'][j%3])}R(135,55,53,60,'#a9876e');R(153,67,17,24,'#c8ac7b');R(149,57,25,10,'#d9c09c');R(204,56,57,67,'#e1b653');d(72,115);banner('DREAM / YELLOW / BRONZE')}
if(m===1){for(let j=0;j<7;j++){let x=17+j*46;R(x,53,36,77,'#387c8f');R(x+4,57,28,68,'#9acdd0');person(x+17,105,'#aeb4ca','#687086',j)}d(158,119);T('7:00',135,52,'#ffe1a9',13);banner('THE CLOCK / THE EYELASH')}
if(m===2){R(39,50,244,80,'#20536c');for(let j=0;j<6;j++){let x=52+j*39;R(x,79,28,37,'#4d8294');R(x+9,63,9,17,'#edb57b');R(x+11,66,4,24,'#b8e6db')}d(68,118);R(116,51,139,16,'#20334e');T('M = M(t)',151,62,'#ffe0ac',10);banner('CALCULATION / INTRUSIVE MEMORY')}
if(m===3){d(64,116);s(256,114);R(127,54,67,55,'#2d4662');L(127,54,67,55,'#d6b1d8');T('S-4711',136,75,'#ffdaae',10);T('REPORT?',138,95,'#a1eae2',9);banner('GUARDIAN / HESITATION')}
if(m===4){d(66,115);R(123,53,146,72,'#d6bf99');R(132,61,128,56,'#e8d7b8');T('STATE',166,74,'#5e3f54',12);T('GAZETTE',153,90,'#5e3f54',12);T('LIBERTY?',155,107,'#76556c',9);banner('NEWSPAPER / OPPOSITION')}
if(m===5){d(91,116);o(234,114);R(141,65,42,41,'#426958');for(let j=0;j<5;j++){let x=148+j*7;R(x,74,3,29,'#7cc686');R(x-2,69,8,7,'#f6efe1')}banner('O-90 / LILY OF THE VALLEY')}
if(m===6){R(44,50,232,80,'#214a63');R(60,60,200,62,'#2f6d84');R(148,62,28,42,'#9dd4d4');R(155,70,14,25,'#153e58');d(92,113);R(216,63,29,32,'#d5c5a5');T('MED',220,83,'#574a54',9);banner('MEDICAL BUREAU / NO REPORT')}
}

function w008(m){
 const D=(x,y)=>person(x,y,'#d6b9ab','#ac7652',1),O=(x,y)=>person(x,y,'#daa0c3','#d4a77d',2),P=(x,y)=>person(x,y,'#a3a8c9','#34384d',3);
 const B=s=>{R(14,22,292,21,'#10283e');L(14,22,292,21,'#82dacf');T(s,22,36,'#ffdaa4',8)};
 const tri=()=>{for(let j=0;j<3;j++){let x=[160,95,235][j],y=[56,127,127][j];R(x-4,y-4,9,9,'#ffb777')}for(let i=0;i<90;i++){let p=i/89;R(160+(95-160)*p,56+(127-56)*p,2,2,'#90e2e0');R(160+(235-160)*p,56+(127-56)*p,2,2,'#90e2e0');R(95+(235-95)*p,127,2,2,'#90e2e0')}};
 if(m===0){R(20,52,280,75,'#355570');for(let j=0;j<8;j++){let x=26+j*35;R(x,78,19,26,'#a3a8ba');R(x+5,67,9,12,'#e5c0a2')}R(107,55,110,57,'#26354e');T('sqrt(-1)',119,88,'#eec7ff',16);D(64,115);B('PLAPPA / AN UNFAMILIAR ROOT')}
 if(m===1){D(81,115);R(137,53,128,70,'#314364');L(137,53,128,70,'#b6a9d9');T('I WAS ILL?',144,76,'#ffdca6',10);T('OR AFRAID?',149,100,'#e4b5fc',11);B('REVISITING THE RECORD')}
 if(m===2){R(64,49,192,82,'#2c5a72');L(64,49,192,82,'#a0e2de');T('GUARDIANS',123,69,'#f7ddba',10);for(let j=0;j<5;j++)person(110+j*25,112,'#8ca6be','#6b728d',j);D(49,114);B('16:10 / THE UNENTERED DOOR')}
 if(m===3){D(56,115);P(260,114);O(198,114);R(117,53,69,54,'#45395e');T('R-13',132,79,'#ffe0ad',13);T('?',149,99,'#dcb7e9',12);B('THE POET / THE MATHEMATICIAN')}
 if(m===4){D(55,113);P(166,113);O(268,113);R(94,55,28,27,'#bfa77e');R(231,72,33,21,'#c19a8d');R(139,79,41,15,'#a6c9d0');B('OLD FRIENDS / MOVED CHAIRS')}
 if(m===5){P(75,114);D(269,113);R(116,55,117,64,'#2e4762');L(116,55,117,64,'#d2accb');T('POEM',153,75,'#ffdda9',12);T('SENTENCE',132,95,'#f4bfa5',9);B('THE POET / PUBLIC PUNISHMENT')}
 if(m===6){tri();D(54,113);P(254,114);O(160,110);R(244,59,38,29,'#627e91');R(248,63,30,22,'#747292');B('D-503 / O-90 / R-13 TRIANGLE')}
}

function w009(m){
const D=(x,y)=>person(x,y,'#d2baa9','#a97e60',1),P=(x,y)=>person(x,y,'#a4a6c9','#343d50',3);
const B=s=>{R(12,22,296,21,'#102b43');L(12,22,296,21,'#9cece0');T(s,20,36,'#ffdbaf',8)};
const plaza=()=>{R(0,43,320,86,'#28536a');for(let j=0;j<8;j++){let inset=j*11;R(inset,111-j*8,320-inset*2,4,j%2?'#4f8b9e':'#94bdc5')}R(131,62,60,53,'#9c9dad');R(139,55,44,10,'#d3c0a6');R(151,67,19,43,'#496070')};
const leader=(x,y)=>{R(x-17,y-32,34,8,'#4b5a69');R(x-13,y-24,26,12,'#b8b2ac');R(x-19,y-12,38,31,'#5b6774');R(x-16,y+19,12,14,'#273a49');R(x+4,y+19,12,14,'#273a49');R(x-30,y-7,13,24,'#c2b7a5');R(x+17,y-7,13,24,'#c2b7a5')};
if(m===0){plaza();for(let j=0;j<8;j++)person(24+j*39,118,['#aac4cf','#b7a6d1'][j%2],'#7f7886',j);B('SIXTY-SIX CONCENTRIC TIERS')}
if(m===1){plaza();R(155,88,12,18,'#d4b7a2');R(152,103,18,24,'#d9dad6');R(152,117,18,3,'#735076');B('ONE CONDEMNED PERSON')}
if(m===2){plaza();leader(163,81);R(180,53,64,35,'#354e67');R(183,56,58,29,'#6d8192');B('THE CAST-IRON HAND')}
if(m===3){plaza();person(52,115,'#95a9c7','#4f546c',1);R(209,56,77,48,'#263f59');L(209,56,77,48,'#e0b992');T('STEEL',222,78,'#ffd9a7',11);T('LAW',232,94,'#addfe3',10);B('STATE VERSE / ORDER VS CHAOS')}
if(m===4){plaza();P(57,117);D(264,117);R(130,54,70,54,'#423857');T('R-13',148,78,'#ffdca4',12);R(158,90,13,3,'#dfa4b7');B('R-13 / A PALE PERFORMANCE')}
if(m===5){plaza();R(116,48,90,83,'#142235');R(121,53,80,73,'#253e57');R(139,61,45,55,'#647b86');R(139,61,45,2,'#a0dfdd');R(125,87,70,35,'#0b1a2c');T('SILENCE',132,106,'#c6ced8',11);B('AN EXECUTION / NON-GRAPHIC')}
if(m===6){plaza();leader(160,80);for(let j=0;j<7;j++){let x=32+j*43;R(x,120,2,10,'#4da17b');R(x-4,114,9,7,j%2?'#f1b77d':'#e4aac9')}B('CHEERS / FLOWERS / LOSS')}
}

function w010(m){
const D=(x,y)=>person(x,y,'#d3b5a1','#a87959',1),I=(x,y,yellow=false)=>person(x,y,yellow?'#e4bb62':'#a98aca','#343045',2);
const B=s=>{R(12,21,296,23,'#0f2942');L(12,21,296,23,'#89e2dc');T(s,20,36,'#ffdda6',8)};
const clock=(x,y,v)=>{R(x,y,82,37,'#213b55');L(x,y,82,37,'#92e9df');T(v,x+11,y+25,'#ffe2ad',14)};
if(m===0){R(58,49,207,80,'#2c5a6c');R(69,56,187,70,'#5b8e9a');person(229,114,'#a3a9c1','#938a87',2);D(62,115);R(132,64,51,40,'#e8ceaf');R(155,84,8,8,'#243d5a');B('U / LETTER / REGISTRY')}
if(m===1){D(66,114);R(115,49,151,83,'#254259');R(127,55,126,66,'#ead8c0');R(136,66,110,44,'#d9acba');T('I-330',163,84,'#3b2d50',14);T('21:00',164,101,'#3b2d50',11);B('A PINK-TICKET APPOINTMENT')}
if(m===2){for(let j=0;j<8;j++){let x=j*46-6;R(x,29,37,105,'#2d6577');R(x+5,35,28,94,'#70bcb4');R(x+10,39,18,86,'#19485e')}D(173,116);clock(29,52,'20:45');B('THE FRAGILE GLASS NIGHT')}
if(m===3){D(68,115);I(254,114);R(114,52,103,66,'#3b3a65');L(114,52,103,66,'#caacd8');T('48 HRS',130,78,'#ffdfba',13);T('NO REPORT',127,97,'#f2b3ad',10);B('MISSED DEADLINE / NEW RISK')}
if(m===4){R(20,49,280,77,'#423555');for(let j=0;j<5;j++)R(35+j*54,50,47,77,'#614d75');D(84,116);R(185,70,82,35,'#24485c');for(let j=0;j<8;j++)R(195+j*9,80+Math.sin(t/12+j)*7,3,14,'#8fe4da');B('MEMBRANE / LISTENING != KNOWING')}
if(m===5){R(24,48,272,82,'#44374d');D(67,115);I(255,113,true);R(124,54,76,64,'#273c55');L(124,54,76,64,'#bb9ed1');T('I',146,78,'#f4c5e9',16);T('I',176,103,'#ffcb9a',16);R(124,110,76,6,'#c0807e');B('TWO SELVES / CONFLICT / BOUNDARY')}
if(m===6){clock(123,56,'22:25');D(63,117);R(240,50,39,61,'#2d5874');R(243,53,33,55,'#77bab6');R(247,62,24,31,'#193e56');R(159,106,13,6,'#d2bd97');B('CURFEW / FLIGHT / INSOMNIA')}
}

function w011(m){
const D=(x,y)=>person(x,y,'#ccb5a2','#9f7659',1),P=(x,y)=>person(x,y,'#a6b0d0','#353b52',2),O=(x,y)=>person(x,y,'#dda4c6','#cfa277',3);
const B=s=>{R(13,22,294,21,'#112c44');L(13,22,294,21,'#8dece0');T(s,22,36,'#ffd7a6',8)};
const mirror=()=>{R(131,49,85,81,'#8c779e');R(136,54,75,72,'#c1dcdd');R(143,61,62,60,'#32687c');R(167,75,15,20,'#e2b29a');R(163,68,23,8,'#674f5b');R(159,95,31,22,'#526e92')};
if(m===0){R(0,20,320,99,'#8996a9');for(let j=0;j<11;j++){let x=(j*39+t/5)%320;R(x,40+(j%3)*15,52,8,'#d3d3c6')}R(0,119,320,16,'#425b77');D(161,117);B('MILKY GOLD / AN OPAQUE SKY')}
if(m===1){mirror();D(80,114);R(238,53,38,48,'#413b67');T('WHO?',240,81,'#ffdfac',10);B('THE STRANGER IN THE MIRROR')}
if(m===2){D(69,116);P(255,116);R(129,57,73,55,'#334761');L(129,57,73,55,'#e2b6c9');T('R-13',141,86,'#ffe4b4',14);B('THE POET RETURNS')}
if(m===3){R(52,49,223,79,'#3b4267');R(73,61,78,50,'#e2c18c');R(171,61,77,50,'#a3b4bf');T('EVE',93,86,'#4e4056',14);T('ADAM',187,86,'#2a4763',12);T('FREE?',105,106,'#4e4056',9);T('HAPPY?',180,106,'#2a4763',9);B('THE EDEN QUESTION / TWO OPTIONS')}
if(m===4){D(62,114);P(266,114);R(126,57,80,52,'#d3a1c2');L(126,57,80,52,'#f0caa2');T('O-90',145,79,'#312948',13);T('TICKET',140,100,'#312948',10);B('O-90 / DIFFERING AFFECTION')}
if(m===5){D(73,114);P(252,114);R(122,49,91,73,'#493858');T('I-330',143,76,'#f3bfdc',12);T('?',162,103,'#ffdaaa',19);R(131,110,74,4,'#d39182');B('JEALOUSY / UNINVITED FEELING')}
if(m===6){D(72,116);P(259,114);R(132,65,69,47,'#b9a2c8');R(136,68,61,41,'#e8d5c2');T('POEMS',146,91,'#66546b',10);B('APOLOGY / THE TRIANGLE SHIFTS')}
}
function frame(){g.setTransform(3,0,0,3,0,0);g.imageSmoothingEnabled=false;city();const mode=data.scenes[n].mode;if(data.id==='W011'){w011(mode);R(0,0,320,17,'#081221');T('ONE STATE / RECORD '+data.id,6,12,'#80f2e9',8);R(0,157,320,23,'#061224');R(0,157,320,2,'#e89b60');T('ACT '+(n+1)+'/7  '+data.scenes[n].setting.slice(0,21),7,171,'#ffcf9c',8);T(paused?'PAUSED':'CANVAS2D',258,171,'#89e9da',7);return;}if(data.id==='W010'){w010(mode);R(0,0,320,17,'#081221');T('ONE STATE / RECORD '+data.id,6,12,'#80f2e9',8);R(0,157,320,23,'#061224');R(0,157,320,2,'#e89b60');T('ACT '+(n+1)+'/7  '+data.scenes[n].setting.slice(0,21),7,171,'#ffcf9c',8);T(paused?'PAUSED':'CANVAS2D',258,171,'#89e9da',7);return;}if(data.id==='W009'){w009(mode);R(0,0,320,17,'#081221');T('ONE STATE / RECORD '+data.id,6,12,'#80f2e9',8);R(0,157,320,23,'#061224');R(0,157,320,2,'#e89b60');T('ACT '+(n+1)+'/7  '+data.scenes[n].setting.slice(0,21),7,171,'#ffcf9c',8);T(paused?'PAUSED':'CANVAS2D',258,171,'#89e9da',7);return;}if(data.id==='W008'){w008(mode);R(0,0,320,17,'#081221');T('ONE STATE / RECORD '+data.id,6,12,'#80f2e9',8);R(0,157,320,23,'#061224');R(0,157,320,2,'#e89b60');T('ACT '+(n+1)+'/7  '+data.scenes[n].setting.slice(0,21),7,171,'#ffcf9c',8);T(paused?'PAUSED':'CANVAS2D',258,171,'#89e9da',7);return;}if(data.id==='W007'){w007(mode);R(0,0,320,17,'#081221');T('ONE STATE / RECORD '+data.id,6,12,'#80f2e9',8);R(0,157,320,23,'#061224');R(0,157,320,2,'#e89b60');T('ACT '+(n+1)+'/7  '+data.scenes[n].setting.slice(0,21),7,171,'#ffcf9c',8);T(paused?'PAUSED':'CANVAS2D',258,171,'#89e9da',7);return;}if(data.id==='W006'){w006(mode);R(0,0,320,17,'#081221');T('ONE STATE / RECORD '+data.id,6,12,'#80f2e9',8);R(0,157,320,23,'#061224');R(0,157,320,2,'#e89b60');T('ACT '+(n+1)+'/7  '+data.scenes[n].setting.slice(0,21),7,171,'#ffcf9c',8);T(paused?'PAUSED':'CANVAS2D',258,171,'#89e9da',7);return;}if(data.id==='W005'){w005(mode);R(0,0,320,17,'#081221');T('ONE STATE / RECORD '+data.id,6,12,'#80f2e9',8);R(0,157,320,23,'#061224');R(0,157,320,2,'#e89b60');T('ACT '+(n+1)+'/7  '+data.scenes[n].setting.slice(0,21),7,171,'#ffcf9c',8);T(paused?'PAUSED':'CANVAS2D',258,171,'#89e9da',7);return;}if(data.id==='W004'){w004(mode);R(0,0,320,17,'#081221');T('ONE STATE / RECORD '+data.id,6,12,'#80f2e9',8);R(0,157,320,23,'#061224');R(0,157,320,2,'#e89b60');T('ACT '+(n+1)+'/7  '+data.scenes[n].setting.slice(0,21),7,171,'#ffcf9c',8);T(paused?'PAUSED':'CANVAS2D',258,171,'#89e9da',7);return;}if(data.id==='W003'){w003(mode);R(0,0,320,17,'#081221');T('ONE STATE / RECORD '+data.id,6,12,'#80f2e9',8);R(0,157,320,23,'#061224');R(0,157,320,2,'#e89b60');T('ACT '+(n+1)+'/7  '+data.scenes[n].setting.slice(0,21),7,171,'#ffcf9c',8);T(paused?'PAUSED':'CANVAS2D',258,171,'#89e9da',7);return;}if(data.id==='W002'){w002(mode);R(0,0,320,17,'#081221');T('ONE STATE / RECORD '+data.id,6,12,'#80f2e9',8);R(0,157,320,23,'#061224');R(0,157,320,2,'#e89b60');T('ACT '+(n+1)+'/7  '+data.scenes[n].setting,7,171,'#ffcf9c',8);T(paused?'PAUSED':'CANVAS2D',258,171,'#89e9da',7);return;}const d=(x,y)=>person(x,y,'#c5b1a4','#a37c58'),o=(x,y)=>person(x,y,'#d4a3c2','#be956b');if(mode===0){R(75,50,173,80,'#24526c');L(75,50,173,80,'#8de9e5');R(82,57,156,67,'#14354d');d(165,109);R(103,71,38,26,'#3d7d8c');T('D-503',105,86,'#ffcd92',9)}if(mode===1){R(39,41,245,82,'#183348');L(39,41,245,82,'#8ce5e0');T('TABLE OF HOURS',88,56,'#ffca8d',10);for(let j=0;j<7;j++){R(57+j*34,67,29,23,j%2?'#2b5c70':'#3e7186');T(('0'+(j+1)).slice(-2),62+j*34,81,'#d7f0e4',9)}d(160,113)}if(mode===2){R(42,49,238,78,'#1a4055');for(let j=0;j<6;j++){let x=62+j*40;R(x,88,26,27,'#2f6684');R(x+4,93,18,12,'#91dee0')}R(140,31,40,75,'#b1bac0');R(151,19,17,14,'#f3b16e');d(77,112);T('INTEGRAL',137,122,'#ffe1a4',9)}if(mode===3){d(112,109);o(207,109);for(let j=0;j<7;j++)R(23+j*43,48,23,10,'#467b8b');T('TWO NUMBERS',109,67,'#ffca94',9)}if(mode===4){R(0,43,320,90,'#1b4556');for(let x=0;x<320;x+=14)R(x,57,5,68,'#489b78');R(0,80,320,8,'#92c18b');d(174,119);T('THE GREEN WALL',109,43,'#ffe0aa',9)}if(mode===5){d(120,111);R(166,49,97,72,'#203b55');L(166,49,97,72,'#8bd0df');T('1 + 1 = ?',180,84,'#ffe0b0',10);T('DOUBT',188,99,'#d7b2f2',9)}if(mode===6){d(101,111);o(223,111);R(130,49,63,62,'#1a354e');L(130,49,63,62,'#d3a7c8');T('W001',145,78,'#ffcea0',11);T('?',157,99,'#b4f1ec',14)}R(0,0,320,17,'#081221');T('ONE STATE / RECORD '+data.id,6,12,'#80f2e9',8);R(0,157,320,23,'#061224');R(0,157,320,2,'#e89b60');T('ACT '+(n+1)+'/7  '+data.scenes[n].setting.slice(0,21),7,171,'#ffcf9c',8);T(paused?'PAUSED':'CANVAS2D',258,171,'#89e9da',7)}function persist(){try{localStorage.setItem(storage,JSON.stringify({scene:n,heard:[...heard],answers}))}catch(e){}}function tone(){if(!sound)return;try{const ac=new (window.AudioContext||window.webkitAudioContext)(),osc=ac.createOscillator(),v=ac.createGain();osc.type='triangle';osc.frequency.value=280+(n*40);v.gain.value=.025;osc.connect(v);v.connect(ac.destination);osc.start();osc.stop(ac.currentTime+.065);osc.onended=()=>ac.close()}catch(e){}}function render(){const s=data.scenes[n];q('act').textContent='ACT '+(n+1)+' / 7 · '+s.setting;q('heading').textContent=s.title;q('story').textContent=s.story;q('speaker').textContent=s.speaker;q('speech').textContent=s.line;q('observed').textContent=heard.has(n)?s.observation:'Inspect this act to record its source-bound observation.';q('inferred').textContent=heard.has(n)?s.inference:'Not yet inspected.';q('question').textContent=s.question;let area=q('choices');area.replaceChildren();s.choices.forEach((item,i)=>{const b=document.createElement('button');b.textContent=item;b.className=answers[n]===i?'primary':'';b.onclick=()=>{answers[n]=i;tone();render()};area.appendChild(b)});q('response').textContent=answers[n]===undefined?'Choose an interpretation to test the witness boundary.':s.reply[answers[n]];q('back').disabled=n===0;q('next').disabled=n===6;q('inspect').disabled=heard.has(n);q('count').textContent=heard.size+'/7';q('progress').style.width=(heard.size/7*100)+'%';q('export').disabled=heard.size!==7;persist();frame()}function go(x){n=Math.min(6,Math.max(0,n+x));tone();render()}q('back').onclick=()=>go(-1);q('next').onclick=()=>go(1);q('inspect').onclick=()=>{heard.add(n);tone();render()};q('motion').onclick=()=>{paused=!paused;q('motion').textContent=paused?'RESUME MOTION':'PAUSE MOTION';frame()};q('sound').onclick=()=>{sound=!sound;q('sound').textContent=sound?'SOUND ON':'SOUND OFF';tone()};q('export').onclick=()=>{const packet={record:data.id,source:'original literary interpretation, one ancestry',observed:[...heard].sort(),choices:answers,local_timestamp:new Date().toISOString(),independent_attestation:false};const blob=new Blob([JSON.stringify(packet,null,2)],{type:'application/json'}),url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download='WE-'+data.id+'-witness.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),2000)};q('reset').onclick=()=>{if(confirm('Reset this browser record?')){n=0;heard.clear();answers={};render()}};document.addEventListener('keydown',e=>{if(e.target.closest('button,input,textarea'))return;if(e.key==='ArrowRight')go(1);if(e.key==='ArrowLeft')go(-1);if(e.key.toLowerCase()==='i')q('inspect').click()});function tick(){if(!paused){t++;frame()}requestAnimationFrame(tick)}render();requestAnimationFrame(tick)})();