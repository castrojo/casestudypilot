# Containerization Strategy for MCP Integration

## Overview

This document outlines the strategy for moving toward a **fully containerized workflow** where none of the casestudypilot tooling runs on the user's host machine. The MCP integration (Issue #16) is the first step in this direction.

## Current State (Issue #16 Implementation)

### Hybrid Approach
- **User's Host**: Python CLI tools (`casestudypilot` package)
- **Docker Container**: MCP Server (landscape-mcp-server)
- **Communication**: stdio via `docker run` subprocess

```
┌─────────────────────────────────────┐
│ User's Host Machine                 │
│                                     │
│  ┌──────────────────────────────┐  │
│  │ casestudypilot CLI (Python)  │  │
│  │ - verify-company             │  │
│  │ - validate-projects          │  │
│  │ - MCPClient wrapper          │  │
│  └──────────┬───────────────────┘  │
│             │ subprocess.Popen      │
│             ↓                       │
│  ┌──────────────────────────────┐  │
│  │ Docker Container (MCP)       │  │
│  │ landscape-mcp-server:main    │  │
│  │ - stdio communication        │  │
│  └──────────────────────────────┘  │
│                                     │
└─────────────────────────────────────┘
```

### Benefits of Current Approach
- ✅ Quick to implement
- ✅ No container orchestration needed
- ✅ Works with existing Python environment
- ✅ Easy debugging (Python on host)

### Limitations
- ❌ Requires Python + dependencies on host
- ❌ Container startup overhead per CLI invocation
- ❌ No container reuse (--rm flag)
- ❌ Platform-specific behavior (Docker paths, permissions)

## Target State: Fully Containerized Workflow

### Goal
Run **all** casestudypilot tooling in containers, with host machine only needing:
1. Docker/Podman
2. Git (for cloning repository)
3. Optional: docker-compose or make for orchestration

### Architecture Vision

```
┌─────────────────────────────────────────────────────────┐
│ User's Host Machine                                     │
│                                                         │
│  ┌───────────────────────────────────────────────────┐ │
│  │ docker-compose.yml or Makefile                     │ │
│  │ - Orchestrates all containers                      │ │
│  └───────────────┬───────────────────────────────────┘ │
│                  │                                      │
│                  ↓                                      │
│  ┌───────────────────────────────────────────────────┐ │
│  │ Container Network: casestudypilot                  │ │
│  │                                                    │ │
│  │  ┌──────────────────────────────────────────────┐ │ │
│  │  │ casestudypilot-cli Container                 │ │ │
│  │  │ - Python 3.11 + all dependencies            │ │ │
│  │  │ - CLI tools (verify-company, etc.)          │ │ │
│  │  │ - Communicates with MCP via network         │ │ │
│  │  └──────────────┬───────────────────────────────┘ │ │
│  │                 │ HTTP or gRPC                    │ │
│  │                 ↓                                  │ │
│  │  ┌──────────────────────────────────────────────┐ │ │
│  │  │ landscape-mcp-server Container               │ │ │
│  │  │ - MCP server (persistent)                    │ │ │
│  │  │ - Landscape data cached                      │ │ │
│  │  │ - JSON-RPC over HTTP/stdio                   │ │ │
│  │  └──────────────────────────────────────────────┘ │ │
│  │                                                    │ │
│  │  ┌──────────────────────────────────────────────┐ │ │
│  │  │ Future: github-mcp-server Container          │ │ │
│  │  └──────────────────────────────────────────────┘ │ │
│  │                                                    │ │
│  └────────────────────────────────────────────────────┘ │
│                                                         │
│  Volume Mounts:                                         │
│  - ./case-studies (output)                              │
│  - ./docs/plans (plans)                                 │
│  - ./.cache (MCP cache, landscape data)                 │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

## Migration Path

### Phase 1: Current Implementation (Issue #16)
**Status:** In Progress  
**Goal:** Basic MCP integration with hybrid approach

**Deliverables:**
- MCPClient that spawns Docker containers via subprocess
- CLI tools on host that use MCPClient
- Integration tests that require Docker
- Documentation of containerization strategy (this document)

**Files:**
- `casestudypilot/mcp_client.py` - subprocess-based MCP client
- `docker-compose.yml` - Optional manual MCP server startup
- `docs/containerization-strategy.md` - This document

### Phase 2: Persistent MCP Server (Future)
**Status:** Planned  
**Goal:** Keep MCP server running, avoid startup overhead

**Approach:**
```yaml
# docker-compose.yml (enhanced)
services:
  landscape-mcp:
    image: ghcr.io/cncf/landscape-mcp-server:main
    container_name: landscape-mcp
    restart: unless-stopped
    command:
      - "--data-url"
      - "https://landscape.cncf.io/data/full.json"
    networks:
      - casestudypilot
    expose:
      - "3000"  # HTTP endpoint (if MCP supports it)
    volumes:
      - mcp-cache:/data  # Persist landscape data

volumes:
  mcp-cache:

networks:
  casestudypilot:
