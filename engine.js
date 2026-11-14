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

function w012(m){
const D=(x,y)=>person(x,y,'#d3b5a0','#a87858',1);
const S=(x,y)=>{person(x,y,'#8292b6','#383954',2);R(x-10,y-30,20,3,'#cda6ac')};
const B=(s)=>{R(12,22,296,20,'#0e2c41');L(12,22,296,20,'#9de9de');T(s,20,35,'#ffe1af',8)};
const book=(x,y)=>{R(x,y,83,50,'#a998b8');R(x+5,y+5,73,40,'#e4d9c3');for(let j=0;j<5;j++){R(x+11,y+13+j*6,26,2,'#9888ac');R(x+44,y+13+j*6,27,2,'#9b88ac')}};
if(m===0){D(57,114);for(let j=0;j<9;j++){let a=j/9*Math.PI*2,x=196+Math.cos(a)*48,y=84+Math.sin(a)*39;R(x,y,6,6,'#c7adf3')}T('FINITE',172,89,'#ffdda9',10);B('THE COMFORT OF A CIRCLE')}
if(m===1){R(18,54,283,68,'#25485e');R(26,85,269,7,'#86b3c4');for(let j=0;j<7;j++){R(26+j*39,107,24,6,'#acc5ce')}D(60,114);book(156,61);B('UNDERGROUND / R-13 POEMS')}
if(m===2){D(90,115);S(249,114);R(139,56,52,46,'#36526b');T('ANGEL?',143,85,'#d2b4ef',11);B('THE WITNESS BEHIND HIM')}
if(m===3){D(58,114);R(112,51,159,75,'#253e58');L(112,51,159,75,'#b09bd2');T('2 x 2 = 4',135,89,'#ffdda5',15);B('TRUE EQUATION / ETHICAL LEAP')}
if(m===4){D(78,114);S(246,114);R(132,57,68,45,'#4b3c65');T('...',152,88,'#d8b9f1',18);B('THE GUARDIAN SAYS NOTHING')}
if(m===5){D(57,114);R(113,50,160,78,'#275268');for(let j=0;j<4;j++){let x=121+j*38;R(x,60,29,48,['#e9b574','#b7a2d0','#a6cfcb','#d7ada6'][j]);T(['2x2','ODE','LAW','SONG'][j],x+3,88,'#273750',8)}B('COMMISSIONED POETRY')}
if(m===6){D(55,114);R(115,60,155,49,'#47798e');R(146,44,90,18,'#c8d3dc');R(179,29,21,15,'#f2b57a');R(164,72,57,36,'#a5cbd1');T('INTEGRAL',151,124,'#ffddaf',10);B('THE STATE SENT TO THE STARS')}
}

function w013(m){
const D=(x,y)=>person(x,y,'#d4b8a3','#ab7858',1),I=(x,y)=>person(x,y,'#a17fae','#333046',2);
const B=s=>{R(10,22,300,21,'#10283d');L(10,22,300,21,'#97dcd8');T(s,18,36,'#ffe0ad',8)};
const fog=()=>{for(let j=0;j<12;j++){let x=((j*47+t/5)%384)-40,y=30+j%5*17;R(x,y,72,9,j%2?'#a5bac2':'#728e9e')}};
const house=()=>{R(45,47,235,86,'#4f4964');R(55,56,214,74,'#282b46');R(69,70,59,60,'#8c725f');R(146,62,32,44,'#c2a47e');R(196,63,49,47,'#4e4566');R(204,70,33,30,'#b28c83')};
if(m===0){fog();D(61,114);T('?',204,84,'#f7d9d1',24);B('THE TRANSPARENT CITY DISAPPEARS')}
if(m===1){fog();D(64,115);R(123,56,144,66,'#3a5771');L(123,56,144,66,'#d0ded8');T('11:45',156,86,'#ffe0ad',15);T('WORK = 12:00',142,105,'#f3cfba',9);B('THE CALL / THE MISSED HOUR')}
if(m===2){fog();D(69,114);I(261,114);R(126,58,90,48,'#4e3e60');T('THOU',142,85,'#efbbdc',15);B('THE ANCIENT WORD')}
if(m===3){R(47,51,227,80,'#2d6273');R(54,57,213,68,'#4c8194');D(62,114);I(259,114);person(167,114,'#b3a4a1','#43464d',3);R(134,52,58,16,'#e5d2bd');T('MEDICAL',139,63,'#33364e',8);B('A DOCTOR / TWO CERTIFICATES')}
if(m===4){R(0,19,320,104,'#4b8899');for(let j=0;j<6;j++){let x=(j*61+t/4)%330;R(x,42+j%3*19,37,5,'#bcdae0')}R(80,88,168,29,'#47748c');R(106,76,119,15,'#c6e1dd');D(151,110);I(205,110);B('THE AERO / RETURN TO THE HOUSE')}
if(m===5){house();D(95,115);I(218,115);for(let j=0;j<8;j++){let x=145+j*9,y=70+Math.sin(t/13+j)*11;R(x,y,4,4,'#edbbd0')}B('OUTSIDE THE PINK TICKET SYSTEM')}
if(m===6){house();D(78,115);R(194,57,56,53,'#b5a38d');R(204,66,38,35,'#4a4057');R(224,56,7,18,'#e4ca97');R(223,55+Math.sin(t/9)*4,12,3,'#aabbb8');T('WHERE?',141,120,'#ffe0ae',11);B('MOVING KEY / I-330 ABSENT')}
}

function w014(m){
const D=(x,y)=>person(x,y,'#d5b7a1','#a87856',1),O=(x,y)=>person(x,y,'#dda8c4','#d0a17c',2);
const B=s=>{R(13,22,294,21,'#10283c');L(13,22,294,21,'#94e2dc');T(s,21,36,'#ffe2b3',8)};
const window=()=>{R(37,48,247,80,'#2c566e');R(44,55,233,69,'#5294a9');for(let j=0;j<4;j++){R(89+j*46,55,5,69,'#92dacf')}};
if(m===0){window();D(71,113);person(262,113,'#a5a1b6','#aaa09a',3);R(134,61,83,52,'#edd9b6');R(148,69,54,34,'#d2acc4');T('CERT',156,91,'#453e5a',10);B('A CERTIFICATE / A CLAIM')}
if(m===1){window();D(68,115);person(249,113,'#a5b4c6','#7a7584',2);R(129,60,76,50,'#30405a');T('?',159,93,'#ffe1b1',22);B('THE NEIGHBOR / UNREADABLE')}
if(m===2){window();D(106,114);O(204,114);R(133,54,64,44,'#55405f');T('MINE?',139,83,'#e8c4e0',12);B('O-90 / THE WORD MINE')}
if(m===3){R(20,45,280,88,'#4a4162');for(let j=0;j<7;j++)R(24+j*42,46,35,88,'#6a5d80');D(58,114);R(226,86,46,6,'#d3bea5');R(233,95,14,19,'#dcb699');B('CURTAIN / BOOK / REACTION')}
if(m===4){window();D(72,116);O(251,114);R(132,61,70,45,'#2f455c');T('SECRET',142,88,'#ffd9a7',11);B('WHAT HE DOES NOT TELL HER')}
if(m===5){R(0,112,320,21,'#8baec0');R(0,133,320,19,'#4e718c');R(117,54,132,55,'#35536a');R(124,61,118,41,'#a4bdd0');D(76,132);O(256,112);T('SORRY',139,91,'#ffe4b8',12);B('THE UNBEARABLY COLD FLOOR')}
if(m===6){window();D(65,114);R(174,52,103,78,'#284759');R(184,58,83,70,'#85a8b6');R(211,58,4,70,'#d1dade');O(245,112);R(215,110,16,4,'#d2bdc8');T('WAIT!',131,87,'#ffd9b0',11);B('ELEVATOR DOWN / UNRESOLVED')}
}

function w015(m){
const D=(x,y)=>person(x,y,'#d4b8a1','#ac795a',1),Bld=(x,y)=>person(x,y,'#aabbd4','#d2ccb9',2),W=(x,y,k)=>person(x,y,'#86acbd','#7f849a',k);
const tag=s=>{R(10,22,300,21,'#0d2c42');L(10,22,300,21,'#95e0dc');T(s,19,36,'#ffdfab',8)};
const ship=()=>{R(24,72,273,46,'#396f88');R(46,59,228,14,'#78b0c1');R(90,51,131,9,'#bed9dd');R(107,83,107,25,'#1d4b67');for(let k=0;k<7;k++){R(67+k*34,75,4,40,'#b1d5d9')}R(152,44,20,13,'#debb92')};
if(m===0){ship();D(59,117);Bld(256,115);R(137,56,60,44,'#333e62');T('NO ID',142,82,'#ffcf9e',11);tag('AN UNNUMBERED INTRUDER')}
if(m===1){R(95,49,128,81,'#27495d');R(112,63,91,58,'#9ac6cd');R(117,68,81,51,'#18354e');R(136,50,44,11,'#b9dee1');R(161,62,6,57,'#ffd1a8');R(185,75,6,37,'#a99cc8');T('GAS',135,90,'#ffb6a9',11);T('BELL',134,107,'#ffb6a9',11);tag('THE OPERATION DEPARTMENT')}
if(m===2){D(65,115);Bld(253,114);R(133,52,76,61,'#40365a');T('IMAGINE',139,79,'#efd0ee',9);T('?',162,103,'#ffd0a7',19);tag('A RUMORED OPERATION')}
if(m===3){ship();D(65,113);R(13,42,290,4,'#f4bf88');for(let j=0;j<6;j++)R(20+j*54,48,31,4,'#e1b87e');tag('WARM GLASS / THE INTEGRAL')}
if(m===4){ship();for(let j=0;j<7;j++)W(24+j*45,120,j);for(let j=0;j<9;j++){let x=30+j*31;R(x,63+Math.sin(t/14+j)*5,3,8,'#79dcf0')}D(161,117);tag('THE MIRROR-LIKE SEA')}
if(m===5){ship();D(66,116);W(251,115,3);R(129,55,89,57,'#4b3d61');T('BETTER?',143,86,'#ffdfaf',12);tag('AN INNOCENT QUESTION')}
if(m===6){R(30,51,262,80,'#283b55');ship();R(78,57,190,8,'#546b86');R(152,57,13,60,'#ecad70');D(68,116);T('NO RUDDER',135,123,'#ffceaa',10);tag('MOVING WITHOUT DIRECTION')}
}

