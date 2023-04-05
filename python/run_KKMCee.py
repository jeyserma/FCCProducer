
import sys
import os
import subprocess
import random
import config

######################################################
### CONFIG
######################################################
tag = "winter2023" # corresponds to detector configuration
kkmc_card = "kkmc_ee_mumu_ecm240_noFSR" # KKMCee card (in cards/$TAG/generator/kkmcee)
pythia_card = "p8_ee_default_zpole" # Pythia card; different vertex distributions for z/h pole

nevents = 10000
njobs = 1000 # -1 means to run locally (dry run)

######################################################


cwd = os.getcwd()
stack = config.stacks[tag]
priority = 'group_u_FCC.local_gen'
queue = "workday" # espresso microcentury longlunch workday tomorrow testmatch nextweek

conv_lhe = f"{cwd}/utils/convLHE/convLHE"
kkmcee_dir = f"/afs/cern.ch/work/j/jaeyserm/fccee/FCCProducer/generator/KKMCee/"


xing = 0 # crossing angle in mrad, still under development
xing_ = "%s"%xing
suffix = ""


kkmcee_card_def = f"{cwd}/cards/{tag}/generator/kkmcee/{kkmc_card}.input"
pythia_def_card = f"{cwd}/cards/{tag}/generator/pythia/{pythia_card}.cmd"
delphes_card = f"{cwd}/cards/{tag}/delphes/card_IDEA.tcl"
delphes_cfg_card = f"{cwd}/cards/{tag}/delphes/edm4hep_IDEA.tcl"

name = f"{kkmc_card}{suffix}"
submit_dir = f"{cwd}/submit/{tag}/{name}/"
out_dir = f"/eos/experiment/fcc/users/j/jaeyserm/sampleProduction/{tag}/{name}/"
local_dir = f"{cwd}/local/{tag}/{name}/"

def make(seed, savedir):
    
    fOutName = f"{savedir}/submit_{seed}.sh"
    if os.path.exists(fOutName):
        return -1
    rootOutName = f"events_{seed}.root"
    if os.path.exists(f"{out_dir}/{rootOutName}"):
        return -1
    
    fOut = open(fOutName, 'w')

    fOut.write('#!/bin/bash\n')
    fOut.write('SECONDS=0\n')
    fOut.write('unset LD_LIBRARY_PATH\n')
    fOut.write('unset PYTHONHOME\n')
    fOut.write('unset PYTHONPATH\n')
    fOut.write('mkdir job_%s\n'%seed)
    fOut.write('cd job_%s\n'%seed)
    fOut.write('source %s\n'%stack)

    fOut.write('echo "Run KKMCee"\n')
    fOut.write('cp -r %s/dizet-6.45.tar.gz . \n'%kkmcee_dir)
    fOut.write('tar -zxvf dizet-6.45.tar.gz \n')
    fOut.write('mv dizet-6.45 dizet \n')
    fOut.write('cp %s/.KK2f_defaults ./. \n'%kkmcee_dir)
    fOut.write('mkdir ffbench \n')
    fOut.write('cd ffbench \n')
    fOut.write('cp %s/ProdMC ./. \n'%kkmcee_dir)
    fOut.write('mkdir run \n')
    fOut.write('cd run \n')
            
    fOut.write('cp %s pro.input\n'%(kkmcee_card_def))
    fOut.write('cp %s/iniseed.1  ./iniseed \n'%kkmcee_dir)
    fOut.write('cp %s/semaphore.start ./semaphore \n'%kkmcee_dir)
     
    fOut.write('sed -i -e "s/N_EVENTS/%s/g" pro.input \n'%nevents)
    fOut.write('sed -i -e "s/18539572/%s/g" iniseed \n'%seed)

    fOut.write('../ProdMC \n')
    fOut.write('echo "finished run"\n') 

    # convert LHE file (remove dummy)
    fOut.write('echo "Convert LHE file"\n')
    fOut.write('mv LHE_OUT.LHE ../../ \n')
    fOut.write('cd ../../ \n')
    fOut.write('cp %s . \n'%conv_lhe)
    fOut.write('tac LHE_OUT.LHE > iLHE_OUT.LHE  \n')
    fOut.write('./convLHE iLHE_OUT.LHE %f \n' % xing)
    fOut.write('tac iLHE_OUT_conv.LHE > LHE_OUT_conv.LHE  \n')
    
    # run PythiaDelphes and produce edm4hep
    fOut.write('echo "Run PythiaDelphes"\n')
    fOut.write('cp %s card.cmd\n'%pythia_def_card)
    fOut.write('cp %s card.tcl\n'%delphes_card)
    fOut.write('cp %s edm4hep_output_config.tcl\n'%delphes_cfg_card)

    fOut.write('sed -i -e "s/N_EVENTS/%s/g" card.cmd \n'%nevents)
    fOut.write('echo "Beams:LHEF = LHE_OUT_conv.LHE" >> card.cmd\n')
    fOut.write('echo "Check:epTolErr = 1e-1" >> card.cmd\n')
    fOut.write('echo "LesHouches:matchInOut = off" >> card.cmd\n')
    fOut.write('DelphesPythia8_EDM4HEP card.tcl edm4hep_output_config.tcl card.cmd %s\n'%rootOutName)
    fOut.write('echo "DONE"\n')

    fOut.write('echo "Copy file"\n')
    fOut.write('cp %s %s/\n'%(rootOutName,out_dir))
    
    fOut.write('duration=$SECONDS\n')
    fOut.write('echo "Duration: $(($duration))"\n')
    fOut.write('echo "Events: %d"\n'%nevents)

            
    subprocess.getstatusoutput('chmod 777 %s'%fOutName)
    return fOutName

