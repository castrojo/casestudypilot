# 🐋 Container Quick Start

## Prerequisites

Install either **Podman** (recommended) or **Docker**:

### Podman (Recommended)
```bash
# Fedora/RHEL/CentOS
sudo dnf install podman

# Ubuntu/Debian
sudo apt install podman

# macOS
brew install podman
podman machine init
podman machine start
```

### Docker
See: https://docs.docker.com/get-docker/

### Just (Command Runner)
```bash
# macOS
brew install just

# Linux
cargo install just
# Or download from: https://github.com/casey/just/releases
```

## Quick Start

```bash
# 1. Build the container (one time)
just build

# 2. Generate a case study
just case-study 'https://www.youtube.com/watch?v=VIDEO_ID'

# 3. View output
ls case-studies/
```

## Commands

### `just build`
Build the container image using Chainguard Python.

**When to use:** First time setup, or after updating dependencies.

**Example:**
```bash
just build
```

**Output:**
```
🏗️  Building with podman...
STEP 1/15: FROM cgr.dev/chainguard/python:latest-dev AS builder
...
✅ Build complete!
```

### `just case-study <url>`
Generate a case study from a YouTube URL.

**Example:**
```bash
just case-study 'https://www.youtube.com/watch?v=V6L-xOUdoRQ'
```

**Output:**
- `output/video_data.json` - Video metadata and transcript
- `case-studies/` - Final case study markdown (after full workflow)

**Note:** This command only runs the first step (fetch video data). For the full workflow, you'll need to run additional commands manually or use an LLM agent to orchestrate the complete process.

### `just dev`
Open an interactive development shell with hot-reload.

**When to use:** 
- Debugging the application
- Developing new features
- Running commands manually

**Features:**
- Edit code on host → Changes reflected in container immediately
- No rebuild needed
- Full Python environment available

**Example session:**
```bash
just dev

# Now in container shell
/app $ python -m casestudypilot --help
/app $ python -m casestudypilot validate-transcript /output/data/video_data.json
/app $ exit
```

### `just publish`
Publish the container image to GitHub Container Registry (GHCR).

**Prerequisites:**
1. Create GitHub Personal Access Token (PAT) at https://github.com/settings/tokens
2. Scopes needed: `write:packages`, `read:packages`
3. Login: `echo $GITHUB_TOKEN | podman login ghcr.io -u USERNAME --password-stdin`

**Example:**
```bash
export GITHUB_TOKEN="ghp_xxxxxxxxxxxx"
echo $GITHUB_TOKEN | podman login ghcr.io -u castrojo --password-stdin
just publish
```

## Running Individual CLI Commands

The container exposes all 11 CLI commands. Run them directly with `podman run` (or `docker run`):

### Fetch Video Data
```bash
podman run --rm -it \
    -v ./output:/output/data \
    casestudypilot:latest \
    youtube-data 'https://youtube.com/watch?v=VIDEO_ID' \
    --output /output/data/video_data.json
```

### Validate Transcript
```bash
podman run --rm -it \
    -v ./output:/output/data \
    casestudypilot:latest \
    validate-transcript /output/data/video_data.json
```

### Verify Company
```bash
podman run --rm -it \
    -v ./output:/output/data \
    casestudypilot:latest \
    verify-company "Intuit" --output /output/data/company_verification.json
```

### Extract Screenshots
```bash
podman run --rm -it \
    -v ./output:/output/data \
    -v ./case-studies:/output/case-studies \
    casestudypilot:latest \
    extract-screenshots \
    /output/data/video_data.json \
    /output/data/analysis.json \
    /output/data/sections.json \
    --download-dir /output/case-studies/images/company-slug \
    --output /output/data/screenshots.json
```

### Assemble Case Study
```bash
podman run --rm -it \
    -v ./output:/output/data \
    -v ./case-studies:/output/case-studies \
    casestudypilot:latest \
    assemble \
    /output/data/video_data.json \
    /output/data/analysis.json \
    /output/data/sections.json \
    /output/data/verification.json \
    --screenshots /output/data/screenshots.json
```

### Validate Final Case Study
```bash
podman run --rm -it \
    -v ./case-studies:/output/case-studies \
    -v ./output:/output/data \
    casestudypilot:latest \
    validate /output/case-studies/company.md \
    --threshold 0.60 \
    --output /output/data/validation_results.json
```

