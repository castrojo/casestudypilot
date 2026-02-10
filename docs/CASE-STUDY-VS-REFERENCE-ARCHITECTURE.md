# Case Study vs Reference Architecture: Complete Comparison

## Quick Decision Tree

```
START: You have a CNCF technical talk video
  │
  ├─ Video Length?
  │   ├─ 10-20 minutes → CASE STUDY (likely)
  │   └─ 15-40 minutes → Continue...
  │
  ├─ CNCF Projects Mentioned?
  │   ├─ 2-3 projects → CASE STUDY
  │   ├─ 4 projects → Continue...
  │   └─ 5+ projects → REFERENCE ARCHITECTURE (likely)
  │
  ├─ Content Focus?
  │   ├─ Business story (challenge → solution → impact) → CASE STUDY
  │   └─ Technical architecture (how it's built) → REFERENCE ARCHITECTURE
  │
  ├─ Target Audience?
  │   ├─ Business stakeholders / Executives → CASE STUDY
  │   └─ Engineers / Architects → REFERENCE ARCHITECTURE
  │
  └─ Video Contains Architecture Diagrams?
      ├─ No or minimal → CASE STUDY
      └─ Yes, detailed system architecture → REFERENCE ARCHITECTURE
```

---

## Side-by-Side Comparison

### Content Characteristics

| Dimension | Case Study | Reference Architecture |
|-----------|-----------|----------------------|
| **Primary Goal** | Tell a success story | Document an architecture |
| **Narrative Style** | Story-driven (beginning, middle, end) | Technical documentation |
| **Word Count** | 500-1500 words | 2000-5000 words |
| **Reading Time** | 3-8 minutes | 10-25 minutes |
| **Depth Level** | Overview with key highlights | Comprehensive deep dive |
| **Structure** | 5 narrative sections | 13 technical sections |
| **Tone** | Inspirational, achievement-focused | Technical, instructional |
| **Perspective** | "What we achieved" | "How we built it" |

### Audience & Use Cases

| Aspect | Case Study | Reference Architecture |
|--------|-----------|----------------------|
| **Primary Audience** | C-suite, VPs, business leaders | Lead engineers, architects, technical leaders |
| **Secondary Audience** | Product managers, team leads | Senior engineers, DevOps teams |
| **Reader's Question** | "Should we adopt this?" | "How do we implement this?" |
| **Read When** | Evaluating technology adoption | Planning implementation |
| **Shared With** | Leadership, stakeholders | Engineering teams, architecture review boards |
| **Convinces** | That it works | How it works |
| **Value Delivered** | Business case, ROI | Implementation blueprint |

### Video Requirements

| Requirement | Case Study | Reference Architecture |
|-------------|-----------|----------------------|
| **Length** | 10-20 minutes | 15-40 minutes |
| **Minimum Characters** | 1,000 transcript chars | 2,000 transcript chars |
| **CNCF Projects** | 2+ projects | 5+ projects |
| **Architecture Depth** | Mentioned briefly | Explained in detail |
| **Diagrams in Video** | Optional | Highly recommended |
| **Technical Details** | Moderate | Extensive |
| **Metrics Discussed** | Business metrics | Technical metrics + business metrics |
| **Speaker Profile** | Business or technical | Usually technical (architect, lead engineer) |

### Technical Depth

| Area | Case Study | Reference Architecture |
|------|-----------|----------------------|
| **CNCF Projects** | 2-3 projects named | 5+ projects detailed |
| **Project Detail** | Usage context (1-2 sentences each) | Deep dive (100-200 words each) |
| **Architecture Layers** | May mention | All 3 layers documented (Infrastructure, Platform, Application) |
| **Integration Patterns** | Not required | 2+ patterns required |
| **Version Numbers** | Optional | Expected |
| **Configuration Details** | Not required | Recommended |
| **Code Samples** | Not included | Can be added manually |
| **Deployment Details** | High-level | Detailed (CI/CD, strategies, rollback) |

### Content Structure

#### Case Study (5 Sections)

1. **Background** (100-200 words)
   - Company context
   - Industry and scale
   - Initial situation

