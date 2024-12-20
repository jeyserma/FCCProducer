
import sys, os, glob, shutil
import time
import argparse
import pathlib
import json
import logging
import config
import subprocess
import random

logging.basicConfig(format='%(levelname)s: %(message)s')
logger = logging.getLogger("fcclogger")
logger.setLevel(logging.INFO)


parser = argparse.ArgumentParser()
parser.add_argument("-s", "--submit", action='store_true', help="Submit to batch system")
parser.add_argument("-n", "--nevents", type=int, help="number of events", default=100)
parser.add_argument("-j", "--njobs", type=int, help="number of jobs", default=10)
parser.add_argument("-p", "--process", type=str, help="Process name", default="p8_ee_Z_ecm91p2")
parser.add_argument("-d", "--detector", type=str, help="Detector name", default="IDEA")
parser.add_argument("-c", "--campaign", type=str, help="Campaign name", default="winter2023")
parser.add_argument("-e", "--ext", type=str, help="Extension", default="")
parser.add_argument("--condor_queue", type=str, help="Condor priority", choices=["espresso", "microcentury", "longlunch", "workday", "tomorrow", "testmatch", "nextweek"], default="tomorrow")
parser.add_argument("--condor_priority", type=str, help="Condor priority", default="group_u_FCC.local_gen")
parser.add_argument("--storagedir", type=str, help="Base directory to save the samples", default="/eos/experiment/fcc/users/j/jaeyserm/sampleProduction2024")
parser.add_argument("--skipDelphes", action='store_true', help="Skip Delphes step")


# yfsww parms
parser.add_argument("--ecm", type=float, help="Center-of-mass energy (GeV)", default=163)
parser.add_argument("--mw", type=float, help="W boson mass (MeV)", default=80379) # pdg22 80.377 pm 0.012
parser.add_argument("--ww", type=float, help="W boson width (MeV)", default=2085) # pdg22 2.085 pm 0.042
args = parser.parse_args()

def no2str(no):
    if no%1==0:
        return str(int(no))
    else:
        return str(no).replace(".", "p")

