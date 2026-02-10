# Landscape MCP Server Integration Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Replace direct CNCF Landscape API calls with the CNCF Landscape MCP server as the single source of truth for CNCF membership, projects, and metadata.

**Architecture:** Add MCP client integration layer in Python, refactor existing company verification and project validation to use MCP tools (`query_members`, `query_projects`, `get_project_details`), update skills to reference MCP as authoritative source, and document integration for future agents.

**Tech Stack:** Python 3.11+, MCP Python SDK (mcp), Docker (landscape-mcp-server), existing casestudypilot CLI architecture

**Epic Issue:** #20

---

## Background: Current vs. Target Architecture

### Current State
- **Company Verification:** Direct HTTP call to `https://landscape.cncf.io/api/data.json`, extracts "End User" members, fuzzy matches company names
- **Project Identification:** LLM-based extraction in `transcript-analysis` skill with hardcoded project list, Python validation against hardcoded list (50+ projects)
- **Project Hyperlinks:** Hardcoded mapping in `hyperlinks.py` (19 projects)
- **No Real-Time Data:** Cached API responses, manual updates to hardcoded lists

### Target State
- **Company Verification:** MCP `query_members` tool with `tier="End User Supporter"` filter
- **Project Identification:** MCP `query_projects` tool for validation, `get_project_details` for enrichment
- **Project Hyperlinks:** Dynamic from MCP project data (if available)
- **Real-Time Data:** MCP server auto-fetches latest landscape data on startup
- **Single Source of Truth:** All CNCF data flows through MCP server

### MCP Server Capabilities

**Available Tools:**
1. `query_projects` - Filter projects by maturity, name, dates (graduated/incubating/accepted)
2. `query_members` - Filter members by tier, join dates
3. `get_project_details` - Get detailed info for specific project by name
4. `project_metrics` - Aggregate metrics (incubating count, sandbox joined this year, etc.)
5. `membership_metrics` - Aggregate metrics (gold/silver members joined/raised)

**Data Structure (from MCP):**
```json
// Project
{
  "name": "Kubernetes",
  "category": "CNCF Projects",
  "subcategory": "Orchestration & Management",
  "maturity": "graduated",
  "accepted_at": "2016-03-10",
  "incubating_at": "2017-03-01",
  "graduated_at": "2018-03-06"
}

// Member
{
  "name": "Company Name",
  "category": "CNCF Members",
  "subcategory": "End User Supporter",
  "member_subcategory": "End User Supporter",
  "joined_at": "2023-05-15"
}
```

---

## Task 1: Add MCP Client Infrastructure

**Files:**
- Create: `casestudypilot/mcp_client.py`
- Create: `tests/test_mcp_client.py`
- Modify: `requirements.txt` (add MCP SDK dependency)
- Create: `docker-compose.yml` (for local MCP server development)

**Step 1: Add MCP SDK dependency**

Modify `requirements.txt`:
```
mcp>=0.1.0
```

Run: `pip install -r requirements.txt`
Expected: MCP SDK installed successfully

**Step 2: Create docker-compose.yml for local development**

Create `docker-compose.yml`:
```yaml
version: '3.8'
services:
  landscape-mcp:
    image: ghcr.io/cncf/landscape-mcp-server:main
    command:
      - "--data-url"
      - "https://landscape.cncf.io/data/full.json"
    stdin_open: true
    tty: true
    ports:
      - "3000:3000"
```

**Step 3: Write failing test for MCP client initialization**

Create `tests/test_mcp_client.py`:
```python
import pytest
from casestudypilot.mcp_client import MCPClient

def test_mcp_client_initialization():
    """Test that MCPClient can be initialized with docker command"""
    client = MCPClient()
    assert client is not None
    assert client.is_connected() is False

def test_mcp_client_connect():
    """Test that MCPClient can connect to landscape MCP server"""
    client = MCPClient()
    with client.connect():
        assert client.is_connected() is True
```

Run: `pytest tests/test_mcp_client.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'casestudypilot.mcp_client'"

**Step 4: Implement minimal MCP client**

Create `casestudypilot/mcp_client.py`:
```python
"""MCP client for CNCF Landscape server integration."""

import json
import subprocess
from contextlib import contextmanager
from typing import Any, Dict, List, Optional

from mcp import Client
from mcp.client.stdio import stdio_client