function w016(m){
const D=(x,y)=>person(x,y,'#d2b6a4','#a7795c',1);
const I=(x,y)=>person(x,y,'#9b82be','#323044',2);
const S=(x,y)=>person(x,y,'#798fa7','#3d4555',3);
const doc=(x,y)=>person(x,y,'#d4dde7','#4b5167',4);
const B=s=>{R(12,22,296,21,'#102b44');L(12,22,296,21,'#91e7dd');T(s,20,36,'#ffdfae',8)};
const hosp=()=>{R(38,49,247,84,'#37677b');R(46,57,231,71,'#6a9eae');R(92,67,138,48,'#d0dadf');T('MEDICAL',127,85,'#35485e',12);T('BUREAU',136,104,'#35485e',12)};
if(m===0){R(0,19,320,115,'#b18c44');for(let j=0;j<13;j++){let x=(j*37+t/7)%320;R(x,66+j%3*16,49,6,'#d9b86e')}D(76,113);T('DAY?',167,88,'#584369',20);B('ENDLESS YELLOW DAYS')}
if(m===1){I(57,114);S(127,114);doc(194,114);person(265,114,'#afb8d1','#8a8797',1);R(222,60,62,16,'#2e4560');T('INTEGRAL',228,72,'#ffe0b3',8);B('FOUR COMPANIONS / ONE WORD')}
if(m===2){D(60,115);R(120,51,150,78,'#243e57');L(120,51,150,78,'#b6a1d0');T('I-330',159,76,'#f0c9ec',15);T('NO ARRIVAL',142,101,'#ffcead',10);B('PINK TICKET / AN EMPTY HALL')}
if(m===3){D(65,115);R(124,51,138,78,'#3a5470');L(124,51,138,78,'#90cfcf');T('16:00',145,82,'#f6d8ae',12);T('17:00',145,102,'#f3a98e',12);B('ONE HOUR LOST OUTSIDE')}
if(m===4){R(0,53,320,80,'#396783');for(let j=0;j<7;j++){R(j*51,99,40,4,'#b2d8d9');R(j*51+10,102,22,11,'#557c91')}D(78,111);S(246,112);T('UPSIDE DOWN',123,62,'#f6d3aa',10);B('THE FOLLOWING SHADOW')}
if(m===5){hosp();D(65,115);doc(259,114);R(137,63,62,53,'#284960');R(142,68,52,43,'#b5d4d3');R(148,74,38,29,'#547e8c');T('2D > 3D',141,126,'#ffd6ad',9);B('MIRROR SURFACE / MEMORY DEPTH')}
if(m===6){hosp();D(55,114);doc(260,114);R(125,66,94,39,'#403a61');T('SOUL?',142,83,'#f7c1e3',12);T('WALK',153,99,'#ffe0b1',11);B('NO OPERATION / ANCIENT HOUSE')}
}

function w017(m){
const D=(x,y)=>person(x,y,'#d3b6a2','#ae805d',1),I=(x,y)=>person(x,y,'#e1b861','#353044',2),S=(x,y)=>person(x,y,'#8195b2','#374153',3),doc=(x,y)=>person(x,y,'#d2dce5','#4a4f64',4);
const B=s=>{R(11,22,298,21,'#102a42');L(11,22,298,21,'#93e8df');T(s,19,36,'#ffddac',8)};
const house=()=>{R(29,48,263,84,'#6a4c57');R(37,56,247,76,'#352f43');R(61,67,49,64,'#806a5d');R(139,64,45,56,'#b59b88');R(204,67,63,48,'#53455f')};
const tunnel=()=>{R(0,44,320,90,'#1c2e3e');for(let j=0;j<12;j++){let x=11+j*27;R(x,51,8,5,'#f0c8a5');R(x+3,57,2,75,'#30465b')}R(0,129,320,7,'#59646c')};
if(m===0){R(174,38,7,95,'#9ad9c3');for(let j=0;j<9;j++){let x=190+j*17;R(x,58+j%4*9,20,6,'#4cb783')}R(228,76,23,12,'#7d8862');R(238,77,4,3,'#eed27b');D(65,113);B('AVENUE 59 / GREEN WALL')}
if(m===1){house();D(71,113);person(260,114,'#8da8a1','#c2b09a',1);R(129,53,83,63,'#3f405f');T('I-330?',136,88,'#ffdfb5',12);B('THE CARETAKER / EMPTY ROOM')}
if(m===2){house();D(66,113);S(264,114);R(132,59,61,45,'#34475f');T('S-4711',137,87,'#ffdeae',10);B('APPROACHING FOOTSTEPS')}
if(m===3){house();R(140,52,77,78,'#c6b39a');R(146,60,65,70,'#37364b');R(171,53,8,18,'#ffe0ae');R(162,119+Math.sin(t/9)*3,29,4,'#88d6dc');D(67,114);B('THE WARDROBE / HIDDEN LIFT')}
if(m===4){tunnel();D(70,114);R(221,55,46,64,'#a9988f');R(227,62,33,53,'#2c3444');T('?',144,97,'#d5c4f1',20);B('AN ANCIENT UNDERGROUND CORRIDOR')}
if(m===5){tunnel();D(64,114);doc(175,113);I(266,113);R(115,63,40,59,'#8e98a7');B('THE THIN DOCTOR / I-330')}
if(m===6){house();D(61,114);I(259,114);R(125,52,99,51,'#304861');T('+ 2 DAYS',137,73,'#ffdbb2',11);T('16:00',145,93,'#a6f0dd',13);B('COURTYARD / SCRAPED FINGERS')}
}

function w018(m){
 const D=(x,y)=>person(x,y,'#d2b6a1','#a57859',1),I=(x,y)=>person(x,y,'#b899ca','#35334d',2),O=(x,y)=>person(x,y,'#e2a8c2','#c6a07c',3),U=(x,y)=>person(x,y,'#b8adbd','#98897c',4);
 const B=s=>{R(10,22,300,21,'#132b43');L(10,22,300,21,'#96ebe1');T(s,18,36,'#ffe1b8',8)};
 const glass=()=>{R(31,50,259,82,'#24445d');R(40,56,242,74,'#6097aa');for(let j=0;j<5;j++)R(56+j*45,57,4,72,'#a3d8d8')};
 const closet=()=>{R(134,47,91,85,'#a38a9f');R(139,53,81,76,'#31445c');R(143,57,72,67,'#577d9b');R(177,52,5,73,'#c4d6d6')};
 if(m===0){glass();closet();D(74,114);I(256,113);R(172,50,5,82,'#f4d5a0');B('DREAM / MIRROR / FALSE AWAKENING')}
 if(m===1){D(68,114);R(120,51,158,75,'#303c5b');T('sqrt(-1)',139,85,'#ddbeef',16);T('SOUL?',164,109,'#ffe1aa',12);B('IMAGINARY NUMBER / ANALOGY')}
 if(m===2){glass();for(let j=0;j<7;j++){let x=30+j*43;person(x,115,'#a1b8c8','#737c8b',j)}R(127,53,84,45,'#364561');T('50 CHEWS',131,80,'#ffdfb9',10);B('SYNCHRONIZED MEAL')}
 if(m===3){D(68,114);R(121,49,154,81,'#d2bfd4');R(128,56,140,67,'#e9dccc');T('EPIC?',145,79,'#494062',13);T('NOVEL!',143,102,'#66527a',14);B('THE DIARY CHANGES SHAPE')}
 if(m===4){glass();D(165,114);R(45,62,81,44,'#3b5170');T('2h 08m',54,88,'#ffdbb1',12);R(218,62,52,53,'#384560');B('A FINGER APART FROM THE HAND')}
 if(m===5){glass();D(67,114);U(264,114);R(132,56,76,52,'#e2c8b2');R(142,67,56,30,'#e4aabf');T('FROM?',144,93,'#513a53',10);B('U / THE UNKNOWN ENVELOPE')}
 if(m===6){glass();D(65,114);O(258,114);R(125,50,91,76,'#e9d6c6');R(136,64,68,3,'#a78f9b');R(136,76,68,3,'#a78f9b');R(136,88,60,3,'#a78f9b');R(188,100,10,9,'#77778e');T('O-90',150,118,'#4e4358',12);B('A GOODBYE / NEVER AGAIN')}
}

function w019(m){
 const D=(x,y)=>person(x,y,'#d3b4a0','#a47658',1),O=(x,y)=>person(x,y,'#d9a6c7','#cfa379',2),mess=(x,y)=>person(x,y,'#8495ad','#3a3d58',3);
 const tag=s=>{R(11,22,298,21,'#102c43');L(11,22,298,21,'#92e4dd');T(s,19,36,'#ffe0b3',8)};
 const ship=()=>{R(19,70,282,48,'#386c87');R(44,58,231,14,'#8dbac5');R(100,80,112,29,'#19475f');for(let j=0;j<7;j++)R(58+j*35,74,4,44,'#b5d9dd')};
 const room=()=>{R(33,49,253,83,'#315a72');R(42,57,234,72,'#6aa0ab');for(let j=0;j<4;j++)R(87+j*43,57,4,71,'#a9d5d8')};
 if(m===0){ship();D(53,116);R(259,77,45,9,'#e9b17d');R(273,59,19,18,'#f8d4a5');R(291,48,12,8,'#8fdce8');tag('ENGINE TEST / HUMAN LOSS')}
 if(m===1){ship();D(57,114);R(122,50,158,75,'#2e405d');T('~12 PEOPLE',129,80,'#f2c7b4',13);T('NOT ZERO',151,104,'#ffe1b1',12);tag('SMALL RATE != SMALL LOSS')}
 if(m===2){room();D(66,115);mess(258,114);R(129,57,80,53,'#e6c0cb');T('I-330',145,80,'#493652',12);T('TICKET',141,100,'#493652',10);tag('THE SLOPING-FOREHEAD MESSENGER')}
 if(m===3){room();D(67,115);R(132,52,87,67,'#d9c1d4');R(142,60,69,52,'#e9dccc');T('CURTAINS',144,84,'#4c3b56',9);T('AS IF',152,102,'#4c3b56',10);tag('PLANNED APPEARANCE / NO VISIT')}
 if(m===4){R(38,53,247,77,'#305a6b');R(48,63,224,63,'#7a9aa9');R(139,70,67,45,'#d1c4ae');R(163,61,17,17,'#f5cfac');O(72,113);D(264,113);R(149,87,36,5,'#c7a7ca');tag('O-90 RESCUES A CHILD')}
 if(m===5){room();D(64,115);O(258,115);R(129,54,89,56,'#4d405f');T('A CHILD?',137,82,'#ffe1b5',12);T('RISK',151,103,'#e5a8be',10);tag('A WISH / A DANGEROUS CHOICE')}
 if(m===6){room();D(65,114);O(260,114);R(139,51,64,73,'#e4bdce');R(146,61,51,55,'#f4ddc1');T('I-330',152,84,'#4b395c',10);T('CHECK',153,103,'#4b395c',9);tag('ONE TICKET / UNRESOLVED FUTURE')}
}

