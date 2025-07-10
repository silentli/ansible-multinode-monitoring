"""
Tests for the Node Exporter role.
"""
import pytest
import os
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# Load configuration from environment variables - will raise KeyError if missing
NODE_EXPORTER_PORT = os.environ["NODE_EXPORTER_PORT"]
NODE_EXPORTER_USER = os.environ["NODE_EXPORTER_USER"]
NODE_EXPORTER_GROUP = os.environ["NODE_EXPORTER_GROUP"]
NODE_EXPORTER_SERVICE_NAME = os.environ["NODE_EXPORTER_SERVICE_NAME"]
NODE_EXPORTER_INSTALL_DIR = os.environ["NODE_EXPORTER_INSTALL_DIR"]


def test_NODE_EXPORTER_SERVICE_running(host, has_node_exporter):
    """Test that Node Exporter service is running on hosts with node exporter."""
    if has_node_exporter:
        service = host.service(NODE_EXPORTER_SERVICE_NAME)
        assert service.is_running
        assert service.is_enabled


def test_node_exporter_port_listening(host, has_node_exporter):
    """Test that Node Exporter is listening on the correct port on hosts with node exporter."""
    if has_node_exporter:
        socket = host.socket(f"tcp://0.0.0.0:{NODE_EXPORTER_PORT}")
        assert socket.is_listening


def test_node_exporter_user_and_group(host, has_node_exporter):
    """Test that Node Exporter user and group exist on hosts with node exporter."""
    if has_node_exporter:
        user = host.user(NODE_EXPORTER_USER)
        group = host.group(NODE_EXPORTER_GROUP)
        assert user.exists
        assert group.exists


def test_node_exporter_binary_exists(host, has_node_exporter):
    """Test that Node Exporter binary exists on hosts with node exporter."""
    if has_node_exporter:
        binary = host.file(f"{NODE_EXPORTER_INSTALL_DIR}/node_exporter")
        assert binary.exists
        assert binary.is_file
        assert binary.mode == 0o755


def test_node_exporter_systemd_service_exists(host, has_node_exporter):
    """Test that Node Exporter systemd service file exists on hosts with node exporter."""
    if has_node_exporter:
        service_file = host.file(f"/etc/systemd/system/{NODE_EXPORTER_SERVICE_NAME}.service")
        assert service_file.exists
        assert service_file.is_file


def test_node_exporter_systemd_service_content(host, has_node_exporter):
    """Test Node Exporter systemd service content on hosts with node exporter."""
    if has_node_exporter:
        service_file = host.file(f"/etc/systemd/system/{NODE_EXPORTER_SERVICE_NAME}.service")
        assert service_file.contains(f"ExecStart={NODE_EXPORTER_INSTALL_DIR}/node_exporter")
        assert service_file.contains(f"User={NODE_EXPORTER_USER}")
        assert service_file.contains(f"Group={NODE_EXPORTER_GROUP}")


def test_node_exporter_process_running(host, has_node_exporter):
    """Test that Node Exporter process is running on hosts with node exporter."""
    if has_node_exporter:
        try:
            process = host.process.get(comm="node_exporter")
            assert process is not None
            assert "node_exporter" in process.comm
        except RuntimeError:
            # Process not found, which is a failure
            assert False, "Node Exporter process not found"


def test_node_exporter_firewall_rule(host, has_node_exporter):
    """
    Test that firewall allows Node Exporter port on hosts with node exporter.
    Only checks Ubuntu/Debian with UFW.
    """
    if not has_node_exporter:
        return
    if host.system_info.distribution not in ["ubuntu", "debian"]:
        pytest.skip("Firewall test only runs on Ubuntu/Debian with UFW")

    ufw_status = host.run("ufw status")
    if ufw_status.rc != 0 or "Status: inactive" in ufw_status.stdout:
        return  # UFW not active

    import re
    port_rule = f"{NODE_EXPORTER_PORT}/tcp"
    
    # Check for explicit ALLOW rule
    if re.search(rf"{re.escape(port_rule)}\s+ALLOW", ufw_status.stdout):
        return  # Port explicitly allowed
    
    # Check for explicit DENY/REJECT rule
    if re.search(rf"{re.escape(port_rule)}\s+(DENY|REJECT)", ufw_status.stdout):
        pytest.fail(f"UFW is active and port {port_rule} is explicitly denied")
    
    # If not found, skip (not explicitly allowed or denied)
    pytest.skip(f"UFW active but port {port_rule} is not explicitly allowed or denied")


def test_node_exporter_metrics_endpoint(host, has_node_exporter):
    """Test that Node Exporter metrics endpoint is accessible on hosts with node exporter."""
    if has_node_exporter:
        result = host.run(f"curl -s -o /dev/null -w '%{{http_code}}' http://localhost:{NODE_EXPORTER_PORT}/metrics")
        assert result.rc == 0
        assert result.stdout == "200"


def test_node_exporter_metrics_content(host, has_node_exporter):
    """Test that Node Exporter returns metrics content on hosts with node exporter."""
    if has_node_exporter:
        result = host.run(f"curl -s http://localhost:{NODE_EXPORTER_PORT}/metrics")
        assert result.rc == 0
        assert "node_exporter_build_info" in result.stdout
        assert "go_gc_duration_seconds" in result.stdout


def test_node_exporter_collectors_enabled(host, has_node_exporter):
    """Test that Node Exporter has expected collectors enabled on hosts with node exporter."""
    if has_node_exporter:
        result = host.run(f"curl -s http://localhost:{NODE_EXPORTER_PORT}/metrics")
        assert result.rc == 0
        # Check for common collectors
        assert "node_cpu_seconds_total" in result.stdout
        assert "node_memory_MemTotal_bytes" in result.stdout
        assert "node_filesystem_size_bytes" in result.stdout
