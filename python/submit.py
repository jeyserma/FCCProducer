
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
parser.add_argument("--condor_queue", type=str, help="Condor priority", choices=["espresso", "microcentury", "longlunch", "workday", "tomorrow", "testmatch", "nextweek"], default="workday")
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

class FCCProducer:

    def __init__(self, process, campaign, detector, storagedir, args):
        self.process = process
        self.campaign = campaign
        self.detector = detector
        self.generator = process.split("_")[0]
        self.storagedir = storagedir
    
        self.cwd = os.getcwd()
        self.stack = config.stacks[campaign]

        self.process_card = f"{self.cwd}/cards/{self.campaign}/generator/{self.generator}/{self.process}.py"
        self.delphes_card = f"{self.cwd}/cards/{self.campaign}/delphes/card_{self.detector}.tcl"
        self.delphes_card_edm4hep = f"{self.cwd}/cards/{self.campaign}/delphes/edm4hep_{self.detector}.tcl"

        sys.path.insert(0, os.path.dirname(self.process_card))
        self.process_module = __import__(self.process)
        self.ext = ""
        for parm in self.process_module.parms:
            fmt = no2str(getattr(args, parm))
            self.ext += f"_{parm}{fmt}"
        self.process += self.ext
        if args.ext != "":
            self.process += f"_{args.ext}"

        self.submit_dir = f"{self.cwd}/submit/{self.campaign}/{self.detector}/{self.process}/"
        self.out_dir = f"{self.storagedir}/{self.campaign}/{self.detector}/{self.process}/"
        self.local_dir = f"{self.cwd}/local/{self.campaign}/{self.detector}/{self.process}/"
        
        self.condor_queue = args.condor_queue
        self.condor_priority = args.condor_priority
        self.args = args


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



    def parse_p8(self, fOut, rootFn, seed, nevents):
        pythia_card = self.process_module.cfg.format(seed=seed, nevents=nevents).replace("\"", "\"")
        parms = self.process_module.parms
        for parm in parms:
            if parm=="ecm":
                ecm = str(args.ecm)
                pythia_card = pythia_card.replace(f"<{parm}>", ecm)
        fOut.write(f"echo '{pythia_card}' > card.cmd\n")
        fOut.write(f'echo "Random:seed = {seed}" >> card.cmd\n')
        fOut.write(f'echo "Main:numberOfEvents = {nevents}" >> card.cmd\n')

        fOut.write(f"cp {self.delphes_card} card.tcl\n")
        fOut.write(f"cp {self.delphes_card_edm4hep} edm4hep_output_config.tcl\n")
        fOut.write("echo \"START DelphesPythia8_EDM4HEP\"\n")
        fOut.write(f"DelphesPythia8_EDM4HEP card.tcl edm4hep_output_config.tcl card.cmd {rootFn}\n")
        fOut.write("echo \"DONE DelphesPythia8_EDM4HEP\"\n")

    def parse_wz3p6(self, fOut, rootFn, seed, nevents):
        whizard_card = self.process_module.cfg.format(seed=seed, nevents=nevents).replace("\"", "\"")
        parms = self.process_module.parms
        for parm in parms:
            if parm=="ecm":
                ecm = str(args.ecm)
                whizard_card = whizard_card.replace(f"<{parm}>", ecm)
        fOut.write(f"echo '{whizard_card}' > card.sin\n")

        fOut.write("echo \"START Whizard\"\n")
        fOut.write("whizard card.sin \n")
        fOut.write("echo \"DONE Whizard\"\n")
        
        fOut.write('echo "START DelphesSTDHEP_EDM4HEP"\n')
        fOut.write(f"cp {self.delphes_card} card.tcl\n")
        fOut.write(f"cp {self.delphes_card_edm4hep} edm4hep_output_config.tcl\n")
        fOut.write(f"DelphesSTDHEP_EDM4HEP card.tcl edm4hep_output_config.tcl {rootFn} proc.stdhep\n")
        fOut.write("echo \"DONE DelphesSTDHEP_EDM4HEP\"\n")

    def parse_wz3p8(self, fOut, rootFn, seed, nevents):
        whizard_card = self.process_module.cfg.format(seed=seed, nevents=nevents).replace("\"", "\"")
        parms = self.process_module.parms
        for parm in parms:
            if parm=="ecm":
                ecm = str(args.ecm)
                whizard_card = whizard_card.replace(f"<{parm}>", ecm)
        pythia_card = self.process_module.cfg_pythia.format(nevents=nevents).replace("\"", "\"")
        fOut.write(f"echo '{pythia_card}' > card.cmd\n")
        fOut.write(f"echo '{whizard_card}' > card.sin\n")

        fOut.write("echo \"START Whizard\"\n")
        fOut.write("whizard card.sin \n")
        fOut.write("echo \"DONE Whizard\"\n")

        if self.args.skipDelphes:
            return

        fOut.write('echo "START DelphesSTDHEP_EDM4HEP"\n')
        fOut.write(f"cp {self.delphes_card} card.tcl\n")
        fOut.write(f"cp {self.delphes_card_edm4hep} edm4hep_output_config.tcl\n")
        fOut.write(f"DelphesSTDHEP_EDM4HEP card.tcl edm4hep_output_config.tcl {rootFn} proc.stdhep\n")
        fOut.write("echo \"DONE DelphesSTDHEP_EDM4HEP\"\n")

    def parse_yfsww(self, fOut, rootFn, seed, nevents):
        seed_ = str(seed).rjust(12)
        nevents_ = str(nevents).rjust(12)

        parms = self.process_module.parms
        yfsww_card = self.process_module.cfg.format(seed=seed_, nevents=nevents_).replace("\"", "\"")
        for parm in parms:
            if parm=="mw":
                mw = str(args.mw/1000.).rjust(12)
                yfsww_card = yfsww_card.replace(f"<{parm}>", mw)
            if parm=="ecm":
                ecm = str(args.ecm).rjust(12)
                yfsww_card = yfsww_card.replace(f"<{parm}>", ecm)
            if parm=="ww":
                ww = str(args.ww/1000.).rjust(12)
                yfsww_card = yfsww_card.replace(f"<{parm}>", ww)
        pythia_card = self.process_module.cfg_pythia.format(nevents=nevents).replace("\"", "\"")
        fOut.write(f"echo '{yfsww_card}' > yfsww.input\n")
        fOut.write(f"echo '{pythia_card}' > card.cmd\n")

        yfsww_dir = f"{self.cwd}/generator/YFSWW/"
        fOut.write("echo \"START YFSWW\"\n")
        fOut.write(f"cp {yfsww_dir}/yfsww . \n")
        fOut.write(f"cp {yfsww_dir}/data_DEFAULTS . \n")
        fOut.write("./yfsww \n")
        fOut.write("echo \"DONE YFSWW\"\n")

        if self.args.skipDelphes:
            return
        fOut.write('echo "START DelphesPythia8_EDM4HEP"\n')
        fOut.write(f"cp {self.delphes_card} card.tcl\n")
        fOut.write(f"cp {self.delphes_card_edm4hep} edm4hep_output_config.tcl\n")
        fOut.write(f"DelphesPythia8_EDM4HEP card.tcl edm4hep_output_config.tcl card.cmd {rootFn}\n")
        fOut.write("echo \"DONE DelphesPythia8_EDM4HEP\"\n")

    def parse_rsanc(self, fOut, rootFn, seed, nevents):
        seed_ = str(seed).rjust(12)
        nevents_ = str(nevents).rjust(12)

        parms = self.process_module.parms
        rsanc_card = self.process_module.cfg.format(seed=seed_, nevents=nevents_).replace("\"", "\"")
        for parm in parms:
            if parm=="ecm":
                ecm = str(args.ecm)
                rsanc_card = rsanc_card.replace(f"<{parm}>", ecm)

        pythia_card = self.process_module.cfg_pythia.format(nevents=nevents).replace("\"", "\"")
        fOut.write(f"echo '{rsanc_card}' > input.conf\n")
        fOut.write(f"echo '{pythia_card}' > card.cmd\n")

        rsanc_dir = f"{self.cwd}/generator/ReneSANCe/"
        fOut.write("echo \"START ReneSANCe\"\n")
        fOut.write(f"cp {rsanc_dir}/renesance . \n")
        fOut.write(f"cp -r {rsanc_dir}/share . \n")
        fOut.write(f"sed -i -e 's/N_EVENTS/{nevents}/g' share/renesance/schema/foam.schema \n")
        fOut.write(f"./renesance -f input.conf -s {seed} | tee rsanc.output \n")
        fOut.write("echo \"DONE ReneSANCe\"\n")

        if self.args.skipDelphes:
            return

        fOut.write('echo "START DelphesPythia8_EDM4HEP"\n')
        fOut.write(f"cp {self.delphes_card} card.tcl\n")
        fOut.write(f"cp {self.delphes_card_edm4hep} edm4hep_output_config.tcl\n")
        fOut.write(f"DelphesPythia8_EDM4HEP card.tcl edm4hep_output_config.tcl card.cmd {rootFn}\n")
        fOut.write("echo \"DONE DelphesPythia8_EDM4HEP\"\n")

    def parse_kkmcee(self, fOut, rootFn, seed, nevents):
        seed_ = str(seed).rjust(12)
        nevents_ = str(nevents).rjust(12)

        parms = self.process_module.parms
        kkmcee_card = self.process_module.cfg.format(seed=seed_, nevents=nevents_).replace("\"", "\"")
        for parm in parms:
            if parm=="ecm":
                ecm = str(args.ecm).rjust(12)
                kkmcee_card = kkmcee_card.replace(f"<{parm}>", ecm)

        pythia_card = self.process_module.cfg_pythia.format(nevents=nevents).replace("\"", "\"")
        fOut.write(f"echo '{kkmcee_card}' > kkmcee.input\n")
        fOut.write(f"echo '{pythia_card}' > card.cmd\n")

        kkmcee_dir = f"{self.cwd}/generator/KKMCee/"
        fOut.write("echo \"START KKMCee\"\n")
        fOut.write(f"cp -r {kkmcee_dir}/dizet-6.45.tar.gz . \n")
        fOut.write("tar -zxvf dizet-6.45.tar.gz \n")
        fOut.write("mv dizet-6.45 dizet \n")
        fOut.write(f"cp {kkmcee_dir}/KK2f_defaults . \n")
        fOut.write(f"cp {kkmcee_dir}/KKMCee . \n")
        fOut.write('./KKMCee | tee kkmcee.output \n')
        fOut.write("echo \"DONE KKMCee\"\n")

        if self.args.skipDelphes:
            return

        fOut.write('echo "START DelphesPythia8_EDM4HEP"\n')
        fOut.write(f"cp {self.delphes_card} card.tcl\n")
        fOut.write(f"cp {self.delphes_card_edm4hep} edm4hep_output_config.tcl\n")
        fOut.write(f"DelphesPythia8_EDM4HEP card.tcl edm4hep_output_config.tcl card.cmd {rootFn}\n")
        fOut.write("echo \"DONE DelphesPythia8_EDM4HEP\"\n")

def main():

    producer = FCCProducer(args.process, args.campaign, args.detector, args.storagedir, args)
    if args.submit:
        producer.generate_submit(njobs=args.njobs, nevents=args.nevents)
    else:
        producer.generate_local(run=True, nevents=args.nevents)



if __name__ == "__main__":
    main()