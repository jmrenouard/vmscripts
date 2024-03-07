#!/bin/bash

mkdir -p $HOME/.conf
cp id_rsa $HOME/.conf
chmod 600  $HOME/.conf/id_rsa

mkdir -p $HOME/.ssh
cp id_rsa $HOME/.ssh/id_rsa_vms
chmod 600  $HOME/.ssh/id_rsa_vms
(
echo 'Host *'
echo "  IdentityFile $HOME/.ssh/id_rsa_vms
        User root
        #UserKnownHostsFile=/dev/null
        StrictHostKeyChecking = no
"
grep 192 Vagrantfile | sed -E 's/.vm.network "private_network", ip: "/ /g;s/"//g' | grep -Ev '.*#' |xargs -n 2 | perl -pe 's/(.+)\s+(.+)$/Host $1\n\tHostName $2/g'
)> $HOME/.ssh/config
chmod 600 $HOME/.ssh/config
cat $HOME/.ssh/config
