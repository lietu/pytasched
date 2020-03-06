#!/usr/bin/env sh
#
# This file is for installing the larger dependencies that rarely change such
# as OS packages, utilities and so on.
#

set -exu

# Set up user accounts
addgroup -g ${GID} -S ${GROUP}
adduser -u ${UID} -S ${USER} -G ${GROUP} -G wheel -D
# Allow su - user
sed -i -E "s@${USER}:(.*):/sbin/nologin@${USER}:\1:/bin/ash@" /etc/passwd

# Setting up dependencies
apk add --virtual build-dependencies \
  curl \
  gcc \
  g++ \
  make \
  musl-dev

# Installing some more clear deps
pip install --upgrade pip

# Ensure the WORKON_HOME exists, is empty and owned by ${USER}
if [[ ! -d "${WORKON_HOME}" ]]; then
  mkdir "${WORKON_HOME}"
fi
rm -rf "${WORKON_HOME:?}"/*
chown -R ${USER}:${GROUP} "${WORKON_HOME}"

# Install Poetry for ${USER}
su - ${USER} -c "curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python"
su - ${USER} -c '. ~/.poetry/env; poetry config virtualenvs.in-project false'
su - ${USER} -c ". ~/.poetry/env; poetry config virtualenvs.path ${WORKON_HOME}"

# Allow the next script to run as ${USER}
chown -R ${USER}:${GROUP} /src
