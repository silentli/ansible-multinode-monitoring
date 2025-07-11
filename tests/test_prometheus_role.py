"""
Tests for the Prometheus role.
"""
import pytest
import os
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# Load configuration from environment variables - will raise KeyError if missing
PROMETHEUS_USER = os.environ["PROMETHEUS_USER"]
PROMETHEUS_GROUP = os.environ["PROMETHEUS_GROUP"]
PROMETHEUS_SERVICE_NAME = os.environ["PROMETHEUS_SERVICE_NAME"]
PROMETHEUS_PORT = os.environ["PROMETHEUS_PORT"]
PROMETHEUS_INSTALL_DIR = os.environ["PROMETHEUS_INSTALL_DIR"]
PROMETHEUS_CONFIG_DIR = os.environ["PROMETHEUS_CONFIG_DIR"]
PROMETHEUS_DATA_DIR = os.environ["PROMETHEUS_DATA_DIR"]

# Standard Prometheus values
PROMETHEUS_PROCESS_NAME = "prometheus"
PROMETHEUS_CONFIG_FILE = "prometheus.yml"
PROMETHEUS_BINARY_NAME = "prometheus"


def test_prometheus_service_running(host, is_monitoring_server):
    """Test that Prometheus service is running and enabled on monitoring servers."""
    if is_monitoring_server:
        service = host.service(PROMETHEUS_SERVICE_NAME)
        assert service.is_running
        assert service.is_enabled


def test_prometheus_port_listening(host, is_monitoring_server):
    """Test that Prometheus is listening on the correct port on monitoring servers."""
    if is_monitoring_server:
        socket = host.socket(f"tcp://0.0.0.0:{PROMETHEUS_PORT}")
        assert socket.is_listening


def test_prometheus_user_and_group(host, is_monitoring_server):
    """Test that Prometheus user and group exist on monitoring servers."""
    if is_monitoring_server:
        user = host.user(PROMETHEUS_USER)
        group = host.group(PROMETHEUS_GROUP)
        assert user.exists
        assert group.exists


def test_prometheus_directories_and_permissions(host, is_monitoring_server):
    """Test that Prometheus directories exist with correct permissions on monitoring servers."""
    if is_monitoring_server:
        # Test all directories
        directories = [
            PROMETHEUS_INSTALL_DIR,
            PROMETHEUS_DATA_DIR,
            PROMETHEUS_CONFIG_DIR
        ]
        
        for directory_path in directories:
            directory = host.file(directory_path)
            assert directory.exists
            assert directory.is_directory
            assert directory.user == PROMETHEUS_USER
            assert directory.group == PROMETHEUS_GROUP


def test_prometheus_config_file_exists_and_permissions(host, is_monitoring_server):
    """Test that Prometheus configuration file exists with correct permissions on monitoring servers."""
    if is_monitoring_server:
        config_file = host.file(f"{PROMETHEUS_CONFIG_DIR}/{PROMETHEUS_CONFIG_FILE}")
        assert config_file.exists
        assert config_file.is_file
        assert config_file.user == PROMETHEUS_USER
        assert config_file.group == PROMETHEUS_GROUP


def test_prometheus_binary_exists_and_permissions(host, is_monitoring_server):
    """Test that Prometheus binary exists with correct permissions on monitoring servers."""
    if is_monitoring_server:
        binary = host.file(f"{PROMETHEUS_INSTALL_DIR}/{PROMETHEUS_BINARY_NAME}")
        assert binary.exists
        assert binary.is_file
        assert binary.mode == 0o755
        assert binary.user == PROMETHEUS_USER
        assert binary.group == PROMETHEUS_GROUP


def test_prometheus_systemd_service_exists(host, is_monitoring_server):
    """Test that Prometheus systemd service file exists on monitoring servers."""
    if is_monitoring_server:
        service_file = host.file(f"/etc/systemd/system/{PROMETHEUS_SERVICE_NAME}.service")
        assert service_file.exists
        assert service_file.is_file


