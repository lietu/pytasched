#!/usr/bin/env sh
#
# This file is for building the Python dependencies which frequently change
#

set -eu

# Set up working environment before everything else (it's quite spammy with -x)
. ~/.poetry/env

set -x

poetry install