### Run All Validations
```bash
podman run --rm -it \
    -v ./output:/output/data \
    casestudypilot:latest \
    validate-all \
    /output/data/video_data.json \
    /output/data/analysis.json \
    /output/data/sections.json \
    /output/data/verification.json
```

## Using Docker Instead of Podman

The Justfile auto-detects your container runtime. If you have Docker installed instead of Podman, it will work automatically.

To explicitly use Docker in manual commands:
```bash
# Replace 'podman' with 'docker'
docker run --rm -it -v ./output:/output/data casestudypilot:latest --help
```

## Pulling from GHCR

Once published, anyone can pull and use the image:

```bash
# Pull the image
podman pull ghcr.io/castrojo/casestudypilot:latest

# Use it directly (no build needed!)
podman run --rm -it \
    -v ./output:/output/data \
    ghcr.io/castrojo/casestudypilot:latest \
    youtube-data 'https://youtube.com/watch?v=VIDEO_ID'
```

## Troubleshooting

### "command not found: just"
Install Just: https://github.com/casey/just#installation

### "command not found: podman" and "command not found: docker"
Install at least one container runtime (see Prerequisites above).

### Permission denied on volumes (Linux with SELinux)
Add `:Z` flag for SELinux contexts:
```bash
podman run -v ./output:/output/data:Z casestudypilot:latest ...
```

### Image size concerns
- **Production image:** ~50-70MB (using Chainguard Python)
- **Development image:** ~100MB (includes dev tools)
- **Zero CVEs by default** (Chainguard benefit)

To check your image size:
```bash
podman images casestudypilot:latest
```

### Build failures
If the build fails, try:
```bash
# Clear build cache
podman system prune -a

# Rebuild from scratch
just build
```

### Volume mount issues on macOS
If volumes don't work on macOS, ensure Podman machine is running:
```bash
podman machine start
podman machine list
```

## Why Chainguard?

CaseStudyPilot uses Chainguard Python images for security and efficiency:

- ✅ **Minimal size** - 50-70MB vs 180MB for python:slim
- ✅ **Zero CVEs** - 97.6% fewer vulnerabilities than standard images
- ✅ **Daily updates** - Automatic security patches
- ✅ **Supply chain security** - Built-in SBOM and Sigstore signing
- ✅ **Production-ready** - Used by Fortune 500 companies (Snowflake, GitLab, Canva)
- ✅ **Distroless** - No shell or package manager in production (attack surface minimization)

Learn more: https://www.chainguard.dev/chainguard-images

## Next Steps

- See [README.md](../README.md) for full application documentation
- See [AGENTS.md](../AGENTS.md) for LLM agent workflows
- See [CONTRIBUTING.md](../CONTRIBUTING.md) for development guide

## Full Workflow Example

Here's how to run the complete case study generation workflow using containers:

```bash
# Step 1: Build container (one time)
just build

# Step 2: Fetch video data
just case-study 'https://www.youtube.com/watch?v=VIDEO_ID'

# Step 3: Validate transcript
podman run --rm -it \
    -v ./output:/output/data \
    casestudypilot:latest \
    validate-transcript /output/data/video_data.json

# Step 4-6: LLM agent performs analysis
# (transcript-correction, transcript-analysis, case-study-generation skills)
# This requires an LLM agent - see AGENTS.md

# Step 7: Verify company
podman run --rm -it \
    -v ./output:/output/data \
    casestudypilot:latest \
    verify-company "Company Name" --output /output/data/company_verification.json

# Step 8: Extract screenshots
podman run --rm -it \
    -v ./output:/output/data \
    -v ./case-studies:/output/case-studies \
    casestudypilot:latest \
    extract-screenshots \
    /output/data/video_data.json \
    /output/data/analysis.json \
    /output/data/sections.json \
    --download-dir /output/case-studies/images/company-slug \
    --output /output/data/screenshots.json

# Step 9: Assemble case study
podman run --rm -it \
    -v ./output:/output/data \
    -v ./case-studies:/output/case-studies \
    casestudypilot:latest \
    assemble \
    /output/data/video_data.json \
    /output/data/analysis.json \
    /output/data/sections.json \
    /output/data/verification.json \
    --screenshots /output/data/screenshots.json

# Step 10: Validate final quality
podman run --rm -it \
    -v ./case-studies:/output/case-studies \
    -v ./output:/output/data \
    casestudypilot:latest \
    validate /output/case-studies/company.md \
    --threshold 0.60

# Done! View your case study
cat case-studies/company.md
```