2. **Challenge** (150-250 words)
   - Problem statement
   - Technical or business constraints
   - Why change was needed

3. **Solution** (200-400 words)
   - Technologies adopted (2-3 CNCF projects)
   - High-level architecture
   - Implementation approach

4. **Impact** (150-300 words)
   - Business metrics (cost savings, revenue)
   - Technical improvements (speed, reliability)
   - Team benefits (productivity, morale)

5. **Conclusion** (50-100 words)
   - Key takeaways
   - Future plans

#### Reference Architecture (13 Sections)

1. **Executive Summary** (100-200 words)
   - High-level overview for technical leaders
   - Key projects and patterns

2. **Background & Context** (300-500 words)
   - Company and industry context
   - Business requirements
   - Why this architecture was needed

3. **Technical Challenge** (300-500 words)
   - Specific technical problems
   - Scale or performance challenges
   - Constraints and requirements

4. **Architecture Overview** (400-600 words)
   - **3-layer breakdown:**
     - Infrastructure (compute, network, storage)
     - Platform (CI/CD, service mesh, observability)
     - Application (microservices, data layer)

5. **Architecture Diagrams** (200-400 words)
   - Component diagram (textual specification)
   - Data flow diagram (textual specification)

6. **CNCF Projects Deep Dive** (600-1000 words)
   - **For each of 5+ projects:**
     - Version used
     - Specific use case
     - Configuration highlights
     - Integration with other projects
     - Lessons learned

7. **Integration Patterns** (300-500 words)
   - How projects work together
   - Communication patterns
   - Data flow patterns

8. **Implementation Details** (400-600 words)
   - Concrete configurations
   - Resource requirements
   - Scaling characteristics

9. **Deployment Architecture** (200-400 words)
   - CI/CD pipeline
   - Deployment strategies
   - Rollback procedures

10. **Security Considerations** (200-400 words)
    - Authentication/authorization
    - Network security
    - Secrets management

11. **Observability & Operations** (300-500 words)
    - Monitoring stack
    - Dashboards and alerts
    - Incident response

12. **Results & Impact** (200-400 words)
    - Performance improvements
    - Operational metrics
    - Business impact

13. **Lessons Learned & Best Practices** (200-400 words)
    - What worked well
    - Challenges faced
    - Advice for others

### Validation & Quality

| Validation Checkpoint | Case Study | Reference Architecture |
|----------------------|-----------|----------------------|
| **Transcript Quality** | ≥1,000 chars, 50 segments, 100 words | ≥2,000 chars, 100 segments, 200 words |
| **Company Identification** | Required, confidence ≥0.7 | Required, confidence ≥0.7 |
| **CNCF Projects** | Minimum 2 (WARN at 1, CRITICAL at 0) | Minimum 5 (WARN at 4, CRITICAL at <4) |
| **Architecture Layers** | Not validated | All 3 required (CRITICAL if missing) |
| **Integration Patterns** | Not validated | Minimum 2 (WARN at 1, CRITICAL at 0) |
| **Metric Fabrication** | Checked (warn only) | Checked (CRITICAL) |
| **Company Consistency** | Checked (CRITICAL) | Checked (CRITICAL) |
| **Quality Score Threshold** | ≥0.60 (multi-factor) | ≥0.70 (technical depth) |
| **Scoring Algorithm** | 4-dimensional (structure, depth, CNCF, formatting) | 5-dimensional (project depth, specificity, implementation, metrics, architecture) |

### Scoring Algorithms

#### Case Study Quality Score

```python
quality_score = (
    0.30 * structure_score +      # Required sections present
    0.40 * content_depth_score +  # Word counts per section
    0.20 * cncf_mentions_score +  # 2+ projects referenced
    0.10 * formatting_score       # Markdown quality
)

# Threshold: ≥0.60 for PASS
```

#### Reference Architecture Technical Depth Score

```python
technical_depth_score = (
    0.25 * cncf_project_depth +      # 5+ projects, detailed descriptions
    0.20 * technical_specificity +    # Concrete implementation details
    0.20 * implementation_detail +    # Version numbers, configurations
    0.20 * metric_quality +           # Quantifiable results with citations
    0.15 * architecture_completeness  # All 3 layers documented
)

# Threshold: ≥0.70 for PASS
```