class MCPClient:
    """Client for interacting with CNCF Landscape MCP server."""

    def __init__(
        self,
        docker_image: str = "ghcr.io/cncf/landscape-mcp-server:main",
        data_url: str = "https://landscape.cncf.io/data/full.json",
    ):
        """Initialize MCP client with docker configuration.
        
        Args:
            docker_image: Docker image for landscape MCP server
            data_url: URL to CNCF landscape data JSON
        """
        self.docker_image = docker_image
        self.data_url = data_url
        self._client: Optional[Client] = None
        self._connected = False

    def is_connected(self) -> bool:
        """Check if client is connected to MCP server."""
        return self._connected

    @contextmanager
    def connect(self):
        """Context manager for MCP server connection.
        
        Yields:
            Self for method chaining
            
        Example:
            with client.connect():
                members = client.query_members(tier="End User Supporter")
        """
        # Docker command to run MCP server in stdio mode
        command = [
            "docker",
            "run",
            "-i",
            "--rm",
            self.docker_image,
            "--data-url",
            self.data_url,
        ]

        try:
            # Start MCP server via stdio
            self._process = subprocess.Popen(
                command,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            
            # Create MCP client connection
            self._client = Client(stdio_client(self._process))
            self._connected = True
            
            yield self
            
        finally:
            self._connected = False
            if self._process:
                self._process.terminate()
                self._process.wait(timeout=5)

    def query_members(
        self,
        tier: Optional[str] = None,
        joined_from: Optional[str] = None,
        joined_to: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """Query CNCF members with filters.
        
        Args:
            tier: Membership tier (e.g., "End User Supporter", "Gold", "Silver")
            joined_from: Filter members joined on/after date (YYYY-MM-DD)
            joined_to: Filter members joined on/before date (YYYY-MM-DD)
            limit: Maximum results (default 100)
            
        Returns:
            List of member dictionaries with name, category, subcategory, joined_at
            
        Raises:
            RuntimeError: If client not connected
        """
        if not self._connected or not self._client:
            raise RuntimeError("Client not connected. Use connect() context manager.")

        args = {"limit": limit}
        if tier:
            args["tier"] = tier
        if joined_from:
            args["joined_from"] = joined_from
        if joined_to:
            args["joined_to"] = joined_to

        result = self._client.call_tool("query_members", args)
        
        # Parse JSON response from MCP tool
        response = json.loads(result["content"][0]["text"])
        return response["members"]

    def query_projects(
        self,
        maturity: Optional[str] = None,
        name: Optional[str] = None,
        graduated_from: Optional[str] = None,
        graduated_to: Optional[str] = None,
        incubating_from: Optional[str] = None,
        incubating_to: Optional[str] = None,
        accepted_from: Optional[str] = None,
        accepted_to: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """Query CNCF projects with filters.
        
        Args:
            maturity: Project maturity (graduated, incubating, sandbox)
            name: Filter by project name (case-insensitive substring)
            graduated_from: Filter projects graduated on/after date (YYYY-MM-DD)
            graduated_to: Filter projects graduated on/before date (YYYY-MM-DD)
            incubating_from: Filter projects incubating on/after date (YYYY-MM-DD)
            incubating_to: Filter projects incubating on/before date (YYYY-MM-DD)
            accepted_from: Filter projects accepted on/after date (YYYY-MM-DD)
            accepted_to: Filter projects accepted on/before date (YYYY-MM-DD)
            limit: Maximum results (default 100)
            
        Returns:
            List of project dictionaries with name, category, maturity, dates
            
        Raises:
            RuntimeError: If client not connected
        """
        if not self._connected or not self._client:
            raise RuntimeError("Client not connected. Use connect() context manager.")

        args = {"limit": limit}
        if maturity:
            args["maturity"] = maturity
        if name:
            args["name"] = name
        if graduated_from:
            args["graduated_from"] = graduated_from
        if graduated_to:
            args["graduated_to"] = graduated_to
        if incubating_from:
            args["incubating_from"] = incubating_from
        if incubating_to:
            args["incubating_to"] = incubating_to
        if accepted_from:
            args["accepted_from"] = accepted_from
        if accepted_to:
            args["accepted_to"] = accepted_to

        result = self._client.call_tool("query_projects", args)
        
        # Parse JSON response from MCP tool
        response = json.loads(result["content"][0]["text"])
        return response["projects"]

    def get_project_details(self, name: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific project.
        
        Args:
            name: Project name to search (case-insensitive)
            
        Returns:
            Project dictionary with details or None if not found
            
        Raises:
            RuntimeError: If client not connected
        """
        if not self._connected or not self._client:
            raise RuntimeError("Client not connected. Use connect() context manager.")

        result = self._client.call_tool("get_project_details", {"name": name})
        
        # Parse JSON response from MCP tool
        response = json.loads(result["content"][0]["text"])
        projects = response["projects"]
        
        return projects[0] if projects else None
```

**Step 5: Run tests to verify implementation**

Run: `pytest tests/test_mcp_client.py -v`
Expected: PASS (tests may need Docker running; consider mocking for CI)

**Step 6: Add integration test with real MCP server**

Append to `tests/test_mcp_client.py`:
```python
@pytest.mark.integration
def test_query_members_end_user():
    """Integration test: Query End User Supporter members"""
    client = MCPClient()
    with client.connect():
        members = client.query_members(tier="End User Supporter", limit=10)
        
        assert len(members) > 0
        assert all("name" in m for m in members)
        assert all("joined_at" in m for m in members)

@pytest.mark.integration
def test_query_projects_graduated():
    """Integration test: Query graduated projects"""
    client = MCPClient()
    with client.connect():
        projects = client.query_projects(maturity="graduated", limit=10)
        
        assert len(projects) > 0
        assert all("name" in p for p in projects)
        assert all(p["maturity"] == "graduated" for p in projects)

@pytest.mark.integration
def test_get_project_details_kubernetes():
    """Integration test: Get Kubernetes project details"""
    client = MCPClient()
    with client.connect():
        project = client.get_project_details("Kubernetes")
        
        assert project is not None
        assert project["name"] == "Kubernetes"
        assert project["maturity"] == "graduated"
        assert "graduated_at" in project
```

Run: `pytest tests/test_mcp_client.py -v -m integration` (requires Docker)
Expected: PASS with real MCP server data

**Step 7: Commit MCP client infrastructure**

```bash
git add casestudypilot/mcp_client.py tests/test_mcp_client.py requirements.txt docker-compose.yml
git commit -m "feat: add MCP client for CNCF Landscape server integration"
```

---

## Task 2: Refactor Company Verification to Use MCP

**Files:**
- Modify: `casestudypilot/tools/company_verifier.py`
- Modify: `tests/test_company_verifier.py`

**Step 1: Write failing test for MCP-based verification**

Modify `tests/test_company_verifier.py` (add new test):
```python
from unittest.mock import MagicMock, patch

def test_verify_company_with_mcp():
    """Test company verification using MCP client"""
    with patch('casestudypilot.tools.company_verifier.MCPClient') as mock_mcp:
        # Mock MCP response
        mock_client = MagicMock()
        mock_client.query_members.return_value = [
            {"name": "Intuit Inc.", "joined_at": "2023-05-15"},
            {"name": "Adobe Inc.", "joined_at": "2022-09-10"},
        ]
        mock_mcp.return_value.__enter__.return_value = mock_client
        
        result = verify_company("Intuit")
        
        assert result["is_member"] is True
        assert result["matched_name"] == "Intuit Inc."
        assert result["confidence"] >= 0.70
        assert result["match_method"] in ["exact", "fuzzy"]
```

Run: `pytest tests/test_company_verifier.py::test_verify_company_with_mcp -v`
Expected: FAIL (function not yet updated to use MCP)

**Step 2: Refactor verify_company to use MCP client**

Modify `casestudypilot/tools/company_verifier.py`:

1. Add import at top:
```python
from casestudypilot.mcp_client import MCPClient
```

2. Replace `fetch_landscape_data()` and `extract_enduser_members()` usage:

```python
def verify_company(company_name: str) -> Dict[str, Any]:
    """Verify if a company is a CNCF end-user member using MCP server.
    
    Args:
        company_name: Company name to verify
        
    Returns:
        Dictionary with verification results:
        {
            "query_name": str,
            "matched_name": str,
            "confidence": float,
            "is_member": bool,
            "match_method": "exact|fuzzy|none",
            "joined_at": str (optional)
        }
    """
    try:
        # Query End User Supporter members from MCP server
        with MCPClient().connect() as client:
            members = client.query_members(tier="End User Supporter", limit=1000)
        
        # Extract member names
        member_names = [m["name"] for m in members]
        
        # Find best match
        match_result = find_best_match(company_name, member_names)
        
        # Enrich with joined_at date if match found
        if match_result["is_member"]:
            for member in members:
                if member["name"] == match_result["matched_name"]:
                    match_result["joined_at"] = member.get("joined_at")
                    break
        
        return match_result
        
    except Exception as e:
        # Fallback to legacy API if MCP fails
        logging.warning(f"MCP verification failed, using legacy API: {e}")
        landscape_data = fetch_landscape_data()
        member_list = extract_enduser_members(landscape_data)
        return find_best_match(company_name, member_list)
```

**Step 3: Run tests to verify MCP integration**

Run: `pytest tests/test_company_verifier.py -v`
Expected: PASS (mocked tests should work)

**Step 4: Add integration test with real MCP**

Append to `tests/test_company_verifier.py`:
```python
@pytest.mark.integration
def test_verify_company_integration():
    """Integration test: Verify real company using MCP"""
    # Test with known CNCF member (update with current member)
    result = verify_company("Intuit")
    
    # Assertions may vary based on current membership
    assert "is_member" in result
    assert "matched_name" in result
    assert "confidence" in result
    assert "match_method" in result
```

Run: `pytest tests/test_company_verifier.py -v -m integration`
Expected: PASS with real MCP data

**Step 5: Update CLI command to show joined_at date**

Modify `casestudypilot/__main__.py` in `verify_company_command`:

```python
def verify_company_command(company_name: str):
    """CLI command for verify-company"""
    result = verify_company(company_name)
    
    # Save to JSON
    with open("company_verification.json", "w") as f:
        json.dump(result, f, indent=2)
    
    # Print result with joined_at if available
    if result["is_member"]:
        joined_info = f" (joined {result['joined_at']})" if "joined_at" in result else ""
        print(f"✅ {result['matched_name']} is a CNCF member{joined_info}")
        print(f"   Match confidence: {result['confidence']:.2f} ({result['match_method']})")
        sys.exit(0)
    else:
        print(f"❌ {company_name} is not a CNCF member")
        sys.exit(1)
```

**Step 6: Commit company verification refactor**

```bash
git add casestudypilot/tools/company_verifier.py tests/test_company_verifier.py casestudypilot/__main__.py
git commit -m "refactor: use MCP server for company verification with joined_at enrichment"
```

---

## Task 3: Add MCP-Based Project Validation CLI Tool

**Files:**
- Create: `casestudypilot/tools/mcp_project_validator.py`
- Create: `tests/test_mcp_project_validator.py`
- Modify: `casestudypilot/__main__.py` (add CLI command)

**Step 1: Write failing test for project validation**

Create `tests/test_mcp_project_validator.py`:
```python
import pytest
from casestudypilot.tools.mcp_project_validator import (
    validate_projects,
    get_all_cncf_projects,
)

def test_validate_projects_all_valid():
    """Test validation when all projects are CNCF projects"""
    projects = ["Kubernetes", "Prometheus", "Envoy"]
    
    result = validate_projects(projects)
    
    assert result["valid_count"] == 3
    assert result["invalid_count"] == 0
    assert len(result["valid_projects"]) == 3
    assert result["is_valid"] is True

def test_validate_projects_some_invalid():
    """Test validation when some projects are not CNCF projects"""
    projects = ["Kubernetes", "InvalidProject", "Prometheus"]
    
    result = validate_projects(projects)
    
    assert result["valid_count"] == 2
    assert result["invalid_count"] == 1
    assert "InvalidProject" in result["invalid_projects"]
    assert result["is_valid"] is False

def test_get_all_cncf_projects():
    """Test fetching all CNCF projects from MCP"""
    projects = get_all_cncf_projects()
    
    assert len(projects) > 0
    assert all("name" in p for p in projects)
    assert all("maturity" in p for p in projects)
```

Run: `pytest tests/test_mcp_project_validator.py -v`
Expected: FAIL with "ModuleNotFoundError"

**Step 2: Implement MCP project validator**

Create `casestudypilot/tools/mcp_project_validator.py`:
```python
"""Project validation using CNCF Landscape MCP server."""

from typing import Dict, List, Any
from casestudypilot.mcp_client import MCPClient


def get_all_cncf_projects(cache: bool = True) -> List[Dict[str, Any]]:
    """Get all CNCF projects from MCP server.
    
    Args:
        cache: Whether to use cached results (default True)
        
    Returns:
        List of all CNCF projects with name, maturity, dates
    """
    # TODO: Implement caching mechanism for performance
    with MCPClient().connect() as client:
        # Query all projects (no filters, high limit)
        projects = client.query_projects(limit=1000)
    
    return projects


def validate_projects(project_names: List[str]) -> Dict[str, Any]:
    """Validate that project names are CNCF projects using MCP.
    
    Args:
        project_names: List of project names to validate
        
    Returns:
        Dictionary with validation results:
        {
            "valid_count": int,
            "invalid_count": int,
            "valid_projects": [{"name": str, "maturity": str, ...}],
            "invalid_projects": [str],
            "is_valid": bool (True if all valid)
        }
    """
    all_projects = get_all_cncf_projects()
    
    # Create case-insensitive lookup
    project_lookup = {
        p["name"].lower(): p for p in all_projects
    }
    
    valid_projects = []
    invalid_projects = []
    
    for name in project_names:
        name_lower = name.lower()
        
        # Check exact match first
        if name_lower in project_lookup:
            valid_projects.append(project_lookup[name_lower])
        else:
            # Try fuzzy match (substring)
            found = False
            for project_name, project_data in project_lookup.items():
                if name_lower in project_name or project_name in name_lower:
                    valid_projects.append(project_data)
                    found = True
                    break
            
            if not found:
                invalid_projects.append(name)
    
    return {
        "valid_count": len(valid_projects),
        "invalid_count": len(invalid_projects),
        "valid_projects": valid_projects,
        "invalid_projects": invalid_projects,
        "is_valid": len(invalid_projects) == 0,
    }


def enrich_project_with_details(project_name: str) -> Dict[str, Any]:
    """Get detailed project information from MCP server.
    
    Args:
        project_name: Project name to look up
        
    Returns:
        Project details dictionary or empty dict if not found
    """
    with MCPClient().connect() as client:
        project = client.get_project_details(project_name)
    
    return project if project else {}
```

**Step 3: Run tests to verify implementation**

Run: `pytest tests/test_mcp_project_validator.py -v`
Expected: Tests should now pass (may need mocking for unit tests)

**Step 4: Add CLI command for project validation**

Modify `casestudypilot/__main__.py`, add new command:
```python
@app.command()
def validate_projects(
    projects_json: str = typer.Argument(..., help="Path to JSON file with project names array")
):
    """Validate that project names are CNCF projects using MCP server.
    
    Exit codes:
    - 0: All projects are valid CNCF projects
    - 1: Some projects are invalid (WARNING)
    - 2: Most projects are invalid or validation error (CRITICAL)
    """
    try:
        # Load project names from JSON
        with open(projects_json, "r") as f:
            data = json.load(f)
        
        # Extract project names (support both array and analysis format)
        if isinstance(data, list):
            project_names = data
        elif "cncf_projects" in data:
            project_names = [p["name"] for p in data["cncf_projects"]]
        else:
            print("❌ Invalid JSON format", file=sys.stderr)
            sys.exit(2)
        
        # Validate using MCP
        from casestudypilot.tools.mcp_project_validator import validate_projects
        result = validate_projects(project_names)
        
        # Determine exit code
        if result["is_valid"]:
            print(f"✅ All {result['valid_count']} projects are valid CNCF projects")
            sys.exit(0)
        
        # Calculate invalid ratio
        total = result["valid_count"] + result["invalid_count"]
        invalid_ratio = result["invalid_count"] / total if total > 0 else 1.0
        
        if invalid_ratio > 0.5:
            # CRITICAL: More than 50% invalid
            print(f"❌ CRITICAL: {result['invalid_count']}/{total} projects are invalid")
            print(f"   Invalid projects: {', '.join(result['invalid_projects'])}")
            sys.exit(2)
        else:
            # WARNING: Some invalid
            print(f"⚠️  WARNING: {result['invalid_count']}/{total} projects are invalid")
            print(f"   Invalid projects: {', '.join(result['invalid_projects'])}")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Validation error: {e}", file=sys.stderr)
        sys.exit(2)
```

**Step 5: Test CLI command**

Create test file `test_projects.json`:
```json
["Kubernetes", "Prometheus", "Envoy"]
```

Run: `python -m casestudypilot validate-projects test_projects.json`
Expected: "✅ All 3 projects are valid CNCF projects" (exit code 0)

**Step 6: Commit project validation tool**

```bash
git add casestudypilot/tools/mcp_project_validator.py tests/test_mcp_project_validator.py casestudypilot/__main__.py
git commit -m "feat: add MCP-based project validation CLI tool"
```

---

## Task 4: Update transcript-analysis Skill to Reference MCP

**Files:**
- Modify: `.github/skills/transcript-analysis/SKILL.md`

**Step 1: Update skill to reference MCP as source of truth**

Modify `.github/skills/transcript-analysis/SKILL.md`:

Replace the "Identify CNCF Projects" section:

**OLD:**
```markdown
### Identify CNCF Projects

Look for mentions of CNCF projects like:
- Kubernetes, Prometheus, Envoy, CoreDNS, containerd
- Fluentd, Jaeger, Vitess, Helm, Argo CD, Flux
- Cilium, Linkerd, Istio, etcd, CRI-O, Harbor
- ... (28 projects listed)
```

**NEW:**
```markdown
### Identify CNCF Projects

**Source of Truth:** CNCF Landscape MCP Server (via `query_projects` tool)

Look for mentions of CNCF projects. All extracted projects MUST be validated against the MCP server as the authoritative source. The validation CLI tool `validate-projects` will verify your analysis.

**Common CNCF Projects (Examples):**
- **Graduated:** Kubernetes, Prometheus, Envoy, CoreDNS, containerd, Fluentd, Jaeger, Vitess, Helm, Harbor, etcd, Rook, TiKV, gRPC, CNI
- **Incubating:** Argo, Cilium, Linkerd, Istio, Falco, Dragonfly, Flux, Knative, OpenTelemetry
- **Sandbox:** (Many projects - check MCP server for current list)

**Validation:** After extraction, your output will be validated using:
```bash
python -m casestudypilot validate-projects transcript_analysis.json
```

Projects not found in the MCP server will cause a CRITICAL validation failure.

**Best Practices:**
- Use exact project names as mentioned in the transcript
- If unsure about a project, include it - validation will catch non-CNCF projects
- Include maturity level if mentioned (graduated, incubating, sandbox)
```

**Step 2: Add note about MCP integration to skill header**

Add after the "Purpose" section:
```markdown
## Data Sources

**CNCF Membership & Projects:** This skill references CNCF data that is validated against the CNCF Landscape MCP Server. All company membership and project identification is verified programmatically using the MCP `query_members` and `query_projects` tools.
```

**Step 3: Commit skill update**

```bash
git add .github/skills/transcript-analysis/SKILL.md
git commit -m "docs: update transcript-analysis skill to reference MCP server"
```

---

## Task 5: Update validation.py to Use MCP Project Validator

**Files:**
- Modify: `casestudypilot/validation.py`
- Modify: `tests/test_validation.py`

**Step 1: Write failing test for MCP-based validation**

Modify `tests/test_validation.py`, add test:
```python
from unittest.mock import patch

def test_validate_analysis_with_mcp_projects():
    """Test that validate_analysis uses MCP for project validation"""
    analysis = {
        "cncf_projects": [
            {"name": "Kubernetes", "usage_context": "orchestration"},
            {"name": "Prometheus", "usage_context": "monitoring"},
        ],
        # ... other required fields
    }
    
    with patch('casestudypilot.validation.validate_projects') as mock_validate:
        mock_validate.return_value = {
            "valid_count": 2,
            "invalid_count": 0,
            "is_valid": True,
        }
        
        result = validate_analysis(analysis)
        
        # Should call MCP project validator
        mock_validate.assert_called_once()
        assert result.is_pass or result.is_warning  # Should not fail
```

Run: `pytest tests/test_validation.py::test_validate_analysis_with_mcp_projects -v`
Expected: FAIL (function not yet using MCP validator)

**Step 2: Update validate_analysis to use MCP validator**

Modify `casestudypilot/validation.py`:

1. Add import:
```python
from casestudypilot.tools.mcp_project_validator import validate_projects
```

2. Update the CNCF projects validation section:
```python
def validate_analysis(analysis: Dict[str, Any]) -> ValidationResult:
    """Validate transcript_analysis output with MCP server verification."""
    issues = []
    
    # Existing validations...
    
    # CNCF Projects validation using MCP
    cncf_projects = analysis.get("cncf_projects", [])
    if len(cncf_projects) == 0:
        issues.append("No CNCF projects identified (CRITICAL)")
        return ValidationResult(is_critical=True, issues=issues)
    
    if len(cncf_projects) == 1:
        issues.append("Only 1 CNCF project identified (WARNING: may lack technical depth)")
    
    # Validate projects against MCP server
    project_names = [p["name"] for p in cncf_projects]
    try:
        mcp_result = validate_projects(project_names)
        
        if not mcp_result["is_valid"]:
            # Some projects not found in CNCF landscape
            invalid = mcp_result["invalid_projects"]
            if mcp_result["invalid_count"] / len(project_names) > 0.5:
                # CRITICAL: More than 50% invalid
                issues.append(
                    f"CRITICAL: {mcp_result['invalid_count']} projects not found in CNCF landscape: "
                    f"{', '.join(invalid)}"
                )
                return ValidationResult(is_critical=True, issues=issues)
            else:
                # WARNING: Some invalid
                issues.append(
                    f"WARNING: {mcp_result['invalid_count']} projects not found in CNCF landscape: "
                    f"{', '.join(invalid)}"
                )
    except Exception as e:
        # MCP validation failed - log warning but don't fail
        issues.append(f"WARNING: MCP project validation failed: {e}")
    
    # Rest of validation...
    
    return ValidationResult(
        is_critical=False,
        issues=issues if issues else None
    )
```

**Step 3: Run tests to verify MCP integration**

Run: `pytest tests/test_validation.py -v`
Expected: PASS

**Step 4: Commit validation updates**

```bash
git add casestudypilot/validation.py tests/test_validation.py
git commit -m "refactor: use MCP project validator in analysis validation"
```

---

## Task 6: Update case-study-agent Workflow Documentation

**Files:**
- Modify: `.github/agents/case-study-agent.md`

**Step 1: Update Step 4 (Company Verification) to mention MCP**

Modify `.github/agents/case-study-agent.md`, Step 4:

**OLD:**
```markdown
### Step 4: Verify Company Membership

Verify the company is a CNCF end-user member using the verify-company CLI tool.

```bash
python -m casestudypilot verify-company "$COMPANY_NAME"
```
```

**NEW:**
```markdown
### Step 4: Verify Company Membership

Verify the company is a CNCF end-user member using the verify-company CLI tool. This tool queries the CNCF Landscape MCP Server for real-time membership data.

**Data Source:** CNCF Landscape MCP Server (`query_members` tool with `tier="End User Supporter"`)

```bash
python -m casestudypilot verify-company "$COMPANY_NAME"
```

**Output:** Creates `company_verification.json` with:
- `matched_name`: Official company name in CNCF landscape
- `confidence`: Match confidence score (0.0-1.0)
- `is_member`: Boolean membership status
- `joined_at`: Date company joined CNCF (YYYY-MM-DD)
```

**Step 2: Update Step 6 (Analysis Validation) to mention MCP**

Modify `.github/agents/case-study-agent.md`, Step 6:

Add after the validation command:
```markdown
**MCP Integration:** The `validate-analysis` command internally validates CNCF projects against the Landscape MCP Server using the `query_projects` tool. Projects not found in the landscape will trigger a CRITICAL failure.
```

**Step 3: Add MCP section to agent header**

Add after the "Mission" section:
```markdown
## Data Sources & Integration

**CNCF Landscape MCP Server:** This agent uses the CNCF Landscape MCP Server (Docker: `ghcr.io/cncf/landscape-mcp-server:main`) as the single source of truth for:

1. **Company Membership Verification** (Step 4): `query_members` tool with `tier="End User Supporter"`
2. **Project Validation** (Step 6): `query_projects` tool for all extracted CNCF projects
3. **Real-Time Data**: MCP server fetches latest landscape data on startup (`https://landscape.cncf.io/data/full.json`)

**Benefits:**
- No hardcoded member/project lists
- Real-time accuracy
- Single source of truth
- Automatic updates when landscape changes
```

**Step 4: Update version number**

Change agent version from `2.2.0` to `2.3.0`:
```markdown
---
name: case-study-agent
version: 2.3.0
---
```

**Step 5: Commit agent workflow updates**

```bash
git add .github/agents/case-study-agent.md
git commit -m "docs: update case-study-agent to document MCP server integration (v2.3.0)"
```

---

## Task 7: Update AGENTS.md Documentation

**Files:**
- Modify: `AGENTS.md`

**Step 1: Add MCP Server section to "Core Operating Principles"**

Modify `AGENTS.md`, add new section after "4. CLI for Data, Skills for Content":

```markdown
### 5. MCP Servers for External Data Sources

**Use MCP (Model Context Protocol) servers when:**
- ✅ Accessing external authoritative data (CNCF Landscape, GitHub APIs)
- ✅ Real-time data that changes frequently
- ✅ Data that requires authentication or complex APIs
- ✅ Standardized tool interfaces across multiple agents

**Pattern: CLI Tool + MCP Client**
```python
# CLI tool wraps MCP client for agent use
def verify_company(company_name: str) -> Dict[str, Any]:
    with MCPClient().connect() as client:
        members = client.query_members(tier="End User Supporter")
    # Process and return standardized format
    return {"is_member": True, "matched_name": "Company"}
```

**Why this pattern?**
- CLI tools abstract MCP complexity from agents
- Agents call familiar CLI commands, not MCP directly
- Easy to mock/test without MCP server
- Fallback to direct APIs if MCP unavailable

**Example: CNCF Landscape MCP Server**
```bash
# Agent calls CLI tool
python -m casestudypilot verify-company "Intuit"

# CLI tool internally:
# 1. Connects to MCP server (Docker container)
# 2. Calls query_members tool
# 3. Returns standardized JSON
```
```

**Step 2: Update "Current Implementation: Case Study Generation" summary**

Modify the Step 4 description:
```markdown
4. **Verify CNCF membership** (MCP: query_members)
```

Modify the Step 6 description:
```markdown
6. **Skill:** Analyze transcript (transcript-analysis) → Validate analysis (MCP: query_projects)
```

**Step 3: Add MCP to "Framework Extension Examples"**

Add new example after "Example 2: Documentation Auditor":

```markdown
### Example 3: GitHub Issue Analyzer

**New MCP integration:** `github-mcp-server`

```markdown
# Use existing GitHub MCP Server
"github": {
  "command": "npx",
  "args": ["-y", "@modelcontextprotocol/server-github"],
  "env": {
    "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_TOKEN}"
  }
}
```

**New CLI tool:** `fetch-issue-context`

```bash
python -m casestudypilot fetch-issue-context 16
# Uses GitHub MCP to fetch issue, comments, related PRs
# Returns unified context JSON
```

**New agent:** `issue-context-agent`

```markdown
1. Fetch issue context → fetch-issue-context (uses GitHub MCP)
2. Apply context-analysis skill
3. Generate response with full context
4. Post comment on issue
```
```

**Step 4: Update version history**

Modify the "Version History" section:
```markdown
- **v2.3.0** (February 2026) - Added CNCF Landscape MCP Server integration
- **v2.2.0** (February 2026) - Added fail-fast validation framework
```

**Step 5: Commit AGENTS.md updates**

```bash
git add AGENTS.md
git commit -m "docs: add MCP server integration patterns to AGENTS.md (v2.3.0)"
```

---

## Task 8: Update README.md with MCP Documentation

**Files:**
- Modify: `README.md`

**Step 1: Add MCP section to "Features" or create new "Data Sources" section**

Add after existing features:
```markdown
### Data Sources

- **CNCF Landscape MCP Server:** Real-time CNCF membership and project data
  - Company verification: End User Supporter member lookup
  - Project validation: All CNCF projects with maturity levels
  - Single source of truth for CNCF data
  - Auto-updates from `https://landscape.cncf.io/data/full.json`
```

**Step 2: Add MCP setup to "Installation" or "Development Setup"**

Add new subsection:
```markdown
#### MCP Server Setup (Optional for Development)

The project uses the CNCF Landscape MCP Server for membership and project data. The server is automatically started via Docker when needed, but you can run it manually for testing:

```bash
# Using docker-compose
docker-compose up landscape-mcp

# Or directly
docker run -i --rm \
  ghcr.io/cncf/landscape-mcp-server:main \
  --data-url https://landscape.cncf.io/data/full.json
```

**Requirements:**
- Docker installed and running
- Internet access to fetch landscape data

**Note:** CLI tools will automatically start the MCP server in Docker when needed.
```

**Step 3: Update CLI commands documentation**

Modify the `verify-company` command description:
```markdown
#### verify-company

Verify if a company is a CNCF end-user member using the Landscape MCP Server.

```bash
python -m casestudypilot verify-company "Company Name"
```

**Data Source:** CNCF Landscape MCP Server (`query_members` tool)

**Output:** `company_verification.json`
```json
{
  "query_name": "Company Name",
  "matched_name": "Company Name Inc.",
  "confidence": 0.95,
  "is_member": true,
  "match_method": "fuzzy",
  "joined_at": "2023-05-15"
}
```

**Exit Codes:**
- `0`: Company is a CNCF member
- `1`: Company is not a CNCF member
```

Add new command documentation:
```markdown
#### validate-projects

Validate that project names are CNCF projects using the Landscape MCP Server.

```bash
python -m casestudypilot validate-projects projects.json
```

**Input Format:**
```json
["Kubernetes", "Prometheus", "Envoy"]
```

Or analysis format:
```json
{
  "cncf_projects": [
    {"name": "Kubernetes", "usage_context": "..."},
    {"name": "Prometheus", "usage_context": "..."}
  ]
}
```

**Data Source:** CNCF Landscape MCP Server (`query_projects` and `get_project_details` tools)

**Exit Codes:**
- `0`: All projects are valid CNCF projects
- `1`: Some projects are invalid (< 50% invalid)
- `2`: Most projects are invalid or validation error (≥ 50% invalid)
```

**Step 4: Commit README updates**

```bash
git add README.md
git commit -m "docs: add MCP server integration documentation to README"
```

---

## Task 9: Add Caching Layer for MCP Queries (Performance Optimization)

**Files:**
- Create: `casestudypilot/mcp_cache.py`
- Create: `tests/test_mcp_cache.py`
- Modify: `casestudypilot/mcp_client.py`

**Step 1: Write failing test for cache**

Create `tests/test_mcp_cache.py`:
```python
import pytest
from casestudypilot.mcp_cache import MCPCache
import time

def test_cache_set_and_get():
    """Test basic cache set and get"""
    cache = MCPCache(ttl_seconds=60)
    
    cache.set("test_key", {"data": "value"})
    result = cache.get("test_key")
    
    assert result == {"data": "value"}

def test_cache_expiry():
    """Test that cache entries expire after TTL"""
    cache = MCPCache(ttl_seconds=1)
    
    cache.set("test_key", {"data": "value"})
    time.sleep(1.1)
    result = cache.get("test_key")
    
    assert result is None

def test_cache_clear():
    """Test cache clearing"""
    cache = MCPCache(ttl_seconds=60)
    
    cache.set("key1", "value1")
    cache.set("key2", "value2")
    cache.clear()
    
    assert cache.get("key1") is None
    assert cache.get("key2") is None
```

Run: `pytest tests/test_mcp_cache.py -v`
Expected: FAIL with "ModuleNotFoundError"

**Step 2: Implement simple in-memory cache**

Create `casestudypilot/mcp_cache.py`:
```python
"""Simple in-memory cache for MCP query results."""

import time
from typing import Any, Dict, Optional


class MCPCache:
    """Thread-safe in-memory cache with TTL."""

    def __init__(self, ttl_seconds: int = 300):
        """Initialize cache with TTL (default 5 minutes).
        
        Args:
            ttl_seconds: Time-to-live for cache entries in seconds
        """
        self.ttl_seconds = ttl_seconds
        self._cache: Dict[str, tuple[Any, float]] = {}

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache if not expired.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if expired/missing
        """
        if key not in self._cache:
            return None

        value, timestamp = self._cache[key]
        
        # Check if expired
        if time.time() - timestamp > self.ttl_seconds:
            del self._cache[key]
            return None

        return value

    def set(self, key: str, value: Any) -> None:
        """Set value in cache with current timestamp.
        
        Args:
            key: Cache key
            value: Value to cache
        """
        self._cache[key] = (value, time.time())

    def clear(self) -> None:
        """Clear all cache entries."""
        self._cache.clear()

    def cleanup_expired(self) -> int:
        """Remove expired entries from cache.
        
        Returns:
            Number of entries removed
        """
        now = time.time()
        expired_keys = [
            key
            for key, (_, timestamp) in self._cache.items()
            if now - timestamp > self.ttl_seconds
        ]

        for key in expired_keys:
            del self._cache[key]

        return len(expired_keys)


# Global cache instance (5 minute TTL)
_global_cache = MCPCache(ttl_seconds=300)


def get_cache() -> MCPCache:
    """Get global MCP cache instance.
    
    Returns:
        Global MCPCache instance
    """
    return _global_cache
```

**Step 3: Run cache tests**

Run: `pytest tests/test_mcp_cache.py -v`
Expected: PASS

**Step 4: Integrate cache into MCPClient**

Modify `casestudypilot/mcp_client.py`:

1. Add import:
```python
from casestudypilot.mcp_cache import get_cache
import hashlib
import json
```

2. Update `query_members` to use cache:
```python
def query_members(
    self,
    tier: Optional[str] = None,
    joined_from: Optional[str] = None,
    joined_to: Optional[str] = None,
    limit: int = 100,
    use_cache: bool = True,
) -> List[Dict[str, Any]]:
    """Query CNCF members with filters (cached).
    
    Args:
        ... (existing args)
        use_cache: Whether to use cached results (default True)
    """
    if not self._connected or not self._client:
        raise RuntimeError("Client not connected. Use connect() context manager.")

    # Generate cache key from args
    cache_key = f"members:{tier}:{joined_from}:{joined_to}:{limit}"
    
    # Check cache
    if use_cache:
        cache = get_cache()
        cached_result = cache.get(cache_key)
        if cached_result is not None:
            return cached_result

    # Cache miss - query MCP
    args = {"limit": limit}
    if tier:
        args["tier"] = tier
    if joined_from:
        args["joined_from"] = joined_from
    if joined_to:
        args["joined_to"] = joined_to

    result = self._client.call_tool("query_members", args)
    response = json.loads(result["content"][0]["text"])
    members = response["members"]
    
    # Cache result
    if use_cache:
        cache.set(cache_key, members)
    
    return members
```

3. Update `query_projects` similarly:
```python
def query_projects(
    self,
    # ... existing args
    use_cache: bool = True,
) -> List[Dict[str, Any]]:
    """Query CNCF projects with filters (cached)."""
    # Generate cache key
    cache_key = f"projects:{maturity}:{name}:{graduated_from}:{graduated_to}:{incubating_from}:{incubating_to}:{accepted_from}:{accepted_to}:{limit}"
    
    # Check cache
    if use_cache:
        cache = get_cache()
        cached_result = cache.get(cache_key)
        if cached_result is not None:
            return cached_result
    
    # Cache miss - query MCP
    # ... existing code ...
    
    # Cache result
    if use_cache:
        cache.set(cache_key, projects)
    
    return projects
```

**Step 5: Add cache statistics logging**

Add method to MCPClient:
```python
def get_cache_stats(self) -> Dict[str, int]:
    """Get cache statistics.
    
    Returns:
        Dictionary with cache stats (size, expired count)
    """
    cache = get_cache()
    size = len(cache._cache)
    expired = cache.cleanup_expired()
    
    return {
        "size": size,
        "expired_cleaned": expired,
    }
```

**Step 6: Test caching performance**

Create integration test:
```python
@pytest.mark.integration
def test_cache_performance():
    """Test that caching improves performance"""
    import time
    
    client = MCPClient()
    
    with client.connect():
        # First query (cache miss)
        start = time.time()
        members1 = client.query_members(tier="End User Supporter", limit=10)
        time1 = time.time() - start
        
        # Second query (cache hit)
        start = time.time()
        members2 = client.query_members(tier="End User Supporter", limit=10)
        time2 = time.time() - start
        
        # Cache should be faster
        assert time2 < time1 / 2  # At least 2x faster
        assert members1 == members2  # Same results
```

Run: `pytest tests/test_mcp_client.py::test_cache_performance -v -m integration`
Expected: PASS (cached query should be much faster)

**Step 7: Commit caching implementation**

```bash
git add casestudypilot/mcp_cache.py tests/test_mcp_cache.py casestudypilot/mcp_client.py tests/test_mcp_client.py
git commit -m "feat: add in-memory caching layer for MCP queries (5min TTL)"
```

---

## Task 10: Update Hyperlinks to Use MCP Project Data (Optional Enhancement)

**Files:**
- Modify: `casestudypilot/hyperlinks.py`
- Create: `casestudypilot/tools/mcp_hyperlink_generator.py`

**Note:** This task is optional as the MCP server may not provide project URLs. If URLs are not available, keep existing hardcoded mapping as fallback.

**Step 1: Investigate if MCP provides project URLs**

Manually test:
```bash
docker run -i --rm ghcr.io/cncf/landscape-mcp-server:main --data-url https://landscape.cncf.io/data/full.json
# Then query: get_project_details with name "Kubernetes"
# Check if response includes URL/homepage field
```

If URLs are available, proceed with Steps 2-6. Otherwise, skip this task.

**Step 2: Create hyperlink generator that fetches from MCP**

Create `casestudypilot/tools/mcp_hyperlink_generator.py`:
```python
"""Generate hyperlinks for CNCF projects using MCP data."""

from typing import Dict
from casestudypilot.mcp_client import MCPClient
from casestudypilot.hyperlinks import PROJECT_URLS as FALLBACK_URLS


def get_project_url(project_name: str) -> str:
    """Get project URL from MCP server or fallback.
    
    Args:
        project_name: Project name to look up
        
    Returns:
        Project URL or empty string if not found
    """
    try:
        with MCPClient().connect() as client:
            project = client.get_project_details(project_name)
        
        # Check if MCP provides URL (field name may vary)
        if project and "homepage" in project:
            return project["homepage"]
        elif project and "url" in project:
            return project["url"]
    except Exception:
        pass
    
    # Fallback to hardcoded mapping
    return FALLBACK_URLS.get(project_name, "")


def generate_hyperlink_mapping() -> Dict[str, str]:
    """Generate complete hyperlink mapping from MCP + fallback.
    
    Returns:
        Dictionary mapping project names to URLs
    """
    # Start with fallback
    mapping = FALLBACK_URLS.copy()
    
    # Enhance with MCP data
    try:
        with MCPClient().connect() as client:
            projects = client.query_projects(limit=1000)
        
        for project in projects:
            name = project["name"]
            # Add if not in fallback or to update
            if "homepage" in project:
                mapping[name] = project["homepage"]
            elif "url" in project:
                mapping[name] = project["url"]
    except Exception:
        # If MCP fails, return fallback only
        pass
    
    return mapping
```

**Step 3: Update assembler to use MCP hyperlinks**

Modify `casestudypilot/tools/assembler.py`:
```python
from casestudypilot.tools.mcp_hyperlink_generator import generate_hyperlink_mapping

def assemble_case_study(...):
    # Generate hyperlinks from MCP + fallback
    hyperlink_mapping = generate_hyperlink_mapping()
    
    # Use dynamic mapping for hyperlinking
    # ... rest of assembler logic
```

**Step 4-6:** Add tests, verify, and commit (only if MCP provides URLs)

---

## Task 11: Add CI/CD for MCP Integration Tests

**Files:**
- Modify: `.github/workflows/test.yml` (or equivalent CI config)

**Step 1: Add Docker service to CI workflow**

Modify `.github/workflows/test.yml`:
```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    # Add Docker service for MCP server
    services:
      landscape-mcp:
        image: ghcr.io/cncf/landscape-mcp-server:main
        options: --interactive --tty
        # Note: MCP server runs on stdio, not HTTP, so no ports needed
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov
      
      - name: Run unit tests
        run: pytest tests/ -v --cov=casestudypilot
      
      - name: Run integration tests (with MCP)
        run: pytest tests/ -v -m integration
        # Integration tests will start MCP server via Docker
```

**Step 2: Add pytest markers configuration**

Create `pytest.ini`:
```ini
[pytest]
markers =
    integration: Integration tests requiring external services (MCP, Docker)
    slow: Slow tests that may take >1 minute
```

**Step 3: Test CI locally**

Run: `pytest tests/ -v -m integration`
Expected: All integration tests pass with Docker available

**Step 4: Commit CI updates**

```bash
git add .github/workflows/test.yml pytest.ini
git commit -m "ci: add MCP integration tests to CI workflow"
```

---

## Task 12: Final Integration Testing and Documentation

**Files:**
- Create: `docs/mcp-integration.md`
- Modify: `CONTRIBUTING.md` (add MCP development notes)

**Step 1: Run full end-to-end test**

Test the complete case study workflow:
```bash
# 1. Fetch video data
python -m casestudypilot youtube-data "https://youtube.com/watch?v=VIDEO_ID"

# 2. Validate transcript (should still work)
python -m casestudypilot validate-transcript video_data.json

# 3. Verify company (now uses MCP)
python -m casestudypilot verify-company "Intuit"

# 4. Generate analysis (LLM skill)
# Apply transcript-analysis skill manually

# 5. Validate analysis (now uses MCP for projects)
python -m casestudypilot validate-analysis transcript_analysis.json

# 6. Validate projects directly (new MCP tool)
python -m casestudypilot validate-projects transcript_analysis.json

# All steps should PASS
```

**Step 2: Create comprehensive MCP integration documentation**

Create `docs/mcp-integration.md`:
```markdown
# CNCF Landscape MCP Server Integration

## Overview

This project uses the **CNCF Landscape MCP Server** as the single source of truth for CNCF membership and project data. The MCP (Model Context Protocol) server provides standardized tools for querying the CNCF landscape.

## Architecture

```
┌─────────────────────────────────────────────────────┐
│ Agents (case-study-agent)                          │
│ - Orchestrate workflows                             │
│ - Call CLI tools for data                           │
└─────────────────┬───────────────────────────────────┘
                  │
                  ↓
┌─────────────────────────────────────────────────────┐
│ CLI Tools (verify-company, validate-projects)       │
│ - Wrap MCP client                                   │
│ - Return standardized JSON                          │
│ - Exit codes for validation                         │
└─────────────────┬───────────────────────────────────┘
                  │
                  ↓
┌─────────────────────────────────────────────────────┐
│ MCP Client (casestudypilot/mcp_client.py)          │
│ - Manages Docker container lifecycle               │
│ - Calls MCP tools (query_members, query_projects)  │
│ - Caches results (5 minute TTL)                     │
└─────────────────┬───────────────────────────────────┘
                  │
                  ↓
┌─────────────────────────────────────────────────────┐
│ Landscape MCP Server (Docker container)             │
│ - Fetches landscape data on startup                 │
│ - Provides 5 tools (query, metrics)                 │
│ - Stdio communication (JSON-RPC)                    │
└─────────────────────────────────────────────────────┘
                  │
                  ↓
┌─────────────────────────────────────────────────────┐
│ CNCF Landscape Data (landscape.cncf.io)            │
│ - https://landscape.cncf.io/data/full.json         │
│ - Authoritative source                              │
└─────────────────────────────────────────────────────┘
```

## MCP Tools Used

### 1. query_members
**Purpose:** Find CNCF members by tier and join date  
**Used by:** `verify-company` CLI tool  
**Example:**
```python
with MCPClient().connect() as client:
    members = client.query_members(tier="End User Supporter", limit=100)
```

**Response:**
```json
{
  "count": 150,
  "members": [
    {
      "name": "Intuit Inc.",
      "category": "CNCF Members",
      "subcategory": "End User Supporter",
      "member_subcategory": "End User Supporter",
      "joined_at": "2023-05-15"
    }
  ]
}
```

### 2. query_projects
**Purpose:** Find CNCF projects by maturity, name, dates  
**Used by:** `validate-projects` CLI tool, `validation.py`  
**Example:**
```python
with MCPClient().connect() as client:
    projects = client.query_projects(maturity="graduated", limit=50)
```

**Response:**
```json
{
  "count": 25,
  "projects": [
    {
      "name": "Kubernetes",
      "category": "CNCF Projects",
      "subcategory": "Orchestration & Management",
      "maturity": "graduated",
      "accepted_at": "2016-03-10",
      "incubating_at": "2017-03-01",
      "graduated_at": "2018-03-06"
    }
  ]
}
```

### 3. get_project_details
**Purpose:** Get detailed info for specific project  
**Used by:** `validate-projects` CLI tool  
**Example:**
```python
with MCPClient().connect() as client:
    project = client.get_project_details("Kubernetes")
```

## Caching Strategy

**Problem:** MCP queries require Docker container startup and data fetching (slow)

**Solution:** In-memory cache with 5-minute TTL (`casestudypilot/mcp_cache.py`)

**Benefits:**
- First query: ~2-3 seconds (Docker + data fetch)
- Cached queries: <10ms (in-memory lookup)
- Automatic expiry ensures fresh data
- Thread-safe for concurrent workflows

**Usage:**
```python
# Caching enabled by default
members = client.query_members(tier="End User Supporter")  # Cache miss
members = client.query_members(tier="End User Supporter")  # Cache hit

# Disable caching for real-time data
members = client.query_members(tier="End User Supporter", use_cache=False)
```

## Fallback Strategy

**Problem:** MCP server may be unavailable (no Docker, network issues)

**Solution:** Legacy API fallback in `company_verifier.py`

```python
try:
    # Primary: MCP server
    with MCPClient().connect() as client:
        members = client.query_members(tier="End User Supporter")
except Exception as e:
    # Fallback: Direct API call
    logging.warning(f"MCP failed, using legacy API: {e}")
    landscape_data = fetch_landscape_data()
    member_list = extract_enduser_members(landscape_data)
```

## Development Setup

### 1. Install MCP SDK
```bash
pip install -r requirements.txt  # Includes mcp>=0.1.0
```

### 2. Test MCP Server Connection
```bash
# Manual test
docker run -i --rm \
  ghcr.io/cncf/landscape-mcp-server:main \
  --data-url https://landscape.cncf.io/data/full.json

# Test with CLI tool
python -m casestudypilot verify-company "Intuit"
```

### 3. Run Integration Tests
```bash
# Requires Docker running
pytest tests/ -v -m integration
```

## Troubleshooting

### Error: "Docker daemon not running"
**Solution:** Start Docker Desktop or Docker daemon

### Error: "Unable to connect to MCP server"
**Solution:** Check Docker image pull: `docker pull ghcr.io/cncf/landscape-mcp-server:main`

### Error: "Timeout connecting to landscape data"
**Solution:** Check network connectivity to `landscape.cncf.io`

### Slow MCP queries
**Solution:** Check cache hit rate with `client.get_cache_stats()`. Cache TTL is 5 minutes.

## Migration from Legacy API

**Before (Direct API):**
```python
# Direct HTTP call
landscape_data = fetch_landscape_data()
members = extract_enduser_members(landscape_data)
```

**After (MCP):**
```python
# MCP client
with MCPClient().connect() as client:
    members_data = client.query_members(tier="End User Supporter")
    members = [m["name"] for m in members_data]
```

**Benefits:**
- Standardized interface
- Real-time data (no stale cache files)
- Rich metadata (join dates, maturity levels)
- Reusable across agents

## Future Enhancements

1. **Persistent cache:** Use Redis or file-based cache for cross-process sharing
2. **MCP connection pooling:** Reuse Docker containers across CLI invocations
3. **Project URL enrichment:** Add project homepages to hyperlink mapping
4. **Webhook updates:** Trigger cache invalidation on landscape updates
5. **Additional MCP servers:** GitHub, Crunchbase, etc.

## References

- MCP Server: https://github.com/cncf/automation/tree/main/utilities/landscape-mcp-server
- CNCF Landscape: https://landscape.cncf.io
- MCP Specification: https://modelcontextprotocol.org
```

**Step 3: Update CONTRIBUTING.md with MCP notes**

Modify `CONTRIBUTING.md`, add section:
```markdown
## Working with MCP Integration

### Local Development

MCP integration requires Docker. To test locally:

```bash
# Start MCP server (optional - CLI tools auto-start)
docker-compose up landscape-mcp

# Test company verification
python -m casestudypilot verify-company "Test Company"

# Test project validation
echo '["Kubernetes", "Prometheus"]' > test_projects.json
python -m casestudypilot validate-projects test_projects.json
```

### Writing MCP Integration Tests

**Unit tests:** Mock MCPClient
```python
from unittest.mock import patch, MagicMock

def test_verify_company():
    with patch('module.MCPClient') as mock_mcp:
        mock_client = MagicMock()
        mock_client.query_members.return_value = [...]
        # Test logic
```

**Integration tests:** Mark with `@pytest.mark.integration`
```python
@pytest.mark.integration
def test_real_mcp():
    client = MCPClient()
    with client.connect():
        # Test with real Docker container
```

### Caching Behavior

- Cache TTL: 5 minutes (configurable in `mcp_cache.py`)
- Cache key: Query parameters (tier, maturity, dates, etc.)
- Clear cache: `from casestudypilot.mcp_cache import get_cache; get_cache().clear()`

### Debugging MCP Issues

Enable verbose logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

Check Docker logs:
```bash
docker ps  # Find container ID
docker logs <container-id>
```
```

**Step 4: Run final test suite**

```bash
# All tests
pytest tests/ -v --cov=casestudypilot

# Coverage report
pytest tests/ --cov=casestudypilot --cov-report=html
open htmlcov/index.html
```

**Step 5: Commit documentation**

```bash
git add docs/mcp-integration.md CONTRIBUTING.md
git commit -m "docs: add comprehensive MCP integration documentation"
```

---

## Task 13: Create Pull Request

**Step 1: Push branch to remote**

```bash
git push -u origin feature/landscape-mcp-integration
```

**Step 2: Create PR with gh CLI**

```bash
gh pr create --title "Integrate CNCF Landscape MCP Server (Issue #16)" --body "$(cat <<'EOF'
## Summary

Integrates the CNCF Landscape MCP Server as the single source of truth for CNCF membership and project data. Replaces direct API calls with MCP client, adds caching layer, and updates all agents/skills to reference MCP as authoritative source.

**Resolves:** #16

## Changes

### New Features
- **MCP Client** (`mcp_client.py`): Python client for Landscape MCP Server with Docker integration
- **Caching Layer** (`mcp_cache.py`): 5-minute TTL in-memory cache for MCP queries
- **Project Validator** (`mcp_project_validator.py`): Validate CNCF projects using MCP
- **CLI Command** (`validate-projects`): New command for project validation with exit codes

### Refactored Components
- **Company Verifier** (`company_verifier.py`): Now uses MCP `query_members` tool with fallback to legacy API
- **Analysis Validation** (`validation.py`): Validates CNCF projects against MCP server
- **Case Study Agent** (v2.3.0): Updated to document MCP integration

### Documentation
- **AGENTS.md**: Added MCP server integration patterns (v2.3.0)
- **README.md**: Added MCP setup and CLI documentation
- **docs/mcp-integration.md**: Comprehensive MCP integration guide
- **Skills**: Updated `transcript-analysis` to reference MCP as source of truth

### Testing
- Unit tests with mocking for all MCP integration
- Integration tests marked with `@pytest.mark.integration`
- CI/CD updated to run integration tests with Docker

## Architecture

```
Agents → CLI Tools → MCP Client → MCP Server (Docker) → CNCF Landscape Data
                         ↓
                   Cache Layer (5min TTL)
                         ↓
                   Fallback to Legacy API
```

## Benefits

✅ **Real-Time Data**: No stale hardcoded lists - always fresh from landscape  
✅ **Single Source of Truth**: MCP server as authoritative CNCF data source  
✅ **Rich Metadata**: Join dates, maturity levels, acceptance dates  
✅ **Performance**: 5-minute cache makes queries <10ms after first fetch  
✅ **Resilience**: Fallback to legacy API if MCP unavailable  
✅ **Future-Proof**: Easy to add more MCP servers (GitHub, Crunchbase, etc.)

## Testing

```bash
# Unit tests
pytest tests/ -v

# Integration tests (requires Docker)
pytest tests/ -v -m integration

# End-to-end workflow
python -m casestudypilot verify-company "Intuit"
python -m casestudypilot validate-projects projects.json
```

## Breaking Changes

None - backward compatible with fallback to legacy API.

## Migration Notes

Existing workflows will automatically use MCP when available. No changes required to agent workflows or skill invocations.

EOF
)"
```

**Step 3: Link PR to issue**

GitHub will auto-link via "Resolves: #16" in PR body.

**Step 4: Verify PR created**

Run: `gh pr view`
Expected: PR details displayed with issue link

---

## Post-Implementation Checklist

After completing all tasks:

- [ ] All unit tests pass (`pytest tests/ -v`)
- [ ] All integration tests pass with Docker (`pytest tests/ -v -m integration`)
- [ ] Company verification uses MCP with fallback
- [ ] Project validation uses MCP for all CNCF projects
- [ ] Caching improves performance (2x+ faster on cache hit)
- [ ] Documentation updated (AGENTS.md, README.md, skills)
- [ ] CI/CD runs integration tests
- [ ] PR created and linked to issue #16
- [ ] Case study agent version bumped to 2.3.0

---

## Rollback Plan

If MCP integration causes issues:

1. **Revert commits:**
   ```bash
   git revert <commit-hash-range>
   ```

2. **Fallback mechanism:**
   - MCP client already has try/except with legacy API fallback
   - No manual rollback needed for runtime

3. **Disable MCP in CI:**
   - Comment out integration tests in `.github/workflows/test.yml`
   - Unit tests will still pass with mocking

---

## Success Criteria

✅ **Issue #16 requirements met:**
- Skills use landscape MCP server as source of truth
- Fully utilized by agents/skills
- Documentation updated for future agents

✅ **Technical requirements:**
- All tests passing (unit + integration)
- Performance acceptable (<3s for first query, <10ms cached)
- Fallback works if MCP unavailable
- CI/CD validates integration

✅ **Documentation requirements:**
- AGENTS.md explains MCP patterns
- README.md has setup instructions
- Skills reference MCP as authoritative
- Comprehensive troubleshooting guide

---

**Plan Version:** 1.0  
**Created:** 2026-02-09  
**Estimated Time:** 8-12 hours (full implementation + testing)  
**Tasks:** 13 major tasks, ~60 steps total
