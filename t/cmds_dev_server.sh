#!/bin/sh
set -e
set -ux
scriptDir=$(basename $0)
repoDir=$( git rev-parse --show-toplevel )
cd ${repoDir}

# re-setup all links:
./setup.sh clean
# no files
#./setup.sh prepare
./setup.sh launch
./setup.sh verify
./setup.sh "kill"