class DDSimProducer:

    def __init__(self, stack, geo_file, input_dir, output_dir, submit_dir):
        self.stack = stack
        self.geo_file = geo_file
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.submit_dir = submit_dir
        
        #self.condor_queue = "espresso"
        self.condor_priority = "group_u_FCC.local_gen"

        self.cwd = os.getcwd()

    def generate(self, base_dir, save_dir, seed, nevents):

        submitFn = f"{base_dir}/submit_{seed}.sh"
        rootFn = f"{save_dir}/events_{seed}.root"
        if os.path.exists(submitFn):
            logger.warning(f"File {submitFn} already exists")
            return -1
        if os.path.exists(f"{save_dir}/{rootFn}"):
            logger.warning(f"File {rootFn} already exists")
            return -1

        fOut = open(submitFn, "w")
        fOut.write("#!/bin/bash\n")
        fOut.write("SECONDS=0\n")
        fOut.write("unset LD_LIBRARY_PATH\n")
        fOut.write("unset PYTHONHOME\n")
        fOut.write("unset PYTHONPATH\n")
        fOut.write(f"mkdir job_{seed}\n")
        fOut.write(f"cd job_{seed}\n")
        fOut.write(f"source {self.stack}\n")

        # parse the generator-dependent configs
        if self.generator == "p8":
            self.parse_p8(fOut, rootFn, seed, nevents)
        elif self.generator == "wz3p6":
            self.parse_wz3p6(fOut, rootFn, seed, nevents)
        elif self.generator == "wz3p8":
            self.parse_wz3p8(fOut, rootFn, seed, nevents)
        elif self.generator == "yfsww":
            self.parse_yfsww(fOut, rootFn, seed, nevents)
        elif self.generator == "rsanc":
            self.parse_rsanc(fOut, rootFn, seed, nevents)
        elif self.generator == "kkmcee":
            self.parse_kkmcee(fOut, rootFn, seed, nevents)

        fOut.write("duration=$SECONDS\n")
        fOut.write("echo \"Duration: $(($duration))\"\n")
        fOut.write(f"echo \"Events: {nevents}\"\n")

        subprocess.getstatusoutput(f"chmod 777 {submitFn}")
        return submitFn

    def generate_submit(self, njobs, nevents):
        if not os.path.exists(self.submit_dir):
            os.makedirs(self.submit_dir)
        if not os.path.exists(self.out_dir):
            os.makedirs(self.out_dir)

        #nevents = f"{self.out_dir}/nevents.txt"
        #if os.path.exists(nevents):
        #    ii = input("Events file exist, take number of events from that file? (y/n)")
        #    #if ii=="y":
        #    #    nevents 

        execs = []
        njob = 0
        while njob < njobs:
            seed = f"{random.randint(10000,32768)}" # seed depends on generator?
            sh = self.generate(self.submit_dir, self.out_dir, seed, nevents)
            if sh == -1:
                continue
            njob += 1
            logger.info(f"Prepare job {njob} with seed {seed}")
            execs.append(sh)
            
        condorFn = f'{self.submit_dir}/condor.cfg'
        fOut = open(condorFn, 'w')

        fOut.write(f'executable     = $(filename)\n')
        fOut.write(f'Log            = {self.submit_dir}/condor_job.$(ClusterId).$(ProcId).log\n')
        fOut.write(f'Output         = {self.submit_dir}/condor_job.$(ClusterId).$(ProcId).out\n')
        fOut.write(f'Error          = {self.submit_dir}/condor_job.$(ClusterId).$(ProcId).error\n')
        fOut.write(f'getenv         = True\n')
        fOut.write(f'environment    = "LS_SUBCWD={self.submit_dir}"\n')
        fOut.write(f'requirements   = ( (OpSysAndVer =?= "CentOS7") && (Machine =!= LastRemoteHost) && (TARGET.has_avx2 =?= True) )\n')
   
        fOut.write(f'on_exit_remove = (ExitBySignal == False) && (ExitCode == 0)\n')
        fOut.write(f'max_retries    = 3\n')
        fOut.write(f'+JobFlavour    = "{self.condor_queue}"\n')
        fOut.write(f'+AccountingGroup = "{self.condor_priority}"\n')
        
        execsStr = ' '.join(execs) 
        fOut.write(f'queue filename matching files {execsStr}\n')
        fOut.close()
        
        subprocess.getstatusoutput(f'chmod 777 {condorFn}')
        os.system(f"condor_submit {condorFn}")
    
        # save number of events per job to text file
        os.system(f"echo {nevents} > {self.out_dir}/nevents.txt")

    def generate_local(self, nevents=100, seed=32768, run=False):
        if os.path.exists(self.local_dir):
            logger.error(f"Please remove test dir {self.local_dir}")
            sys.exit(1)
        os.makedirs(self.local_dir)
        logger.info(f"Generate events locally ({self.local_dir})")
        sh = self.generate(self.local_dir, self.local_dir, seed, nevents)
        if run:
            os.system(f"cd {self.local_dir} && {sh} | tee output.txt")
        logger.info(f"Done, saved to {self.local_dir}")

        # extract cross-section
        logger.info(f"Cross-section and meta info:")
        if self.generator == "yfsww":
            cmd = f"cat {self.local_dir}/job_{seed}/yfsww.output | grep 'MC Best, XPAR, YFSWW3'"
            os.system(cmd)
        elif self.generator == "kkmcee":
            cmd = f"cat {self.local_dir}/job_{seed}/kkmcee.output | grep 'xSecPb, xErrP'"
            os.system(cmd)
        elif self.generator == "rsanc":
            cmd = f"cat {self.local_dir}/job_{seed}/rsanc.output | grep 'MCresult (Tot)'"
            os.system(cmd)


    def parse_wz3p6_gen(self, sinFile, nJobs=100):
        self.condor_queue = "workday"
        sinFile = os.path.abspath(sinFile)
        if not os.path.exists(self.submit_dir):
            os.makedirs(self.submit_dir)
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

        execs = []
        for iJob in range(0, nJobs):
            fOutName = f"{self.output_dir}/proc_{iJob}.stdhep"
            submitFn = f"{self.submit_dir}/submit_{iJob}.sh"
            fOut = open(submitFn, "w")
            fOut.write("#!/bin/bash\n")
            fOut.write("SECONDS=0\n")
            fOut.write("unset LD_LIBRARY_PATH\n")
            fOut.write("unset PYTHONHOME\n")
            fOut.write("unset PYTHONPATH\n")
            fOut.write(f"source {self.stack}\n")
            fOut.write(f"cp {sinFile} card.sin \n")
            fOut.write(f"sed -i 's/$SEED/{iJob}/g' card.sin\n")
            fOut.write("echo \"START Whizard\"\n")
            fOut.write("whizard card.sin \n")
            fOut.write("echo \"DONE Whizard\"\n")
            fOut.write(f"cp proc.stdhep {fOutName}\n")
            execs.append(submitFn)

        # condor submission
        condorFn = f'{self.submit_dir}/condor.cfg'
        fOut = open(condorFn, 'w')

        fOut.write(f'executable     = $(filename)\n')
        fOut.write(f'Log            = {self.submit_dir}/condor_job.$(ClusterId).$(ProcId).log\n')
        fOut.write(f'Output         = {self.submit_dir}/condor_job.$(ClusterId).$(ProcId).out\n')
        fOut.write(f'Error          = {self.submit_dir}/condor_job.$(ClusterId).$(ProcId).error\n')
        fOut.write(f'getenv         = False\n')
        fOut.write(f'environment    = "LS_SUBCWD={self.submit_dir}"\n')
        fOut.write(f'requirements   = ( (OpSysAndVer =?= "AlmaLinux9") && (Machine =!= LastRemoteHost))\n') # && (TARGET.has_avx2 =?= True)
   
        fOut.write(f'on_exit_remove = (ExitBySignal == False) && (ExitCode == 0)\n')
        fOut.write(f'max_retries    = 3\n')
        fOut.write(f'+JobFlavour    = "{self.condor_queue}"\n')
        fOut.write(f'+AccountingGroup = "{self.condor_priority}"\n')
        
        execsStr = ' '.join(execs) 
        fOut.write(f'queue filename matching files {execsStr}\n')
        fOut.close()
        
        subprocess.getstatusoutput(f'chmod 777 {condorFn}')
        os.system(f"condor_submit {condorFn}")


    def parse_wz3p6_sim(self):
        self.condor_queue = "tomorrow"
        if not os.path.exists(self.submit_dir):
            os.makedirs(self.submit_dir)
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

        # find all input files
        pair_files = []
        for root, dirs, files in os.walk(self.input_dir):
            for file in files:
                if file.endswith(".stdhep"):
                    full_path = os.path.join(root, file)
                    pair_files.append(full_path)

        # create job file per file
        execs = []
        for iJob, fIn in enumerate(pair_files):
        
            fOutName = self.output_dir  + "/" + os.path.basename(fIn).replace(".stdhep", f"_{iJob}") # no .root for reconstruction step (is appended automatically)
            #cmd = f"ddsim --compactFile  --inputFiles {fIn} --outputFile {fOut} -N -1 --crossingAngleBoost 0.015" #  

            submitFn = f"{self.submit_dir}/submit_{iJob}.sh"
            fOut = open(submitFn, "w")
            fOut.write("#!/bin/bash\n")
            fOut.write("SECONDS=0\n")
            fOut.write("unset LD_LIBRARY_PATH\n")
            fOut.write("unset PYTHONHOME\n")
            fOut.write("unset PYTHONPATH\n")
            #fOut.write(f"mkdir job_{seed}\n")
            #fOut.write(f"cd job_{seed}\n")
            fOut.write(f"source {self.stack}\n")
            fOut.write(f"git clone https://github.com/key4hep/CLDConfig.git -b r2024-04-12\n")
            fOut.write(f"cd CLDConfig/CLDConfig\n")
            fOut.write("echo \"START DDSIM\"\n")
            fOut.write(f"ddsim --compactFile {self.geo_file} --outputFile output.sim.root --inputFiles {fIn} --numberOfEvents -1 --crossingAngleBoost 0.015\n")
            fOut.write(f"k4run CLDReconstruction.py --inputFiles output.sim.root --outputBasename {fOutName} --num-events -1\n")
            fOut.write("echo \"DONE DDSIM\"\n")
            
            #if "CLD" in self.geo_file:
            #    fOut.write(f"wget https://raw.githubusercontent.com/key4hep/CLDConfig/main/CLDConfig/cld_steer.py\n")
            #    cmd += " --steeringFile cld_steer.py"
            
            #fOut.write(f"{cmd} \n")
            fOut.write("echo \"DONE DDSIM\"\n")
            execs.append(submitFn)

        # condor submission
        condorFn = f'{self.submit_dir}/condor.cfg'
        fOut = open(condorFn, 'w')

        fOut.write(f'executable     = $(filename)\n')
        fOut.write(f'Log            = {self.submit_dir}/condor_job.$(ClusterId).$(ProcId).log\n')
        fOut.write(f'Output         = {self.submit_dir}/condor_job.$(ClusterId).$(ProcId).out\n')
        fOut.write(f'Error          = {self.submit_dir}/condor_job.$(ClusterId).$(ProcId).error\n')
        fOut.write(f'getenv         = False\n')
        fOut.write(f'environment    = "LS_SUBCWD={self.submit_dir}"\n')
        fOut.write(f'requirements   = ( (OpSysAndVer =?= "AlmaLinux9") && (Machine =!= LastRemoteHost))\n') # && (TARGET.has_avx2 =?= True)
        #fOut.write(f'requirements   = ((Machine =!= LastRemoteHost))\n')
   
        fOut.write(f'on_exit_remove = (ExitBySignal == False) && (ExitCode == 0)\n')
        fOut.write(f'max_retries    = 3\n')
        fOut.write(f'+JobFlavour    = "{self.condor_queue}"\n')
        fOut.write(f'+AccountingGroup = "{self.condor_priority}"\n')
        
        execsStr = ' '.join(execs) 
        fOut.write(f'queue filename matching files {execsStr}\n')
        fOut.close()
        
        subprocess.getstatusoutput(f'chmod 777 {condorFn}')
        os.system(f"condor_submit {condorFn}")



    def parse_gp(self):
        self.condor_queue = "longlunch"
        if not os.path.exists(self.submit_dir):
            os.makedirs(self.submit_dir)
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

        # find all input files
        pair_files = []
        for root, dirs, files in os.walk(self.input_dir):
            for file in files:
                if file.endswith(".pairs"):
                    full_path = os.path.join(root, file)
                    pair_files.append(full_path)

        # create job file per file
        execs = []
        for iJob, fIn in enumerate(pair_files):
        
            fOut = self.output_dir  + "/" + os.path.basename(fIn).replace(".pairs", f"_{iJob}.root")
            cmd = f"ddsim --compactFile {self.geo_file} --inputFiles {fIn} --outputFile {fOut} -N -1 --crossingAngleBoost 0.015" #  

            submitFn = f"{self.submit_dir}/submit_{iJob}.sh"
            fOut = open(submitFn, "w")
            fOut.write("#!/bin/bash\n")
            fOut.write("SECONDS=0\n")
            fOut.write("unset LD_LIBRARY_PATH\n")
            fOut.write("unset PYTHONHOME\n")
            fOut.write("unset PYTHONPATH\n")
            #fOut.write(f"mkdir job_{seed}\n")
            #fOut.write(f"cd job_{seed}\n")
            fOut.write(f"source {self.stack}\n")
            fOut.write(f"uname -r\n")
            fOut.write(f"which python\n")
            fOut.write("echo \"START DDSIM\"\n")
            fOut.write(f"{cmd} \n")
            fOut.write("echo \"DONE DDSIM\"\n")
            execs.append(submitFn)

        # condor submission
        condorFn = f'{self.submit_dir}/condor.cfg'
        fOut = open(condorFn, 'w')

        fOut.write(f'executable     = $(filename)\n')
        fOut.write(f'Log            = {self.submit_dir}/condor_job.$(ClusterId).$(ProcId).log\n')
        fOut.write(f'Output         = {self.submit_dir}/condor_job.$(ClusterId).$(ProcId).out\n')
        fOut.write(f'Error          = {self.submit_dir}/condor_job.$(ClusterId).$(ProcId).error\n')
        fOut.write(f'getenv         = False\n')
        fOut.write(f'environment    = "LS_SUBCWD={self.submit_dir}"\n')
        fOut.write(f'requirements   = ( (OpSysAndVer =?= "AlmaLinux9") && (Machine =!= LastRemoteHost))\n') # && (TARGET.has_avx2 =?= True)
        #fOut.write(f'requirements   = ((Machine =!= LastRemoteHost))\n')
   
        fOut.write(f'on_exit_remove = (ExitBySignal == False) && (ExitCode == 0)\n')
        fOut.write(f'max_retries    = 3\n')
        fOut.write(f'+JobFlavour    = "{self.condor_queue}"\n')
        fOut.write(f'+AccountingGroup = "{self.condor_priority}"\n')
        
        execsStr = ' '.join(execs) 
        fOut.write(f'queue filename matching files {execsStr}\n')
        fOut.close()
        
        subprocess.getstatusoutput(f'chmod 777 {condorFn}')
        os.system(f"condor_submit {condorFn}")