**Key Difference:** Reference architecture scoring is **more stringent** (0.70 vs 0.60) and emphasizes **technical specificity** over narrative structure.

### Workflow & Agent

| Workflow Step | Case Study Agent (v2.2.0) | Reference Architecture Agent (v1.0.0) |
|---------------|---------------------------|-------------------------------------|
| **Total Steps** | 14 steps | 18 steps |
| **Validation Checkpoints** | 5 checkpoints | 7 checkpoints (5 critical) |
| **Transcript Correction** | Yes (transcript-correction skill) | Yes (transcript-correction skill) |
| **Analysis Skill** | transcript-analysis | transcript-deep-analysis |
| **Generation Skill** | case-study-generation | reference-architecture-generation |
| **Additional Skills** | None | architecture-diagram-specification |
| **Screenshots** | 3 screenshots | 6+ screenshots |
| **Assembly Tool** | assemble | assemble-reference-architecture |
| **Template** | case_study.md.j2 | reference_architecture.md.j2 |
| **Output Directory** | case-studies/ | reference-architectures/ |
| **Processing Time** | ~5-10 minutes | ~15-25 minutes |

### Output Files

#### Case Study Output

```
case-studies/
├── company-name.md                      # Main content (~800 words)
└── images/
    └── company-name/
        ├── screenshot-1.jpg             # Key moment 1
        ├── screenshot-2.jpg             # Key moment 2
        └── screenshot-3.jpg             # Key moment 3
```

**Filename pattern:** `company-name.md` (slugified company name)

**YAML Frontmatter:**
```yaml
---
title: "Company Name Case Study"
company: "Company Name"
industry: "Technology"
cncf_projects:
  - "Kubernetes"
  - "Prometheus"
video_url: "https://youtube.com/..."
publication_date: "2026-02-10"
---
```

#### Reference Architecture Output

```
reference-architectures/
├── company-name-platform.md                    # Main content (~3500 words)
└── images/
    └── company-name-platform/
        ├── screenshot-1.jpg                    # Infrastructure layer
        ├── screenshot-2.jpg                    # Platform services
        ├── screenshot-3.jpg                    # Application layer
        ├── screenshot-4.jpg                    # Integration pattern
        ├── screenshot-5.jpg                    # Observability stack
        ├── screenshot-6.jpg                    # Security/deployment
        └── [potentially more screenshots]
```

**Filename pattern:** `company-name-descriptive-title.md` (includes architecture descriptor)

**YAML Frontmatter:**
```yaml
---
title: "Reference Architecture: Company Name Cloud-Native Platform"
subtitle: "Multi-cluster Kubernetes with Service Mesh and Progressive Delivery"
company: "Company Name"
industry: "Technology"
video_url: "https://youtube.com/..."
publication_date: "2026-02-10"
tab_status: "ready_for_submission"
primary_patterns:
  - "Multi-cluster orchestration"
  - "Service mesh architecture"
  - "Progressive delivery"
---
```

### CNCF TAB Submission

| Aspect | Case Study | Reference Architecture |
|--------|-----------|----------------------|
| **Designed for TAB Submission** | No | Yes |
| **TAB Submission Guidance** | Not included | Automatically generated |
| **TAB Quality Bar** | Below threshold | Meets or exceeds threshold |
| **Technical Depth** | Insufficient for TAB review | Sufficient for TAB review |
| **Typical TAB Use Case** | Not applicable | Example architecture for community |
| **Promotion Potential** | Internal sharing, blog posts | CNCF website, training materials |

---

## Detailed Decision Scenarios

### Scenario 1: KubeCon Keynote (20 minutes)

**Video Details:**
- Speaker: CTO of major company
- Content: Company's cloud-native journey
- Projects: Kubernetes, Prometheus, Envoy mentioned
- Focus: Business transformation story