function w020(m){
const D=(x,y)=>person(x,y,'#d4b8a5','#a7795a',1),O=(x,y)=>person(x,y,'#dba7c7','#d0a17a',2);
const B=s=>{R(11,22,298,21,'#102940');L(11,22,298,21,'#94e9e0');T(s,19,36,'#ffe1b1',8)};
const platform=()=>{R(45,114,232,19,'#465e70');R(95,70,130,44,'#385572');R(116,54,88,18,'#9cacc1')};
if(m===0){D(68,113);R(125,59,113,52,'#2e3e5c');for(let j=0;j<8;j++){let x=140+j*12,y=84+Math.sin(t/13+j)*15;R(x,y,4,5,j%2?'#f4b67f':'#a7e9d9')}B('ELECTRICAL DISCHARGE / SILENCE')}
if(m===1){platform();D(65,114);R(207,61,65,51,'#263c57');T('O-90?',213,85,'#f6c4da',11);T('IF...',220,103,'#ffdaa8',9);B('AN IMAGINED SENTENCE / NOT FACT')}
if(m===2){D(66,114);R(125,52,151,66,'#324663');T('RIGHT',140,76,'#ffcda5',13);T('PUNISH?',141,101,'#e9c2f1',13);B('A RIGHT THAT CANNOT BE REFUSED')}
if(m===3){D(56,114);for(let j=0;j<3;j++){let x=119+j*55;R(x,66,42,46,['#9d806c','#c5a66f','#78b6c6'][j]);T(['CLAY','GOLD','GLASS'][j],x+2,91,'#243a52',8)}R(193,53,8,15,'#f7b587');B('ACID TEST / UNPROVEN PREMISE')}
if(m===4){D(50,115);R(141,61,4,45,'#a9bacb');R(105,64,77,4,'#e1bc89');R(115,74,3,24,'#d1b2c6');R(175,74,3,24,'#d1b2c6');R(101,99,43,6,'#a6d4d2');R(161,99,43,6,'#e0bc92');T('1 g',101,93,'#ffdfb5',10);T('1 TON',164,93,'#ffdfb5',10);B('GRAM / TON / RIGHTS ARE NOT MASS')}
if(m===5){platform();D(54,116);R(126,48,152,63,'#3c466d');T('2 x 2 = 4',149,71,'#ffcda9',12);T('LAW?',178,94,'#dfc0ea',12);B('CORRECT ARITHMETIC / INVALID LEAP')}
if(m===6){R(0,46,320,87,'#263b59');R(151,51,17,82,'#acc5d4');R(158,43,4,92,'#f1bb83');R(65,72,65,4,'#74acc3');R(197,72,64,4,'#74acc3');R(83,82,28,21,'#404460');R(214,82,28,21,'#9db8cc');T('+0',76,61,'#ffdda9',13);T('-0',208,61,'#ffdda9',13);T('SAME REAL ZERO',93,122,'#d1bbef',10);D(32,114);B('ZERO CLIFF / METAPHOR NOT PROOF')}
}

function w021(m){
const D=(x,y)=>person(x,y,'#d4b7a1','#a67c5f',1),U=(x,y)=>person(x,y,'#baadbf','#9d8c87',2),S=(x,y)=>person(x,y,'#8097bb','#41495b',3),C=(x,y)=>person(x,y,'#a3aea3','#aea899',4);
const H=s=>{R(11,22,298,21,'#122c44');L(11,22,298,21,'#95e8df');T(s,20,36,'#ffdfb1',8)};
const ice=()=>{R(0,43,320,91,'#829aa8');for(let i=0;i<9;i++){let x=i*39+Math.sin(t/20+i)*3;R(x,67+i%3*10,34,53,'#658fa6');R(x+5,75+i%3*9,23,36,'#b4d9dd');R(x+9,76+i%3*9,3,34,'#ebf3e4')}};
const ancient=()=>{R(30,49,260,83,'#725964');R(40,58,237,74,'#3f3d4f');R(56,68,39,63,'#9b7863');R(135,67,48,64,'#bea38d');R(215,68,45,46,'#554c5c')};
if(m===0){D(65,114);R(121,54,160,66,'#39526d');R(148,61,104,52,'#e1c5cc');T('I-330',173,82,'#4c3755',13);T('NOT HERE',166,101,'#4c3755',10);H('PINK TICKET / ABSENT PERSON')}
if(m===1){ice();D(59,113);for(let j=0;j<6;j++){let x=(j*58+t/5)%320;R(x,53+j%3*11,47,5,'#c2d8d6')}H('BLUE ICE / WIND / CLOUDS')}
if(m===2){ancient();D(64,113);C(262,113);R(126,54,80,57,'#454460');T('EXIT?',141,87,'#ffdda9',12);for(let j=0;j<6;j++)R(203+j*15,44+j%3*4,7,4,'#232c46');H('GREEN WALL / UNFOUND EXIT')}
if(m===3){ancient();D(64,114);S(257,114);for(let j=0;j<6;j++){let x=57+j*43,y=51+j%3*10;R(x,y,30,5,'#a7e7de');R(x+7,y+6,3,7,'#e8bd98')}H('GUARDIANS / PREVENTION')}
if(m===4){R(28,49,267,86,'#304e68');R(41,60,240,66,'#6596ab');D(69,115);R(125,57,111,59,'#e7d8c7');T('UNANIMITY',134,82,'#4a455f',10);T('...?',160,102,'#4a455f',12);H('AUTHOR CANNOT WRITE')}
if(m===5){R(25,49,270,86,'#31506c');D(70,113);U(256,113);R(131,54,86,58,'#b7b0c6');R(139,62,70,45,'#d1d1ce');T('FISH?',149,91,'#4b506e',12);H('THE MOST DIFFICULT LOVE')}
if(m===6){R(27,49,265,82,'#374460');D(61,114);U(265,113);R(130,56,90,58,'#3c395d');T('RUMORS',141,80,'#ffcca7',11);T('?',165,103,'#d9b8e1',19);H('UNANIMITY / UNSPOKEN RUMOR')}
}

function w022(m){
const D=(x,y)=>person(x,y,'#d4b6a3','#a77759',1),G=(x,y)=>person(x,y,'#7a93b5','#364459',2),F=(x,y)=>person(x,y,'#b5a3c4','#bb6c5d',3),S=(x,y)=>person(x,y,'#8999b3','#3b4357',4);
const B=s=>{R(10,22,300,21,'#102c43');L(10,22,300,21,'#98eae1');T(s,18,36,'#ffe1b6',8)};
const march=()=>{for(let j=0;j<8;j++){let x=11+j*42;person(x,116,'#94a9c1','#657080',j)}R(0,131,320,5,'#79a5ad')};
const tower=()=>{R(139,43,44,89,'#47637c');R(147,46,29,29,'#cedde0');R(160,45,4,33,'#586980');T('13:06',145,94,'#ffe5b7',9)};
if(m===0){march();tower();B('THE TABLE OF HOURS / FROZEN WAVES')}
if(m===1){tower();G(59,115);person(163,113,'#c5b1ab','#977a83',2);G(260,115);R(195,87,42,3,'#7adcf0');B('THREE PRISONERS / ELECTRIC WHIP')}
if(m===2){march();F(164,112);R(126,50,69,45,'#483e63');T('STOP!',137,79,'#ffd1bf',14);B('A WOMAN BREAKS THE ROWS')}
if(m===3){D(55,113);F(260,113);R(126,55,90,54,'#4e4168');T('I-330?',136,78,'#ffd8b8',12);T('NOT HER',139,99,'#e8b4cd',10);B('A CORRECTED IDENTIFICATION')}
if(m===4){G(73,114);D(158,114);G(254,114);R(124,52,77,41,'#373b60');T('HELD',141,78,'#ffd4b2',13);B('D-503 DETAINED')}
if(m===5){G(62,114);D(161,113);S(258,114);R(125,52,89,49,'#cbb5d1');T('NOTE',148,81,'#473d5e',12);T('NO SHOUT',136,97,'#473d5e',9);B('S-4711 TESTIFIES / RELEASE')}
if(m===6){march();D(162,116);R(116,48,91,53,'#314963');T('MICROBE',127,75,'#eac3d9',12);T('ME?',147,96,'#ffe0b4',12);B('THE BODY / THE INDIVIDUAL')}
}

