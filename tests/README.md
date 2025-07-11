# Ansible Multinode Monitoring: Test Suite

Tests for Ansible roles using **pytest + testinfra** on Vagrant VMs.

## Quick Start

```bash
pip install -r tests/requirements.txt
make setup
make test
```

## Test Types
- **Role tests**: Validate each Ansible role (MariaDB, Prometheus, Grafana, Node Exporter, Mock Service)
- **Integration tests**: Check end-to-end service connectivity

## Running Tests

**All tests:**
```bash
make test
```

**Role-specific:**
```bash
make test-mariadb      # MariaDB (db-node)
make test-prometheus   # Prometheus (monitor-node)
make test-node-exporter # Node Exporter (all nodes)
make test-grafana      # Grafana (monitor-node)
make test-mock-service # Mock Service (app-node)
```

**Direct pytest:**
```bash
pytest --connection=ansible --ansible-inventory=inventory/hosts.ini tests/
```

## Configuration
- Only MariaDB tests need a vault password file:
  ```bash
  # Create .vault_pass file with the password
  ```
  (Automatically used by pytest via `pytest.ini`)

## Troubleshooting
- **VM issues**: `make status` or `vagrant status`
- **Vault errors**: Only for MariaDB, ensure `.vault_pass` exists

## Testing Philosophy
- **Fast feedback**: Each test checks a single thing for clear failures
- **Role-focused**: Tests match Ansible roles for easy debugging
- **Simple, maintainable**: Minimal dependencies, easy to extend
