# Scripts, Functions, and Targets Reference

Technical reference verified directly against the scripts, Makefiles, Python generators, and JSON/YAML files in **vmscripts**.

## Root Environment & Workstation Scripts

| File | Language | Key Exports / Purpose | Notes |
| :--- | :--- | :--- | :--- |
| `profile` | Bash | Exports `VMS_DIR`, `SCRIPT_DIR`, `DEFAULT_PRIVATE_KEY`, `$all_vms`; sources `vagrant.sh` | Hardcodes `$HOME/GIT_REPOS/vmscripts/vms` and `$HOME/GIT_REPOS/dbscripts` |
| `vagrant.sh` | Bash | `vlist`, `vinfo`, `vdelete`, `vstart`, `vstart_noprov`, `vstop`, `vgetPrivateIp`, `vgetLogicalNames`, `vgetLogicalGroups`, `vgenInventory`, `vgenAlias`, `vgenAliasU`, `vssh_get_host_pattern_list`, `vssh_get_host_list`, `vssh_exec`, `vssh_cmd`, `vssh_copy`, `vsetupTempAnsible`, `vsetupVMs`, `vupdateScript`, `local_updateScript`, `winalias` | Uses `$VMS_DIR/Vagrantfile` and `rsync` + `ssh` as `root` |
| `docker.sh` | Bash | Aliases `dcu`, `dcub`, `dcs`, `dcd`, `dcr`, `dcl`, `dex`, `dps`, `dsa`, `dpsa`, `drm`, `drme`, `drma`, `drmi`, `dimg`, `dvlm`, `dlog`, `dlogf`, `dstart`, `dstop`, `drun`, `drunp`; functions `dfrom`, `dbash` | Safe to source directly |
| `linode.sh` | Bash | `llist`, `lcreate`, `lchangeHostname`, `lssh`, `lgetLinodeId`, `lgetLinodePublicIp`, `lgetLinodePrivateIp`, `lchangepasswd`, `ldelete`, `lgenInventory`, `lgenAnsibleConfig`, `lgenHosts`, `lcleanHosts`, `lgenAlias`, `lsetupHosts`, `lcopy`, `lupdateScript`, `lexec` | Wraps `linode-cli` / `linode-cli.exe` |
| `installSoft.sh` | POSIX Shell | RHEL/Fedora `dnf` installer (`check` lists RPMs) | Calls `exit 0` at `L38` before `init_vagrant.sh` / `start.sh` |
| `installSoft2.sh` | POSIX Shell | Extended RHEL/Fedora `dnf` installer (`check` mode supported) | Calls `exit 0` at `L35` before disk resize / `vms/` calls |
| `installSoft_ubuntu.sh` | Bash | Modular Ubuntu workstation bootstrap (`initsoft`, `initvms`, `initconf`, `initpy`, `initgo`, `initkube`) | Installs VS Code, VirtualBox, Vagrant, Docker CE, Python/Go/Kubernetes tools |
| `genVirtualBox.py` | Python | Empty file (`0` bytes) | Placeholder |

## `vms/` VirtualBox & Vagrant Utilities

| Script | Language | Behavior |
| :--- | :--- | :--- |
| `vms/init_vagrant.sh` | Bash | Installs `vagrant-vbguest`, `vagrant-hostmanager`, `vagrant-persistent-storage`; pass `check` to run `vagrant plugin list` |
| `vms/start.sh` / `start_noprov.sh` | Bash | Runs `vagrant up --provider=virtualbox --provision` / `--no-provision` |
| `vms/up.sh` | POSIX Shell | Starts `mariadb1 mariadb2 mariadb3 mariadb4 haproxy1` with `timeout 30s` |
| `vms/stop.sh` / `destroy.sh` | Bash | Halts or destroys VMs; `destroy.sh` also removes `*_data.vdi` disk files |
| `vms/status.sh` / `info.sh` | Bash | Displays running status (`grep virtualbox`), `ssh-config`, ping, IPs, and `/etc/hosts` |
| `vms/genSshConfig.sh` | Bash | Copies `id_rsa` to `~/.conf` and `~/.ssh/id_rsa_vms`; appends `192.*` Vagrant hosts to `~/.ssh/config` |
| `vms/config.py` / `mygenconf.py` / `mygenscript.py` | Python | `key=value` CLI parameter overrides (`output=`, `vm_number=` in `mygenconf.py` only, `vm_name_prefix=`, `vm_ram=`, `vm_vcpu=`); outputs `Vagrantfile`, `inventory`, `putty_<vm>.bat` (`mygenscript.py` requires the integer default `vm_number=5` from `config.py`) |
| `vms/package.py` | Python | Builds `ansible_vagrant.zip` excluding `.vagrant`, `__pycache__`, `data/*` |

