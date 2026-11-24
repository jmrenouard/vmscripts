# Tutorial 2: Docker Database Sandboxes and Linode Labs

In this tutorial, you use **vmscripts** to manage local Docker database containers (`docker.sh`, `docker/Makefile`), configure LXD/Docker bridge forwarding, and generate Linode provisioning scripts (`linode/`).

## Prerequisites

- Docker Engine and GNU `make` for local container targets.
- `linode-cli`, `pwgen`, and `python3` if testing cloud provisioning scripts under `linode/`.

## Step 1: Load Docker Shell Helpers (`docker.sh`)

Source `docker.sh` in your Bash session to unlock short container aliases (`dcu`, `dcd`, `dpsa`, `drma`) and dynamic helpers (`dfrom`, `dbash`):

```bash
source ./docker.sh
declare -f dfrom dbash
```

For example, `dbash mariadb` looks up the first container matching `mariadb` via `dfrom mariadb` and opens an interactive `bash` shell.

## Step 2: Launch Local Database Containers via `docker/Makefile`

```mermaid
flowchart LR
    SEC["make create_secrets"] --> RUN["make start_mariadb / start_postgres / start_cassandra"]
    RUN --> CHK["make list_containers / make log_mariadb"]
    CHK --> CLEAN["make stop_all / make cleanup_all"]
```

Change `SECRET_PASSWORD` in `docker/Makefile` from the default `Admin2024_` before real use, then create secret files and boot containers:

```bash
cd docker
make create_secrets
make start_mariadb
make list_containers
```

Stop and clean up when finished:

```bash
make stop_mariadb
make cleanup_mariadb
```

Notice that `docker/Makefile` binds MariaDB to host port `3307` (`start_mariadb`) and MariaDB 10.6 to `3308` (`start_mariadb106`), while MySQL uses `3306` (`start_mysql`) and `3309` (`start_mysql57`), and PostgreSQL uses `5432` (`start_postgres`).

## Step 3: Allow LXD + Docker Coexistence (`lxd/docker_iptables.sh`)

When Docker and LXD run on the same Linux host, Docker's default `DOCKER-USER` chain blocks traffic over `lxdbr0`. Review `lxd/docker_iptables.sh`:

```bash
sudo bash lxd/docker_iptables.sh
```

It flushes `DOCKER-USER` and appends bidirectional `ACCEPT` rules on interface `lxdbr0`.

## Step 4: Generate Linode Creation and Deletion Scripts (`linode/`)

Under `linode/`, `linode/config.py` defines `defaults_elk` (`elk_elksrv`, `elk_pgsrv1`, `elk_pgsrv2`) and `defaults_mariadb`. Running `linode/mygenconf.py` offline writes `<prefix>_generate_linodes.sh` and `<prefix>_drop_linodes.sh` wrapping `lcreate` and `ldelete` from `linode.sh` (omit `nb_linode_vms=` because `mygenconf.py` expects the integer default from `linode/config.py`). After instances exist, `linode/mygenscript.py` queries public IPs via `linode-cli` to build `putty_*.bat` and `<prefix>_provision_linodes.sh`. Test offline script generation in an isolated folder:

```bash
mkdir -p /tmp/linode_test && cd /tmp/linode_test
PYTHONPATH=/path/to/vmscripts/linode python3 /path/to/vmscripts/linode/mygenconf.py generic_prefix=demo
bash -n demo_generate_linodes.sh && bash -n demo_drop_linodes.sh
```

> **Security Warning**: `linode/config.py` (`defaults_elk`) and `linode/elk_generate_linodes.sh` contain a committed sample password (`eixo1hoo7Goo7suu9v`). Always override `vm_generic_password` before generating real cloud instances.

## Next Steps

- Cloud and Docker runbooks: [How to Manage Docker and Cloud Environments](../02-how-to-guides/manage-docker-and-cloud-envs.md).
- Complete parameter reference: [Scripts, Functions, and Targets Reference](../03-reference/scripts-functions-and-targets.md).