function w023(m){
const D=(x,y)=>person(x,y,'#d2b5a2','#a67858',1),I=(x,y)=>person(x,y,'#d1ab86','#35344e',2),U=(x,y)=>person(x,y,'#b7b0c8','#9c8c88',3);
const tag=s=>{R(11,22,298,21,'#102b43');L(11,22,298,21,'#96e7df');T(s,19,36,'#ffe1b1',8)};
const room=()=>{R(31,49,260,85,'#315b73');R(40,57,242,74,'#6399ad');for(let j=0;j<5;j++)R(60+j*43,57,4,74,'#b1e4e1');R(172,88,65,40,'#5a4668')};
const flower=(x,y)=>{R(x,y,3,12,'#6eb18e');R(x-5,y-7,13,7,'#e4a6c2');R(x-2,y-11,7,16,'#f2c09d')};
if(m===0){room();D(62,114);for(let j=0;j<8;j++)flower(102+j*23,68+(j%3)*16);tag('THOUSAND-YEAR FLOWERS')}
if(m===1){room();D(59,114);U(257,114);R(133,53,85,48,'#dbb5cf');T('I-330',151,79,'#493c5b',13);R(240,48,18,18,'#bbd7ec');tag('U / PINK TICKET / BLUE MOON')}
if(m===2){room();D(84,115);I(217,113);for(let j=0;j<10;j++){let x=114+j*10,y=76+Math.sin(j+t/17)*13;R(x,y,4,5,j%2?'#edb5db':'#abece3')}T('CRYSTAL',125,61,'#ffe0b1',11);tag('THE CRYSTAL DISSOLVES')}
if(m===3){room();D(65,115);I(256,114);R(127,55,94,53,'#4b3c61');T('TEST?',143,79,'#f2c2df',14);T('MINE?',145,99,'#ffe1aa',11);tag('LOVE / OBEDIENCE / TEST')}
if(m===4){room();D(65,114);I(259,114);R(124,55,93,59,'#2f4764');T('20 MIN',138,83,'#ffe1ae',12);T('REMEMBER?',134,103,'#dfc3e9',9);tag('THE STOPPED METRONOME')}
if(m===5){room();D(66,114);I(263,114);for(let j=0;j<6;j++){let x=125+j*19,y=76+(j%2)*25;R(x,y,16,23,'#e8d9cb');R(x+3,y+5,10,2,'#a78a9a')}tag('THE MANUSCRIPT SCATTERS')}
if(m===6){room();D(64,113);I(262,113);R(124,54,109,58,'#473c65');T('IF ONLY...',132,79,'#ffd9ba',11);T('INTEGRAL?',133,101,'#a6e4df',10);tag('AFTER THE HOLIDAY / IF ONLY')}
}

function w024(m){
const D=(x,y)=>person(x,y,'#d2b4a1','#a77958',1),I=(x,y)=>person(x,y,'#ba98c8','#37314d',2);
const tag=s=>{R(11,22,298,21,'#122b42');L(11,22,298,21,'#96e9df');T(s,20,36,'#ffdeb1',8)};
const room=()=>{R(30,51,260,82,'#2d556b');R(39,58,241,74,'#6498a8');for(let k=0;k<5;k++)R(58+k*42,58,4,74,'#a9d9db')};
const square=()=>{R(30,55,260,76,'#305370');R(132,52,55,70,'#647e92');R(146,54,27,23,'#c1d8d8');for(let k=0;k<9;k++)person(16+k*37,122,'#8daac1','#6f7e92',k)};
if(m===0){room();D(60,115);R(127,61,100,47,'#324563');for(let j=0;j<9;j++){let x=133+j*10,y=83+Math.sin(t/9+j)*16;R(x,y,4,6,j%2?'#f2a77a':'#9fe8da')}tag('ENGINE OVERHEATING / LOGIC STEAMS')}
if(m===1){room();D(65,115);R(117,54,151,62,'#403b60');T('L = f(D)',135,87,'#ecd1f4',18);T('WANT / FEAR',138,107,'#ffd8ac',10);tag('LOVE AS A SYMBOLIC LIMIT')}
if(m===2){square();D(62,120);I(262,120);R(122,52,80,47,'#4d3f63');T('TOMORROW',130,79,'#ffd8af',10);tag('THE PAIN OF DISTANCE')}
if(m===3){room();D(57,115);R(122,53,104,68,'#bf9eb5');R(133,61,82,52,'#e5d8c9');T('NEW UNIF',143,80,'#493c59',11);T('EASTER',151,101,'#493c59',10);tag('NEW UNIFORMS / OLD RITUAL')}
if(m===4){square();R(113,53,105,53,'#354567');T('VOTE',144,79,'#ffd1b1',13);T('PUBLIC',134,98,'#a7e7e2',10);tag('VISIBLE VOTES / GUARDIAN WATCH')}
if(m===5){room();D(58,115);R(124,54,113,64,'#e6d5cd');R(132,64,97,42,'#d5b9c6');for(let j=0;j<4;j++)R(136,69+j*10,88,3,'#b18ea3');L(132,63,95,43,'#f2b283');T('X',172,98,'#ad5162',22);tag('CROSS OUT EVERYTHING')}
if(m===6){room();D(65,114);R(129,55,95,63,'#3a3c61');R(146,78,62,11,'#c2b3d6');T('NO',163,87,'#3b3152',10);T('TOMORROW',136,105,'#ffd9b4',10);tag('THE PHONE / YOU SHALL SEE')}
}

function w025(m){
const D=(x,y)=>person(x,y,'#d4b6a1','#a87859',1),I=(x,y)=>person(x,y,'#d6a5bd','#38334a',2),G=(x,y)=>person(x,y,'#899cb9','#394358',3),R13=(x,y)=>person(x,y,'#b29aa3','#6a4d55',4);
const tag=s=>{R(11,22,298,21,'#102b43');L(11,22,298,21,'#96ece4');T(s,19,36,'#ffe0b2',8)};
const stands=()=>{R(0,49,320,84,'#375773');for(let j=0;j<7;j++){R(13+j*43,67+j%3*12,32,4,'#89b4ca');person(18+j*43,117,'#9aacc2','#657b8a',j)}};
const aero=()=>{R(145,54,53,11,'#aac7d0');R(154,48,37,6,'#e8d7b7');R(162,65,18,5,'#6e8aa2')};
if(m===0){stands();D(55,116);R(128,53,96,54,'#3d3e63');T('HYMN',153,82,'#ffdfad',13);T('GUILT',151,100,'#e0c2e5',10);tag('MUSICAL TOWER / UNCONFESSED')}
if(m===1){stands();aero();R(121,77,87,40,'#464a6b');T('BENEFACTOR',126,101,'#ffe1b2',9);tag('DESCENT / TREMBLING WEB')}
if(m===2){stands();D(45,116);I(161,116);R13(255,116);R(129,53,75,36,'#473b60');T('WHY?',148,78,'#ffd7bb',13);tag('I-330 AND R-13')}
if(m===3){stands();for(let j=0;j<8;j++){let x=20+j*40;R(x,62,5,22,'#d2b4a9');R(x-3,55,11,10,'#e9bfa3')}I(234,115);R(125,86,94,22,'#4f3b5b');T('OPPOSED!',132,101,'#f5c4d7',11);tag('THOUSANDS OF HANDS OPPOSE')}
if(m===4){stands();for(let j=0;j<9;j++){let x=13+j*34;R(x,70+Math.sin(t/13+j)*6,20,3,j%2?'#eda87f':'#bba2cc')}R(129,51,90,49,'#413d5a');T('O-90?',140,80,'#f9d0d8',12);tag('CHAOS / O-90 UNRESOLVED')}
if(m===5){stands();D(60,114);R13(165,113);I(256,112);R(133,49,73,51,'#593c5c');T('STOP!',141,80,'#ffd4bd',12);tag('D-503 STRIKES R-13')}
if(m===6){stands();D(86,115);I(221,115);R(124,49,105,52,'#3b3a65');T('TOMORROW?',133,76,'#f2c1ea',10);T('UNKNOWN',144,97,'#ffdaa8',11);tag('POSSIBILITY / NO KNOWN OUTCOME')}
}

function w026(m){
const D=(x,y)=>person(x,y,'#d1b5a0','#ac7b5b',1),S=(x,y)=>person(x,y,'#809bb6','#3c455e',2),B=(x,y)=>person(x,y,'#a8b3ca','#898496',3);
const tag=s=>{R(11,22,298,21,'#102a42');L(11,22,298,21,'#95e9df');T(s,19,36,'#ffdeae',8)};
const cityglass=()=>{R(27,48,268,84,'#315972');for(let j=0;j<6;j++){R(42+j*43,53,31,77,'#6198a9');R(50+j*43,59,15,65,'#23445e')}};
const mephi=(x,y,w=63)=>{R(x,y,w,32,'#e8ece4');T('MEPHI',x+5,y+21,'#2dbd77',12)};
if(m===0){cityglass();D(67,115);R(137,54,88,55,'#3b4760');T('WORLD?',146,87,'#ffd9aa',12);tag('THE ROUND SUN / A COASTING MOTOR')}
if(m===1){cityglass();D(56,115);R(123,49,134,75,'#e5dbc8');T('UNANIMOUS',131,69,'#47425b',10);T('48TH',161,91,'#47425b',14);T('NOON DECREE',133,109,'#47425b',9);tag('THE STATE GAZETTE / OMITTED VOTES')}
if(m===2){cityglass();D(54,113);S(249,114);mephi(118,47,76);T('?',152,113,'#ffdfb3',18);tag('MEPHI / S-4711 CANNOT REACH')}
if(m===3){R(0,49,320,84,'#2c465b');for(let j=0;j<7;j++){let x=9+j*45;mephi(x,57+j%2*35,39)}D(168,113);tag('THE UNDERGROUND POSTER RASH')}
if(m===4){R(0,48,320,84,'#2a4963');for(let j=0;j<7;j++)person(20+j*44,116,'#a6a6c1','#77788b',j);R(112,53,103,42,'#483e5d');T('41 C?',141,82,'#ffc6bc',14);tag('ANXIETY / FEVER AS METAPHOR')}
if(m===5){R(21,75,282,46,'#467b90');R(56,58,203,17,'#99c4cc');for(let j=0;j<6;j++)R(55+j*40,78,4,40,'#bfdfe0');D(53,114);B(265,113);T('TRIAL FLIGHT?',125,94,'#ffe0b0',9);tag('INTEGRAL LOADING / NO LAUNCH YET')}
if(m===6){R(20,75,283,46,'#3b728b');R(59,58,206,17,'#95c2cd');D(58,115);B(257,114);mephi(150,44,60);T('FALLING?',124,114,'#f9c5b2',10);tag('THE WHITE SQUARE / FALLING PLANE')}
}

