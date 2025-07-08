"""
Tests for the Mock Service role.
"""
import pytest
import os
from dotenv import load_dotenv

load_dotenv()

# Load configuration from environment variables - will raise KeyError if missing
MOCK_SERVICE_USER = os.environ["MOCK_SERVICE_USER"]
MOCK_SERVICE_GROUP = os.environ["MOCK_SERVICE_GROUP"]
MOCK_SERVICE_WORKING_DIR = os.environ["MOCK_SERVICE_WORKING_DIR"]
MOCK_SERVICE_SCRIPT_PATH = os.environ["MOCK_SERVICE_SCRIPT_PATH"]
MOCK_SERVICE_LOG_FILE = os.environ["MOCK_SERVICE_LOG_FILE"]
MOCK_SERVICE_PORT = os.environ["MOCK_SERVICE_PORT"]
MOCK_SERVICE_SYSTEMD_SERVICE = os.environ["MOCK_SERVICE_SYSTEMD_SERVICE"]
MOCK_SERVICE_NAME = os.environ["MOCK_SERVICE_NAME"]

def test_mock_service_running(host, is_mock_service_server):
    """Test that Mock Service is running and enabled."""
    if is_mock_service_server:
        service = host.service(MOCK_SERVICE_NAME)
        assert service.is_running
        assert service.is_enabled

def test_mock_service_port_listening(host, is_mock_service_server):
    """Test that Mock Service is listening on the correct port."""
    if is_mock_service_server:
        socket = host.socket(f"tcp://0.0.0.0:{MOCK_SERVICE_PORT}")
        assert socket.is_listening

def test_mock_service_user_and_group(host, is_mock_service_server):
    """Test that Mock Service user and group exist."""
    if is_mock_service_server:
        user = host.user(MOCK_SERVICE_USER)
        group = host.group(MOCK_SERVICE_GROUP)
        assert user.exists
        assert group.exists

def test_mock_service_files_and_permissions(host, is_mock_service_server):
    """Test that Mock Service files exist with correct permissions."""
    if is_mock_service_server:
        # Test script file
        script = host.file(MOCK_SERVICE_SCRIPT_PATH)
        assert script.exists
        assert script.is_file
        assert script.mode == 0o755
        assert script.user == MOCK_SERVICE_USER
        assert script.group == MOCK_SERVICE_GROUP
        
        # Test systemd service file
        service_file = host.file(MOCK_SERVICE_SYSTEMD_SERVICE)
        assert service_file.exists
        assert service_file.is_file
        
        # Test working directory
        work_dir = host.file(MOCK_SERVICE_WORKING_DIR)
        assert work_dir.exists
        assert work_dir.is_directory
        assert work_dir.user == MOCK_SERVICE_USER
        assert work_dir.group == MOCK_SERVICE_GROUP
        
        # Test log file
        log_file = host.file(MOCK_SERVICE_LOG_FILE)
        assert log_file.exists

def test_mock_service_systemd_configuration(host, is_mock_service_server):
    """Test Mock Service systemd service configuration."""
    if is_mock_service_server:
        service_file = host.file(MOCK_SERVICE_SYSTEMD_SERVICE)
        assert service_file.contains(MOCK_SERVICE_SCRIPT_PATH)
        assert service_file.contains(f"User={MOCK_SERVICE_USER}")
        assert service_file.contains(f"Group={MOCK_SERVICE_GROUP}")

def test_mock_service_endpoints(host, is_mock_service_server):
    """Test that Mock Service HTTP endpoints are accessible."""
    if is_mock_service_server:
        # Test root endpoint
        result = host.run(f"curl -s -o /dev/null -w '%{{http_code}}' http://localhost:{MOCK_SERVICE_PORT}")
        assert result.rc == 0
        assert result.stdout == "200"
        
        # Test health endpoint
        result = host.run(f"curl -s -o /dev/null -w '%{{http_code}}' http://localhost:{MOCK_SERVICE_PORT}/health")
        assert result.rc == 0
        assert result.stdout == "200"
        
        # Test metrics endpoint
        result = host.run(f"curl -s -o /dev/null -w '%{{http_code}}' http://localhost:{MOCK_SERVICE_PORT}/metrics")
        assert result.rc == 0
        assert result.stdout == "200"

def test_mock_service_metrics_format(host, is_mock_service_server):
    """Test that Mock Service returns proper Prometheus metrics format."""
    if is_mock_service_server:
        result = host.run(f"curl -s http://localhost:{MOCK_SERVICE_PORT}/metrics")
        assert result.rc == 0
        # Check for Prometheus metrics format
        assert "# HELP" in result.stdout
        assert "# TYPE" in result.stdout
        assert "mock_service_" in result.stdout 
