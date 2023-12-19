! 1) Settings that will be used in a main program.
Main:numberOfEvents = N_EVENTS     	! number of events to generate
Main:timesAllowErrors = 5        	! abort run after this many flawed events
Random:setSeed = on
Random:seed = N_SEED                ! initialize random generator with a seed

! 2) Settings related to output in init(), next() and stat().
Init:showChangedSettings = on      	! list changed settings
Init:showChangedParticleData = off 	! list changed particle data
Next:numberCount = 100            	! print message every n events
Next:numberShowInfo = 1            	! print event information n times
Next:numberShowProcess = 1         	! print process record n times
Next:numberShowEvent = 0           	! print event record n times
Stat:showPartonLevel = off

! 3) Beam parameter settings. Values below agree with default ones.
Beams:idA = 11                   	! first beam, e- = 11
Beams:idB = -11                  	! second beam, e+ = -11

Beams:eCM = 91.2               		! CM energy of collision

Beams:allowMomentumSpread  = off

! Vertex smearing :
Beams:allowVertexSpread = on
Beams:sigmaVertexX = 5.96e-3   
Beams:sigmaVertexY = 23.8E-6 
Beams:sigmaVertexZ = 0.397     
Beams:sigmaTime = 10.89    !  36.3 ps

WeakSingleBoson:ffbar2ffbar(s:gmZ) = on

PartonLevel:ISR = off               ! initial-state radiation
PartonLevel:FSR = on               	! final-state radiation

! Decays
!Z0
23:onMode = off
23:onIfAny = 2 ! 2 3 4 5 6

ParticleDecays:limitCylinder = on
ParticleDecays:xyMax = 2250.
ParticleDecays:zMax = 2500.