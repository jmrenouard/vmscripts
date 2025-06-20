#!/bin/bash

export VMS_DIR="$HOME/GIT_REPOS/vmscripts/vms"
export SCRIPT_DIR="$HOME/GIT_REPOS/dbscripts"
export _DIR="$HOME/GIT_REPOS/dbscripts"

[ -z "$DEFAULT_PRIVATE_KEY" ] && export DEFAULT_PRIVATE_KEY="$VMS_DIR/id_rsa"

#export proxy_vms="proxy1,proxy2"
export proxy_vms="proxy1"
export db_vms="dbsrv1,dbsrv2,dbsrv3"
export app_vms="app1"
export docker_vms="docker0,docker1,docker2"
#export all_vms="app1,mgt1,proxy1,proxy2,dbsrv1,dbsrv2,dbsrv3"
export all_vms="$proxy_vms,$db_vms,$app_vms"

#slack vagrant linode vagrant
[ -f "${VMS_DIR}/../vagrant.sh" ] && source ${VMS_DIR}/../vagrant.sh
for module in is utils git network jupyter ansible ;do
    [ -f "${SCRIPT_DIR}/${module}.sh" ] && source ${SCRIPT_DIR}/${module}.sh
done

if [ -d "/usr/local/go/bin" ]; then
export PATH=$PATH:/usr/local/go/bin
fi
