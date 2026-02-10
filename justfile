# CaseStudyPilot - Containerized CNCF Case Study Generator

# Auto-detect container runtime (try podman first, fallback to docker)
container := `command -v podman >/dev/null 2>&1 && echo "podman" || echo "docker"`

# Image name
image := "casestudypilot:latest"

# Show available commands
default:
    @echo "CaseStudyPilot - Container Commands"
    @echo "===================================="
    @echo ""
    @echo "Available commands:"
    @echo "  just build                 Build the container"
    @echo "  just case-study <url>      Generate case study from YouTube URL"
    @echo "  just dev                   Open development shell"
    @echo "  just publish               Publish to GitHub Container Registry"
    @echo ""
    @echo "Using: {{container}}"

# Build the container
build:
    @echo "🏗️  Building with {{container}}..."
    {{container}} build -t {{image}} .
    @echo "✅ Build complete!"

# Generate case study from YouTube URL
case-study url:
    @echo "🎬 Generating case study from: {{url}}"
    @echo "📦 Using: {{container}}"
    {{container}} run --rm -it \
        -v ./case-studies:/output/case-studies \
        -v ./output:/output/data \
        {{image}} \
        youtube-data "{{url}}"

# Development shell with hot-reload
dev:
    @echo "🔥 Starting development shell..."
    @echo "💡 Your code changes will be reflected immediately"
    {{container}} run --rm -it \
        -v ./casestudypilot:/app/casestudypilot \
        -v ./templates:/app/templates \
        -v ./output:/output/data \
        -v ./case-studies:/output/case-studies \
        --entrypoint /bin/sh \
        cgr.dev/chainguard/python:latest-dev

# Publish to GitHub Container Registry
publish:
    @echo "🚀 Publishing to ghcr.io/castrojo/casestudypilot..."
    {{container}} tag {{image}} ghcr.io/castrojo/casestudypilot:latest
    {{container}} push ghcr.io/castrojo/casestudypilot:latest
    @echo "✅ Published!"
