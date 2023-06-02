# -*- coding: utf-8 -*-
from yade import ymport, utils , plot
import math

# utils.readParamsFromTable(P='box_112_1520',R=1.,Y=1e9,A=0.1,F=0,T=0,C=0,CONF=0,RATE=0.01,MAX=1,OUTFILE='default',noTableOk=True)
# from yade.params.table import *

#------------- PARAMETERS ARE DEFINED HERE

#### pre-existing packing
PACK='box_112_por0.3_9976'

#### loading conditions !!! 
confinement=-250e3 # confining pressure
strainRate=-0.1 # strain rate

#### Simulation control !!!
iterMax=50000 # maximum number of iterations
saveData=int(iterMax/1000) # data record interval
saveVTK=int(iterMax/1) # Vtk files record interval
OUT='correction_triax_250e3_0.1' # name of outut files

#### Microproperties (interparticle parameters)
DENS=2700/0.7 # this one can be adjusted for different reasons (porosity of packing vs porosity of material / increase time step (no gravity -> no real effect on the result)

intR=1.4 # allows near neighbour interaction (can be adjusted for every packing / the bigger -> the more brittle / careful when intR is too large -> bonds can be created "over" particles) -> intR can be calibrated to reach a certain coordination number K (see calculation on line 115)
YOUNG=40e9 # this one controls the Young's modulus of the material
ALPHA=0.25 # this one controls the material Poisson's ratio of the material
TENS=5e6 # this one controls the tensile strength UTS of the material
COH=100e6 # this one controls the compressive strength UCS of the material, more precisely, the ratio UCS/UTS (from my experience: COH should be >= to TENS, >= 10*TENS for competent materials like concrete)
FRICT=35 # this one controls the slope of the failure envelope (effect mainly visible on triaxial compression tests)

#### example values
### granite -> needs K=13
#YOUNG=68e9 
#ALPHA=0.333
#TENS=8e6 
#COH=16e7
#FRICT=10

### Fontainebleau sandstone -> needs K=10
#YOUNG=50e9 
#ALPHA=0.25
#TENS=45e5 
#COH=45e6
#FRICT=18

#### claystone -> needs K=8
#YOUNG=10e9 
#ALPHA=0.1
#TENS=12e6 
#COH=12e6
#FRICT=7

#------------- NO NEED TO MODIFY ANYTHING HERE

#### material definition
def sphereMat(): return JCFpmMat(type=1,density=DENS,young=YOUNG,poisson = ALPHA,frictionAngle=radians(FRICT),tensileStrength=TENS,cohesion=COH)
def wallMat(): return JCFpmMat(type=0,density=DENS,young=YOUNG,frictionAngle=radians(0))

#### preprocessing to get dimensions
O.bodies.append(ymport.text(PACK+'.spheres',scale=1.,shift=Vector3(0,0,0),material=sphereMat))

dim=utils.aabbExtrema()
xinf=dim[0][0]
xsup=dim[1][0]
X=xsup-xinf
yinf=dim[0][1]
ysup=dim[1][1]
Y=ysup-yinf
zinf=dim[0][2]
zsup=dim[1][2]
Z=zsup-zinf

R=0
Rmax=0
Rmin=1e6
nbSpheres=0.
for o in O.bodies:
 if isinstance(o.shape,Sphere):
   nbSpheres+=1
   R+=o.shape.radius
   if o.shape.radius>Rmax:
     Rmax=o.shape.radius
   if o.shape.radius<Rmin:
     Rmin=o.shape.radius
Rmean=R/nbSpheres

print('nbSpheres=',nbSpheres,' | Rmean=',Rmean, ' | Rmax/Rmin=', Rmax/Rmin)

#### IMPORTANT LINE HERE
O.reset() # all previous lines were for getting dimensions of the packing to create walls at the right positions (below) because walls have to be genrated after spheres for FlowEngine

#### create walls
mn,mx=Vector3(xinf+0.1*Rmean,yinf+0.1*Rmean,zinf+0.1*Rmean),Vector3(xsup-0.1*Rmean,ysup-0.1*Rmean,zsup-0.1*Rmean)
walls=utils.aabbWalls(oversizeFactor=1.5,extrema=(mn,mx),thickness=min(X,Y,Z)/100.,material=wallMat)
wallIds=O.bodies.append(walls)

#### import pre-existing specimen
O.bodies.append(ymport.text(PACK+'.spheres',scale=1.,shift=Vector3(0,0,0),material=sphereMat))

