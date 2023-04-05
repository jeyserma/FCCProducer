# FCCProducer
Currently supports Whizard and KKMC.

## Setup
Initialize the environment:

```shell
source ./setup.sh
```


## MC production
The cards are stored in the cards/tag/generator directory, for both Whizard and KKMC. For each final state and center-of-mass, a card must be defined. 

Detector simulation and reconstruction is done using Delphes, the corresponding cards are stored under the cards/tag/delphes directory.

The tag corresponds to a certain configuration (detector and accelerator parameters). This is in line with the official FCC Monte Carlo production campaign.

To produce events, execute either the following commands:

```shell
python python/run_KKMCee.py
python python/run_Whizard.py
```

The number of events and input configuration has to be defined in the python files.
