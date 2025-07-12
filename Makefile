# Ansible Multinode Monitoring - Makefile
# This Makefile provides targets for setting up, testing, and managing the monitoring stack

.PHONY: help install-ansible install-deps check-prerequisites provision start destroy shutdown clean status
.PHONY: test test-fast test-integration test-smoke test-all-roles
.PHONY: test-mariadb test-prometheus test-node-exporter test-grafana test-mock-service
.PHONY: test-database test-monitoring setup setup-vault deploy deploy-database deploy-app deploy-monitoring check-health

# Default target
.DEFAULT_GOAL := help

# Colors for help output
BLUE := \033[36m
NC := \033[0m

# Common variables
ANSIBLE_CMD := ansible-playbook -i inventory/hosts.ini --vault-password-file=.vault_pass
PYTEST_CMD := pytest --connection=ansible --ansible-inventory=inventory/hosts.ini

help: ## Show this help message
	@echo "$(BLUE)Ansible Multinode Monitoring - Available Targets:$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "$(BLUE)%-20s$(NC) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(BLUE)Quick Start:$(NC)"
	@echo "  make setup          # Complete setup (install deps + provision VMs)"
	@echo "  make deploy         # Deploy the monitoring stack"
	@echo "  make test           # Run all tests"
	@echo "  make check-health   # Check service health"
	@echo ""
	@echo "$(BLUE)VM Management:$(NC)"
	@echo "  make provision      # Create and provision VMs"
	@echo "  make start          # Start existing VMs"
	@echo "  make shutdown       # Shutdown VMs (preserves data)"
	@echo "  make destroy        # Destroy VMs (permanent removal)"
	@echo "  make status         # Show VM status"

# =============================================================================
# PREREQUISITES AND INSTALLATION
# =============================================================================

check-prerequisites: ## Check if required tools are installed
	@echo "Checking prerequisites..."
	@command -v vagrant >/dev/null 2>&1 || { echo "Error: vagrant is not installed"; exit 1; }
	@command -v ansible >/dev/null 2>&1 || { echo "Error: ansible is not installed. Run 'make install-ansible'"; exit 1; }
	@command -v python3 >/dev/null 2>&1 || { echo "Error: python3 is not installed"; exit 1; }
	@command -v pip3 >/dev/null 2>&1 || { echo "Error: pip3 is not installed"; exit 1; }
	@test -f .vault_pass || { echo "Error: .vault_pass file not found in project root"; exit 1; }
	@echo "✓ All prerequisites are installed"

install-ansible: ## Install Ansible (platform-specific)
	@echo "Installing Ansible..."
	@if [ "$(shell uname)" = "Darwin" ]; then \
		echo "Installing Ansible via Homebrew..."; \
		brew install ansible || { echo "Error: Failed to install Ansible via Homebrew"; exit 1; }; \
	elif command -v apt-get >/dev/null 2>&1; then \
		echo "Installing Ansible via apt..."; \
		sudo apt-get update && sudo apt-get install -y ansible || { echo "Error: Failed to install Ansible via apt"; exit 1; }; \
	elif command -v yum >/dev/null 2>&1; then \
		echo "Installing Ansible via yum..."; \
		sudo yum install -y ansible || { echo "Error: Failed to install Ansible via yum"; exit 1; }; \
	elif command -v dnf >/dev/null 2>&1; then \
		echo "Installing Ansible via dnf..."; \
		sudo dnf install -y ansible || { echo "Error: Failed to install Ansible via dnf"; exit 1; }; \
	else \
		echo "Error: Unsupported package manager. Please install Ansible manually."; \
		exit 1; \
	fi
	@echo "✓ Ansible installed successfully"

install-deps: ## Install Python testing dependencies
	@echo "Installing Python dependencies..."
	pip3 install -r tests/requirements.txt
	@echo "✓ Python dependencies installed"

# =============================================================================
# VAGRANT MANAGEMENT
# =============================================================================

provision: check-prerequisites ## Provision Vagrant VMs
	@echo "Provisioning Vagrant VMs..."
	vagrant up --provision
	@echo "✓ VMs provisioned successfully"

start: check-prerequisites ## Start existing Vagrant VMs (without provisioning)
	@echo "Starting Vagrant VMs..."
	vagrant up
	@echo "✓ VMs started"

destroy: ## Destroy Vagrant VMs (permanent removal)
	@echo "Destroying Vagrant VMs..."
	vagrant destroy -f
	@echo "✓ VMs destroyed"

shutdown: ## Shutdown Vagrant VMs (preserves data)
	@echo "Shutting down Vagrant VMs..."
	vagrant halt
	@echo "✓ VMs shut down"

status: ## Show Vagrant VM status
	vagrant status

# =============================================================================
# DEPLOYMENT
# =============================================================================

deploy: check-prerequisites ## Deploy the complete monitoring stack
	@echo "Deploying monitoring stack..."
	$(ANSIBLE_CMD) playbooks/setup_all.yml
	@echo "✓ Monitoring stack deployed"

check-health: check-prerequisites ## Check health of all services
	@echo "Checking service health..."
	$(ANSIBLE_CMD) playbooks/monitoring_check.yml
	@echo "✓ Health check completed"

# Individual deployment targets
deploy-database: check-prerequisites ## Deploy database servers only
	@echo "Deploying database servers..."
	$(ANSIBLE_CMD) playbooks/setup_database.yml
	@echo "✓ Database servers deployed"

deploy-app: check-prerequisites ## Deploy app servers only
	@echo "Deploying app servers..."
	$(ANSIBLE_CMD) playbooks/setup_mock_service.yml
	@echo "✓ App servers deployed"

deploy-monitoring: check-prerequisites ## Deploy monitoring servers only
	@echo "Deploying monitoring servers..."
	$(ANSIBLE_CMD) playbooks/setup_monitoring.yml
	@echo "✓ Monitoring servers deployed"

# Debug-enabled deployment targets
deploy-database-debug: check-prerequisites ## Deploy database servers with debug output
	@echo "Deploying database servers with debug..."
	DEBUG=true $(ANSIBLE_CMD) playbooks/setup_database.yml
	@echo "✓ Database servers deployed with debug"

deploy-app-debug: check-prerequisites ## Deploy app servers with debug output
	@echo "Deploying app servers with debug..."
	DEBUG=true $(ANSIBLE_CMD) playbooks/setup_mock_service.yml
	@echo "✓ App servers deployed with debug"

deploy-monitoring-debug: check-prerequisites ## Deploy monitoring servers with debug output
	@echo "Deploying monitoring servers with debug..."
	DEBUG=true $(ANSIBLE_CMD) playbooks/setup_monitoring.yml
	@echo "✓ Monitoring servers deployed with debug"

deploy-debug: check-prerequisites ## Deploy complete stack with debug output
	@echo "Deploying monitoring stack with debug..."
	DEBUG=true $(ANSIBLE_CMD) playbooks/setup_all.yml
	@echo "✓ Monitoring stack deployed with debug"

# =============================================================================
# TESTING
# =============================================================================

test: ## Run all role tests (recommended)
	@echo "Running all role tests..."
	make test-all-roles

test-fast: ## Run fast tests (skip slow ones)
	@echo "Running fast tests..."
	$(PYTEST_CMD) tests/ -m "not slow" -v

test-integration: ## Run integration tests (cross-node connectivity)
	@echo "Running integration tests..."
	$(PYTEST_CMD) --hosts=monitoring_servers tests/test_integration.py -v

test-smoke: ## Run smoke tests
	@echo "Running smoke tests..."
	$(PYTEST_CMD) tests/ -m smoke -v

# Role-specific tests
test-mariadb: ## Run MariaDB role tests (requires vault password)
	@echo "Running MariaDB role tests..."
	$(PYTEST_CMD) --hosts=database_servers tests/test_mariadb_role.py -v

test-prometheus: ## Run Prometheus role tests
	@echo "Running Prometheus role tests..."
	$(PYTEST_CMD) --hosts=monitoring_servers tests/test_prometheus_role.py -v

test-node-exporter: ## Run Node Exporter role tests
	@echo "Running Node Exporter role tests..."
	$(PYTEST_CMD) --hosts=node_exporters tests/test_node_exporter_role.py -v

test-grafana: ## Run Grafana role tests
	@echo "Running Grafana role tests..."
	$(PYTEST_CMD) --hosts=monitoring_servers tests/test_grafana_role.py -v

test-mock-service: ## Run Mock Service role tests
	@echo "Running Mock Service role tests..."
	$(PYTEST_CMD) --hosts=app_servers tests/test_mock_service_role.py -v

# Convenience targets for common test combinations
test-database: test-mariadb ## Run all database-related tests

test-monitoring: test-prometheus test-grafana ## Run all monitoring-related tests

test-all-roles: test-mariadb test-prometheus test-node-exporter test-grafana test-mock-service ## Run all role tests

# =============================================================================
# SETUP AND CLEANUP
# =============================================================================

setup: install-ansible install-deps provision ## Complete setup (install deps + provision VMs)
	@echo "✓ Complete setup finished"
	@echo ""
	@echo "$(BLUE)Next steps:$(NC)"
	@echo "  make setup-vault    # Set up vault configuration"
	@echo "  make deploy         # Deploy the monitoring stack"
	@echo "  make test           # Run tests to verify deployment"

setup-vault: ## Set up vault configuration interactively
	@echo "Setting up vault configuration..."
	@if [ -f "scripts/setup-vault.sh" ]; then \
		./scripts/setup-vault.sh; \
	else \
		echo "Error: scripts/setup-vault.sh not found"; \
		echo "Please create the script first or set up vault manually"; \
		exit 1; \
	fi

clean: ## Clean up test artifacts and cache files
	@echo "Cleaning up..."
	rm -f test_report.html
	rm -rf .pytest_cache
	rm -rf __pycache__
	rm -rf tests/__pycache__
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
	@echo "✓ Cleanup completed"

# =============================================================================
# DEVELOPMENT HELPERS
# =============================================================================

lint: ## Run linting checks (if you add linting tools)
	@echo "Linting not configured yet."

format: ## Format code (if you add formatting tools)
	@echo "Code formatting not configured yet."
