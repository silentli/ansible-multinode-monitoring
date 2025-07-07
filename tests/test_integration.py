"""
Integration tests for cross-node connectivity in the monitoring stack.
"""
import pytest


def test_database_connectivity(host, is_monitoring_server):
    """Test that monitoring server can connect to database."""
    if is_monitoring_server:
        result = host.run("nc -z -w 2 db-node 3306")
        assert result.rc == 0


def test_mock_service_connectivity(host, is_monitoring_server):
    """Test that monitoring server can connect to mock service."""
    if is_monitoring_server:
        result = host.run("nc -z -w 2 app-node 8080")
        assert result.rc == 0


def test_node_exporter_connectivity(host, is_monitoring_server):
    """Test that monitoring server can connect to node exporters."""
    if is_monitoring_server:
        result1 = host.run("nc -z -w 2 app-node 9100")
        result2 = host.run("nc -z -w 2 db-node 9100")
        assert result1.rc == 0
        assert result2.rc == 0
