#!/usr/bin/env sh
#
# This file is for launching the application in the container
#

set -eu

# Set up working environment before everything else (it's quite spammy with -x)
. ~/.poetry/env

set -x

poetry run python -m pytasched