function w027(m){
 const D=(x,y)=>person(x,y,'#d1b3a0','#a97a59',1),I=(x,y)=>person(x,y,'#d2a0c2','#393046',2),Doc=(x,y)=>person(x,y,'#d4d5d8','#555666',3),G=(x,y)=>person(x,y,'#8eaaa2','#77635c',4);
 const label=s=>{R(10,22,300,21,'#102a42');L(10,22,300,21,'#93eadd');T(s,18,36,'#ffe2b5',8)};
 const tunnel=()=>{R(0,45,320,88,'#23344b');for(let j=0;j<12;j++){let x=8+j*28;R(x,53,8,5,'#f4cba2');R(x+3,60,2,68,'#3e5365')}R(0,129,320,6,'#676879')};
 const forest=()=>{R(0,43,320,90,'#2b765b');R(0,117,320,19,'#53905a');for(let j=0;j<9;j++){let x=9+j*40;R(x,56,7,69,'#846752');R(x-15,49,38,17,'#478753');R(x-6,42,22,14,'#75ab67')}for(let j=0;j<12;j++){let x=10+j*29;R(x,126+(j%3)*2,13,4,'#a2ce76')}};
 const rock=()=>{R(111,67,98,66,'#ae946e');R(129,57,61,12,'#d9bd8d')};
 if(m===0){tunnel();D(55,114);I(267,114);R(218,53,52,74,'#9d9689');R(222,58,44,68,'#2a384a');T('16:15',134,94,'#ffd9b0',12);label('SHE IS LATE / HIDDEN DOOR')}
 if(m===1){forest();D(68,113);I(256,113);R(130,53,72,55,'#264e62');T('OUTSIDE',133,84,'#ffdaaa',11);label('THE WALL WAS NOT DESTROYED')}
 if(m===2){forest();D(50,114);I(165,114);Doc(267,114);label('THE THIN DOCTOR IN THE FOREST')}
 if(m===3){forest();for(let j=0;j<10;j++){let x=13+j*31;person(x,116,j%3===0?'#98acc0':'#a58e7c',j%3===0?'#6c7288':'#665344',j)}label('300-400 PEOPLE / A LIVING WORLD')}
 if(m===4){forest();rock();I(163,73);for(let j=0;j<8;j++)person(17+j*42,115,'#aa9882','#725c55',j);T('INTEGRAL',126,108,'#ffdbac',9);label('THE SHIP MUST BE OURS')}
 if(m===5){forest();rock();R(120,83,80,39,'#d6c59c');T('MEPHI',130,110,'#31ba75',15);D(60,115);G(266,114);R(239,76,16,8,'#c7a17b');label('WOODEN CUP / MEPHI REVEALED')}
 if(m===6){forest();D(59,114);I(254,113);R(134,51,82,51,'#293f56');T('S-4711?',140,78,'#ffcdbb',11);T('UNKNOWN',140,97,'#aee8e5',9);label('FLEETING EARS / NO PROOF')}
}

function w028(m){
 const D=(x,y)=>person(x,y,'#d3b6a0','#aa795a',1),I=(x,y)=>person(x,y,'#d2a0c3','#393149',2),U=(x,y)=>person(x,y,'#ada8bd','#99897c',3),S=(x,y)=>person(x,y,'#879db8','#384253',4);
 const label=s=>{R(10,22,300,21,'#102a42');L(10,22,300,21,'#96ebdf');T(s,18,36,'#ffe1b3',8)};
 const room=()=>{R(28,49,264,85,'#30576e');R(37,56,245,75,'#6094a8');for(let j=0;j<5;j++)R(59+j*42,57,4,74,'#b4dedf');R(133,94,58,37,'#544a66')};
 if(m===0){room();D(58,113);I(164,113);U(266,113);R(125,53,86,35,'#4e4063');T('BOTH!',146,77,'#ffceda',13);label('I-330 / U / D-503')}
 if(m===1){room();D(58,113);I(262,113);R(121,52,120,57,'#394d66');R(137,67,27,27,'#d0dce1');R(176,64,35,35,'#c5bfcf');T('TABLES',132,109,'#ffdfac',9);label('CLOSED AUDITORIUMS / WHITE MEDICS')}
 if(m===2){room();D(68,113);I(265,114);R(129,53,93,56,'#393c5c');R(148,67,14,30,'#d1b3a2');for(let j=0;j<4;j++)R(147+j*6,62,4,8,'#aa805f');T('ANCESTRY?',139,106,'#e7bfdc',9);label('A HAIRY HAND / A HYPOTHESIS')}
 if(m===3){R(0,43,320,90,'#357052');R(0,119,320,17,'#75a65f');for(let j=0;j<8;j++){let x=12+j*41;R(x,58,6,61,'#8a6b53');R(x-13,48,34,18,'#4a985d')}I(65,114);D(259,114);T('TWO HALVES',127,76,'#ffe3b5',11);T('H2 + O',145,100,'#acecde',12);label('WAR / TWO BRANCHES OF HUMANITY')}
 if(m===4){R(0,43,320,90,'#1b3f51');R(40,67,98,43,'#4e666e');R(185,67,98,43,'#5c466a');T('ENTROPY',51,91,'#b7e4e3',11);T('ENERGY',199,91,'#f6bb84',12);for(let j=0;j<7;j++){let x=144+j*7,y=88+Math.sin(t/8+j)*15;R(x,y,3,4,'#fac484')}I(162,114);label('MEPHISTO / ENTROPY / ENERGY')}
 if(m===5){room();I(59,114);D(263,114);person(160,114,'#b1a6a1','#5b4f55',3);R(127,52,86,39,'#453d65');T('S-4711!',134,78,'#f9c1d0',12);label('MESSENGER / GUARDIANS APPROACH')}
 if(m===6){room();D(60,114);S(259,114);U(167,114);R(127,52,85,54,'#ead8cf');for(let j=0;j<4;j++)R(135,61+j*9,66,2,'#a98e9c');T('HIDE?',143,99,'#493c56',11);label('OPAQUE BODY / HIDDEN PAGES')}
}

function w029(m){
const D=(x,y)=>person(x,y,'#d2b4a1','#a7795d',1),O=(x,y)=>person(x,y,'#e0a5c2','#c99b79',2);
const tag=s=>{R(10,22,300,21,'#102940');L(10,22,300,21,'#92e6df');T(s,18,36,'#ffe0b1',8)};
const wall=()=>{R(10,46,139,89,'#2f7b70');for(let j=0;j<8;j++)R(17+j*17,54,6,78,'#9bd9cd');R(176,48,128,87,'#74485c');R(188,60,98,75,'#483a4f')};
const threads=()=>{for(let j=0;j<16;j++){let x=(j*37+t*.27)%320,y=49+(j*17)%76;R(x,y,16,1,'#e1ddc8')}};
if(m===0){wall();D(56,115);threads();R(176,57,101,36,'#345269');T('BAROMETER',183,75,'#ffe1b2',9);T('FALLING',199,90,'#ffe1b2',9);tag('QUIET / CLOUDS / INVISIBLE THREADS')}
if(m===1){wall();D(55,114);O(259,114);R(127,53,84,43,'#4e4565');T('O-90',143,80,'#f3c5d6',14);tag('O-90 / NEW LIFE')}
if(m===2){wall();D(60,114);O(257,114);R(125,51,96,49,'#513f66');T('A KISS',141,78,'#ffccd9',13);T('WITHDRAW',134,96,'#ffe0a7',9);tag('TENDERNESS / RECOIL')}
if(m===3){wall();D(57,114);O(257,114);R(127,52,92,59,'#493b5e');T('DANGER',141,77,'#ffc2bf',12);T('PITY',149,98,'#e3c2e8',12);tag('THE UNAUTHORIZED CHILD')}
if(m===4){wall();D(56,114);O(258,114);R(128,56,89,43,'#3c5c6a');T('FOREST?',135,83,'#a7f1da',13);tag('AN ESCAPE PROPOSED')}
if(m===5){wall();D(56,114);O(259,114);R(130,52,83,56,'#553e63');T('I-330?',138,78,'#ffe0b1',13);T('NO!',155,100,'#ffc0ca',15);tag('O-90 REFUSES')}
if(m===6){wall();D(65,114);O(290,113);threads();R(125,56,99,43,'#3d455e');T('UNRESOLVED',132,82,'#f4c6d8',10);tag('UNNATURAL COMPRESSION')}
}

