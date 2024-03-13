
generator = "wz3p6"
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
$shower_method          = "PYTHIA6"
$hadronization_method   = "PYTHIA6"
!?ps_PYTHIA_verbose     = true

# ALEPH tune
$ps_PYTHIA_PYGIVE = "MSTJ(28)=0;PMAS(25,1)=125.;PMAS(25,2)=0.4143E-02;MSTJ(41)=2;MSTU(22)=2000;PARJ(21)=0.362;PARJ(26)=0.27;PARJ(41)=0.4;PARJ(42)=0.824;PARJ(81)=0.286;PARJ(82)=1.47;MSTJ(11)=3;PARJ(54)=0.04;PARJ(55)=0.0018;PARJ(1)=0.105;PARJ(3)=0.71;PARJ(2)=0.283;PARJ(11)=0.54;PARJ(12)=0.46;PARJ(13)=0.65;PARJ(14)=0.12;PARJ(15)=0.04;PARJ(16)=0.12;PARJ(17)=0.20;PARJ(19)=0.58;MSTP(71)=1;MSTP(151)=1;PARP(151)=5.96e-3;PARP(152)=23.8E-6;PARP(153)=0.397;PARP(154)=10.89"







integrate (proc) {{ iterations = 10:100000:"gw", 5:200000:"" }}

n_events = {nevents}
seed = {seed}

sample_format =  stdhep
$extension_stdhep = "stdhep"
simulate (proc) {{checkpoint = 100}}







'''