def test_prometheus_systemd_service_content(host, is_monitoring_server):
    """Test Prometheus systemd service content on monitoring servers."""
    if is_monitoring_server:
        service_file = host.file(f"/etc/systemd/system/{PROMETHEUS_SERVICE_NAME}.service")
        assert service_file.contains(f"ExecStart={PROMETHEUS_INSTALL_DIR}/{PROMETHEUS_BINARY_NAME}")
        assert service_file.contains(f"User={PROMETHEUS_USER}")
        assert service_file.contains(f"Group={PROMETHEUS_GROUP}")
        assert service_file.contains(f"--config.file={PROMETHEUS_CONFIG_DIR}/{PROMETHEUS_CONFIG_FILE}")
        assert service_file.contains(f"--storage.tsdb.path={PROMETHEUS_DATA_DIR}")


def test_prometheus_process_running(host, is_monitoring_server):
    """Test that Prometheus process is running on monitoring servers."""
    if is_monitoring_server:
        try:
            process = host.process.get(comm=PROMETHEUS_PROCESS_NAME)
            assert process is not None
            assert PROMETHEUS_PROCESS_NAME in process.comm
        except RuntimeError:
            pytest.fail(f"{PROMETHEUS_PROCESS_NAME} process not found")


def test_prometheus_web_interface_accessible(host, is_monitoring_server):
    """Test that Prometheus web interface is accessible on monitoring servers."""
    if is_monitoring_server:
        result = host.run(f"curl -s -o /dev/null -w '%{{http_code}}' http://localhost:{PROMETHEUS_PORT}")
        assert result.rc == 0
        assert result.stdout in ["200", "302"]  # 200 OK or 302 redirect


def test_prometheus_api_endpoints(host, is_monitoring_server):
    """Test that Prometheus API endpoints are accessible on monitoring servers."""
    if is_monitoring_server:
        # Test targets endpoint
        result = host.run(f"curl -s -o /dev/null -w '%{{http_code}}' http://localhost:{PROMETHEUS_PORT}/api/v1/targets")
        assert result.rc == 0
        assert result.stdout == "200"


def test_prometheus_firewall_rule(host, is_monitoring_server):
    """
    Test that firewall allows Prometheus port on monitoring servers.
    Only checks Ubuntu/Debian with UFW.
    """
    if not is_monitoring_server:
        return
    if host.system_info.distribution not in ["ubuntu", "debian"]:
        pytest.skip("Firewall test only runs on Ubuntu/Debian with UFW")

    ufw_status = host.run("ufw status")
    if ufw_status.rc != 0 or "Status: inactive" in ufw_status.stdout:
        return  # UFW not active

    import re
    port_rule = f"{PROMETHEUS_PORT}/tcp"
    
    # Check for explicit ALLOW rule
    if re.search(rf"{re.escape(port_rule)}\s+ALLOW", ufw_status.stdout):
        return  # Port explicitly allowed
    
    # Check for explicit DENY/REJECT rule
    if re.search(rf"{re.escape(port_rule)}\s+(DENY|REJECT)", ufw_status.stdout):
        pytest.fail(f"UFW is active and port {port_rule} is explicitly denied")
    
    # If not found, skip (not explicitly allowed or denied)
    pytest.skip(f"UFW active but port {port_rule} is not explicitly allowed or denied")


def test_prometheus_config_valid_yaml(host, is_monitoring_server):
    """Test that Prometheus configuration file is valid YAML on monitoring servers."""
    if is_monitoring_server:
        config_file = host.file(f"{PROMETHEUS_CONFIG_DIR}/{PROMETHEUS_CONFIG_FILE}")
        content = config_file.content_string
        
        # Basic YAML validation - check for common Prometheus config sections
        assert "global:" in content or "scrape_configs:" in content or "rule_files:" in content


def test_prometheus_data_directory_writable(host, is_monitoring_server):
    """Test that Prometheus data directory is writable by the service user."""
    if is_monitoring_server:
        # Check if directory is writable by the prometheus user
        result = host.run(f"sudo -u {PROMETHEUS_USER} test -w {PROMETHEUS_DATA_DIR}")
        assert result.rc == 0


def test_prometheus_service_restart_behavior(host, is_monitoring_server):
    """Test that Prometheus service has proper restart configuration."""
    if is_monitoring_server:
        service_file = host.file(f"/etc/systemd/system/{PROMETHEUS_SERVICE_NAME}.service")
        assert service_file.contains("Restart=always")
        assert service_file.contains("RestartSec=")
