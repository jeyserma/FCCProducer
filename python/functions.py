
import sys
import os
import glob
import datetime
import subprocess
import config


def copy_cmd():

    return "cp"
    
    
def submit_condor(submitDir, execs, queue):

    fOutName = 'condor.cfg'
    fOutFullName = f'{submitDir}/{fOutName}'
    fOut = open(fOutFullName, 'w')
            

    fOut.write(f'executable     = $(filename)\n')
    fOut.write(f'Log            = {submitDir}/condor_job.$(ClusterId).$(ProcId).log\n')
    fOut.write(f'Output         = {submitDir}/condor_job.$(ClusterId).$(ProcId).out\n')
    fOut.write(f'Error          = {submitDir}/condor_job.$(ClusterId).$(ProcId).error\n')
    fOut.write(f'getenv         = True\n')
    fOut.write(f'environment    = "LS_SUBCWD={submitDir}"\n')
    fOut.write(f'requirements   = ( (OpSysAndVer =?= "CentOS7") && (Machine =!= LastRemoteHost) && (TARGET.has_avx2 =?= True) )\n')
   
    # Tier2 using BOSCO: no requirements nor desired sites
    #fOut.write('requirements   = ( BOSCOCluster =!= "t3serv008.mit.edu" && BOSCOCluster =!= "ce03.cmsaf.mit.edu" && BOSCOCluster =!= "eofe8.mit.edu")\n')

    #fOut.write('+DESIRED_Sites = "mit_tier3"\n')
    #fOut.write('+DESIRED_Sites = "mit_tier2"\n')
    #fOut.write('+DESIRED_Sites = "T2_AT_Vienna,T2_BE_IIHE,T2_BE_UCL,T2_BR_SPRACE,T2_BR_UERJ,T2_CH_CERN,T2_CH_CERN_AI,T2_CH_CERN_HLT,T2_CH_CERN_Wigner,T2_CH_CSCS,T2_CH_CSCS_HPC,T2_CN_Beijing,T2_DE_DESY,T2_DE_RWTH,T2_EE_Estonia,T2_ES_CIEMAT,T2_ES_IFCA,T2_FI_HIP,T2_FR_CCIN2P3,T2_FR_GRIF_IRFU,T2_FR_GRIF_LLR,T2_FR_IPHC,T2_GR_Ioannina,T2_HU_Budapest,T2_IN_TIFR,T2_IT_Bari,T2_IT_Legnaro,T2_IT_Pisa,T2_IT_Rome,T2_KR_KISTI,T2_MY_SIFIR,T2_MY_UPM_BIRUNI,T2_PK_NCP,T2_PL_Swierk,T2_PL_Warsaw,T2_PT_NCG_Lisbon,T2_RU_IHEP,T2_RU_INR,T2_RU_ITEP,T2_RU_JINR,T2_RU_PNPI,T2_RU_SINP,T2_TH_CUNSTDA,T2_TR_METU,T2_TW_NCHC,T2_UA_KIPT,T2_UK_London_IC,T2_UK_SGrid_Bristol,T2_UK_SGrid_RALPP,T2_US_Caltech,T2_US_Florida,T2_US_MIT,T2_US_Nebraska,T2_US_Purdue,T2_US_UCSD,T2_US_Vanderbilt,T2_US_Wisconsin,T3_CH_CERN_CAF,T3_CH_CERN_DOMA,T3_CH_CERN_HelixNebula,T3_CH_CERN_HelixNebula_REHA,T3_CH_CMSAtHome,T3_CH_Volunteer,T3_US_HEPCloud,T3_US_NERSC,T3_US_OSG,T3_US_PSC,T3_US_SDSC"\n')
            
            
            
    fOut.write(f'on_exit_remove = (ExitBySignal == False) && (ExitCode == 0)\n')
    fOut.write(f'max_retries    = 3\n')
    fOut.write(f'+JobFlavour    = "{queue}"\n')
    if config.priority:
        fOut.write(f'+AccountingGroup = "{config.priority}"\n')
    
            
    #fOut.write('use_x509userproxy = True\n')
    #fOut.write('x509userproxy = /home/submit/jaeyserm/x509up_u204569\n')
    #fOut.write('+AccountingGroup = "analysis.jaeyserm"\n')
    #fOut.write('+REQUIRED_OS = "rhel7"\n')
            
    execsStr = ' '.join(execs) 
    fOut.write(f'queue filename matching files {execsStr}\n')
    fOut.close()
    
    subprocess.getstatusoutput(f'chmod 777 {fOutFullName}')
    os.system(f"condor_submit {fOutFullName}")


