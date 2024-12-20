
generator = "kkmcee"
parms = []


cfg = r'''
----------cccccccccccccccccccccccccccccommentttttttttttttttttttttttttttttttttttt
BeginX
********************************************************************************
*               ACTUAL DATA FOR THIS PARTICULAR RUN
********************************************************************************
*indx_____data______ccccccccc0ccccccccc0ccccccccc0ccccccccc0ccccccccc0ccccccccc0
 1600   {nevents} number of events to be generated
 1700   {seed} seed, 0<=IJKLIN<=900000000
    1   240               CMSEne =xpar( 1) ! CMS total energy [GeV]
   25              3      KeyFix=0 normal, =2 beamsstrahlung =3,4 for gaussian BES 
   50              0      KeyHad=xpar(50)  Default is  1
   20              1      KeyISR=xpar(20)  Default is  1, for beams       |<<<<|
   21              1      KeyFSR=xpar(21)  Default is  1, for all final fermions
*indx_____data______ccccccccc0ccccccccc0ccccccccc0ccccccccc0ccccccccc0ccccccccc0
   80          0.0e0      ParBES(0) E1=0 will be replaced by CMSene/2
   81          0.0e0      ParBES(1) E2=0 will be replaced by CMSene/2
   82      0.00185e0      ParBES(2) sigma1/E1
   83      0.00185e0      ParBES(3) sigma2/E2
   84        0.000e0      ParBES(3) rho correlation parameter, dimensionles
********************************************************************************
*     Define process
  401              1      KFfin, muon
  100              1      store lhe file to (LHE_OUT.LHE)
************************* one can change the lhf file name between brackets 
********************************************************************************
  502      91.1876e0      MZ  =xpar(502)  pdg22
  503       .23122e0      SwSq  =xpar(503) sin_squared of EW angle, pdg22
  504       2.4952e0      GammZ =xpar(504) Z width, pdg22
  505       80.379e0      MW    =xpar(505) W mass,  pdg22
  506        2.085e0      GammW =xpar(506) W width, pdg22
********************************************************************************
EndX
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
Next:numberCount = 10              ! print message every n events
Next:numberShowLHA = 10            ! print LHA information n times
Next:numberShowInfo = 10           ! print event information n times
Next:numberShowProcess = 10        ! print process record n times
Next:numberShowEvent = 10          ! print event record n times
Stat:showPartonLevel = off         ! additional statistics on MPI

! 3) Tell Pythia that LHEF input is used
Beams:frameType = 4
Beams:setProductionScalesFromLHEF = off
Beams:allowMomentumSpread  = off
Beams:LHEF = LHE_OUT.LHE

! Vertex smearing
Beams:allowVertexSpread = on
Beams:sigmaVertexX = 0.0098
Beams:sigmaVertexY = 2.54e-5
Beams:sigmaVertexZ = 0.646
Beams:sigmaTime = 1.937

! 4) Settings for the event generation process in the Pythia8 library.
PartonLevel:ISR = off               ! initial-state radiation
PartonLevel:FSR = on                ! final-state radiation

Check:epTolErr = 1e-1               ! default 1e-4, necessary to allow BES
LesHouches:matchInOut = off


'''