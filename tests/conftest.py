"""
Pytest configuration and fixtures for Ansible role testing.
"""
import pytest
import logging

# Configure logging to show only our debug messages
logging.basicConfig(
    level=logging.DEBUG,
    format='%(levelname)s: %(message)s',
    force=True
)

# Suppress debug messages from other libraries
logging.getLogger('pytest').setLevel(logging.WARNING)
logging.getLogger('testinfra').setLevel(logging.WARNING)
logging.getLogger('paramiko').setLevel(logging.WARNING)
logging.getLogger('urllib3').setLevel(logging.WARNING)
logging.getLogger('requests').setLevel(logging.WARNING)


@pytest.fixture(autouse=True)
def skip_if_not_linux(host):
    """Skip all tests if the target is not Linux."""
    if host.system_info.type != "linux":
        pytest.skip("These tests only run on Linux targets")


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
    return 'app_servers' in host.ansible.get_variables().get('group_names', [])


@pytest.fixture
def has_node_exporter(host):
    """Check if host has node exporter."""
    return 'node_exporters' in host.ansible.get_variables().get('group_names', [])