if __name__=="__main__":

    if njobs == -1:
        if os.path.exists(local_dir):
            print(f"Please remove test dir {local_dir}")
            quit()
        os.makedirs(local_dir)
        out_dir = local_dir
        sh = make(1111111111, local_dir)
        os.system('cd %s && %s'%(local_dir, sh))
        
        # extract cross-section
        os.system('cat %s/job_1111111111/ffbench/run/pro.output | grep KK2f_Finalize -B 1 -A 15'%local_dir)
    else:
        if not os.path.exists(submit_dir):
            os.makedirs(submit_dir)
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)
    
        execs = []
        njob = 0
        while njob < njobs:
            seed = f"{random.randint(1000000000,9999999999)}"
            sh = make(seed, submit_dir)
            if sh == -1:
                continue
            njob += 1
            print(f"Prepare job {njob} with seed {seed}")
            execs.append(sh)
            
        fOutName = f'{submit_dir}/condor.cfg'
        fOut = open(fOutName, 'w')

        fOut.write(f'executable     = $(filename)\n')
        fOut.write(f'Log            = {submit_dir}/condor_job.$(ClusterId).$(ProcId).log\n')
        fOut.write(f'Output         = {submit_dir}/condor_job.$(ClusterId).$(ProcId).out\n')
        fOut.write(f'Error          = {submit_dir}/condor_job.$(ClusterId).$(ProcId).error\n')
        fOut.write(f'getenv         = True\n')
        fOut.write(f'environment    = "LS_SUBCWD={submit_dir}"\n')
        fOut.write(f'requirements   = ( (OpSysAndVer =?= "CentOS7") && (Machine =!= LastRemoteHost) && (TARGET.has_avx2 =?= True) )\n')
   
        fOut.write(f'on_exit_remove = (ExitBySignal == False) && (ExitCode == 0)\n')
        fOut.write(f'max_retries    = 3\n')
        fOut.write(f'+JobFlavour    = "{queue}"\n')
        fOut.write(f'+AccountingGroup = "{priority}"\n')
        
        execsStr = ' '.join(execs) 
        fOut.write(f'queue filename matching files {execsStr}\n')
        fOut.close()
        
        subprocess.getstatusoutput(f'chmod 777 {fOutName}')
        os.system(f"condor_submit {fOutName}")
