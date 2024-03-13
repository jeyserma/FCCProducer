
generator = "yfsww"
parms = ["ecm", "mw", "ww"]


cfg = r'''
*//////////////////////////////////////////////////////////////////////////////
*//                                                                          //
*//                 Input data for YFSWW3: ISR + EW + FSR                    //
*//                                                                          //
*//////////////////////////////////////////////////////////////////////////////
BeginX
*<-i><----data-----><-------------------comments------------------------------>
 1600   {nevents} number of events to be generated
 1700   {seed} seed, 0<=IJKLIN<=900000000
    1   <ecm> CMSEne =xpar( 1) ! CMS total energy [GeV]
 1500            0d0 BESB1  =xpar( 1500) ! beam1 spread 0.132d-2
 1501            0d0 BESB2  =xpar( 1501) ! beam2 spread  0.132d-2
 1502              0 BESRHO =xpar( 1501) ! correlation beam spread
    2     1.16639d-5 Gmu    =xpar( 2) ! Fermi Constant  
    3       128.07d0 alfWin =xpar( 3) ! alpha QED at WW tresh. scale (inverse) 
    4      91.1876d0 aMaZ   =xpar( 4) ! Z mass   
    5       2.4952d0 GammZ  =xpar( 5) ! Z width      
    6   <mw> aMaW   =xpar( 6) ! W mass 
    7   <ww> GammW  =xpar( 7) ! W with, For gammW<0 it is RECALCULATED
    8           1d-6 VVmin  =xpar( 8) ! Photon spectrum parameter
    9         0.99d0 VVmax  =xpar( 9) ! Photon spectrum parameter
   10            4d0 WtMax  =xpar(10) ! max weight for reject. 
   11        125.1D0 aMH    =xpar(11) ! Higgs mass  
   12        0.013D0 aGH    =xpar(12) ! Higgs width 
   13       0.1185d0 alpha_s=xpar(13) ! QCD coupling const.
*<-i><----data-----><-------------------comments------------------------------>
* YFSWW3 SPECIFIC PARAMETERS !!!
*=============================================================================
 2001            7d0 KeyCor =xpar(2001)   Radiative Correction switch
*                    KeyCor   =0: Born
*                             =1: Above + ISR
*                             =2: Above + Coulomb Correction
*                             =3: Above + YFS Full Form-Factor Correction
*                             =4: Above + Radiation from WW
*                             =5: Above + Exact O(alpha) EWRC, NL virtual corr.
*                                 calculated non-coherently (OLD BEST!)
*                             =6: As Above but Approximate EWRC (faster!),
*                                 with pretabulation and linear interpolation. 
*                             =7: As KeyCor=5, but O(alpha) EW corrections 
*                                 calculated fully coherently (BEST!)
*=============================================================================
 1014            1d0 KeyCul =xpar(1014)
*                    =0 No Coulomb correction 
*                    =1 "Normal" Coulomb correction 
*                    =2 "Screened-Coulomb" Ansatz for Non-Factorizable Corr. 
 1021            0d0 KeyBra =xpar(1021)
*                    = 0 Born branching ratios, no mixing
*                    = 1 branching ratios from input
*                    = 2 branching ratios with mixing and naive QCD 
*                       calculated in IBA from the CKM matrix (PDG 2000); 
*                       see routine filexp for more details (file filexp.f)
 1023            1d0 KeyZet =xpar(1023)
*                    = 0, Z width in z propagator: s/m_z *gamm_z
*                    = 1, Z width in z propagator:   m_z *gamm_z
*                    = 2, Z zero width in z propagator.
 1026            1d0 KeyWu  =xpar(1026)
*                    = 0 w width in w propagator: s/m_w *gamm_w
*                    = 1 w width in w propagator:   m_w *gamm_w
*                    = 2 no (0) w width in w propagator.
 1031            0d0 KeyWgt =xpar(1031)
*                    =0, unweighted events (wt=1), for apparatus Monte Carlo
*                    =1, weighted events, option faster and safer
 1041            1d0 KeyMix =xpar(1041)
*                    KeyMix EW "Input Parameter Scheme" choices. 
*                    =0 "LEP2 Workshop "95" scheme (for Born and ISR only!)
*                    =1 G_mu scheme (RECOMMENDED)
* W decays: 1=ud, 2=cd, 3=us, 4=cs, 5=ub, 6=cb, 7=e, 8=mu, 9=tau, 0=all chan.
 1055            0d0 KeyDWm =xpar(1055)    W- decay: 7=(ev), 0=all ch.   
 1056            0d0 KeyDWp =xpar(1056)    W+ decay: 7=(ev), 0=all ch.  
 1057           16d0 Nout   =xpar(1057)    Output unit no, for Nout<0, Nout=16
*============================================================================= 
*                  TAUOLA, PHOTOS, JETSET
*   >>> If you want to switch them OFF, uncomment the lines below <<< 
*<-i><----data-----><-------------------comments------------------------------>
 1071           -1d0 Jak1   =xpar(1071)   Decay mode tau+ (by Pythia)
 1072           -1d0 Jak2   =xpar(1072)   Decay mode tau- (by Pythia)
 1074            0d0 IfPhot =xpar(1074)   PHOTOS switch (by Pythia)
 1073            0d0 Itdkrc =xpar(1073)   Bremsstrahlung switch in Tauola 
 1075            0d0 IfHadM =xpar(1075)   Hadronization W-
 1076            0d0 IfHadP =xpar(1076)   Hadronization W+
EndX
*//////////////////////////////////////////////////////////////////////////////
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

! Vertex smearing
Beams:allowVertexSpread = off

! 4) Settings for the event generation process in the Pythia8 library.
PartonLevel:ISR = off               ! initial-state radiation
PartonLevel:FSR = on                ! final-state radiation

Check:epTolErr = 1e-1               ! default 1e-4, necessary to allow BES
LesHouches:matchInOut = off

Beams:LHEF = events.lhe

ColourReconnection:reconnect = off

'''