# -*- coding: utf-8 -*-
# encoding: utf-8

O=Omega()
from yade import geom,utils,pack,ymport,export

#### material definition
def sphereMat(): return FrictMat(density=2500,young=1e9,poisson=0.3,frictionAngle=radians(1)) # frictionAngle will afect the final porosity of the packing: small->denser packing / large->looser packing

#### in box (can be adapted for cylinder and sphere)
# dimensions of box
X=1.
Y=1.
Z=2.
# volume of box
totVol=X*Y*Z
# name of output file (containing the list of particles making up the assembly)
NAME='box_112_por0.3'
# mean size of particles
sphereRad=0.5*min(X,Y,Z)/18. # defined as a function of the box dimensions (you could give a value instead)
# functions that generate the initial cloud of particles inside the box
pred=pack.inAlignedBox((0.,0.,0.),(X,Y,Z))
O.bodies.append(pack.randomDensePack(pred,radius=sphereRad,rRelFuzz=0.333,spheresInCell=3000,memoizeDb=None,returnSpherePack=False,color=(0.9,0.8,0.6),material=sphereMat)) #,memoizeDb='/tmp/gts-triax-packings.sqlite'
O.bodies.append(geom.facetBox((X/2.,Y/2.,Z/2.),(X/2.,Y/2.,Z/2.),fixed=True,wire=True,material=sphereMat))

#### get dimensions
R=0
Rmax=0
Rmin=1e6
nbSpheres=0.
for o in O.bodies:
 if isinstance(o.shape,Sphere):
   o.shape.color=(0.7,0.5,0.3)
   nbSpheres+=1
   R+=o.shape.radius
   if o.shape.radius>Rmax:
     Rmax=o.shape.radius
   if o.shape.radius<Rmin:
     Rmin=o.shape.radius
Rmean=R/nbSpheres

print('nbSpheres=',nbSpheres,' | Rmean=',Rmean, ' | Rmax/Rmin=', Rmax/Rmin)

#### engines
O.engines=[ForceResetter(),
           InsertionSortCollider([Bo1_Sphere_Aabb(),Bo1_Facet_Aabb()]),
           InteractionLoop(
               [Ig2_Sphere_Sphere_ScGeom(),Ig2_Facet_Sphere_ScGeom()],
               [Ip2_FrictMat_FrictMat_FrictPhys()],
               [Law2_ScGeom_FrictPhys_CundallStrack()]
           ),
           NewtonIntegrator(damping=0.6,label='newton')
]

#### visualization
from yade import qt
v=qt.Controller()
v=qt.View()

#### define time step
O.dt=0.1*utils.PWaveTimeStep();

#O.run()
comp=0
while 1:
    if comp<0.7:
      volSpheres=0.
      for o in O.bodies:
          if isinstance(o.shape,Sphere):
              o.shape.radius*=1.001
              volSpheres+=(4./3.)*pi*(o.shape.radius)**3.
      comp=volSpheres/totVol
    O.run(100,True)
    unb=unbalancedForce()
    print('unbF:',unb,' compacity: ',comp,' iter:',O.iter)
    if unb<0.005 and comp>=0.7 : # unb<0.1 or O.iter>50000 we may define other criteria (e.g. based on the compacity (or porosity): if comp>=givenValue, e.g., 0.666).
        print('final density=',comp)
        O.run(100,True)
        break

#### export compacted packing
export.text(NAME+'_'+str(int(nbSpheres))+'.spheres')
