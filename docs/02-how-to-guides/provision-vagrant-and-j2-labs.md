# How to Provision Vagrant and Jinja2 Labs

Use this procedure to configure, start, verify, and destroy VirtualBox labs under `vms/` or `vm-vagrant/`.

## Prerequisites

- Confirm Vagrant and VirtualBox are installed on the host.
- Confirm Python 3 is installed on the host.
- Confirm `j2cli` and `puttygen` are installed when you use `vm-vagrant/`.

NOTE: Check script parameters and targets in [Reference](../03-reference/scripts-functions-and-targets.md). Read runtime comparisons in [Architecture](../04-explanation/vm-and-container-lab-architecture.md).

## Procedure

### Prepare Fresh SSH Keys

WARNING: Legacy private keys in `vms/` and `vm-vagrant/` are public in Git history. Generate fresh SSH keys before you expose VMs on shared or bridged networks.

1. Generate new RSA and PuTTY keys inside `vm-vagrant/`:

```bash
cd vm-vagrant
make generate_keys
```

2. Copy the new private key to `vms/id_rsa` and restrict file permissions:

```bash
cp id_rsa_vm ../vms/id_rsa && chmod 600 id_rsa_vm ../vms/id_rsa
```

### Generate Configuration Artifacts

1. Review `vm-vagrant/server.json` and set `"enabled": 1` on required nodes.
2. Render `Vagrantfile`, Ansible configuration, inventory, PuTTY registry, and SSH aliases:

```bash
make generate_vagrantfile
make generate_conf_ansible
make generate_bashrc
```

3. If you use static `vms/`, generate a custom `Vagrantfile` with `vms/mygenconf.py`:

```bash
cd ../vms
python3 mygenconf.py output=Vagrantfile vm_number=3
```

### Install Plugins and Boot VMs

1. Install required Vagrant plugins if they are absent:

```bash
sh init_vagrant.sh
```

2. Start all VirtualBox virtual machines:

```bash
sh start.sh
```

3. Generate your user SSH configuration from `Vagrantfile`:

```bash
sh genSshConfig.sh
```

## Validation

Check plugin status, VM run state, and guest connectivity:

```bash
sh init_vagrant.sh check
sh status.sh
sh info.sh
```

Confirm each active VM shows status `running` and responds to `ping -c1`.

## Rollback

If VM setup fails or lab work ends, halt all virtual machines cleanly:

```bash
sh stop.sh
```

CAUTION: The `vms/destroy.sh` script deletes VMs and removes `*_data.vdi` disk files permanently. Back up needed database data before you destroy VMs.

Run destruction or `vm-vagrant/` cleanup to remove all lab artifacts:

```bash
sh destroy.sh
```

In `vm-vagrant/`, run `make cleanup` to halt VMs and erase generated files:

```bash
cd ../vm-vagrant
make cleanup
```
