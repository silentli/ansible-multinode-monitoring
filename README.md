# Ansible Multinode Monitoring

A modular Ansible project to automate the setup and monitoring of a multi-node environment with MariaDB, Mock Service, Node Exporter, Prometheus, and Grafana.

## Project Structure

```
ansible-multinode-monitoring/
├── inventory/           # Host inventory (INI format)
├── playbooks/           # Main playbooks for setup and checks
├── roles/               # Ansible roles for each component
├── files/               # Static files (if any)
├── group_vars/          # Group-specific variables and secrets
└── tests/               # (reserved for future test playbooks and scripts)
```

## Design

- **Role-based:** Each service (mariadb, mock_service, node_exporter, prometheus, grafana) is managed by its own reusable Ansible role.
- **Group-driven:** Inventory groups (`app_servers`, `database_servers`, `monitoring_servers`) define where each service runs.
- **Orchestrated setup:** The `setup_all.yml` master playbook runs all setups in the correct order and performs health checks.
- **Idempotent:** All playbooks and roles are safe to re-run.

## Vagrant-based VM Provisioning

- The included `Vagrantfile` provisions three VMs (app-node, db-node, monitor-node) with static IPs.
- The `inventory/hosts.ini` is pre-configured to match the Vagrant environment.

**Quick start:**
```bash
# Bring up the VMs
vagrant up

# Destroy the VMs
vagrant destroy -f
```

## Quick Start

1. **Configure your inventory:**  
   Edit `inventory/hosts.ini` to match your environment (default matches Vagrant setup).

2. **Run the full setup:**  
   ```bash
   ansible-playbook -i inventory/hosts.ini playbooks/setup_all.yml
   ```

3. **Check service health:**  
   ```bash
   ansible-playbook -i inventory/hosts.ini playbooks/monitoring_check.yml
   ```

## Playbooks

- `setup_database.yml` — Sets up MariaDB and Node Exporter on database servers.
- `setup_mock_service.yml` — Sets up Mock Service and Node Exporter on app servers.
- `setup_monitoring.yml` — Sets up Prometheus and Grafana on monitoring servers.
- `setup_all.yml` — Orchestrates the full stack setup and health checks.
- `monitoring_check.yml` — Performs live health checks on all services.