#!/bin/bash

# Setup script for Ansible Vault configuration
# This script helps users set up their vault files and password

set -e

echo "Setting up Ansible Vault configuration..."

# Create vault password file if missing
if [ ! -f ".vault_pass" ]; then
    echo "Creating .vault_pass file..."
    read -s -p "Enter your vault password: " VAULT_PASSWORD
    echo
    echo "$VAULT_PASSWORD" > .vault_pass
    chmod 600 .vault_pass
    echo "Created .vault_pass file"
else
    echo ".vault_pass already exists. Skipping creation."
fi

# Create database vault file if missing
if [ ! -f "group_vars/database_servers/vault.yml" ]; then
    echo "Creating database vault file..."
    mkdir -p group_vars/database_servers
    cat > group_vars/database_servers/vault.yml << 'EOF'
# Database server vault variables
# Change these passwords before encrypting!

mariadb_root_password: "changeme_root_password"
mariadb_user_password: "changeme_user_password"
EOF
    echo "Created group_vars/database_servers/vault.yml"
    echo "   Edit this file to change passwords, then encrypt it with:"
    echo "   ansible-vault encrypt group_vars/database_servers/vault.yml"
else
    echo "group_vars/database_servers/vault.yml already exists. Skipping."
fi

# Create monitoring vault file if missing
if [ ! -f "group_vars/monitoring_servers/vault.yml" ]; then
    echo "Creating monitoring vault file..."
    mkdir -p group_vars/monitoring_servers
    cat > group_vars/monitoring_servers/vault.yml << 'EOF'
# Monitoring server vault variables
# Change these passwords before encrypting!

grafana_admin_password: "changeme_admin_password"
EOF
    echo "Created group_vars/monitoring_servers/vault.yml"
    echo "   Edit this file to change passwords, then encrypt it with:"
    echo "   ansible-vault encrypt group_vars/monitoring_servers/vault.yml"
else
    echo "group_vars/monitoring_servers/vault.yml already exists. Skipping."
fi

echo ""
echo "Vault setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit the vault files with your desired passwords"
echo "2. Encrypt them:"
echo "   ansible-vault encrypt group_vars/database_servers/vault.yml"
echo "   ansible-vault encrypt group_vars/monitoring_servers/vault.yml"
echo "3. Use 'make' for common operations:"
echo "   make deploy      # Deploy the stack"
echo "   make test        # Run all tests"
echo "   make check-health # Check service health"
echo "   make help        # See all available commands"
