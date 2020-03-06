#!/usr/bin/env sh
#
# This step is for initializing the runtime environment
#

set -exu

# Create runtime user
addgroup -g ${GID} -S ${GROUP}
adduser -u ${UID} -S ${USER} -G ${GROUP} -D

sed -i -E 's@'${USER}':(.*):/sbin/nologin@'${USER}':\1:/bin/ash@' /etc/passwd
chmod +x /home/${USER}/.poetry/bin/*

# Allow ${USER} to edit contents while installing things
chown -R ${USER}:${GROUP} .

# Poetry configuration
su ${USER} -c '. ~/.poetry/env; poetry config virtualenvs.in-project false'
su ${USER} -c ". ~/.poetry/env; poetry config virtualenvs.path ${WORKON_HOME}"

# Activate settings from Docker ENV
cp settings_docker.py settings_local.py

# Ensure user cannot edit the filesystem contents
chown -R root:root .