function w030(m){
const D=(x,y)=>person(x,y,'#d3b5a1','#ad795a',1),I=(x,y)=>person(x,y,'#cea0c3','#363149',2);
const tag=s=>{R(10,22,300,21,'#102b43');L(10,22,300,21,'#9ce9e0');T(s,17,36,'#ffe2b1',8)};
const house=()=>{R(23,46,275,87,'#66556c');for(let j=0;j<8;j++){R(31+j*36,54+j%3*15,28,18,['#a65b4e','#5f957a','#cb9c5e','#b58a67'][j%4])}};
const dome=()=>{R(24,46,272,87,'#2b5770');for(let j=0;j<5;j++){let x=34+j*54;R(x,75,46,57,'#497b8f');R(x+8,58,28,20,'#cb8974')}};
if(m===0){house();D(61,114);I(256,113);R(130,55,88,51,'#332d4e');T('INTEGRAL',137,81,'#ffe2bb',10);T('TAKEOVER?',135,98,'#b9ebe3',9);tag('TRIAL FLIGHT / SEIZURE PROPOSED')}
if(m===1){house();D(57,114);I(261,114);R(129,52,96,55,'#353952');T('12:00',146,78,'#f4c29c',15);T('DINING HALL',136,99,'#a3e6e0',9);tag('MIDDAY BELL / PLAN ONLY')}
if(m===2){house();D(57,114);I(263,114);R(116,53,122,53,'#293d58');T('n + 1',142,80,'#ffd49c',16);T('NO LAST n',127,101,'#acefe2',11);tag('LAST NUMBER / LAST REVOLUTION?')}
if(m===3){house();D(58,113);I(261,114);R(124,52,99,57,'#30475e');for(let j=0;j<8;j++){let x=132+j*11,y=83+Math.sin(t/11+j)*14;R(x,y,4,6,j%2?'#fab480':'#a4eada')}T('ENTROPY',143,107,'#ffe1b6',9);tag('EQUILIBRIUM / CONTRAST')}
if(m===4){house();D(55,113);I(264,114);R(119,52,106,58,'#2b4362');R(157,62,23,23,'#e3c3a3');R(171,71,6,6,'#f4d78b');T('GALILEO',137,104,'#e5d1f0',11);tag('ORBITS WITHIN LARGER ORBITS')}
if(m===5){house();D(61,114);I(262,114);R(126,50,97,57,'#413656');T('12:00',141,78,'#fbd5ac',17);T('I AGREE',139,101,'#f1b8d3',10);tag('A PROMISE / NO ACTION YET')}
if(m===6){dome();D(55,114);R(122,52,110,65,'#e2d4cc');for(let j=0;j<3;j++)R(132+j*30,69,26,34,'#becbd0');T('UNKNOWN X',137,114,'#593f55',10);tag('AUDITORIUM / UNKNOWN TOMORROW')}
}

function w031(m){
const D=(x,y)=>person(x,y,'#d5b4a0','#a97859',1),I=(x,y)=>person(x,y,'#cea5ca','#373049',2),U=(x,y)=>person(x,y,'#b1abc0','#928379',3),B=(x,y)=>person(x,y,'#a3aebc','#646a79',4);
const tag=s=>{R(10,22,300,21,'#102b44');L(10,22,300,21,'#96e7df');T(s,17,36,'#ffe2b6',8)};
const room=()=>{R(23,48,274,85,'#2d546d');R(34,56,252,76,'#6593a8');for(let j=0;j<5;j++)R(51+j*48,57,4,72,'#aee0e1')};
const hospital=()=>{R(26,50,267,84,'#d5e0e1');R(36,59,247,72,'#8aa7b7');R(79,97,162,14,'#f3f3ee');R(106,90,105,8,'#a9d3d7')};
const ship=()=>{R(16,70,284,62,'#41728f');R(52,55,210,19,'#a4cad0');for(let j=0;j<6;j++)R(64+j*35,78,5,48,'#b4d8db')};
if(m===0){room();D(57,113);R(125,51,105,63,'#efe3d0');T('GREAT',149,72,'#454560',13);T('OPERATION',131,96,'#454560',11);T('X-RAY x3',138,107,'#855568',9);tag('STATE GAZETTE / FANCY AS ILLNESS')}
if(m===1){hospital();D(58,113);B(264,113);R(137,54,80,35,'#e9f3f2');T('X-RAY?',146,78,'#555372',12);tag('THE AUDITORIUM / A WHITE TABLE')}
if(m===2){ship();D(58,114);B(260,113);R(121,51,110,59,'#2c4560');T('+1 DAY',140,77,'#ffd5ae',15);T('FLIGHT',149,99,'#b5efeb',11);tag('THE INTEGRAL / FLIGHT POSTPONED')}
if(m===3){room();D(57,113);U(263,113);R(123,51,111,59,'#463f60');T('FORGIVEN',134,78,'#f6c6e1',12);T('CHILDREN?',138,101,'#ffe3b4',10);tag('U / CHILDREN / RESTRAINTS')}
if(m===4){room();D(55,113);I(265,113);R(120,52,115,57,'#364661');T('-273 C',134,79,'#a9ebf0',17);T('STONES?',147,100,'#f0c0df',11);tag('HAPPINESS / DIVINE MINUS')}
if(m===5){room();D(60,114);I(263,114);R(113,52,124,60,'#484164');R(118,80,48,6,'#a4e7de');R(191,80,40,6,'#f2ac7d');R(173,67,8,33,'#f5d2ae');T('COLLISION',132,104,'#f5bbdd',11);tag('TWO TRAINS / OPPOSING DESIRES')}
if(m===6){room();D(57,114);I(261,114);R(118,52,118,61,'#344c65');T('DAY + 2',133,76,'#fbd4a7',12);T('12:00',145,99,'#aeeae0',15);tag('A NEW NOON / UNFINISHED PLAN')}
}

function w032(m){
 const D=(x,y)=>person(x,y,'#d6b5a1','#aa785a',1),O=(x,y)=>person(x,y,'#d7a2be','#c19979',2),S=(x,y)=>person(x,y,'#8b9db7','#3f465b',3),B=(x,y)=>person(x,y,'#a7b5c2','#667081',4);
 const tag=s=>{R(10,22,300,21,'#102b43');L(10,22,300,21,'#9aeae2');T(s,17,36,'#ffe3b6',8)};
 const city=()=>{R(0,45,320,88,'#345775');for(let j=0;j<7;j++){let x=12+j*46;R(x,59,36,74,'#5a91a9');R(x+11,66,15,58,'#2a4b68')}};
 const dock=()=>{R(12,73,296,59,'#3c7594');R(40,57,226,17,'#a6cfda');for(let j=0;j<7;j++)R(55+j*33,79,4,49,'#c4dce1')};
 const crowd=()=>{for(let j=0;j<8;j++)person(14+j*42,119,'#93a8be','#687d8c',j)};
 if(m===0){dock();D(59,114);R(126,52,99,58,'#343f5e');T('TOMORROW',135,78,'#ffd5b5',12);T('?',164,103,'#d9b7e9',20);tag('I KNOW / I DO NOT BELIEVE')}
 if(m===1){dock();D(55,114);B(266,114);R(126,53,99,53,'#3d4560');T('15 T',150,77,'#b4efeb',14);T('1000 T',140,100,'#ffd3a5',14);tag('FUEL CALCULATION / FUEL ORDER')}
 if(m===2){city();crowd();R(119,51,116,43,'#f4e8d8');T('OPERATED',129,73,'#5b5065',12);T('50',167,89,'#5b5065',10);tag('OPERATED NUMBERS / BANNER')}
 if(m===3){city();crowd();for(let j=0;j<7;j++){let x=28+j*43;R(x,79,25,5,'#e0c5ba')}R(120,51,113,42,'#523f64');T('RUN!',146,80,'#ffd2ba',16);tag('ENCIRCLED / BREAK THROUGH')}
 if(m===4){city();D(62,114);O(253,114);R(122,52,111,52,'#4d3d60');T('MY CHILD',133,80,'#ffd1d9',13);T('HELP',151,99,'#ffe6b1',11);tag('O-90 / PROTECTIVE DUTY')}
 if(m===5){city();D(59,114);O(161,114);S(276,114);R(118,53,112,52,'#3d4761');T('YES',152,79,'#b4f0da',15);T('FOLLOWED?',134,98,'#ffd6b7',10);tag('O-90 AGREES / S-4711 APPEARS')}
 if(m===6){city();D(56,114);O(262,114);R(119,52,112,59,'#e6d8cc');R(142,64,67,39,'#f4e8dc');T('TO I-330',136,89,'#55445f',11);tag('NOTE / FAREWELL / DELIVERY UNKNOWN')}
}

