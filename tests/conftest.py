"""
Pytest configuration and fixtures for Ansible role testing.
"""
import pytest


@pytest.fixture
def is_database_server(host):
    """Check if host is a database server."""
    return 'database_servers' in host.ansible.get_variables().get('group_names', [])


@pytest.fixture
def is_monitoring_server(host):
    """Check if host is a monitoring server."""
    return 'monitoring_servers' in host.ansible.get_variables().get('group_names', [])


@pytest.fixture
def is_mock_service_server(host):
    """Check if host is a mock service server."""
    return 'mock_service_servers' in host.ansible.get_variables().get('group_names', [])


@pytest.fixture
def has_node_exporter(host):
    """Check if host has node exporter."""
    return 'node_exporters' in host.ansible.get_variables().get('group_names', []) 