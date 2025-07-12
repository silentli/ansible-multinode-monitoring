# Ansible Multinode Monitoring

A modular Ansible project to automate setup and monitoring of a multi-node environment with MariaDB, Mock Service, Node Exporter, Prometheus, and Grafana.

## Features
- **Role-based:** Each service is managed by its own reusable Ansible role.
- **Group-driven:** Inventory groups (`app_servers`, `database_servers`, `monitoring_servers`) define where each service runs.
- **Orchestrated setup:** The `setup_all.yml` playbook runs all setups in order and performs health checks.
- **Idempotent:** All playbooks and roles are safe to re-run.
- **Vagrant integration:** One-command VM provisioning for local testing.
- **Secure secrets:** Uses Ansible Vault for sensitive data, with example files for easy onboarding.
- **Comprehensive tests:** Fast, role-focused, and integration tests using pytest + testinfra.

## Project Structure
```
ansible-multinode-monitoring/
├── inventory/           # Host inventory (INI format)
├── playbooks/           # Main playbooks for setup and checks
├── roles/               # Ansible roles for each component
├── group_vars/          # Group-specific variables and secrets
├── tests/               # Automated test suite (pytest + testinfra)
└── Vagrantfile          # Local VM provisioning
```

## Prerequisites

### For Local Development (Vagrant)
- **Vagrant** (2.2.0+) with VirtualBox or libvirt provider
- **Ansible** (2.9+) installed locally
- **Python 3.11+** for running tests
- **Make** (for using the provided Makefile commands)

### Python Dependencies (for testing)
```bash
pip install -r tests/requirements.txt
```

## Quick Start
1. **Provision VMs and install dependencies:**
   ```bash
   make setup
   ```
2. **Set up vault configuration:**
   ```bash
   make setup-vault
   ```
   This creates vault files with default passwords. **Edit them to change passwords, then encrypt them.**
3. **Deploy the stack:**
   ```bash
   make deploy
   ```
4. **Run all tests:**
   ```bash
   make test
   ```
5. **Check service health:**
   ```bash
   make check-health
   ```

## Useful Make Commands
- `make setup` — Provision VMs and install dependencies
- `make deploy` — Deploy the complete stack
- `make test` — Run all role and integration tests
- `make check-health` — Run health checks on all services
- `make destroy` — Destroy all VMs
- `make status` — Show VM status
- `make test-mariadb` — Test MariaDB role only
- `make test-prometheus` — Test Prometheus role only
- `make test-grafana` — Test Grafana role only
- `make test-node-exporter` — Test Node Exporter role only
- `make test-mock-service` — Test Mock Service role only
- `make help` — See all available commands

## Vault Configuration
- Sensitive variables are encrypted with Ansible Vault.
- The `make setup-vault` command creates vault files with default passwords and sets up the vault password file.
- **Important:** Edit the generated vault files to change default passwords before encrypting them.
- Store your vault password in `.vault_pass` (never commit this file).
- **After vault setup, use `make` for all common operations (deploy, test, check-health, help).**

## Testing
- Located in `tests/` and powered by pytest + testinfra.
- Covers all roles (MariaDB, Prometheus, Grafana, Node Exporter, Mock Service) and integration flows.
- Fast feedback: Each test checks a single thing for clear failures.
- Role-focused: Tests match Ansible roles for easy debugging.
- Simple, maintainable, and easy to extend.

## Playbooks
- `setup_database.yml` — MariaDB and Node Exporter on database servers
- `setup_mock_service.yml` — Mock Service and Node Exporter on app servers
- `setup_monitoring.yml` — Prometheus and Grafana on monitoring servers
- `setup_all.yml` — Orchestrates the full stack setup and health checks
- `monitoring_check.yml` — Performs live health checks on all services

## Updates
- All playbooks and roles use FQCN (Fully Qualified Collection Name) for clarity.
- Example vault files for easy onboarding and secure secrets management.
- Comprehensive, maintainable test suite for all roles and integration.