def main():

    #input_dir = ""
    #stack = "/cvmfs/sw.hsf.org/key4hep/setup.sh -r 2024-04-12"
    #geo_file = ""

    #output_dir = "/eos/experiment/fcc/users/j/jaeyserm/fullSim/gp_output/wzp6_ee_eeH_ecm240_stdhep/"
    #submit_dir = "wzp6_ee_eeH_ecm240_stdhep"
    #producer = DDSimProducer(stack, geo_file, input_dir, output_dir, submit_dir)
    #producer.parse_wz3p6_gen("cards/fullSim/wzp6_ee_eeH_ecm240.sin", 2000)

    #output_dir = "/eos/experiment/fcc/users/j/jaeyserm/fullSim/gp_output/wzp6_ee_eeH_mH-higher-50MeV_ecm240_stdhep/"
    #submit_dir = "wzp6_ee_eeH_mH-higher-50MeV_ecm240_stdhep"
    #producer = DDSimProducer(stack, geo_file, input_dir, output_dir, submit_dir)
    #producer.parse_wz3p6_gen("cards/fullSim/wzp6_ee_eeH_mH-higher-50MeV_ecm240.sin", 2000)


    #output_dir = "/eos/experiment/fcc/users/j/jaeyserm/fullSim/gp_output/wzp6_ee_eeH_mH-lower-50MeV_ecm240_stdhep/"
    #submit_dir = "wzp6_ee_eeH_mH-lower-50MeV_ecm240_stdhep"
    #producer = DDSimProducer(stack, geo_file, input_dir, output_dir, submit_dir)
    #producer.parse_wz3p6_gen("cards/fullSim/wzp6_ee_eeH_mH-lower-50MeV_ecm240.sin", 2000)

    # source /cvmfs/sw.hsf.org/key4hep/setup.sh -r 2024-04-12
    # ddsim --compactFile $K4GEO/FCCee/IDEA/compact/IDEA_o1_v03/IDEA_o1_v03.xml --inputFiles /eos/experiment/fcc/users/b/brfranco/background_files/guineaPig_andrea_June2024_v23/data999/pairs.pairs --outputFile PATH_TO_OUTPUT.root -N -1 --crossingAngleBoost 0.015




    # old FCC lattice (v23 is the new FCC lattice)
    #input_dir = "/eos/experiment/fcc/users/b/brfranco/background_files/guineaPig_andrea_Apr2024"
    #output_dir = "/eos/experiment/fcc/users/j/jaeyserm/guineapig/gp_output/CLD_guineaPig_andrea_Apr2024"
    #submit_dir = "submit/CLD_guineaPig_andrea_Apr2024"
    #producer = DDSimProducer(stack, geo_file, input_dir, output_dir, submit_dir)
    #producer.parse_gp()


    #######################
    ## IDEA
    #######################
    stack = "/cvmfs/sw-nightlies.hsf.org/key4hep/setup.sh -r 2024-10-01"
    geo_file = "$K4GEO/FCCee/IDEA/compact/IDEA_o1_v03/IDEA_o1_v03.xml"

    #input_dir = "/eos/experiment/fcc/users/b/brfranco/background_files/guineaPig_andrea_June2024_v23"
    #output_dir = "/eos/experiment/fcc/users/j/jaeyserm/VTXStudiesFullSim/IDEA_guineaPig_andrea_June2024_v23"
    #submit_dir = "submit/IDEA_guineaPig_andrea_June2024_v23"
    #producer = DDSimProducer(stack, geo_file, input_dir, output_dir, submit_dir)
    #producer.parse_gp()

    #input_dir = "/eos/experiment/fcc/users/b/brfranco/background_files/guineaPig_andrea_June2024_v23_vtx000"
    #output_dir = "/eos/experiment/fcc/users/j/jaeyserm/VTXStudiesFullSim/IDEA_guineaPig_andrea_June2024_v23_vtx000"
    #submit_dir = "submit/IDEA_guineaPig_andrea_June2024_v23_vtx000"
    #producer = DDSimProducer(stack, geo_file, input_dir, output_dir, submit_dir)
    #producer.parse_gp()

    #input_dir = "/eos/experiment/fcc/users/b/brfranco/background_files/guineaPig_andrea_June2024_v23"
    #output_dir = "/eos/experiment/fcc/users/j/jaeyserm/VTXStudiesFullSim/IDEA_guineaPig_andrea_June2024_v23_noXing"
    #submit_dir = "submit/IDEA_guineaPig_andrea_June2024_v23_noXing"
    #producer = DDSimProducer(stack, geo_file, input_dir, output_dir, submit_dir)
    #producer.parse_gp()


    #input_dir = "/eos/experiment/fcc/users/j/jaeyserm/fullSim/gp_output/wz3p6_ee_qq_ecm91p2/"
    #output_dir = "/eos/experiment/fcc/users/j/jaeyserm/VTXStudiesFullSim/IDEA_wz3p6_ee_qq_ecm91p2/"
    #submit_dir = "submit/IDEA_wz3p6_ee_qq_ecm91p2"
    #producer = DDSimProducer(stack, geo_file, input_dir, output_dir, submit_dir)
    #producer.parse_wz3p6_sim()

    #input_dir = "/eos/experiment/fcc/users/j/jaeyserm/fullSim/gp_output/wz3p6_ee_qq_ecm91p2/"
    #output_dir = "/eos/experiment/fcc/users/j/jaeyserm/VTXStudiesFullSim/IDEA_wz3p6_ee_qq_ecm91p2_noXing/"
    #submit_dir = "submit/IDEA_wz3p6_ee_qq_ecm91p2_noXing"
    #producer = DDSimProducer(stack, geo_file, input_dir, output_dir, submit_dir)
    #producer.parse_wz3p6_sim()

    #######################
    ## CLD
    #######################
    stack = "/cvmfs/sw.hsf.org/key4hep/setup.sh -r 2024-04-12"
    geo_file = "$K4GEO/FCCee/CLD/compact/CLD_o2_v05/CLD_o2_v05.xml"

    #input_dir = "/eos/experiment/fcc/users/j/jaeyserm/fullSim/gp_output/wzp6_ee_eeH_ecm240_stdhep/"
    #output_dir = "/eos/experiment/fcc/users/j/jaeyserm/fullSim/gp_output/CLD_wzp6_ee_eeH_ecm240/"
    #submit_dir = "submit/CLD_wzp6_ee_eeH_ecm240"
    #producer = DDSimProducer(stack, geo_file, input_dir, output_dir, submit_dir)
    #producer.parse_wz3p6_sim()

    #input_dir = "/eos/experiment/fcc/users/j/jaeyserm/fullSim/gp_output/wzp6_ee_eeH_mH-higher-50MeV_ecm240_stdhep/"
    #output_dir = "/eos/experiment/fcc/users/j/jaeyserm/fullSim/gp_output/CLD_wzp6_ee_eeH_mH-higher-50MeV_ecm240/"
    #submit_dir = "submit/CLD_wzp6_ee_eeH_mH-higher-50MeV_ecm240"
    #producer = DDSimProducer(stack, geo_file, input_dir, output_dir, submit_dir)
    #producer.parse_wz3p6_sim()

    input_dir = "/eos/experiment/fcc/users/j/jaeyserm/fullSim/gp_output/wzp6_ee_eeH_mH-lower-50MeV_ecm240_stdhep/"
    output_dir = "/eos/cms/store/cmst3/group/wmass/jaeyserm/fccee/CLD_wzp6_ee_eeH_mH-lower-50MeV_ecm240/"
    submit_dir = "submit/CLD_wzp6_ee_eeH_mH-lower-50MeV_ecm240"
    producer = DDSimProducer(stack, geo_file, input_dir, output_dir, submit_dir)
    producer.parse_wz3p6_sim()

    #input_dir = "/eos/experiment/fcc/users/b/brfranco/background_files/guineaPig_andrea_June2024_v23"
    #output_dir = "/eos/experiment/fcc/users/j/jaeyserm/VTXStudiesFullSim/CLD_guineaPig_andrea_June2024_v23"
    #submit_dir = "submit/CLD_guineaPig_andrea_June2024_v23"
    #producer = DDSimProducer(stack, geo_file, input_dir, output_dir, submit_dir)
    #producer.parse_gp()

    #input_dir = "/eos/experiment/fcc/users/b/brfranco/background_files/guineaPig_andrea_June2024_v23_vtx000"
    #output_dir = "/eos/experiment/fcc/users/j/jaeyserm/VTXStudiesFullSim/CLD_guineaPig_andrea_June2024_v23_vtx000"
    #submit_dir = "submit/CLD_guineaPig_andrea_June2024_v23_vtx000"
    #producer = DDSimProducer(stack, geo_file, input_dir, output_dir, submit_dir)
    #producer.parse_gp()

    #input_dir = "/eos/experiment/fcc/users/b/brfranco/background_files/guineaPig_andrea_June2024_v23"
    #output_dir = "/eos/experiment/fcc/users/j/jaeyserm/VTXStudiesFullSim/CLD_guineaPig_andrea_June2024_v23_noXing"
    #submit_dir = "submit/CLD_guineaPig_andrea_June2024_v23_noXing"
    #producer = DDSimProducer(stack, geo_file, input_dir, output_dir, submit_dir)
    #producer.parse_gp()

    #input_dir = "/eos/experiment/fcc/users/j/jaeyserm/fullSim/gp_output/wz3p6_ee_qq_ecm91p2/"
    #output_dir = "/eos/experiment/fcc/users/j/jaeyserm/VTXStudiesFullSim/CLD_wz3p6_ee_qq_ecm91p2/"
    #submit_dir = "submit/CLD_wz3p6_ee_qq_ecm91p2"
    #producer = DDSimProducer(stack, geo_file, input_dir, output_dir, submit_dir)
    #producer.parse_wz3p6_sim()

    #input_dir = "/eos/experiment/fcc/users/j/jaeyserm/fullSim/gp_output/wz3p6_ee_qq_ecm91p2/"
    #output_dir = "/eos/experiment/fcc/users/j/jaeyserm/VTXStudiesFullSim/CLD_wz3p6_ee_qq_ecm91p2_noXing/"
    #submit_dir = "submit/CLD_wz3p6_ee_qq_ecm91p2_noXing"
    #producer = DDSimProducer(stack, geo_file, input_dir, output_dir, submit_dir)
    #producer.parse_wz3p6_sim()




if __name__ == "__main__":
    main()
