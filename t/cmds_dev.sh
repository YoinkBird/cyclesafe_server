#!/bin/sh
set -eux
scriptDir=$(basename $0)
repoDir=$( git rev-parse --show-toplevel )
cd ${repoDir}

# re-setup all links:
./setup.sh clean
# no files, but do need to seed with something
./setup.sh testprep
# run self-test code to simulate server post/get (including model hook)
python3 server_api_model.py -post 1
# run self-test code solely for model hook
#+ NOTE: runhook will always depend on -post 1 to generate certain files
#+ disabling while integrating new runhook
# python3 server_api_model.py -post 2

# visualise result
./setup.sh prepverif
