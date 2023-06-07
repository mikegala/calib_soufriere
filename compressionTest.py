from yade import ymport, plot

# utils.readParamsFromTable(P='box_112_por0.3_9976',D=2700,R=1.,Y=1e9,A=0.1,F=0,T=0,C=0,MAX=1,OUTFILE='default',noTableOk=True)
# from yade.params.table import *

################# SIMULATIONS DEFINED HERE

#### pre-existing packing
PACK='box_112_por0.35_wrong_9912'

#### Simulation Control
rate=-0.1 #deformation rate
iterMax=15000 # maximum number of iterations 
saveData=int(iterMax/1000) # data record interval
saveVTK=int(iterMax/10.) # saving output files for paraview 
OUT='comp'+PACK

#### Microproperties (interparticle parameters)
DENS=2700/0.65 # this one can be adjusted for different reasons (porosity of packing vs porosity of material / increase time step (no gravity -> no real effect on the result)

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

#### material definition
def sphereMat(): return JCFpmMat(type=1,density=DENS,young=YOUNG,poisson=ALPHA,tensileStrength=TENS,cohesion=COH,frictionAngle=radians(FRICT))

#### import pre-existing specimen
O.bodies.append(ymport.text(PACK+'.spheres',scale=1.,shift=Vector3(0,0,0),material=sphereMat))

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


################# DEM loop + ENGINES DEFINED HERE

#### help define boundary conditions (see utils.uniaxialTestFeatures)
bb=utils.uniaxialTestFeatures()
negIds,posIds,longerAxis,crossSectionArea=bb['negIds'],bb['posIds'],bb['axis'],bb['area']

O.engines=[ForceResetter(),
           InsertionSortCollider([Bo1_Sphere_Aabb(aabbEnlargeFactor=intR,label='Saabb')]),
           InteractionLoop(
               [Ig2_Sphere_Sphere_ScGeom(interactionDetectionFactor=intR,label='SSgeom')],
               [Ip2_JCFpmMat_JCFpmMat_JCFpmPhys(cohesiveTresholdIteration=1,label='interactionPhys')],
               [Law2_ScGeom_JCFpmPhys_JointedCohesiveFrictionalPM(recordCracks=False,Key=OUT,label='interactionLaw')]
           ),
           UniaxialStrainer(strainRate=rate,axis=longerAxis,asymmetry=0,posIds=posIds,negIds=negIds,crossSectionArea=crossSectionArea,blockDisplacements=1,blockRotations=1,setSpeeds=0,stopStrain=0.1,dead=1,label='strainer'),
           GlobalStiffnessTimeStepper(active=1,timeStepUpdateInterval=10,timestepSafetyCoefficient=0.8,defaultDt=utils.PWaveTimeStep()),
           NewtonIntegrator(damping=0.5,label='newton'),
           PyRunner(iterPeriod=saveData,initRun=True,command='recorder()',label='data'),
           #VTKRecorder(iterPeriod=saveVTK,initRun=True,fileName=OUT+'-',recorders=['spheres','jcfpm','cracks','bstresses'],Key=OUT,dead=0,label='vtk') #uncomment if you want to obtain Paraview files
]

################# RECORDER DEFINED HERE

def recorder():
    yade.plot.addData({'i':O.iter,
        'eps':strainer.strain,
        'sigma':strainer.avgStress,
        'tc':interactionLaw.nbTensCracks,
        'sc':interactionLaw.nbShearCracks,
        'unbF':utils.unbalancedForce()})
    plot.saveDataTxt(OUT)

################# PREPROCESSING

#### manage interaction detection factor during the first timestep and then set default interaction range
O.step();
#### initializes the interaction detection factor
#SSgeom.interactionDetectionFactor=-1.
#Saabb.aabbEnlargeFactor=-1.

##### special treatment for tension tests: reinforcement of bonds close to boundaries: UNCOMMENT IF YOU WANT TO PERFORM A TENSION TEST
#if rate>0:
    #dim=aabbExtrema()
    #layerSize=0.15 # size of the reinforced zone
    #for o in O.bodies:
        #if isinstance(o.shape,Sphere):
            #if ( o.state.pos[longerAxis]<(dim[0][longerAxis]+layerSize*(dim[1][longerAxis]-dim[0][longerAxis])) ) or ( o.state.pos[longerAxis]>(dim[1][longerAxis]-layerSize*(dim[1][longerAxis]-dim[0][longerAxis])) ) :
                #o.shape.color=(1,1,1)

#### coordination number calculation
numSSlinks=0
numCohesivelinks=0
for i in O.interactions:
    if not i.isReal : continue
    if isinstance(O.bodies[i.id1].shape,Sphere) and isinstance(O.bodies[i.id2].shape,Sphere):
      numSSlinks+=1
      # FOR TENSION TEST: these lines reinforce the bonds near the boundaries to avoid rupture along the boundaries
      if O.bodies[i.id1].shape.color==(1,1,1) or O.bodies[i.id2].shape.color==(1,1,1):
          i.phys.FnMax*=100
          i.phys.FsMax*=100
    if i.phys.isCohesive:
      numCohesivelinks+=1
print ("K=", 2.0*numCohesivelinks/nbSpheres) 

#vtk.dead=0
#O.step()
#vtk.iterPeriod=saveVTK

################# SIMULATION REALLY STARTS HERE
strainer.dead=0
O.run(iterMax,True)
