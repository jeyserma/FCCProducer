
generator = "p8"

cfg = '''
! 1) Settings used in the main program.
Random:setSeed = on
Random:seed = {seed}               ! seed
Main:numberOfEvents = {nevents}    ! number of events
Main:timesAllowErrors = 5          ! how many aborts before run stops

! 2) Settings related to output in init(), next() and stat().
Init:showChangedSettings = on      ! list changed settings
Init:showChangedParticleData = off ! list changed particle data
Next:numberCount = 10000           ! print message every n events
Next:numberShowInfo = 1            ! print event information n times
Next:numberShowProcess = 1         ! print process record n times
Next:numberShowEvent = 0           ! print event record n times

! 3) Beam parameter settings. Values below agree with default ones.
Beams:idA = 11                    ! first beam, e = 2212, pbar = -2212
Beams:idB = -11                   ! second beam, e = 2212, pbar = -2212

Beams:allowMomentumSpread  = off

! Vertex smearing :
Beams:allowVertexSpread = on
Beams:sigmaVertexX = 5.96e-3
Beams:sigmaVertexY = 23.8E-6
Beams:sigmaVertexZ = 0.397
Beams:sigmaTime = 10.89 ! 36.3 ps


! 4) Hard process : Z->all
Beams:eCM = 91.2   ! CM energy of collision


WeakSingleBoson:ffbar2gmZ = on

PartonLevel:ISR = on               ! initial-state radiation
PartonLevel:FSR = on               ! final-state radiation
'''

