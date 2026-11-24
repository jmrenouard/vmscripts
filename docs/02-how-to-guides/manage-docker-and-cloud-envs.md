# How to Manage Docker and Cloud Environments

Use this procedure to launch Docker database containers, apply LXD bridge rules, and control Linode instances.

## Prerequisites

- Confirm Docker Engine and GNU `make` are installed on the host.
- Confirm `linode-cli` is authenticated when you deploy cloud instances.

NOTE: Review all ports and defaults in [Scripts, Functions, and Targets Reference](../03-reference/scripts-functions-and-targets.md).

## Procedure

### Prepare and Launch Docker Databases

CAUTION: The default `SECRET_PASSWORD` value inside `docker/Makefile` is public in Git. Change `SECRET_PASSWORD` before you create secrets on shared hosts.

1. Run these commands from the repository root and generate local password files inside `docker/`:

```bash
make -C docker create_secrets
```

2. Load the container shell aliases from the repository root:

```bash
source ./docker.sh
```

3. Start your required database containers inside `docker/`:

```bash
make -C docker start_mariadb
make -C docker start_postgres
```

### Allow LXD Bridge Traffic Through Docker

1. If LXD containers fail to reach the network beside Docker, apply `lxd/docker_iptables.sh`:

```bash
sudo bash lxd/docker_iptables.sh
```

### Generate and Run Linode Scripts

WARNING: Legacy defaults inside `linode/config.py` use a committed sample root password. Override `vm_generic_password` and specify your own public SSH key before you run `lcreate`.

1. Generate creation and deletion scripts inside `linode/` with a custom password:

```bash
(cd linode && python3 mygenconf.py generic_prefix=lab vm_generic_password='StrongUniquePasswordHere')
```

2. Source `linode.sh` and inspect active cloud instances:

```bash
source ./linode.sh
llist
```

## Validation

List active database containers and verify their status:

```bash
make -C docker list_containers
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```

For cloud nodes, verify inventory generation succeeds without errors:

```bash
llist
```

## Rollback

Stop and remove containers after container tests finish:

```bash
make -C docker stop_all
```

CAUTION: Volume cleanup targets (`make cleanup_all`) erase persisted MySQL, MariaDB, Cassandra, and PostgreSQL data volumes permanently. Note that `docker/Makefile` defines the PostgreSQL cleanup target as `cleanuop_postgres`.

Remove all database container volumes after confirmation:

```bash
make -C docker cleanup_all
```

If you no longer need cloud instances, remove each node by label with `ldelete`:

```bash
ldelete lab_elksrv
```