## `vm-vagrant/` Jinja2 & JSON Configuration (`vm-vagrant/Makefile`)

`vm-vagrant/server.json` defines `InstallType`, `PrivateKey`, `Rsa_PrivateKey`, `SshUser`, `Group`, `LabName`, `NetInter*`, and `Vms.<name>` (`distro`, `prefix`, `provision_script`, `ip_private`, `ip_private2`, `public_dhcp_ip`, `nbcpu`, `ram`, `enabled`).

| Target | Outputs / Effect | Notes |
| :--- | :--- | :--- |
| `generate_keys` | Creates `./id_rsa_vm` and `privatekey.ppk` via `ssh-keygen` and `puttygen` | Removes prior `id_rsa*` and `privatekey.ppk` |
| `generate_vagrantfile` | Renders `templates/Vagrantfile.j2` -> `Vagrantfile` via `j2` | Only VMs with `enabled == 1` are emitted |
| `generate_conf_ansible` | Renders `templates/ansible.cfg.j2` -> `ansible.cfg` and `templates/inventory.j2` -> `inventory` | Creates `log/` and `cache/` directories |
| `generate_puttyreg` / `generate_bashrc` | Renders `puttyreg.reg` and `bashrc` | Includes `j2` JSON rendering |
| `generate` | Runs `generate_keys generate_puttyreg generate_conf_ansible generate_bashrc generate_vagrantfile` | Complete config regeneration pipeline |
| `up` / `pup` / `status` / `halt` / `destroy` / `cleanup` | Runs Vagrant lifecycle (`pup` brings up `app1 loadb1 node1 node2 node3`) | `cleanup` deletes generated files and `.vagrant` |
| `debug` | Prints OS and vagrant executable check | Note: `L18` contains an unclosed `$(shell ...` parenthesis |

## `docker/` Targets & Ports (`docker/Makefile`)

| Target | Container / Image | Host Port(s) | Companion Stop / Volume Cleanup |
| :--- | :--- | :--- | :--- |
| `start_mysql` | `mysql:latest` (`mysql`) | `3306:3306` | `stop_mysql` / `cleanup_mysql` |
| `start_mysql57` | `mysql:5.7` (`mysql57`) | `3309:3306` | `stop_mysql57` / `cleanup_mysql57` |
| `start_mariadb` | `mariadb:latest` (`mariadb`) | `3307:3306` | `stop_mariadb` / `cleanup_mariadb` |
| `start_mariadb106` | `mariadb:10.6` (`mariadb106`) | `3308:3306` | `stop_mariadb106` / `cleanup_mariadb106` |
| `start_cassandra` | `cassandra:latest` (`cassandra`) | `19042:9042`, `17199:7199` | `stop_cassandra` / `cleanup_cassandra` |
| `start_cassandra311` | `cassandra:3.11` (`cassandra311`) | `9042:9042`, `7299:7199` | `stop_cassandra311` / `cleanup_cassandra311` |
| `start_postgres` | `postgres:latest` (`postgres`) | `5432:5432` | `stop_postgres` / `cleanuop_postgres` |
| `create_secrets` | Writes `secrets/admin-password`, `~/.my.cnf`, `~/.cassandra/cqlshrc` | — | Uses `SECRET_PASSWORD="Admin2024_"` by default |
| `test_db` / `inject_*` | Clones `datacharmer/test_db` and imports `employees` + `sakila` | `3306`/`3307`/`3308` | `inject_all` |

## `linode/`, `big-vms/`, and `lxd/`

| Path | Language / Format | Description |
| :--- | :--- | :--- |
| `linode/config.py` / `mygenconf.py` / `mygenscript.py` / `shell.py` | Python | `defaults_elk` and `defaults_mariadb` schemas; `mygenconf.py` generates `<prefix>_generate_linodes.sh` and `<prefix>_drop_linodes.sh` offline (uses `defaults['nb_linode_vms']` integer); `mygenscript.py` queries `linode-cli` via `get_public_ip()` to emit `putty_*.bat` and `<prefix>_provision_linodes.sh` |
| `linode/elk_generate_linodes.sh` / `elk_drop_linodes.sh` | Bash | Pre-generated ELK + PostgreSQL Linode provisioning scripts (`defaults_elk`) |
| `big-vms/Vagrantfile` | Ruby (`Vagrant`) | `ubuntu/jammy64` VM (`2548` MB RAM, `4` vCPU, ports `9000`, `3307`, `3308`, `5678`); includes developer synced paths (`C:/Users/jmren/SHARE`, `E:/Lightpath`) |
| `lxd/docker_iptables.sh` | Bash (`iptables`) | Flushes `DOCKER-USER` and adds `ACCEPT` rules for `lxdbr0` |
