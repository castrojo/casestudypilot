"""Tests for MCP client for CNCF Landscape server integration."""

import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from casestudypilot.mcp_client import MCPClient


# =============================================================================
# Unit Tests (No Docker Required - Mocked)
# =============================================================================


def test_mcp_client_initialization():
    """Test that MCPClient can be initialized with docker command."""
    client = MCPClient()
    assert client is not None
    assert client.is_connected() is False


def test_mcp_client_initialization_custom_params():
    """Test MCPClient initialization with custom parameters."""
    client = MCPClient(docker_image="custom/image:tag", data_url="https://custom.url/data.json")
    assert client.docker_image == "custom/image:tag"
    assert client.data_url == "https://custom.url/data.json"
    assert client.is_connected() is False


@patch("casestudypilot.mcp_client.subprocess.Popen")
@patch("casestudypilot.mcp_client.ClientSession")
@patch("casestudypilot.mcp_client.stdio_client")
def test_mcp_client_connect(mock_stdio_client, mock_client_session, mock_popen):
    """Test that MCPClient can connect to landscape MCP server."""
    # Setup mocks
    mock_process = MagicMock()
    mock_popen.return_value = mock_process

    mock_session = AsyncMock()
    mock_client_session.return_value = mock_session

    mock_stdio_client.return_value = MagicMock()

    client = MCPClient()

    with client.connect():
        assert client.is_connected() is True
        # Verify Docker command was called correctly
        mock_popen.assert_called_once()
        call_args = mock_popen.call_args
        assert "docker" in call_args[0][0]
        assert "run" in call_args[0][0]
        assert "-i" in call_args[0][0]
        assert "--rm" in call_args[0][0]
        assert "ghcr.io/cncf/landscape-mcp-server:main" in call_args[0][0]

    # After exiting context, should be disconnected
    assert client.is_connected() is False
    mock_process.terminate.assert_called_once()


@patch("casestudypilot.mcp_client.subprocess.Popen")
@patch("casestudypilot.mcp_client.ClientSession")
@patch("casestudypilot.mcp_client.stdio_client")
def test_query_members_not_connected(mock_stdio_client, mock_client_session, mock_popen):
    """Test that query_members raises error when not connected."""
    client = MCPClient()

    with pytest.raises(RuntimeError, match="Client not connected"):
        client.query_members(tier="End User Supporter")


@patch("casestudypilot.mcp_client.subprocess.Popen")
@patch("casestudypilot.mcp_client.ClientSession")
@patch("casestudypilot.mcp_client.stdio_client")
def test_query_projects_not_connected(mock_stdio_client, mock_client_session, mock_popen):
    """Test that query_projects raises error when not connected."""
    client = MCPClient()

    with pytest.raises(RuntimeError, match="Client not connected"):
        client.query_projects(maturity="graduated")


@patch("casestudypilot.mcp_client.subprocess.Popen")
@patch("casestudypilot.mcp_client.ClientSession")
@patch("casestudypilot.mcp_client.stdio_client")
def test_get_project_details_not_connected(mock_stdio_client, mock_client_session, mock_popen):
    """Test that get_project_details raises error when not connected."""
    client = MCPClient()

    with pytest.raises(RuntimeError, match="Client not connected"):
        client.get_project_details("Kubernetes")


# =============================================================================
# Integration Tests (Require Docker - Mark with @pytest.mark.integration)
# =============================================================================


@pytest.mark.integration
def test_query_members_end_user():
    """Integration test: Query End User Supporter members."""
    client = MCPClient()
    with client.connect():
        members = client.query_members(tier="End User Supporter", limit=10)

        assert len(members) > 0
        assert all("name" in m for m in members)
        assert all("joined_at" in m for m in members)


@pytest.mark.integration
def test_query_projects_graduated():
    """Integration test: Query graduated projects."""
    client = MCPClient()
    with client.connect():
        projects = client.query_projects(maturity="graduated", limit=10)

        assert len(projects) > 0
        assert all("name" in p for p in projects)
        assert all(p["maturity"] == "graduated" for p in projects)


@pytest.mark.integration
def test_get_project_details_kubernetes():
    """Integration test: Get Kubernetes project details."""
    client = MCPClient()
    with client.connect():
        project = client.get_project_details("Kubernetes")

        assert project is not None
        assert project["name"] == "Kubernetes"
        assert project["maturity"] == "graduated"
        assert "graduated_at" in project
