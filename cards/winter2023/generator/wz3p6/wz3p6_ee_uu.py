
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

# OPAL tune
$ps_PYTHIA_PYGIVE = "MSTJ(28)=0;PMAS(25,1)=125.;PMAS(25,2)=0.4143E-02;MSTJ(41)=2;MSTU(22)=2000;PARJ(21)=0.40000;PARJ(41)=0.11000;PARJ(42)=0.52000;PARJ(81)=0.25000;PARJ(82)=1.90000;MSTJ(11)=3;PARJ(54)=-0.03100;PARJ(55)=-0.00200;PARJ(1)=0.08500;PARJ(3)=0.45000;PARJ(4)=0.02500;PARJ(2)=0.31000;PARJ(11)=0.60000;PARJ(12)=0.40000;PARJ(13)=0.72000;PARJ(14)=0.43000;PARJ(15)=0.08000;PARJ(16)=0.08000;PARJ(17)=0.17000;MSTP(3)=1;MSTP(71)=1;MSTP(151)=1;PARP(151)=5.96e-3;PARP(152)=23.8E-6;PARP(153)=0.397;PARP(154)=10.89"







integrate (proc) {{ iterations = 10:100000:"gw", 5:200000:"" }}

n_events = {nevents}
seed = {seed}

sample_format =  stdhep
$extension_stdhep = "stdhep"
simulate (proc) {{checkpoint = 100}}







'''