```

**Changes Required:**
- Modify `MCPClient` to connect to running container (HTTP or stdio over TCP)
- Add health check to verify MCP server is ready
- Add CLI command: `casestudypilot mcp start/stop/status`
- Update integration tests to use persistent container

**Benefits:**
- ✅ No container startup overhead (2-3 seconds per call)
- ✅ Landscape data cached between invocations
- ✅ Better cache hit rate

### Phase 3: CLI in Container (Future)
**Status:** Planned  
**Goal:** Run casestudypilot CLI tools in container

**Approach:**
Create `Dockerfile` for casestudypilot CLI:
```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY casestudypilot/ ./casestudypilot/
COPY templates/ ./templates/
COPY .github/ ./.github/

# Set entrypoint
ENTRYPOINT ["python", "-m", "casestudypilot"]

# Default command
CMD ["--help"]
```

**Usage:**
```bash
# Instead of: python -m casestudypilot verify-company "Intuit"
docker run --rm --network casestudypilot \
  -v $(pwd)/case-studies:/app/case-studies \
  casestudypilot verify-company "Intuit"

# Or with docker-compose:
docker-compose run --rm cli verify-company "Intuit"

# Or with Makefile:
make verify-company COMPANY="Intuit"
```

**docker-compose.yml:**
```yaml
services:
  cli:
    build: .
    container_name: casestudypilot-cli
    networks:
      - casestudypilot
    volumes:
      - ./case-studies:/app/case-studies
      - ./docs:/app/docs
      - ./.cache:/app/.cache
    environment:
      - MCP_SERVER_URL=http://landscape-mcp:3000
    depends_on:
      - landscape-mcp

  landscape-mcp:
    # ... (from Phase 2)
```

**Benefits:**
- ✅ No Python installation required on host
- ✅ Consistent environment (no "works on my machine")
- ✅ Easy to distribute (just docker-compose.yml)
- ✅ Version pinning (Docker image tags)

### Phase 4: Full Orchestration (Future)
**Status:** Planned  
**Goal:** Complete containerized agent workflows

**Approach:**
Add orchestration layer for multi-step workflows:

**Makefile:**
```makefile
.PHONY: help verify-company validate-projects generate-case-study

help:
	@echo "Casestudypilot - Containerized Workflow"
	@echo ""
	@echo "Commands:"
	@echo "  make start           - Start MCP servers"
	@echo "  make verify-company  - Verify CNCF membership"
	@echo "  make validate-projects - Validate CNCF projects"
	@echo "  make generate-case-study - Full workflow"
	@echo "  make stop            - Stop all containers"

start:
	docker-compose up -d

verify-company:
	@test -n "$(COMPANY)" || (echo "Usage: make verify-company COMPANY=\"Company Name\"" && exit 1)
	docker-compose run --rm cli verify-company "$(COMPANY)"

validate-projects:
	@test -f "$(FILE)" || (echo "Usage: make validate-projects FILE=projects.json" && exit 1)
	docker-compose run --rm cli validate-projects "$(FILE)"

generate-case-study:
	@test -n "$(VIDEO_URL)" || (echo "Usage: make generate-case-study VIDEO_URL=\"https://...\"" && exit 1)
	docker-compose run --rm cli youtube-data "$(VIDEO_URL)"
	docker-compose run --rm cli validate-transcript video_data.json
	# ... full workflow

stop:
	docker-compose down
```

**Benefits:**
- ✅ Simple commands for users (`make verify-company COMPANY="Intuit"`)
- ✅ No Docker knowledge required
- ✅ Workflow automation
- ✅ Easy CI/CD integration

## Technical Considerations

### Container Communication
**Current (Phase 1):** stdio via subprocess.Popen
**Future (Phase 2+):** HTTP or gRPC over Docker network

**MCP Protocol Support:**
- stdio (current) - Process-based, ephemeral
- HTTP/SSE - Persistent, network-based
- gRPC - High-performance, streaming

**Decision Point:** Need to verify if landscape-mcp-server supports HTTP endpoints. If not, may need to:
1. Keep stdio but connect to persistent container via `docker exec`
2. Contribute HTTP endpoint to landscape-mcp-server
3. Create proxy service (stdio ↔ HTTP)

### Volume Mounts Strategy
**Read-Only Mounts:**
- `./templates:/app/templates:ro` - Jinja2 templates
- `./.github:/app/.github:ro` - Skills, agent workflows

**Read-Write Mounts:**
- `./case-studies:/app/case-studies` - Generated case studies
- `./docs:/app/docs` - Plans, documentation
- `./.cache:/app/.cache` - MCP cache, landscape data

**Why This Matters:**
- Read-only mounts prevent accidental modification
- Explicit write locations for security
- Cache persistence improves performance

### Platform Compatibility
**Considerations:**
- Linux: Native Docker, best performance
- macOS: Docker Desktop, volume mount performance issues
- Windows: Docker Desktop or WSL2, path translation

**Solutions:**
- Use named volumes instead of bind mounts for performance-critical data (cache)
- Document platform-specific gotchas
- Provide platform-specific docker-compose overrides

### CI/CD Integration
**GitHub Actions (Current):**
```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    services:
      landscape-mcp:
        image: ghcr.io/cncf/landscape-mcp-server:main
