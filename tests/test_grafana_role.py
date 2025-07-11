"""
Tests for the Grafana role.
"""
import pytest
import os
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# Load configuration from environment variables - will raise KeyError if missing
GRAFANA_USER = os.environ["GRAFANA_USER"]
GRAFANA_GROUP = os.environ["GRAFANA_GROUP"]
GRAFANA_SERVICE_NAME = os.environ["GRAFANA_SERVICE_NAME"]
GRAFANA_PORT = os.environ["GRAFANA_PORT"]
GRAFANA_CONFIG_DIR = os.environ["GRAFANA_CONFIG_DIR"]
GRAFANA_DATA_DIR = os.environ["GRAFANA_DATA_DIR"]
GRAFANA_LOG_DIR = os.environ["GRAFANA_LOG_DIR"]

# Standard Grafana values
GRAFANA_PACKAGE_NAME = "grafana"
GRAFANA_PROCESS_NAME = "grafana"
GRAFANA_CONFIG_FILE = "grafana.ini"
GRAFANA_API_HEALTH_ENDPOINT = "/api/health"


def test_grafana_package_installed(host, is_monitoring_server):
    """Test that Grafana package is installed on monitoring servers."""
    if is_monitoring_server:
        package = host.package(GRAFANA_PACKAGE_NAME)
        assert package.is_installed


def test_grafana_service_running(host, is_monitoring_server):
    """Test that Grafana service is running and enabled on monitoring servers."""
    if is_monitoring_server:
        service = host.service(GRAFANA_SERVICE_NAME)
        assert service.is_running
        assert service.is_enabled


def test_grafana_port_listening(host, is_monitoring_server):
    """Test that Grafana is listening on the correct port on monitoring servers."""
    if is_monitoring_server:
        socket = host.socket(f"tcp://0.0.0.0:{GRAFANA_PORT}")
        assert socket.is_listening


def test_grafana_user_and_group(host, is_monitoring_server):
    """Test that Grafana user and group exist on monitoring servers."""
    if is_monitoring_server:
        user = host.user(GRAFANA_USER)
        group = host.group(GRAFANA_GROUP)
        assert user.exists
        assert group.exists


def test_grafana_directories_and_permissions(host, is_monitoring_server):
    """Test that Grafana directories exist with correct permissions on monitoring servers."""
    if is_monitoring_server:
        # Test data directory
        data_dir = host.file(GRAFANA_DATA_DIR)
        assert data_dir.exists
        assert data_dir.is_directory
        assert data_dir.user == GRAFANA_USER
        assert data_dir.group == GRAFANA_GROUP
        
        # Test log directory
        log_dir = host.file(GRAFANA_LOG_DIR)
        assert log_dir.exists
        assert log_dir.is_directory
        
        # Test config directory
        config_dir = host.file(GRAFANA_CONFIG_DIR)
        assert config_dir.exists
        assert config_dir.is_directory


def test_grafana_config_file_exists(host, is_monitoring_server):
    """Test that Grafana configuration file exists on monitoring servers."""
    if is_monitoring_server:
        config_file = host.file(f"{GRAFANA_CONFIG_DIR}/{GRAFANA_CONFIG_FILE}")
        assert config_file.exists
        assert config_file.is_file


def test_grafana_systemd_service_exists(host, is_monitoring_server):
    """Test that Grafana systemd service file exists on monitoring servers."""
    if is_monitoring_server:
        # Check common systemd service locations
        service_locations = [
            f"/etc/systemd/system/{GRAFANA_SERVICE_NAME}.service",
            f"/lib/systemd/system/{GRAFANA_SERVICE_NAME}.service"
        ]
        
        service_exists = False
        for location in service_locations:
            service_file = host.file(location)
            if service_file.exists:
                service_exists = True
                break
        
        assert service_exists


def test_grafana_process_running(host, is_monitoring_server):
    """Test that Grafana process is running on monitoring servers."""
    if is_monitoring_server:
        try:
            process = host.process.get(comm=GRAFANA_PROCESS_NAME)
            assert process is not None
            assert GRAFANA_PROCESS_NAME in process.comm
        except RuntimeError:
            # Process not found, which is a failure
            assert False, f"{GRAFANA_PROCESS_NAME} process not found"


def test_grafana_web_interface_accessible(host, is_monitoring_server):
    """Test that Grafana web interface is accessible on monitoring servers."""
    if is_monitoring_server:
        result = host.run(f"curl -s -o /dev/null -w '%{{http_code}}' http://localhost:{GRAFANA_PORT}")
        assert result.rc == 0
        assert result.stdout in ["200", "302"]  # 200 OK or 302 redirect


def test_grafana_api_endpoints(host, is_monitoring_server):
    """Test that Grafana API endpoints are accessible on monitoring servers."""
    if is_monitoring_server:
        # Test health endpoint
        result = host.run(f"curl -s -o /dev/null -w '%{{http_code}}' http://localhost:{GRAFANA_PORT}{GRAFANA_API_HEALTH_ENDPOINT}")
        assert result.rc == 0
        assert result.stdout == "200"


def test_grafana_firewall_rule(host, is_monitoring_server):
    """Test that firewall allows Grafana port on monitoring servers."""
    if is_monitoring_server:
        ufw_status = host.run("ufw status")
        if ufw_status.rc == 0 and "Status: active" in ufw_status.stdout:
            assert f"{GRAFANA_PORT}/tcp" in ufw_status.stdout


def test_grafana_plugins_directory(host, is_monitoring_server):
    """Test that Grafana plugins directory exists on monitoring servers."""
    if is_monitoring_server:
        plugins_dir = host.file(f"{GRAFANA_DATA_DIR}/plugins")
        assert plugins_dir.exists
        assert plugins_dir.is_directory
