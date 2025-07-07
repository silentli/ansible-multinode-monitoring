"""
Tests for the MariaDB role.
"""
import pytest


@pytest.fixture
def mariadb_variant(host):
    """Determine which MariaDB/MySQL variant is installed and return its details."""
    # Check packages first
    mariadb_server = host.package("mariadb-server")
    mysql_server = host.package("mysql-server")
    
    if mariadb_server.is_installed:
        return {
            'type': 'mariadb',
            'service': host.service("mariadb"),
            'server_package': mariadb_server,
            'client_package': host.package("mariadb-client"),
            'config_file': host.file("/etc/mysql/mariadb.conf.d/50-server.cnf"),
            'socket_file': host.file("/var/run/mysqld/mysqld.sock")
        }
    elif mysql_server.is_installed:
        return {
            'type': 'mysql',
            'service': host.service("mysql"),
            'server_package': mysql_server,
            'client_package': host.package("mysql-client"),
            'config_file': host.file("/etc/mysql/mysql.conf.d/mysqld.cnf"),
            'socket_file': host.file("/var/run/mysql/mysql.sock")
        }
    else:
        pytest.skip("Neither MariaDB nor MySQL server package is installed")


def is_mariadb_process_running(host):
    """Check if MariaDB or MySQL process is running."""
    # Check for both mysqld and mariadbd processes
    #host.process.get(comm="<process_name>") raises RuntimeError if not found

    try:
        mysqld_process = host.process.get(comm="mysqld")
        return mysqld_process is not None
    except RuntimeError:
        try:
            mariadbd_process = host.process.get(comm="mariadbd")
            return mariadbd_process is not None
        except RuntimeError:
            return False


@pytest.mark.integration
def test_mariadb_package_installed(host, is_database_server, mariadb_variant):
    """Test that MariaDB/MySQL package is installed on database servers."""
    if is_database_server:
        assert mariadb_variant['server_package'].is_installed


@pytest.mark.integration
def test_mariadb_client_package_installed(host, is_database_server, mariadb_variant):
    """Test that MariaDB/MySQL client package is installed on database servers."""
    if is_database_server:
        assert mariadb_variant['client_package'].is_installed


@pytest.mark.integration
def test_mariadb_service_running(host, is_database_server, mariadb_variant):
    """Test that MariaDB/MySQL service is running on database servers."""
    if is_database_server:
        assert mariadb_variant['service'].is_running
        assert mariadb_variant['service'].is_enabled


@pytest.mark.integration
def test_mariadb_port_listening(host, is_database_server):
    """Test that MariaDB/MySQL is listening on the correct port on database servers."""
    if is_database_server:
        socket = host.socket("tcp://0.0.0.0:3306")
        assert socket.is_listening


@pytest.mark.integration
def test_mariadb_config_file_exists(host, is_database_server, mariadb_variant):
    """Test that MariaDB/MySQL configuration file exists on database servers."""
    if is_database_server:
        assert mariadb_variant['config_file'].exists


@pytest.mark.integration
def test_mariadb_config_content(host, is_database_server, mariadb_variant):
    """Test MariaDB/MySQL configuration content on database servers."""
    if is_database_server:
        if mariadb_variant['config_file'].exists:
            # Check for bind-address with flexible whitespace
            config_content = mariadb_variant['config_file'].content_string
            assert "bind-address" in config_content
            assert "0.0.0.0" in config_content


@pytest.mark.integration
def test_mariadb_data_directory(host, is_database_server):
    """Test that MariaDB/MySQL data directory exists and has correct permissions on database servers."""
    if is_database_server:
        data_dir = host.file("/var/lib/mysql")
        assert data_dir.exists
        assert data_dir.is_directory
        assert data_dir.user == "mysql"
        assert data_dir.group == "mysql"


@pytest.mark.integration
def test_mariadb_process_running(host, is_database_server):
    """Test that MariaDB/MySQL process is running on database servers."""
    if is_database_server:
        assert is_mariadb_process_running(host)


@pytest.mark.integration
def test_mariadb_socket_exists(host, is_database_server, mariadb_variant):
    """Test that MariaDB/MySQL socket file exists on database servers."""
    if is_database_server:
        assert mariadb_variant['socket_file'].exists


@pytest.mark.integration
def test_mariadb_firewall_rule(host, is_database_server):
    """Test that firewall allows MariaDB/MySQL port on database servers."""
    if is_database_server:
        ufw_status = host.run("ufw status")
        if ufw_status.rc == 0 and "Status: active" in ufw_status.stdout:
            assert "3306/tcp" in ufw_status.stdout