#------------- ENGINES ARE DEFINED HERE

#### simulation is defined here (DEM loop, interaction law, servo control, recording, etc...)
O.engines=[
        ForceResetter(),
        InsertionSortCollider([Bo1_Box_Aabb(),Bo1_Sphere_Aabb(aabbEnlargeFactor=intR,label='Saabb')]),
	InteractionLoop(
		[Ig2_Sphere_Sphere_ScGeom(interactionDetectionFactor=intR,label='SSgeom'),Ig2_Box_Sphere_ScGeom()],
		[Ip2_JCFpmMat_JCFpmMat_JCFpmPhys(cohesiveTresholdIteration=1,label='interactionPhys')],
		[Law2_ScGeom_JCFpmPhys_JointedCohesiveFrictionalPM(recordCracks=False,Key=OUT,label='interactionLaw')]
	),
        TriaxialStressController(internalCompaction=False,dead=1,label='triax'),
        GlobalStiffnessTimeStepper(active=1,timeStepUpdateInterval=10,timestepSafetyCoefficient=0.5,defaultDt=0.1*utils.PWaveTimeStep()),
        NewtonIntegrator(damping=0.5,label="newton"),
        PyRunner(iterPeriod=saveData,initRun=True,command='recorder()',label='data'),
        VTKRecorder(iterPeriod=1,initRun=True,fileName=OUT+'-',recorders=['spheres','bstresses','jcfpm','cracks'],Key=OUT,dead=1,label='vtk')
]

#uncomment if you want to obtain Paraview files
 
#### custom recording functions
e10=e20=e30=0
def recorder():
    global e10,e20,e30
    yade.plot.addData( t=O.time
			,i=O.iter
			,e1=triax.strain[0]-e10
			,e2=triax.strain[1]-e20
			,e3=triax.strain[2]-e30
			,s1=triax.stress(triax.wall_right_id)[0]
			,s2=triax.stress(triax.wall_top_id)[1]
			,s3=triax.stress(triax.wall_front_id)[2]
			,tc=interactionLaw.nbTensCracks
			,sc=interactionLaw.nbShearCracks
			,uf=utils.unbalancedForce()
    )
    plot.saveDataTxt(OUT)

#------------- CREATE BONDS

#### manage interaction detection factor during the first timestep and then set default interaction range (intRadius=1)
O.step();
### initializes the interaction detection factor
SSgeom.interactionDetectionFactor=-1.
Saabb.aabbEnlargeFactor=-1.

#### coordination number calculation
numSSlinks=0
numCohesivelinks=0
for i in O.interactions:
    if not i.isReal : continue
    if isinstance(O.bodies[i.id1].shape,Sphere) and isinstance(O.bodies[i.id2].shape,Sphere):
      numSSlinks+=1
    if i.phys.isCohesive :
      numCohesivelinks+=1
print ("K=", 2.0*numCohesivelinks/nbSpheres)

vtk.dead=0
O.step()
vtk.dead=1
#vtk.iterPeriod=saveVTK

#### SIMULATION REALLY STARTS HERE
triax.dead=0

#### APPLYING ISOTROPIC LOADING

triax.stressMask=7
triax.goal1=confinement
triax.goal2=confinement
triax.goal3=confinement
triax.max_vel=0.01

print ("ISOTROPIC CONFINEMENT!")

while 1:
  if confinement==0: 
    break
  O.run(100,True)
  unb=unbalancedForce()
  #note: triax.stress(k) returns a stress vector, so we need to keep only the normal component
  meanS=abs(triax.stress(triax.wall_right_id)[0]+triax.stress(triax.wall_top_id)[1]+triax.stress(triax.wall_front_id)[2])/3
  print ('unbalanced force:',unb,' mean stress: ',meanS)
  if unb<0.005 and abs(meanS-abs(confinement))/abs(confinement)<0.001:
    O.run(100,True) # to stabilize the system
    e10=triax.strain[0]
    e20=triax.strain[1]
    e30=triax.strain[2]
    break

#### APPLYING DEVIATORIC LOADING

vtk.dead=0
vtk.iterPeriod=1
O.step()
vtk.dead=1

triax.stressMask=3
triax.goal1=confinement
triax.goal2=confinement
triax.goal3=strainRate
triax.max_vel=1

print ("DEVIATORIC LOADING!")

O.run(iterMax,True)

vtk.dead=0
O.step()
