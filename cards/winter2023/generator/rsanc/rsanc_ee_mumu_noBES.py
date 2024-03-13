
generator = "rsanc"
parms = ["ecm"]

cfg = r'''
"ecm": <ecm>,
"pid": 103,
"printLHE": true,
"iqed": 1,
"iew": 1,
"iborn": 0,
"mw": 80.379,
"mz": 91.1876,
"mh": 125.0,
"ww": 2.085,
"wz": 2.4952,
"wh": 0.01,
'''


cfg_pythia = '''
! 1) Settings that will be used in a main program.
Main:numberOfEvents = {nevents}      ! number of events to generate
Main:timesAllowErrors = 100        ! abort run after this many flawed events

! 2) Settings related to output in init(), next() and stat() functions.
Init:showChangedSettings = on      ! list changed settings
Init:showAllSettings = off         ! list all settings
Init:showChangedParticleData = on  ! list changed particle data
Init:showAllParticleData = off     ! list all particle data
Next:numberCount = 1000            ! print message every n events
Next:numberShowLHA = 1             ! print LHA information n times
Next:numberShowInfo = 1            ! print event information n times
Next:numberShowProcess = 1         ! print process record n times
Next:numberShowEvent = 1           ! print event record n times
Stat:showPartonLevel = off         ! additional statistics on MPI

! 3) Tell Pythia that LHEF input is used
Beams:frameType = 4
Beams:setProductionScalesFromLHEF = off
Beams:allowMomentumSpread  = off
Beams:LHEF = Results/events_NLO.lhe

! Vertex smearing
! Vertex smearing
Beams:allowVertexSpread = on
Beams:sigmaVertexX = 5.96e-3
Beams:sigmaVertexY = 23.8E-6
Beams:sigmaVertexZ = 0.397
Beams:sigmaTime = 10.89 ! 36.3 ps

! 4) Settings for the event generation process in the Pythia8 library.
PartonLevel:ISR = off               ! initial-state radiation
PartonLevel:FSR = off               ! final-state radiation

Check:epTolErr = 1e-1               ! default 1e-4, necessary to allow BES
LesHouches:matchInOut = off



'''