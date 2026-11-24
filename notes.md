# Multi-Node DB Lab Execution Notes

Operational cheat sheet showing how `profile` and `vagrant.sh` combine with an external `dbscripts` checkout (`SCRIPT_DIR="$HOME/GIT_REPOS/dbscripts"`) to provision a 3-node MariaDB Galera lab across Vagrant VMs (`dbsrv1`, `dbsrv2`, `dbsrv3`).

> **Prerequisite**: Scripts under `scripts/1_system/...`, `scripts/2_install/...`, `scripts/3_database/...`, and `scripts/8_galera/...` belong to the separate `jmrenouard/dbscripts` repository referenced by `SCRIPT_DIR` in `profile`. Update `VMS_DIR` and `SCRIPT_DIR` before sourcing `profile`.

## Environment Setup and Connectivity Check

```bash
git pull
chmod 600 vms/id_rsa
source ./profile
vssh_cmd "$all_vms" "ip a"
vlist
```

## Remote Provisioning Sequence (`dbscripts` + `vssh_exec`)

### 1. System Preparation and Kernel Tuning

```bash
vssh_exec "$all_vms" "$SCRIPT_DIR/scripts/1_system/1_update.sh"
vssh_cmd "$all_vms" "reboot"

vssh_exec "$all_vms" "$SCRIPT_DIR/scripts/1_system/2_iptables.sh"
vssh_exec "$all_vms" "$SCRIPT_DIR/scripts/1_system/3_selinux.sh"
vssh_exec "$all_vms" "$SCRIPT_DIR/scripts/1_system/4_security.sh"
vssh_exec "$all_vms" "$SCRIPT_DIR/scripts/1_system/5_sysctl.sh"
vssh_exec "$all_vms" "$SCRIPT_DIR/scripts/1_system/6_tuned.sh"
vssh_exec "$all_vms" "$SCRIPT_DIR/scripts/1_system/7_ntp.sh"
```

### 2. MariaDB Package Installation and Configuration

```bash
vssh_exec "$db_vms" "$SCRIPT_DIR/scripts/2_install/1a_install_mariadb_centos.sh"
vssh_exec "$db_vms" "$SCRIPT_DIR/scripts/2_install/3_config_start.sh"
```

### 3. Security Hardening and Sample Dataset

```bash
vssh_exec dbsrv1 "$SCRIPT_DIR/scripts/3_database/1_secure_access.sh"
vssh_exec dbsrv1 "$SCRIPT_DIR/scripts/3_database/2_set_password.sh"
vssh_exec dbsrv1 "$SCRIPT_DIR/scripts/3_database/3_sample_database.sh"
```

### 4. Bootstrap Galera Cluster and Join Replicas

```bash
vssh_exec dbsrv1 "$SCRIPT_DIR/scripts/8_galera/5_bootstrap_node.sh"
vssh_exec dbsrv2,dbsrv3 "$SCRIPT_DIR/scripts/8_galera/6_start_new_node.sh"
```

For full documentation of native `vmscripts` targets, see [docs/index.md](docs/index.md).
