
generator = "wz3p8"
parms = ["ecm"]

cfg = r'''
# whizard v3.0.3

model = SM

# Center of mass energy
sqrts = <ecm> GeV

# Processes
process proc = e1, E1 => u,U

beams = e1, E1 => gaussian => isr
?keep_beams  = true    
?keep_remnants = true

! beams = e1, E1 => gaussian 
gaussian_spread1 = 0.132%
gaussian_spread2 = 0.132%


?isr_handler       = true
$isr_handler_mode = "recoil"
isr_alpha          = 0.0072993
isr_mass           = 0.000511


! Parton shower and hadronization
?ps_fsr_active          = true
?ps_isr_active          = false
?hadronization_active   = true
$shower_method          = "PYTHIA8"
$hadronization_method   = "PYTHIA8"
!?ps_PYTHIA_verbose     = true
$ps_PYTHIA8_config_file = "card.cmd"




integrate (proc) {{ iterations = 10:100000:"gw", 5:200000:"" }}

n_events = {nevents}
seed = {seed}

sample_format = stdhep
$extension_stdhep = "stdhep"
simulate (proc) {{checkpoint = 100}}



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



! Vertex smearing
Beams:allowVertexSpread = on
Beams:sigmaVertexX = 5.96e-3
Beams:sigmaVertexY = 23.8E-6
Beams:sigmaVertexZ = 0.397
Beams:sigmaTime = 10.89 ! 36.3 ps

! 4) Settings for the event generation process in the Pythia8 library.
PartonLevel:ISR = off               ! initial-state radiation
PartonLevel:FSR = on                ! final-state radiation

Check:epTolErr = 1e-1               ! default 1e-4, necessary to allow BES
Check:mTolErr  = 1e-1               ! default 1e-4, necessary to allow BES
LesHouches:matchInOut = off
Check:beams = off
Check:history = off


'''