**Analysis:**
- ✅ 20 minutes (fits both)
- ✅ 3 CNCF projects (fits Case Study, not enough for Ref Arch)
- ✅ Business-focused (Case Study strength)
- ❌ Limited architecture details (Ref Arch weakness)

**Recommendation:** **Case Study**

**Reasoning:** Despite adequate length, the business focus and limited architecture detail make this ideal for a case study. The CTO perspective is perfect for business stakeholders.

---

### Scenario 2: Technical Deep Dive (35 minutes)

**Video Details:**
- Speaker: Principal Engineer
- Content: Multi-cluster Kubernetes platform architecture
- Projects: Kubernetes, Istio, Prometheus, Grafana, Flagger, Argo CD, Jaeger
- Focus: System architecture, integration patterns, implementation

**Analysis:**
- ✅ 35 minutes (ideal for Ref Arch)
- ✅ 7 CNCF projects (exceeds Ref Arch requirement)
- ✅ Technical focus (Ref Arch strength)
- ✅ Architecture diagrams shown
- ✅ Implementation details discussed

**Recommendation:** **Reference Architecture**

**Reasoning:** Perfect fit for reference architecture. Technical depth, multiple projects, architecture focus, and engineer perspective.

---

### Scenario 3: Lightning Talk (10 minutes)

**Video Details:**
- Speaker: Developer
- Content: Quick overview of migration to Kubernetes
- Projects: Kubernetes, Helm
- Focus: Migration approach

**Analysis:**
- ⚠️ 10 minutes (borderline short)
- ⚠️ 2 CNCF projects (minimum for Case Study)
- ✅ Story-driven (Case Study fit)
- ❌ Too short for Ref Arch

**Recommendation:** **Case Study** (with expectations of shorter content)

**Reasoning:** Lightning talks work for case studies but will produce shorter content (~500-800 words). Not suitable for reference architecture due to length and limited depth.

---

### Scenario 4: Architecture Walkthrough (25 minutes)

**Video Details:**
- Speaker: Solutions Architect
- Content: Production platform architecture
- Projects: Kubernetes, Prometheus, Grafana, Linkerd
- Focus: 60% architecture, 40% business impact

**Analysis:**
- ✅ 25 minutes (good for both)
- ⚠️ 4 CNCF projects (borderline)
- ⚠️ Mixed focus (architecture + business)
- ⚠️ Shows some diagrams

**Recommendation:** **Try Reference Architecture first, fall back to Case Study if validation fails**

**Reasoning:** Borderline scenario. The 4 projects will trigger a WARNING in reference architecture validation. If technical depth score is ≥0.70, proceed with reference architecture. If score is 0.60-0.69, consider case study instead.

---

### Scenario 5: Customer Success Story (15 minutes)

**Video Details:**
- Speaker: VP of Engineering
- Content: How adopting cloud-native improved business
- Projects: Kubernetes, AWS services, some CNCF projects
- Focus: Business outcomes, ROI

**Analysis:**
- ✅ 15 minutes (fits both)
- ⚠️ Mix of CNCF and non-CNCF projects
- ✅ Business focus (Case Study strength)
- ❌ VP perspective, not deep technical (Ref Arch weakness)

**Recommendation:** **Case Study**

**Reasoning:** Business-focused success story from executive perspective is ideal for case study. Even if video mentions 5+ projects, the lack of technical depth would likely fail reference architecture validation.

---

### Scenario 6: Observability Stack Implementation (30 minutes)

**Video Details:**
- Speaker: SRE Lead
- Content: Building production observability with CNCF projects
- Projects: Prometheus, Grafana, Jaeger, Loki, OpenTelemetry, Fluentd
- Focus: Implementation details, configurations, integration

**Analysis:**
- ✅ 30 minutes (ideal for Ref Arch)
- ✅ 6 CNCF projects (exceeds requirement)
- ✅ Technical implementation focus
- ✅ Specific configurations discussed
- ✅ Shows dashboards and architecture

**Recommendation:** **Reference Architecture**

**Reasoning:** Textbook reference architecture candidate. SRE perspective with implementation details, 6 projects, and technical focus.

---

## Migration Between Types

### Converting Case Study → Reference Architecture