function w033(m){
 const D=(x,y)=>person(x,y,'#d4b6a2','#a5795b',1);
 const tag=s=>{R(10,22,300,21,'#102b44');L(10,22,300,21,'#a6eae0');T(s,17,36,'#ffe4b6',8)};
 const room=()=>{R(24,48,272,85,'#30586f');R(34,58,252,72,'#6b9bab');for(let j=0;j<5;j++)R(53+j*48,58,4,72,'#bce7e3');R(157,92,62,39,'#604b6c');R(55,96,69,35,'#39566e')};
 const paper=(x,y)=>{R(x,y,110,63,'#efe4d3');for(let j=0;j<4;j++)R(x+10,y+12+j*11,90,3,'#9b97a3')};
 if(m===0){room();D(55,113);paper(126,52);T('THE DAY',139,80,'#4a4561',12);tag('TWO WORDS / EYES AS INSTRUMENTS')}
 if(m===1){room();D(55,113);paper(125,51);T('OPERATION',133,69,'#a34d66',10);T('MANDATORY',133,89,'#a34d66',10);T('TOMORROW',133,107,'#a34d66',9);tag('AN OFFICIAL THREAT / NO OUTCOME YET')}
 if(m===2){room();D(57,114);R(118,51,118,60,'#4b3d63');T('TOMORROW?',126,79,'#f2c0db',12);T('?',166,103,'#ffd6a8',19);tag('TIME CONTINUES / BELIEF FAILS')}
 if(m===3){room();D(59,114);R(128,98,93,18,'#e6d6c8');R(135,113,70,7,'#cab3bb');T('WHY KEEP IT?',126,76,'#ffdfb2',10);tag('THE PAPER FALLS / HABIT BREAKS')}
 if(m===4){room();D(58,115);R(118,53,122,59,'#3c4561');T('DESK',134,75,'#bdeae4',10);T('CHAIR',179,76,'#ffd7b6',10);T('MEMORY',142,98,'#f0bedb',11);tag('THE INVISIBLE SUITCASE')}
 if(m===5){room();D(57,113);R(121,55,110,57,'#3c4663');R(144,68,55,24,'#b8c8d5');R(155,61,32,8,'#98aabc');T('SILENCE',146,107,'#f3c6d5',10);tag('THE PHONE DOES NOT RING')}
 if(m===6){room();D(61,113);paper(127,52);T('FAREWELL',137,86,'#5c4560',13);R(211,62,31,56,'#1d3747');tag('LAST ENTRY? / DEPARTURE UNKNOWN')}
}
function frame(){g.setTransform(3,0,0,3,0,0);g.imageSmoothingEnabled=false;city();const mode=data.scenes[n].mode;if(data.id==='W033'){w033(mode);R(0,0,320,17,'#081221');T('ONE STATE / RECORD '+data.id,6,12,'#80f2e9',8);R(0,157,320,23,'#061224');R(0,157,320,2,'#e89b60');T('ACT '+(n+1)+'/7  '+data.scenes[n].setting.slice(0,21),7,171,'#ffcf9c',8);T(paused?'PAUSED':'CANVAS2D',258,171,'#89e9da',7);return;}if(data.id==='W032'){w032(mode);R(0,0,320,17,'#081221');T('ONE STATE / RECORD '+data.id,6,12,'#80f2e9',8);R(0,157,320,23,'#061224');R(0,157,320,2,'#e89b60');T('ACT '+(n+1)+'/7  '+data.scenes[n].setting.slice(0,21),7,171,'#ffcf9c',8);T(paused?'PAUSED':'CANVAS2D',258,171,'#89e9da',7);return;}if(data.id==='W031'){w031(mode);R(0,0,320,17,'#081221');T('ONE STATE / RECORD '+data.id,6,12,'#80f2e9',8);R(0,157,320,23,'#061224');R(0,157,320,2,'#e89b60');T('ACT '+(n+1)+'/7  '+data.scenes[n].setting.slice(0,21),7,171,'#ffcf9c',8);T(paused?'PAUSED':'CANVAS2D',258,171,'#89e9da',7);return;}if(data.id==='W030'){w030(mode);R(0,0,320,17,'#081221');T('ONE STATE / RECORD '+data.id,6,12,'#80f2e9',8);R(0,157,320,23,'#061224');R(0,157,320,2,'#e89b60');T('ACT '+(n+1)+'/7  '+data.scenes[n].setting.slice(0,21),7,171,'#ffcf9c',8);T(paused?'PAUSED':'CANVAS2D',258,171,'#89e9da',7);return;}if(data.id==='W029'){w029(mode);R(0,0,320,17,'#081221');T('ONE STATE / RECORD '+data.id,6,12,'#80f2e9',8);R(0,157,320,23,'#061224');R(0,157,320,2,'#e89b60');T('ACT '+(n+1)+'/7  '+data.scenes[n].setting.slice(0,21),7,171,'#ffcf9c',8);T(paused?'PAUSED':'CANVAS2D',258,171,'#89e9da',7);return;}if(data.id==='W028'){w028(mode);R(0,0,320,17,'#081221');T('ONE STATE / RECORD '+data.id,6,12,'#80f2e9',8);R(0,157,320,23,'#061224');R(0,157,320,2,'#e89b60');T('ACT '+(n+1)+'/7  '+data.scenes[n].setting.slice(0,21),7,171,'#ffcf9c',8);T(paused?'PAUSED':'CANVAS2D',258,171,'#89e9da',7);return;}if(data.id==='W027'){w027(mode);R(0,0,320,17,'#081221');T('ONE STATE / RECORD '+data.id,6,12,'#80f2e9',8);R(0,157,320,23,'#061224');R(0,157,320,2,'#e89b60');T('ACT '+(n+1)+'/7  '+data.scenes[n].setting.slice(0,21),7,171,'#ffcf9c',8);T(paused?'PAUSED':'CANVAS2D',258,171,'#89e9da',7);return;}if(data.id==='W026'){w026(mode);R(0,0,320,17,'#081221');T('ONE STATE / RECORD '+data.id,6,12,'#80f2e9',8);R(0,157,320,23,'#061224');R(0,157,320,2,'#e89b60');T('ACT '+(n+1)+'/7  '+data.scenes[n].setting.slice(0,21),7,171,'#ffcf9c',8);T(paused?'PAUSED':'CANVAS2D',258,171,'#89e9da',7);return;}if(data.id==='W025'){w025(mode);R(0,0,320,17,'#081221');T('ONE STATE / RECORD '+data.id,6,12,'#80f2e9',8);R(0,157,320,23,'#061224');R(0,157,320,2,'#e89b60');T('ACT '+(n+1)+'/7  '+data.scenes[n].setting.slice(0,21),7,171,'#ffcf9c',8);T(paused?'PAUSED':'CANVAS2D',258,171,'#89e9da',7);return;}if(data.id==='W024'){w024(mode);R(0,0,320,17,'#081221');T('ONE STATE / RECORD '+data.id,6,12,'#80f2e9',8);R(0,157,320,23,'#061224');R(0,157,320,2,'#e89b60');T('ACT '+(n+1)+'/7  '+data.scenes[n].setting.slice(0,21),7,171,'#ffcf9c',8);T(paused?'PAUSED':'CANVAS2D',258,171,'#89e9da',7);return;}if(data.id==='W023'){w023(mode);R(0,0,320,17,'#081221');T('ONE STATE / RECORD '+data.id,6,12,'#80f2e9',8);R(0,157,320,23,'#061224');R(0,157,320,2,'#e89b60');T('ACT '+(n+1)+'/7  '+data.scenes[n].setting.slice(0,21),7,171,'#ffcf9c',8);T(paused?'PAUSED':'CANVAS2D',258,171,'#89e9da',7);return;}if(data.id==='W022'){w022(mode);R(0,0,320,17,'#081221');T('ONE STATE / RECORD '+data.id,6,12,'#80f2e9',8);R(0,157,320,23,'#061224');R(0,157,320,2,'#e89b60');T('ACT '+(n+1)+'/7  '+data.scenes[n].setting.slice(0,21),7,171,'#ffcf9c',8);T(paused?'PAUSED':'CANVAS2D',258,171,'#89e9da',7);return;}if(data.id==='W021'){w021(mode);R(0,0,320,17,'#081221');T('ONE STATE / RECORD '+data.id,6,12,'#80f2e9',8);R(0,157,320,23,'#061224');R(0,157,320,2,'#e89b60');T('ACT '+(n+1)+'/7  '+data.scenes[n].setting.slice(0,21),7,171,'#ffcf9c',8);T(paused?'PAUSED':'CANVAS2D',258,171,'#89e9da',7);return;}if(data.id==='W020'){w020(mode);R(0,0,320,17,'#081221');T('ONE STATE / RECORD '+data.id,6,12,'#80f2e9',8);R(0,157,320,23,'#061224');R(0,157,320,2,'#e89b60');T('ACT '+(n+1)+'/7  '+data.scenes[n].setting.slice(0,21),7,171,'#ffcf9c',8);T(paused?'PAUSED':'CANVAS2D',258,171,'#89e9da',7);return;}if(data.id==='W019'){w019(mode);R(0,0,320,17,'#081221');T('ONE STATE / RECORD '+data.id,6,12,'#80f2e9',8);R(0,157,320,23,'#061224');R(0,157,320,2,'#e89b60');T('ACT '+(n+1)+'/7  '+data.scenes[n].setting.slice(0,21),7,171,'#ffcf9c',8);T(paused?'PAUSED':'CANVAS2D',258,171,'#89e9da',7);return;}if(data.id==='W018'){w018(mode);R(0,0,320,17,'#081221');T('ONE STATE / RECORD '+data.id,6,12,'#80f2e9',8);R(0,157,320,23,'#061224');R(0,157,320,2,'#e89b60');T('ACT '+(n+1)+'/7  '+data.scenes[n].setting.slice(0,21),7,171,'#ffcf9c',8);T(paused?'PAUSED':'CANVAS2D',258,171,'#89e9da',7);return;}if(data.id==='W017'){w017(mode);R(0,0,320,17,'#081221');T('ONE STATE / RECORD '+data.id,6,12,'#80f2e9',8);R(0,157,320,23,'#061224');R(0,157,320,2,'#e89b60');T('ACT '+(n+1)+'/7  '+data.scenes[n].setting.slice(0,21),7,171,'#ffcf9c',8);T(paused?'PAUSED':'CANVAS2D',258,171,'#89e9da',7);return;}if(data.id==='W016'){w016(mode);R(0,0,320,17,'#081221');T('ONE STATE / RECORD '+data.id,6,12,'#80f2e9',8);R(0,157,320,23,'#061224');R(0,157,320,2,'#e89b60');T('ACT '+(n+1)+'/7  '+data.scenes[n].setting.slice(0,21),7,171,'#ffcf9c',8);T(paused?'PAUSED':'CANVAS2D',258,171,'#89e9da',7);return;}if(data.id==='W015'){w015(mode);R(0,0,320,17,'#081221');T('ONE STATE / RECORD '+data.id,6,12,'#80f2e9',8);R(0,157,320,23,'#061224');R(0,157,320,2,'#e89b60');T('ACT '+(n+1)+'/7  '+data.scenes[n].setting.slice(0,21),7,171,'#ffcf9c',8);T(paused?'PAUSED':'CANVAS2D',258,171,'#89e9da',7);return;}if(data.id==='W014'){w014(mode);R(0,0,320,17,'#081221');T('ONE STATE / RECORD '+data.id,6,12,'#80f2e9',8);R(0,157,320,23,'#061224');R(0,157,320,2,'#e89b60');T('ACT '+(n+1)+'/7  '+data.scenes[n].setting.slice(0,21),7,171,'#ffcf9c',8);T(paused?'PAUSED':'CANVAS2D',258,171,'#89e9da',7);return;}if(data.id==='W013'){w013(mode);R(0,0,320,17,'#081221');T('ONE STATE / RECORD '+data.id,6,12,'#80f2e9',8);R(0,157,320,23,'#061224');R(0,157,320,2,'#e89b60');T('ACT '+(n+1)+'/7  '+data.scenes[n].setting.slice(0,21),7,171,'#ffcf9c',8);T(paused?'PAUSED':'CANVAS2D',258,171,'#89e9da',7);return;}if(data.id==='W012'){w012(mode);R(0,0,320,17,'#081221');T('ONE STATE / RECORD '+data.id,6,12,'#80f2e9',8);R(0,157,320,23,'#061224');R(0,157,320,2,'#e89b60');T('ACT '+(n+1)+'/7  '+data.scenes[n].setting.slice(0,21),7,171,'#ffcf9c',8);T(paused?'PAUSED':'CANVAS2D',258,171,'#89e9da',7);return;}if(data.id==='W011'){w011(mode);R(0,0,320,17,'#081221');T('ONE STATE / RECORD '+data.id,6,12,'#80f2e9',8);R(0,157,320,23,'#061224');R(0,157,320,2,'#e89b60');T('ACT '+(n+1)+'/7  '+data.scenes[n].setting.slice(0,21),7,171,'#ffcf9c',8);T(paused?'PAUSED':'CANVAS2D',258,171,'#89e9da',7);return;}if(data.id==='W010'){w010(mode);R(0,0,320,17,'#081221');T('ONE STATE / RECORD '+data.id,6,12,'#80f2e9',8);R(0,157,320,23,'#061224');R(0,157,320,2,'#e89b60');T('ACT '+(n+1)+'/7  '+data.scenes[n].setting.slice(0,21),7,171,'#ffcf9c',8);T(paused?'PAUSED':'CANVAS2D',258,171,'#89e9da',7);return;}if(data.id==='W009'){w009(mode);R(0,0,320,17,'#081221');T('ONE STATE / RECORD '+data.id,6,12,'#80f2e9',8);R(0,157,320,23,'#061224');R(0,157,320,2,'#e89b60');T('ACT '+(n+1)+'/7  '+data.scenes[n].setting.slice(0,21),7,171,'#ffcf9c',8);T(paused?'PAUSED':'CANVAS2D',258,171,'#89e9da',7);return;}if(data.id==='W008'){w008(mode);R(0,0,320,17,'#081221');T('ONE STATE / RECORD '+data.id,6,12,'#80f2e9',8);R(0,157,320,23,'#061224');R(0,157,320,2,'#e89b60');T('ACT '+(n+1)+'/7  '+data.scenes[n].setting.slice(0,21),7,171,'#ffcf9c',8);T(paused?'PAUSED':'CANVAS2D',258,171,'#89e9da',7);return;}if(data.id==='W007'){w007(mode);R(0,0,320,17,'#081221');T('ONE STATE / RECORD '+data.id,6,12,'#80f2e9',8);R(0,157,320,23,'#061224');R(0,157,320,2,'#e89b60');T('ACT '+(n+1)+'/7  '+data.scenes[n].setting.slice(0,21),7,171,'#ffcf9c',8);T(paused?'PAUSED':'CANVAS2D',258,171,'#89e9da',7);return;}if(data.id==='W006'){w006(mode);R(0,0,320,17,'#081221');T('ONE STATE / RECORD '+data.id,6,12,'#80f2e9',8);R(0,157,320,23,'#061224');R(0,157,320,2,'#e89b60');T('ACT '+(n+1)+'/7  '+data.scenes[n].setting.slice(0,21),7,171,'#ffcf9c',8);T(paused?'PAUSED':'CANVAS2D',258,171,'#89e9da',7);return;}if(data.id==='W005'){w005(mode);R(0,0,320,17,'#081221');T('ONE STATE / RECORD '+data.id,6,12,'#80f2e9',8);R(0,157,320,23,'#061224');R(0,157,320,2,'#e89b60');T('ACT '+(n+1)+'/7  '+data.scenes[n].setting.slice(0,21),7,171,'#ffcf9c',8);T(paused?'PAUSED':'CANVAS2D',258,171,'#89e9da',7);return;}if(data.id==='W004'){w004(mode);R(0,0,320,17,'#081221');T('ONE STATE / RECORD '+data.id,6,12,'#80f2e9',8);R(0,157,320,23,'#061224');R(0,157,320,2,'#e89b60');T('ACT '+(n+1)+'/7  '+data.scenes[n].setting.slice(0,21),7,171,'#ffcf9c',8);T(paused?'PAUSED':'CANVAS2D',258,171,'#89e9da',7);return;}if(data.id==='W003'){w003(mode);R(0,0,320,17,'#081221');T('ONE STATE / RECORD '+data.id,6,12,'#80f2e9',8);R(0,157,320,23,'#061224');R(0,157,320,2,'#e89b60');T('ACT '+(n+1)+'/7  '+data.scenes[n].setting.slice(0,21),7,171,'#ffcf9c',8);T(paused?'PAUSED':'CANVAS2D',258,171,'#89e9da',7);return;}if(data.id==='W002'){w002(mode);R(0,0,320,17,'#081221');T('ONE STATE / RECORD '+data.id,6,12,'#80f2e9',8);R(0,157,320,23,'#061224');R(0,157,320,2,'#e89b60');T('ACT '+(n+1)+'/7  '+data.scenes[n].setting,7,171,'#ffcf9c',8);T(paused?'PAUSED':'CANVAS2D',258,171,'#89e9da',7);return;}const d=(x,y)=>person(x,y,'#c5b1a4','#a37c58'),o=(x,y)=>person(x,y,'#d4a3c2','#be956b');if(mode===0){R(75,50,173,80,'#24526c');L(75,50,173,80,'#8de9e5');R(82,57,156,67,'#14354d');d(165,109);R(103,71,38,26,'#3d7d8c');T('D-503',105,86,'#ffcd92',9)}if(mode===1){R(39,41,245,82,'#183348');L(39,41,245,82,'#8ce5e0');T('TABLE OF HOURS',88,56,'#ffca8d',10);for(let j=0;j<7;j++){R(57+j*34,67,29,23,j%2?'#2b5c70':'#3e7186');T(('0'+(j+1)).slice(-2),62+j*34,81,'#d7f0e4',9)}d(160,113)}if(mode===2){R(42,49,238,78,'#1a4055');for(let j=0;j<6;j++){let x=62+j*40;R(x,88,26,27,'#2f6684');R(x+4,93,18,12,'#91dee0')}R(140,31,40,75,'#b1bac0');R(151,19,17,14,'#f3b16e');d(77,112);T('INTEGRAL',137,122,'#ffe1a4',9)}if(mode===3){d(112,109);o(207,109);for(let j=0;j<7;j++)R(23+j*43,48,23,10,'#467b8b');T('TWO NUMBERS',109,67,'#ffca94',9)}if(mode===4){R(0,43,320,90,'#1b4556');for(let x=0;x<320;x+=14)R(x,57,5,68,'#489b78');R(0,80,320,8,'#92c18b');d(174,119);T('THE GREEN WALL',109,43,'#ffe0aa',9)}if(mode===5){d(120,111);R(166,49,97,72,'#203b55');L(166,49,97,72,'#8bd0df');T('1 + 1 = ?',180,84,'#ffe0b0',10);T('DOUBT',188,99,'#d7b2f2',9)}if(mode===6){d(101,111);o(223,111);R(130,49,63,62,'#1a354e');L(130,49,63,62,'#d3a7c8');T('W001',145,78,'#ffcea0',11);T('?',157,99,'#b4f1ec',14)}R(0,0,320,17,'#081221');T('ONE STATE / RECORD '+data.id,6,12,'#80f2e9',8);R(0,157,320,23,'#061224');R(0,157,320,2,'#e89b60');T('ACT '+(n+1)+'/7  '+data.scenes[n].setting.slice(0,21),7,171,'#ffcf9c',8);T(paused?'PAUSED':'CANVAS2D',258,171,'#89e9da',7)}function persist(){try{localStorage.setItem(storage,JSON.stringify({scene:n,heard:[...heard],answers}))}catch(e){}}function tone(){if(!sound)return;try{const ac=new (window.AudioContext||window.webkitAudioContext)(),osc=ac.createOscillator(),v=ac.createGain();osc.type='triangle';osc.frequency.value=280+(n*40);v.gain.value=.025;osc.connect(v);v.connect(ac.destination);osc.start();osc.stop(ac.currentTime+.065);osc.onended=()=>ac.close()}catch(e){}}function render(){const s=data.scenes[n];q('act').textContent='ACT '+(n+1)+' / 7 · '+s.setting;q('heading').textContent=s.title;q('story').textContent=s.story;q('speaker').textContent=s.speaker;q('speech').textContent=s.line;q('observed').textContent=heard.has(n)?s.observation:'Inspect this act to record its source-bound observation.';q('inferred').textContent=heard.has(n)?s.inference:'Not yet inspected.';q('question').textContent=s.question;let area=q('choices');area.replaceChildren();s.choices.forEach((item,i)=>{const b=document.createElement('button');b.textContent=item;b.className=answers[n]===i?'primary':'';b.onclick=()=>{answers[n]=i;tone();render()};area.appendChild(b)});q('response').textContent=answers[n]===undefined?'Choose an interpretation to test the witness boundary.':s.reply[answers[n]];q('back').disabled=n===0;q('next').disabled=n===6;q('inspect').disabled=heard.has(n);q('count').textContent=heard.size+'/7';q('progress').style.width=(heard.size/7*100)+'%';q('export').disabled=heard.size!==7;persist();frame()}function go(x){n=Math.min(6,Math.max(0,n+x));tone();render()}q('back').onclick=()=>go(-1);q('next').onclick=()=>go(1);q('inspect').onclick=()=>{heard.add(n);tone();render()};q('motion').onclick=()=>{paused=!paused;q('motion').textContent=paused?'RESUME MOTION':'PAUSE MOTION';frame()};q('sound').onclick=()=>{sound=!sound;q('sound').textContent=sound?'SOUND ON':'SOUND OFF';tone()};q('export').onclick=()=>{const packet={record:data.id,source:'original literary interpretation, one ancestry',observed:[...heard].sort(),choices:answers,local_timestamp:new Date().toISOString(),independent_attestation:false};const blob=new Blob([JSON.stringify(packet,null,2)],{type:'application/json'}),url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download='WE-'+data.id+'-witness.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),2000)};q('reset').onclick=()=>{if(confirm('Reset this browser record?')){n=0;heard.clear();answers={};render()}};document.addEventListener('keydown',e=>{if(e.target.closest('button,input,textarea'))return;if(e.key==='ArrowRight')go(1);if(e.key==='ArrowLeft')go(-1);if(e.key.toLowerCase()==='i')q('inspect').click()});function tick(){if(!paused){t++;frame()}requestAnimationFrame(tick)}render();requestAnimationFrame(tick)})();