```

**GitHub Actions (Future - Containerized):**
```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Start services
        run: docker-compose up -d
      
      - name: Run tests
        run: docker-compose run --rm cli pytest tests/ -v
      
      - name: Stop services
        run: docker-compose down
```

**Benefits:**
- Same environment in CI and local development
- No "works in CI but not locally" issues

## Security Considerations

### Container Isolation
- Run containers as non-root user where possible
- Use minimal base images (slim, alpine)
- Pin image versions (avoid `:latest` in production)

### Secrets Management
- Never hardcode secrets in Dockerfiles or docker-compose.yml
- Use environment variables for API keys
- Consider Docker secrets for production

### Network Security
- Isolate MCP servers in dedicated Docker network
- Don't expose MCP ports to host (use internal networking)
- Use TLS for production deployments

## Performance Optimization

### Container Startup Time
**Problem:** Cold start overhead (image pull, container creation)

**Solutions:**
1. **Pre-pull images:** `docker-compose pull` before first use
2. **Persistent containers:** Keep MCP servers running (Phase 2)
3. **Image caching:** Use Docker layer caching in CI
4. **Slim images:** Use python:3.11-slim instead of full Python image

### Data Caching
**Problem:** Re-fetching landscape data on every invocation

**Solutions:**
1. **Volume mounts:** Persist landscape data in named volume
2. **In-memory cache:** Keep MCP server running with loaded data (Phase 2)
3. **HTTP cache headers:** Respect ETag/If-Modified-Since from landscape.cncf.io
4. **Periodic updates:** Background job to refresh landscape data

### Build Time
**Problem:** Docker image builds can be slow

**Solutions:**
1. **Multi-stage builds:** Separate dependency installation from app code
2. **Layer caching:** Order Dockerfile commands from least to most frequently changed
3. **.dockerignore:** Exclude unnecessary files from build context

**Example Dockerfile (optimized):**
```dockerfile
FROM python:3.11-slim AS base

WORKDIR /app

# Install dependencies first (cached layer)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code (invalidates cache less frequently)
COPY casestudypilot/ ./casestudypilot/
COPY templates/ ./templates/
COPY .github/ ./.github/

ENTRYPOINT ["python", "-m", "casestudypilot"]
```

## Migration Checklist

### Phase 1: Current Implementation (Issue #16)
- [x] Plan created with containerization strategy
- [ ] MCPClient implemented (subprocess-based)
- [ ] docker-compose.yml created
- [ ] Integration tests use Docker
- [ ] Documentation (this file) written
- [ ] User review of containerization approach

### Phase 2: Persistent MCP Server
- [ ] Research MCP HTTP endpoint support
- [ ] Modify MCPClient for persistent connections
- [ ] Add `casestudypilot mcp start/stop/status` commands
- [ ] Update docker-compose.yml with persistent services
- [ ] Update documentation
- [ ] Benchmark performance improvement

### Phase 3: CLI in Container
- [ ] Create Dockerfile for casestudypilot CLI
- [ ] Update docker-compose.yml with CLI service
- [ ] Test volume mounts for case studies output
- [ ] Update documentation with containerized usage
- [ ] Update CI/CD workflows

### Phase 4: Full Orchestration
- [ ] Create Makefile for common workflows
- [ ] Document all make targets
- [ ] Test on Linux, macOS, Windows
- [ ] Create getting started guide
- [ ] Update CONTRIBUTING.md

## Questions for User Review

1. **Timeline:** Which phase should we target for the next iteration after Phase 1?

2. **HTTP Support:** Should we investigate whether landscape-mcp-server supports HTTP endpoints? Or proceed with stdio-based approach?

3. **Container Runtime:** Should we support both Docker and Podman? Any preference?

4. **Orchestration:** Makefile vs docker-compose commands vs custom CLI (`casestudypilot docker ...`)? What feels most natural?

5. **Distribution:** Should we publish casestudypilot Docker images to a registry (ghcr.io, Docker Hub)? Or keep it local-build-only?

6. **Platform Support:** Any specific platform requirements or constraints (e.g., must work on ARM, must work without Docker Desktop)?

7. **Security:** Are there any organizational security policies we should consider (e.g., approved base images, security scanning)?

## References

- [Model Context Protocol Specification](https://modelcontextprotocol.org)
- [CNCF Landscape MCP Server](https://github.com/cncf/automation/tree/main/utilities/landscape-mcp-server)
- [Docker Compose Best Practices](https://docs.docker.com/compose/production/)
- [Multi-stage Docker Builds](https://docs.docker.com/build/building/multi-stage/)

---

**Document Version:** 1.0  
**Created:** 2026-02-09  
**Last Updated:** 2026-02-09  
**Related Issue:** #16 - Integrate landscape MCP server