def common_parser():

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--type", type=str, choices=["reco", "gen", "genreco"], help="Run type (gen, reco or genreco)", required = True)
    parser.add_argument("--process", type=str, help="MC process", required = True)
    parser.add_argument("--tag", type=str, help="MC tag", required = True)
    
    return parser
    
    
def get_generator(process):

    if process[0:2] == "wz":
        return "whizard"
    else:
        raise Exception(f"No valid generator found for process {process}")
        
        
def parse_card(generator, tag, process, rundir="", nEvents=100, run=False):

    source_card, dest_card = "", ""
    if generator == "whizard":
        source_card = f"{os.getcwd()}/cards/{tag}/generator/{generator}/{process}.sin"
        dest_card = f"{rundir}/whizard.sin"
        
    if not os.path.exists(source_card):
        raise Exception(f"Whizard card {source_card} not found")
        
    return source_card
    seed = int(datetime.datetime.utcnow().strftime('%Y%m%d%H%M%S%f')[:-3])
    os.system(f"cp {source_card} {dest_card}")
    
    

    if run:
        if generator == "whizard":
            os.system(f"sed -i '1in_events = {nEvents}' {dest_card}")
            result = subprocess.run(["whizard", "whizard.sin"], cwd=rundir, text=True)
            print(result.stdout)
            
     
def get_file_ids(indir):

    files = glob.glob(f'{indir}/events_*')
    return [(os.path.basename(f)).split(".")[0].replace("events_", "") for f in files]
                
            
def prepare_job(jobId, generator, tag, process, submitDir, outDir, nEvents=100):

    card = parse_card(generator, tag, process)
    outFile = f'{outDir}/events_{jobId}.stdhep.gz'
    cp = copy_cmd()

    fOutName = f'job{jobId}.sh'
    fOutFullName = f'{submitDir}/{fOutName}'
    fOut = open(fOutFullName, 'w')
    fOut.write('#!/bin/bash\n')
    fOut.write('unset LD_LIBRARY_PATH\n')
    fOut.write('unset PYTHONHOME\n')
    fOut.write('unset PYTHONPATH\n')
    fOut.write(f'mkdir job{jobId}_{process}\n')
    fOut.write(f'cd job{jobId}_{process}\n')
    fOut.write(f'source {config.defaultstack}\n')
            
    fOut.write(f'{cp} {card} thecard.sin\n')
            
    fOut.write(f'echo "n_events = {nEvents}" > header.sin \n')
    fOut.write(f'echo "seed = {jobId}"  >> header.sin \n')
    fOut.write('cat header.sin thecard.sin > card.sin \n')

    fOut.write('whizard card.sin \n')
    fOut.write('status=$?\n')
    fOut.write('if [ $status -ne 0 ]; then\n')
    fOut.write('    echo "Error running Whizard"\n')
    fOut.write('    cd ..\n')
    fOut.write('    exit 1\n')
    fOut.write('fi\n')
    fOut.write('echo "Finished Whizard"\n')
    
    # gzip stdhep file
    fOut.write('gzip proc.stdhep \n')
    fOut.write('status=$?\n')
    fOut.write('if [ $status -ne 0 ]; then\n')
    fOut.write('    echo "Error gzipping proc.stdhep"\n')
    fOut.write('    cd ..\n')
    fOut.write('    exit 1\n')
    fOut.write('fi\n')
    fOut.write('echo "Finished gzipping stdhep"\n')
    
    # check filesize of gzipped stdhep file
    fOut.write(' filesize=$(stat --printf="%s" proc.stdhep.gz)\n')
    fOut.write('if [ $filesize -lt 4 ]; then\n')
    fOut.write('    echo "proc.stdhep smaller than 4 bytes"\n')
    fOut.write('    cd ..\n')
    fOut.write('    exit 1\n')
    fOut.write('fi\n')
    
    
    fOut.write(f'{cp} proc.stdhep.gz {outFile}\n')
    fOut.write('status=$?\n')
    fOut.write('if [ $status -ne 0 ]; then\n')
    fOut.write('    echo "Error copying stdhep.gz file"\n')
    fOut.write('    cd ..\n')
    fOut.write('    exit 1\n')
    fOut.write('fi\n')
    fOut.write('echo "stdhep.gz file copied"\n')

    fOut.write('cd ..\n')
    fOut.close()
    
    subprocess.getstatusoutput(f'chmod 777 {fOutFullName}')

    return fOutFullName
