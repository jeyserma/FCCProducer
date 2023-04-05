source /cvmfs/sw.hsf.org/key4hep/setup.sh

export PYTHONPATH="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd ):$PYTHONPATH"
export PYTHONPATH="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )/python:$PYTHONPATH"

mkdir -p local
mkdir -p submit