**When to consider:**
- Case study technical depth score is 0.65-0.69 (high for case study)
- Original video is 20+ minutes with more technical content
- Community feedback requests more architectural detail

**Process:**
1. Re-label GitHub issue: add `reference-architecture` label
2. Comment on issue: "Requesting reference architecture regeneration - video has sufficient depth"
3. Reference architecture agent will re-process video with deeper analysis
4. Original case study remains in `case-studies/` directory
5. New reference architecture created in `reference-architectures/` directory

**What changes:**
- Uses `transcript-deep-analysis` instead of `transcript-analysis`
- Requires 5+ CNCF projects (may fail if video only has 2-3)
- Generates 13 sections instead of 5
- Technical depth scoring (0.70 threshold instead of 0.60)

### Converting Reference Architecture → Case Study

**When to consider:**
- Reference architecture validation fails (technical depth <0.60)
- Only 3-4 CNCF projects identified
- Video is more business-focused than technical
- Target audience is business stakeholders

**Process:**
1. Remove `reference-architecture` label from issue
2. Add `case-study` label
3. Case study agent will process with lower requirements
4. Case study generated with 5 sections instead of 13

**What changes:**
- Uses simpler `transcript-analysis` instead of `transcript-deep-analysis`
- Requires only 2+ CNCF projects
- Generates 5 narrative sections
- Quality scoring (0.60 threshold instead of 0.70)

### Creating Both from Same Video

**When to consider:**
- Video has both business story and technical architecture
- Want to serve both executive and engineering audiences
- Video is comprehensive (30+ minutes)

**Process:**
1. Create two separate GitHub issues:
   - Issue 1: "Case Study - Company Name" with `case-study` label
   - Issue 2: "Reference Architecture - Company Name Platform" with `reference-architecture` label
2. Use same video URL in both
3. Two agents will process independently
4. Case study: `case-studies/company-name.md`
5. Reference architecture: `reference-architectures/company-name-platform.md`

**Benefits:**
- Case study for executive briefings and business stakeholder sharing
- Reference architecture for engineering teams and TAB submission
- Maximum value extracted from high-quality source material

---

## Common Questions

### "My video has 4 CNCF projects - which should I use?"

**Answer:** Start with **Case Study**.

4 projects is above the case study requirement (2+) but below the reference architecture requirement (5+). Reference architecture validation will trigger a WARNING, and you may end up with a lower technical depth score.

**However:** If the video is very technical with detailed architecture (35+ minutes, system diagrams, implementation details), you could try **Reference Architecture** first. If validation fails, fall back to case study.

### "My video is 18 minutes - is that too short for reference architecture?"

**Answer:** **Borderline, depends on content density.**

18 minutes can work for reference architecture if:
- ✅ Transcript is ≥2000 characters (check caption density)
- ✅ Video discusses 5+ CNCF projects
- ✅ Includes architecture diagrams and implementation details
- ✅ Speaker moves quickly through technical content

If video has long pauses, demo time, or Q&A, it may lack sufficient content. Try reference architecture first - if "Transcript Quality" or "Deep Analysis" validation fails, use case study instead.

### "Can I manually specify which type to generate?"

**Answer:** Yes, via **GitHub issue labels**.

- Add `case-study` label → triggers case-study-agent
- Add `reference-architecture` label → triggers reference-architecture-agent
- Add both labels → both agents process (generates both types)

You can also comment on the issue with explicit instructions:
```
@reference-architecture-agent please generate a reference architecture focusing on the observability stack implementation.
```

### "What if I'm not sure which to choose?"

**Answer:** **Start with Reference Architecture** if video is 15+ minutes and technical.

Reference architecture is more comprehensive - if validation fails, you can fall back to case study. Starting with case study and later wanting reference architecture requires full regeneration.

**Fallback strategy:**
1. Try reference architecture first
2. If "Deep Analysis" validation fails (< 5 projects or < 2 patterns) → regenerate as case study
3. If "Technical Depth Score" is < 0.60 → regenerate as case study

### "Do I lose anything by choosing case study over reference architecture?"

