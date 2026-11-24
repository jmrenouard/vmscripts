# Docker Database & Ansible Sandbox (`docker/`)

The `docker/` directory provides `Makefile` runners, Compose definitions, and an Alpine Ansible container for testing database engines locally without VirtualBox VMs. For step-by-step exercises, see [Tutorial 2](../docs/01-tutorials/02-docker-database-sandboxes-and-linode.md).

## Contents

| File | Purpose |
| :--- | :--- |
| `docker/Makefile` | Single-container database launchers (`mysql`, `mysql57`, `mariadb`, `mariadb106`, `cassandra`, `cassandra311`, `postgres`), log tails, cleanup targets, and `test_db` data loader |
| `docker/Dockerfile` | Alpine-based Ansible runner image (`ansible-playbook -v`) |
| `docker/requirements.txt` | Python package pins used in Docker experiments |
| `docker/galera/docker-compose.yaml` | 3-node MariaDB Galera sandbox definition (`node1`, `node2`, `node3`) |
| `docker/replication/docker-compose.yml` | 1-primary / 2-replica MySQL topology with `Dockerfile.primary`, `Dockerfile.replica`, and `setup-*.sh` |
| `../docker.sh` | Host shell aliases and helper functions (`dcu`, `dcd`, `dex`, `dps`, `dfrom`, `dbash`) |

## Quick Start with `docker/Makefile`

1. Create local Docker secret files and `~/.my.cnf` / `~/.cassandra/cqlshrc` (change `SECRET_PASSWORD` in `docker/Makefile` from the default `Admin2024_` before real use):

```bash
cd docker
make create_secrets
```

2. Launch one or all database engines (requires `sudo` for `enable_pf` sysctl IP forwarding):

```bash
make start_mariadb
make list_containers
```

3. Stop or remove containers and volumes:

```bash
make stop_mariadb
make cleanup_mariadb
```

> **Known Caveats**:
> - `docker/Makefile` spells the PostgreSQL volume cleanup target `cleanuop_postgres` (`L167`), so `make cleanup_all` calls `cleanuop_postgres`.
> - `docker/galera/docker-compose.yaml` uses legacy Compose v1 top-level service keys (`node1`, `node2`, `node3` without `services:`), which modern `docker compose` v2 rejects unless wrapped under `services:`.
> - `docker/replication/docker-compose.yml` sets `SERVER_ID=2` on both `mysql-replica2` and `mysql-replica3`, and `docker/replication/setup-replica.sh` contains unexpanded placeholders (`mysqldump --master-data=2 ....`, `CHANGE MASTER TO ...;`). Review before running replication builds.
