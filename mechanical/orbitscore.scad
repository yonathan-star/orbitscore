// OrbitScore revision A: parametric engineering source, millimetres.
// part: assembly, base, deck, bridge, pod_base, pod_lid, hub, disc
part="assembly";
$fn=64;
disc_r=82; disc_z=37.4; center=[90,90];
patterns=[[1,0,0,0,1,0,0,0,1,0,0,0,1,0,0,0],
          [0,0,0,0,1,0,0,0,0,0,0,0,1,0,0,0],
          [1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0],
          [0,0,0,0,0,0,0,1,0,0,0,0,0,0,1,1]];
module ring(d,h,hole){difference(){cylinder(d=d,h=h);translate([0,0,-.1])cylinder(d=hole,h=h+.2);}}
module base(){difference(){union(){difference(){cube([190,190,31]);translate([2.4,2.4,2.4])cube([185.2,185.2,32]);}
 for(x=[7,183],y=[7,183])translate([x,y,2])cylinder(d=9,h=29);
 // Speaker posts: square 60mm hole pitch below 78mm speaker, optical reader on right.
 for(x=[35,95],y=[110,170])translate([x,y,2])cylinder(d=8,h=7);
 // Reader bar standoffs: PCB lower face z=27.4, thickness1.6; optics up to36mm.
 for(x=[99,182])translate([x,93,2])cylinder(d=7,h=25.4);
 }
 for(x=[7,183],y=[7,183])translate([x,y,0])cylinder(d=3.2,h=34);
 for(x=[35,95],y=[110,170])translate([x,y,0])cylinder(d=2.6,h=12);
 for(x=[99,182])translate([x,93,0])cylinder(d=2.6,h=30);
 translate([-1,60,12])cube([5,18,10]);
 // Bottom speaker grille, keep ribs >2mm
 for(x=[38:6:92])translate([x,116,-1])cube([2.5,49,5]);
}}
module deck(){difference(){union(){cube([190,190,2.4]);translate([90,90,2.4])cylinder(d=14,h=3);}
 for(x=[7,183],y=[7,183])translate([x,y,-1])cylinder(d=3.4,h=5);
 translate([90,90,-1])cylinder(d=3.2,h=9);
 // Windows for sensor lenses. Sensors are separate from the load bearing deck.
 for(r=[26,36,46,56,66,76])translate([90+r,90,-1])cylinder(d=5,h=5);
 // Bridge mounting holes clear of disc outside radius82.
 for(x=[99,182])translate([x,106,-1])cylinder(d=3.2,h=5);
}}
module disc(){difference(){cylinder(r=disc_r,h=.8);translate([0,0,-1])cylinder(d=6.4,h=3);
 for(ch=[0:3],s=[0:15])if(patterns[ch][s])rotate([0,0,-s*22.5])translate([26+10*ch,0,-1])cylinder(d=7,h=3);
 // Timing holes are smaller than the data holes, so data is stable at clock rise.
 for(s=[0:15])rotate([0,0,-s*22.5])translate([66,0,-1])cylinder(d=3,h=3);
 translate([76,0,-1])cylinder(d=7,h=3);
}}
module bridge(){difference(){union(){
 // Removable optical hood, open-ended disc slot; print upside down with supports.
 translate([95,80,0])cube([92,20,2.4]);
 for(x=[99,182])translate([x,106,-17.6])cylinder(d=8,h=20);
 translate([95,98,-17.6])cube([92,2,20]);
 }
 for(x=[99,182])translate([x,106,-16])cylinder(d=3.2,h=22);
 // Emitter bar mounting holes align after flipping its y axis.
 for(x=[99,182])translate([x,87,-1])cylinder(d=3.2,h=5);
}}
module hub(){union(){cylinder(d=12,h=4);translate([0,0,4])cylinder(d=6,h=5);}}
module pod_base(){difference(){union(){difference(){cube([110,110,30]);translate([2.4,2.4,2.4])cube([105.2,105.2,31]);}
 for(x=[9,101],y=[9,101])translate([x,y,2])cylinder(d=7,h=5);
 for(x=[4,106],y=[4,106])translate([x,y,2])cylinder(d=6,h=28);
 }
 for(x=[9,101],y=[9,101])translate([x,y,0])cylinder(d=2.6,h=10);
 for(x=[4,106],y=[4,106])translate([x,y,0])cylinder(d=2.6,h=34);
 translate([14,-1,9])cube([15,5,9]); // Pico USB access, confirm connector depth
 translate([108,15,12])cube([5,25,10]); // optical harness exit
}}
module pod_lid(){difference(){cube([110,110,2.4]);
 for(x=[4,106],y=[4,106])translate([x,y,-1])cylinder(d=3.2,h=5);
 // Panel-mount potentiometers, wired to J4/J5, clear of the Pico module
 for(x=[55,80])translate([x,18,-1])cylinder(d=7.5,h=5);
 // Wide openings expose tactile button stems; final caps must follow measured switch height.
 for(x=[20.25,42.25,64.25],y=[79.25,95.25])translate([x,y,-1])cylinder(d=8,h=5);
 for(x=[83.27,95.27])translate([x,96,-1])cylinder(d=3.5,h=5);
}}
module plunger(){union(){cylinder(d=6,h=20);translate([0,0,20])cylinder(d=12,h=2);}}
module assembly(){
 color("#303b39")base();color("#7b8d7c")translate([0,0,31])deck();
 color("#d7c5a0")translate([90,90,disc_z])disc();
 color("#303b39")translate([0,0,51])bridge();
 color("#ddddcc")translate([90,90,33.4])hub();
 color("#195546")translate([96,84,27.4])cube([90,18,1.6]);
 color("#195546")translate([96,78,48.6])cube([90,18,1.6]);
 color("#303b39")translate([205,40,0])pod_base();
 color("#7b8d7c")translate([205,40,30])pod_lid();
 color("#195546")translate([210,45,7])cube([100,100,1.6]);
 for(x=[260,285])color("#db7f43")translate([x,58,32.4])cylinder(d=16,h=13);
}
if(part=="assembly")assembly();else if(part=="base")base();else if(part=="deck")deck();else if(part=="bridge")bridge();else if(part=="disc")disc();else if(part=="hub")hub();else if(part=="pod_base")pod_base();else if(part=="pod_lid")pod_lid();else if(part=="plunger")plunger();