**Answer:** You lose **architectural depth and detail**, but gain **accessibility and brevity**.

**Case Study provides:**
- ✅ Faster generation (~10 min vs ~20 min)
- ✅ More accessible to business audiences
- ✅ Easier to share in newsletters, blog posts
- ✅ Focused narrative (challenge → solution → impact)

**Reference Architecture provides:**
- ✅ Implementation blueprint for engineers
- ✅ Detailed CNCF project usage
- ✅ Architecture patterns and integration details
- ✅ TAB submission readiness
- ✅ Training material potential

**Best of both worlds:** Generate both types from the same video (see "Creating Both from Same Video" above).

### "Can I submit a case study to CNCF TAB?"

**Answer:** **No, case studies are not suitable for TAB submission.**

TAB expects:
- Technical depth (reference architectures have 0.70 threshold vs 0.60 for case studies)
- Architecture documentation (13 sections vs 5)
- Implementation details (reference architectures have 5+ projects vs 2+)
- Engineering perspective (reference architectures focus on "how" vs case studies focus on "why")

If you want TAB submission, generate a **reference architecture**.

---

## Summary Recommendation Matrix

| Video Characteristics | Recommendation | Confidence |
|----------------------|---------------|-----------|
| 10-15 min, 2-3 projects, business focus | **Case Study** | High |
| 15-20 min, 3-4 projects, mixed focus | **Case Study** | Medium |
| 20-25 min, 4-5 projects, technical focus | **Reference Architecture** (try first) | Medium |
| 25-40 min, 5+ projects, architecture focus | **Reference Architecture** | High |
| 40+ min, 7+ projects, deep technical | **Reference Architecture** | High |
| Executive/VP speaker, business metrics | **Case Study** | High |
| Engineer/Architect speaker, system diagrams | **Reference Architecture** | High |
| Story-driven (challenge → solution → impact) | **Case Study** | High |
| Architecture-driven (layers, patterns, integration) | **Reference Architecture** | High |
| Target: business stakeholders | **Case Study** | High |
| Target: engineering teams | **Reference Architecture** | High |
| Goal: convince leadership | **Case Study** | High |
| Goal: implement similar architecture | **Reference Architecture** | High |
| Goal: CNCF TAB submission | **Reference Architecture** | High |
| Video title contains "Deep Dive", "Architecture", "Implementation" | **Reference Architecture** | Medium-High |
| Video title contains "Journey", "Transformation", "Success Story" | **Case Study** | Medium-High |

---

## Final Recommendations

### Use Case Study When:
1. 🎯 You want to **convince** stakeholders to adopt cloud-native
2. 📊 You need **business metrics** and ROI justification
3. 👔 Your audience is **executives** or business leaders
4. ⏱️ You need **quick, accessible** content
5. 📱 You want to share in **newsletters** or blog posts
6. 🎤 Speaker is CTO, VP, or executive (business perspective)
7. 📖 Video tells a **story** with clear beginning, middle, end

### Use Reference Architecture When:
1. 🏗️ You want to **implement** a similar architecture
2. 🔧 You need **technical blueprints** and implementation details
3. 👨‍💻 Your audience is **engineers** or architects
4. 📋 You need **comprehensive documentation** (2000-5000 words)
5. 🏛️ You plan to **submit to CNCF TAB**
6. 🎤 Speaker is engineer, architect, SRE (technical perspective)
7. 📐 Video shows **system architecture** with diagrams

### Generate Both When:
1. 🎭 Video serves **dual audiences** (business + technical)
2. ⏱️ Video is **30+ minutes** with comprehensive content
3. 📚 You want **maximum value** from high-quality source material
4. 🎯 You have **multiple distribution channels** (exec briefings + engineering training)
5. 🏢 Company is **high-profile** CNCF member with exemplar architecture

---

**Document Version:** 1.0.0  
**Last Updated:** 2026-02-10  
**Related Documents:**
- [REFERENCE-ARCHITECTURE-USER-GUIDE.md](REFERENCE-ARCHITECTURE-USER-GUIDE.md)
- [README.md](../README.md)
- [AGENTS.md](../AGENTS.md)
