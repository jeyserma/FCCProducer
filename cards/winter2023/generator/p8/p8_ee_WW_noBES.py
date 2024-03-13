
generator = "p8"
parms = ["ecm"]

cfg = '''
Random:setSeed = on
Main:numberOfEvents = 1000         ! number of events to generate
Main:timesAllowErrors = 5          ! how many aborts before run stops

! 2) Settings related to output in init(), next() and stat().
Init:showChangedSettings = on      ! list changed settings
Init:showChangedParticleData = off ! list changed particle data
Next:numberCount = 100             ! print message every n events
Next:numberShowInfo = 1            ! print event information n times
Next:numberShowProcess = 1         ! print process record n times
Next:numberShowEvent = 0           ! print event record n times

Beams:idA = 11                     ! first beam, e+ = 11
Beams:idB = -11                    ! second beam, e- = -11
Beams:eCM = <ecm>  ! CM energy of collision

! Vertex smearing
Beams:allowVertexSpread = off

! 3) Hard process
WeakDoubleBoson:ffbar2WW = on
24:m0 = 80.379
24:mWidth = 2.085


! 4) Settings for the event generation process in the Pythia8 library.
PartonLevel:ISR = on
PartonLevel:FSR = on

'''

