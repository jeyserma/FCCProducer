
generator = "wz3p6"
parms = []

cfg = r'''
# whizard v3.0.3

model = SM

# Center of mass energy
sqrts = 91.2 GeV

# Processes

#?vis_diags = true


process proc = A, A => e2,E2

beams = e1, E1 => epa, epa
?keep_beams  = true
?keep_remnants = true

$epa_mode = "Budnev_616e"
epa_alpha          = 0.0072993
epa_mass           = me
epa_q_max          = 1.4142 ! = Photon:Q2max in Pythia
epa_q_min          = 0
epa_x_min          = 0.000001 ! close to zero


isr_alpha          = 0.0072993
isr_mass           = me


?epa_recoil = true
?epa_keep_energy = true

#?epa_handler = true 
#$epa_handler_mode = "recoil" ! gives transverse momentum to gammas (theta != 0)


cuts = all M > 5 GeV [ e2,E2 ]

! Parton shower and hadronization
!?ps_fsr_active          = true
!?ps_isr_active          = false
!?hadronization_active   = true
!$shower_method          = "PYTHIA6"
!?ps_PYTHIA_verbose     = true


!$ps_PYTHIA_PYGIVE = "MSTJ(28)=0; PMAS(25,1)=125.; PMAS(25,2)=0.4143E-02; MSTJ(41)=2; MSTU(22)=2000; PARJ(21)=0.40000; PARJ(41)=0.11000; PARJ(42)=0.52000; PARJ(81)=0.25000; PARJ(82)=1.90000; MSTJ(11)=3; PARJ(54)=-0.03100; PARJ(55)=-0.00200; PARJ(1)=0.08500; PARJ(3)=0.45000; PARJ(4)=0.02500; PARJ(2)=0.31000; PARJ(11)=0.60000; PARJ(12)=0.40000; PARJ(13)=0.72000; PARJ(14)=0.43000; PARJ(15)=0.08000; PARJ(16)=0.08000; PARJ(17)=0.17000; MSTP(3)=1;MSTP(71)=1; MSTP(151)=1; PARP(151)=5.96e-3 ; PARP(152)=23.8E-6; PARP(153)=0.397; PARP(154)=10.89; MSTJ(22)=4; PARJ(73)=2250; PARJ(74)=2500"



integrate (proc) {{ iterations = 10:100000:"gw", 5:200000:"" }}

n_events = {nevents}
seed = {seed}

sample_format =  stdhep
$extension_stdhep = "stdhep"
simulate (proc) {{checkpoint = 100}}
'''