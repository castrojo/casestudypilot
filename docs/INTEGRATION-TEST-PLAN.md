# Reference Architecture Integration Test Plan

## Test Objective

Validate that the reference-architecture-agent workflow executes successfully end-to-end with real YouTube videos, producing high-quality reference architectures that meet CNCF TAB submission standards.

## Test Environment

- **Branch**: `feature/reference-architecture`
- **Worktree**: `.worktrees/reference-architecture/`
- **Container**: Podman with `casestudypilot:latest` image
- **Python Version**: 3.11+ (in container)
- **Dependencies**: All installed via `requirements.txt` and `pyproject.toml`

## Test Videos

### Test 1: Infrastructure-Heavy Video

**Video**: [KubeCon + CloudNativeCon 2023 Talk](https://www.youtube.com/watch?v=rqDrrTKzNd8)

**Video Metadata**:
- **Title**: Check actual title from YouTube
- **Duration**: ~25-30 minutes (estimated)
- **Speaker**: Technical presenter
- **Expected CNCF Projects**: Kubernetes, and potentially others based on content
- **Architecture Focus**: Expected to have infrastructure/platform discussion

**Test Steps**:

```bash
# Step 1: Pre-flight checks
cd /var/home/jorge/src/casestudypilot/.worktrees/reference-architecture
command -v python3
command -v podman
command -v just

# Step 2: Build container (if not already built)
just build

# Step 3: Fetch video data
# This would be done inside container or with installed package
# python -m casestudypilot youtube-data "https://www.youtube.com/watch?v=rqDrrTKzNd8" > test_video_data.json

# Step 4: Validate transcript quality
# python -m casestudypilot validate-transcript test_video_data.json
# Expected: Exit code 0 or 1 (PASS or WARNING)

# Step 5: Apply transcript-correction skill
# Manual LLM task - correct transcript errors

# Step 6: Apply transcript-deep-analysis skill
# Manual LLM task - extract 5+ CNCF projects, 3 layers, integration patterns
# Output: test_deep_analysis.json

# Step 7: Validate deep analysis
# python -m casestudypilot validate-deep-analysis test_deep_analysis.json
# Expected: Exit code 0 (5+ projects, 3 layers, 2+ patterns)

# Step 8: Extract screenshots (6+)
# python -m casestudypilot extract-screenshots test_video_data.json test_deep_analysis.json --download-dir test_screenshots/
# Expected: 6+ .jpg files

# Step 9: Apply architecture-diagram-specification skill
# Manual LLM task - generate textual diagram specifications
# Output: test_diagram_spec.json

# Step 10: Apply reference-architecture-generation skill
# Manual LLM task - generate 13 sections with 2000-5000 words
# Output: test_ref_arch.json

# Step 11: Validate metrics (fabrication check)
# python -m casestudypilot validate-metrics test_ref_arch.json test_video_data.json test_deep_analysis.json
# Expected: Exit code 0 or 1 (all metrics have transcript quotes)

# Step 12: Validate company consistency
# python -m casestudypilot validate-consistency test_ref_arch.json test_video_data.json test_company_verification.json
# Expected: Exit code 0 (consistent company name throughout)

# Step 13: Assemble reference architecture
# python -m casestudypilot assemble-reference-architecture test_ref_arch.json test_screenshots/*.jpg --output test_output.md
# Expected: test_output.md created with 2000-5000 words, 13 sections

# Step 14: Validate technical depth score
# python -m casestudypilot validate-reference-architecture test_ref_arch.json
# Expected: Exit code 0 (score ≥0.70)

# Step 15: Generate TAB submission guidance
# Automatically included in PR description template

# Step 16-18: Create branch, commit, create PR
# git checkout -b ref-arch-test-company-name
# git add reference-architectures/company-name-platform.md reference-architectures/images/company-name-platform/*.jpg
# git commit -m "Add reference architecture for Company Platform"
# gh pr create --title "Reference Architecture: Company Platform" --body "..."
```

**Expected Validation Results**:

| Checkpoint | Tool | Expected Exit Code | Notes |
|-----------|------|-------------------|-------|
| Transcript Quality | validate-transcript | 0 or 1 | ≥2000 chars |
| Deep Analysis | validate-deep-analysis | 0 | 5+ projects, 3 layers, 2+ patterns |
| Metric Fabrication | validate-metrics | 0 or 1 | All metrics cited |
| Company Consistency | validate-consistency | 0 | Consistent company |
| Technical Depth | validate-reference-architecture | 0 | Score ≥0.70 |

**Expected Output**:

```
reference-architectures/
├── company-name-platform.md          # 2500-4000 words
└── images/
    └── company-name-platform/
        ├── screenshot-1.jpg
        ├── screenshot-2.jpg
        ├── screenshot-3.jpg
        ├── screenshot-4.jpg
        ├── screenshot-5.jpg
        └── screenshot-6.jpg
```

**Quality Checks**:

1. ✅ **Word count**: 2000-5000 words
2. ✅ **Structure**: All 13 sections present
3. ✅ **CNCF projects**: 5+ projects with detailed descriptions
4. ✅ **Architecture layers**: Infrastructure, Platform, Application all documented
5. ✅ **Integration patterns**: 2+ patterns described
6. ✅ **Diagrams**: Component and data flow diagrams (textual specifications)
7. ✅ **Screenshots**: 6+ relevant architecture screenshots
8. ✅ **Metrics**: All metrics have transcript citations
9. ✅ **Technical depth score**: ≥0.70
10. ✅ **TAB readiness**: Meets all TAB submission criteria

---

### Test 2: Observability-Focused Video

**Video**: To be selected - KubeCon talk about Prometheus, Grafana, Jaeger, OpenTelemetry

**Expected CNCF Projects**: 
- Prometheus (metrics)
- Grafana (visualization)
- Jaeger (tracing)
- Loki (logs)
- OpenTelemetry (instrumentation)
- Fluentd (log collection)

**Expected Architecture Layers**:
- Infrastructure: Kubernetes clusters, storage for metrics/logs
- Platform: Observability stack (Prometheus, Grafana, Jaeger, Loki)
- Application: Instrumented microservices emitting metrics/traces

**Test Focus**: Validate that observability-heavy architecture is properly captured with emphasis on monitoring, alerting, and tracing patterns.

---

### Test 3: Full-Stack Video

**Video**: To be selected - comprehensive platform talk covering all layers

**Expected CNCF Projects**: 7+ projects spanning infrastructure, platform, and application layers

**Expected Architecture Layers**:
- Infrastructure: Multi-cluster Kubernetes, service mesh, storage
- Platform: CI/CD (Argo CD, Flagger), observability (Prometheus, Grafana), security
- Application: Microservices, API gateway, data layer

**Test Focus**: Validate comprehensive architecture documentation across all 3 layers with complex integration patterns.

---

## Manual Quality Review Checklist

After generating reference architectures, review for:

### Content Quality

- [ ] **Technical Accuracy**: CNCF project descriptions are correct
- [ ] **Version Numbers**: Versions mentioned match video content
- [ ] **Architecture Completeness**: All 3 layers have sufficient detail
- [ ] **Integration Patterns**: Patterns are clearly explained
- [ ] **Implementation Details**: Configurations and specifics are included
- [ ] **Metric Citations**: All metrics have supporting transcript quotes
- [ ] **Company Consistency**: Same company name throughout

### Structure Quality

- [ ] **Section Completeness**: All 13 sections present
- [ ] **Section Length**: Each section meets word count guidelines
  - Executive Summary: 100-200 words
  - Background: 300-500 words
  - Technical Challenge: 300-500 words
  - Architecture Overview: 400-600 words
  - Architecture Diagrams: 200-400 words
  - CNCF Projects: 600-1000 words
  - Integration Patterns: 300-500 words
  - Implementation Details: 400-600 words
  - Deployment Architecture: 200-400 words
  - Security: 200-400 words
  - Observability: 300-500 words
  - Results: 200-400 words
  - Lessons Learned: 200-400 words
  - Conclusion: 100-200 words
- [ ] **Total Word Count**: 2000-5000 words
- [ ] **YAML Frontmatter**: All fields populated correctly

### Screenshot Quality

- [ ] **Relevance**: Screenshots show architecture diagrams or relevant technical content
- [ ] **Quality**: Images are clear and readable
- [ ] **Count**: 6+ screenshots
- [ ] **Association**: Screenshots mapped to correct sections
- [ ] **Captions**: Each screenshot has descriptive caption

### Markdown Quality

- [ ] **Formatting**: Proper markdown syntax
- [ ] **Links**: All internal links work
- [ ] **Tables**: CNCF project table formatted correctly
- [ ] **Lists**: Bulleted and numbered lists formatted correctly
- [ ] **Code Blocks**: None included (diagram specs are textual, not code)
- [ ] **Headers**: Proper heading hierarchy (H2 for sections, H3 for subsections)

### TAB Submission Readiness

- [ ] **Technical Depth Score**: ≥0.70
- [ ] **CNCF Project Count**: 5+ projects
- [ ] **Architecture Documentation**: All 3 layers complete
- [ ] **Implementation Specifics**: Concrete details included
- [ ] **Metric Quality**: Quantifiable results with citations
- [ ] **Professional Tone**: Technical but accessible
- [ ] **Completeness**: No placeholder content or TODOs

---

## Validation Testing

Test all CLI validation commands with various inputs:

### Test validate-deep-analysis

```bash
# Test with valid deep analysis (5+ projects, 3 layers, 2+ patterns)
python -m casestudypilot validate-deep-analysis valid_deep_analysis.json
# Expected: Exit code 0

# Test with warning case (4 projects)
python -m casestudypilot validate-deep-analysis warning_deep_analysis.json
# Expected: Exit code 1

# Test with critical failure (3 projects, missing layer)
python -m casestudypilot validate-deep-analysis critical_deep_analysis.json
# Expected: Exit code 2
```

### Test validate-reference-architecture

```bash
# Test with high quality (score 0.78)
python -m casestudypilot validate-reference-architecture high_quality.json
# Expected: Exit code 0, score ≥0.70

# Test with borderline quality (score 0.65)
python -m casestudypilot validate-reference-architecture borderline.json
# Expected: Exit code 1, score 0.60-0.69

# Test with insufficient quality (score 0.55)
python -m casestudypilot validate-reference-architecture insufficient.json
# Expected: Exit code 2, score <0.60
```

### Test assemble-reference-architecture

```bash
# Test with valid inputs
python -m casestudypilot assemble-reference-architecture \
  ref_arch.json \
  screenshots/*.jpg \
  --output output.md

# Verify:
# - output.md created
# - 2000-5000 words
# - 13 sections present
# - Screenshots copied to images/ directory
# - YAML frontmatter correct
```

---

## Integration Test Results

### Test 1: Infrastructure-Heavy Video (https://www.youtube.com/watch?v=rqDrrTKzNd8)

**Status**: ⏳ Pending execution

**Pre-requisites**:
1. Container built: `just build`
2. Test data directory created: `mkdir -p test-data/test1/`
3. Output directory created: `mkdir -p test-output/test1/`

**Execution Command**:
```bash
# Run full workflow in development shell
just dev
# Then inside container:
# Follow 18-step workflow from reference-architecture-agent.md
```

**Expected Outcome**:
- ✅ All 7 validation checkpoints pass (5 critical)
- ✅ Technical depth score ≥0.70
- ✅ Reference architecture generated with 2000-5000 words
- ✅ 6+ screenshots extracted
- ✅ All 13 sections present and complete

**Actual Outcome**: [To be filled after test execution]

---

### Test 2: Observability-Focused Video

**Status**: ⏳ Pending video selection and execution

---

### Test 3: Full-Stack Video

**Status**: ⏳ Pending video selection and execution

---

## Performance Metrics

Track agent performance:

| Metric | Target | Test 1 | Test 2 | Test 3 |
|--------|--------|--------|--------|--------|
| **Total Processing Time** | 15-25 min | | | |
| **Transcript Fetch** | <1 min | | | |
| **Deep Analysis** | 3-5 min | | | |
| **Screenshot Extraction** | 2-3 min | | | |
| **Content Generation** | 5-10 min | | | |
| **Assembly & Validation** | 1-2 min | | | |
| **Technical Depth Score** | ≥0.70 | | | |
| **Word Count** | 2000-5000 | | | |
| **CNCF Projects** | 5+ | | | |

---

## Known Issues & Workarounds

### Issue 1: Container build time

**Issue**: Initial container build takes 5-10 minutes

**Workaround**: Build once, reuse image for all tests

### Issue 2: YouTube transcript availability

**Issue**: Some videos don't have captions or have poor auto-generated captions

**Workaround**: 
- Test with known good videos (KubeCon talks with manual captions)
- Skip videos without captions (validation will catch this)

### Issue 3: LLM skill execution requires manual intervention

**Issue**: Skills need to be executed by LLM agents, not automated scripts

**Workaround**:
- Document skill execution in test plan
- Create sample skill outputs for validation testing
- Test CLI tools independently with mock data

---

## Test Data Creation

For validation testing without full workflow execution, create sample test data:

### Sample Deep Analysis (valid_deep_analysis.json)

```json
{
  "company": "Test Company",
  "cncf_projects": [
    {"name": "Kubernetes", "category": "Orchestration", "usage": "Container orchestration for 200+ microservices"},
    {"name": "Prometheus", "category": "Monitoring", "usage": "Metrics collection and alerting"},
    {"name": "Grafana", "category": "Visualization", "usage": "Dashboards and visualization"},
    {"name": "Istio", "category": "Service Mesh", "usage": "Service-to-service communication and mTLS"},
    {"name": "Flagger", "category": "Progressive Delivery", "usage": "Automated canary deployments"}
  ],
  "architecture_layers": {
    "infrastructure": "Multi-cluster Kubernetes on AWS EKS...",
    "platform": "CI/CD pipeline with Argo CD, observability with Prometheus...",
    "application": "120 microservices in Go and Python..."
  },
  "integration_patterns": [
    {"name": "Service Mesh Integration", "description": "Istio + Flagger for progressive delivery"},
    {"name": "Observability Stack", "description": "Prometheus + Grafana + Jaeger for full observability"}
  ],
  "screenshot_opportunities": [
    {"timestamp": "5:23", "description": "Infrastructure layer diagram"},
    {"timestamp": "8:45", "description": "Service mesh architecture"},
    {"timestamp": "12:10", "description": "CI/CD pipeline flow"},
    {"timestamp": "15:30", "description": "Observability stack"},
    {"timestamp": "18:20", "description": "Canary deployment process"},
    {"timestamp": "21:45", "description": "Multi-cluster setup"}
  ],
  "sections": {
    "background": "Test Company is a fintech company serving 5 million users...",
    "technical_challenge": "Legacy monolithic architecture caused scaling issues...",
    "architecture_overview": "The architecture consists of three layers...",
    "cncf_projects": "This implementation uses 5 CNCF projects...",
    "integration_patterns": "Two main integration patterns emerged...",
    "results": "The platform now handles 10x more traffic..."
  }
}
```

### Sample Reference Architecture (high_quality.json)

Create JSON with:
- 5+ CNCF projects with detailed descriptions (100+ words each)
- All 13 sections with appropriate word counts
- Concrete implementation details (version numbers, configurations)
- Quantifiable metrics with transcript quotes
- All 3 architecture layers documented

---

## Test Execution Timeline

1. **Day 1**: Build container, create test data, validate CLI tools
2. **Day 2**: Execute Test 1 (infrastructure-heavy video)
3. **Day 3**: Execute Test 2 (observability-focused video)
4. **Day 4**: Execute Test 3 (full-stack video)
5. **Day 5**: Manual quality review, document findings

---

## Success Criteria

Integration testing is successful when:

- ✅ All 3 test videos process successfully
- ✅ All validation checkpoints pass (0 critical failures)
- ✅ Technical depth scores ≥0.70 for all outputs
- ✅ Generated reference architectures meet TAB submission criteria
- ✅ No fabricated metrics (all have transcript citations)
- ✅ Company consistency maintained throughout
- ✅ Performance metrics within targets
- ✅ Manual quality review finds no critical issues

---

**Test Plan Version**: 1.0.0  
**Created**: 2026-02-10  
**Status**: Draft - Ready for execution  
**Next Step**: Execute Test 1 with video rqDrrTKzNd8
