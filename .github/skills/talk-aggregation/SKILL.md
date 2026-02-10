---
name: talk-aggregation
description: Analyzes multiple talks to extract themes, expertise areas, and CNCF project focus
version: 1.0.0
---

# Talk Aggregation Skill

## Purpose

Analyze multiple presenter talks to identify expertise patterns, recurring themes, CNCF project focus, and speaking statistics. This skill synthesizes data across all talks to create a comprehensive view of the presenter's technical focus and community contributions.

## Input Format

```json
{
  "talks": [
    {
      "video_id": "abc123",
      "title": "Kubernetes Community Management Best Practices",
      "date": "2025-10-15",
      "duration": 2700,
      "transcript": "Full transcript text...",
      "description": "Jeffrey discusses community management...",
      "event": "KubeCon North America 2025"
    },
    {
      "video_id": "def456",
      "title": "GitOps with Argo CD",
      "date": "2024-05-20",
      "duration": 1320,
      "transcript": "Full transcript text...",
      "description": "Introduction to GitOps practices...",
      "event": "CloudNativeCon Europe 2024"
    }
  ]
}
```

**Field Descriptions:**

- `talks` (array): List of all talks by the presenter
  - `video_id` (string): YouTube video identifier
  - `title` (string): Talk title
  - `date` (string): Presentation date (YYYY-MM-DD format)
  - `duration` (number): Talk length in seconds
  - `transcript` (string): Full corrected transcript
  - `description` (string): YouTube video description
  - `event` (string, optional): Conference or event name

## Output Format

```json
{
  "expertise_areas": [
    {
      "area": "Kubernetes",
      "context": "Deep community involvement, contributor experience, scalability discussions",
      "talk_count": 5,
      "evidence": ["Container orchestration patterns", "Kubernetes governance", "SIG management"]
    },
    {
      "area": "Community Management",
      "context": "Best practices for open source communities, contributor engagement, sustainability",
      "talk_count": 3,
      "evidence": ["Building inclusive communities", "Maintainer burnout", "Governance models"]
    }
  ],
  "cncf_projects": [
    {
      "name": "Kubernetes",
      "talk_count": 5,
      "usage_context": "Container orchestration, community governance, contributor experience",
      "first_mention": "2022-05",
      "latest_mention": "2025-10"
    },
    {
      "name": "Argo CD",
      "talk_count": 3,
      "usage_context": "GitOps continuous delivery, declarative deployments",
      "first_mention": "2023-03",
      "latest_mention": "2025-10"
    }
  ],
  "recurring_themes": [
    "Open source community sustainability",
    "Scalable infrastructure patterns",
    "GitOps workflows and best practices",
    "Developer experience improvements"
  ],
  "talk_summaries": [
    {
      "video_id": "abc123",
      "summary": "Explores best practices for managing large open source communities, focusing on contributor onboarding, maintainer support, and sustainable governance models. Draws from Kubernetes community experience to provide actionable insights.",
      "key_points": [
        "Contributor onboarding reduces time-to-first-PR",
        "Maintainer rotation prevents burnout",
        "Clear governance enables scaling"
      ],
      "topics": ["Kubernetes", "Community Management", "Governance"]
    }
  ],
  "stats": {
    "total_talks": 8,
    "years_active": {
      "first": 2022,
      "latest": 2025,
      "span": 3
    },
    "total_speaking_minutes": 272,
    "most_active_year": 2025,
    "average_talk_length_minutes": 34
  }
}
```

**Field Descriptions:**

- `expertise_areas` (array): Technical or domain expertise identified
  - `area` (string): Expertise domain name
  - `context` (string): Description of expertise manifestation
  - `talk_count` (number): Number of talks covering this area
  - `evidence` (array of strings): Specific topics demonstrating expertise
- `cncf_projects` (array): CNCF projects discussed across talks
  - `name` (string): Official CNCF project name
  - `talk_count` (number): Number of talks mentioning project
  - `usage_context` (string): How project is discussed/used
  - `first_mention` (string): Earliest talk date (YYYY-MM format)
  - `latest_mention` (string): Most recent talk date (YYYY-MM format)
- `recurring_themes` (array of strings): Cross-talk themes and patterns
- `talk_summaries` (array): Concise summary for each talk
  - `video_id` (string): Video identifier
  - `summary` (string): 50-150 word talk summary
  - `key_points` (array of strings): 3-5 main takeaways
  - `topics` (array of strings): Primary topics covered
- `stats` (object): Speaking activity statistics
  - `total_talks` (number): Total presentation count
  - `years_active` (object): Speaking timeframe
  - `total_speaking_minutes` (number): Sum of all talk durations
  - `most_active_year` (number): Year with most presentations
  - `average_talk_length_minutes` (number): Mean talk duration

## Execution Instructions

### Step 1: Analyze Individual Talks

For each talk, extract:

**Topics Covered:**
- Main technical subjects
- CNCF projects mentioned
- Problem domains addressed
- Solutions discussed

**Key Points:**
- Main arguments or lessons
- Novel insights
- Practical recommendations
- Case studies or examples

**CNCF Projects:**
- Project names (exact capitalization)
- How projects are used/discussed
- Context: implementation, comparison, case study
- Relationship between projects

**Technical Depth:**
- Implementation details
- Architecture patterns
- Specific features discussed
- Production experiences

### Step 2: Identify Expertise Areas

Look across all talks to identify **recurring technical domains**:

**Criteria for Expertise Area:**
- Appears in 2+ talks OR
- Central to 1 major talk (>30 min) with deep technical content
- Demonstrable knowledge depth (not just mentions)

**Common Expertise Areas:**
- Specific technologies (Kubernetes, Prometheus, Istio)
- Technical domains (Observability, Security, Networking)
- Practices (GitOps, SRE, Platform Engineering)
- Organizational topics (Community Management, Developer Experience)

**For each area, determine:**
- **Context:** How expertise manifests (architecture, operations, community, etc.)
- **Talk count:** Number of talks covering this area
- **Evidence:** Specific subtopics that demonstrate expertise

**Example:**
```json
{
  "area": "Observability",
  "context": "Distributed tracing, metrics collection, monitoring best practices for microservices",
  "talk_count": 4,
  "evidence": [
    "Prometheus query optimization",
    "Jaeger deployment patterns",
    "OpenTelemetry instrumentation",
    "SLO/SLI definition"
  ]
}
```

### Step 3: Track CNCF Projects

**Common CNCF Projects:**
- Kubernetes, Prometheus, Envoy, CoreDNS, containerd
- Fluentd, Jaeger, Helm, Argo, Flux, Vitess
- Cilium, Linkerd, Istio, etcd, Harbor, Falco
- Dragonfly, Rook, TiKV, gRPC, CNI, Knative
- OpenTelemetry, SPIFFE, SPIRE, Cortex, Thanos

For each CNCF project mentioned:

1. **Count talks mentioning project**
2. **Extract usage context** - How is it used/discussed?
   - Implementation ("deployed Istio for service mesh")
   - Comparison ("evaluated Linkerd vs Istio")
   - Case study ("Prometheus handles 10M metrics/sec")
   - Tutorial ("how to configure Helm charts")
3. **Track timeline**
   - First mention date (YYYY-MM)
   - Latest mention date (YYYY-MM)

**Prioritization:**
- Order by talk_count (descending)
- Include all projects mentioned in 2+ talks
- Include projects central to 1 major talk

### Step 4: Identify Recurring Themes

Look for **conceptual patterns** across talks:

**Theme Types:**

**Technical Patterns:**
- "Scalable architecture design"
- "Progressive delivery strategies"
- "Multi-cluster management"

**Organizational:**
- "Developer experience optimization"
- "Platform engineering approaches"
- "Inner source adoption"

**Community/Cultural:**
- "Open source sustainability"
- "Building inclusive communities"
- "Contributor engagement"

**Operational:**
- "Production reliability practices"
- "Cost optimization strategies"
- "Security-first architecture"

**Criteria for Theme:**
- Appears in 3+ talks OR
- Central message of 2+ talks
- Represents higher-level concept (not specific tool)

**Format:** Short phrase capturing the theme (5-8 words)

### Step 5: Generate Talk Summaries

For each talk, write a **50-150 word summary**:

**Structure:**
1. **Opening sentence:** Main topic/focus (what is this talk about?)
2. **Body (2-3 sentences):** Key insights, approaches, or findings
3. **Closing:** Outcome, recommendation, or takeaway

**Extract 3-5 key points:**
- Concrete takeaways
- Actionable recommendations
- Notable insights or findings
- Measurable results if applicable

**Identify 3-5 primary topics:**
- Specific technologies
- Domain areas
- Problem/solution categories

**Example:**
```json
{
  "video_id": "xyz789",
  "summary": "Explores the challenges of scaling Kubernetes clusters beyond 1000 nodes, focusing on etcd performance, scheduler optimization, and network plugin selection. Presents real-world case studies from managing a 3000-node cluster, including lessons learned about control plane architecture and monitoring strategies. Provides actionable recommendations for organizations planning large-scale Kubernetes deployments.",
  "key_points": [
    "etcd performance becomes critical above 1000 nodes",
    "Custom scheduler plugins reduce pod scheduling latency",
    "CNI choice significantly impacts network performance",
    "Control plane HA requires 5+ etcd members",
    "Monitoring overhead grows non-linearly with scale"
  ],
  "topics": ["Kubernetes", "Scalability", "etcd", "Networking", "Performance"]
}
```

### Step 6: Calculate Statistics

**Total Talks:**
- Count of talks in input array

**Years Active:**
- Extract year from each talk date
- `first`: Earliest year
- `latest`: Most recent year
- `span`: latest - first (years active)

**Total Speaking Minutes:**
- Sum all talk durations (in seconds)
- Convert to minutes: `sum(durations) / 60`
- Round to nearest integer

**Most Active Year:**
- Count talks per year
- Return year with highest count
- If tie, use most recent year

**Average Talk Length:**
- `total_speaking_minutes / total_talks`
- Round to nearest integer

## Examples

### Example 1: Multi-Topic Speaker

**Input:**
```json
{
  "talks": [
    {
      "video_id": "k8s001",
      "title": "Scaling Kubernetes to 5000 Nodes",
      "date": "2025-06-15",
      "duration": 2400,
      "transcript": "...discusses etcd performance, scheduler optimization...",
      "description": "Deep dive into large-scale Kubernetes"
    },
    {
      "video_id": "gitops002",
      "title": "GitOps with Flux and Argo CD",
      "date": "2025-03-20",
      "duration": 1800,
      "transcript": "...compares Flux and Argo CD for continuous delivery...",
      "description": "GitOps patterns and tooling comparison"
    },
    {
      "video_id": "k8s003",
      "title": "Kubernetes Networking with Cilium",
      "date": "2024-11-10",
      "duration": 2100,
      "transcript": "...eBPF-based networking and observability...",
      "description": "Advanced Kubernetes networking"
    }
  ]
}
```

**Output:**
```json
{
  "expertise_areas": [
    {
      "area": "Kubernetes",
      "context": "Large-scale cluster management, networking, and performance optimization",
      "talk_count": 2,
      "evidence": [
        "Scaling beyond 1000 nodes",
        "etcd performance tuning",
        "CNI selection and optimization",
        "eBPF-based networking"
      ]
    },
    {
      "area": "GitOps",
      "context": "Continuous delivery patterns, tooling evaluation, and best practices",
      "talk_count": 1,
      "evidence": [
        "Flux vs Argo CD comparison",
        "Declarative deployment workflows",
        "Git-based infrastructure management"
      ]
    }
  ],
  "cncf_projects": [
    {
      "name": "Kubernetes",
      "talk_count": 2,
      "usage_context": "Container orchestration at scale, networking and performance optimization",
      "first_mention": "2024-11",
      "latest_mention": "2025-06"
    },
    {
      "name": "Cilium",
      "talk_count": 1,
      "usage_context": "eBPF-based networking and observability for Kubernetes",
      "first_mention": "2024-11",
      "latest_mention": "2024-11"
    },
    {
      "name": "Flux",
      "talk_count": 1,
      "usage_context": "GitOps continuous delivery tool evaluation",
      "first_mention": "2025-03",
      "latest_mention": "2025-03"
    },
    {
      "name": "Argo CD",
      "talk_count": 1,
      "usage_context": "GitOps continuous delivery tool evaluation",
      "first_mention": "2025-03",
      "latest_mention": "2025-03"
    }
  ],
  "recurring_themes": [
    "Scalable infrastructure architecture",
    "Production Kubernetes operations",
    "GitOps deployment patterns"
  ],
  "talk_summaries": [
    {
      "video_id": "k8s001",
      "summary": "Examines the technical challenges of operating Kubernetes clusters at extreme scale, specifically addressing etcd performance bottlenecks, scheduler optimization techniques, and control plane architecture. Shares production experiences from managing a 5000-node cluster, including monitoring strategies and capacity planning approaches.",
      "key_points": [
        "etcd performance critical beyond 1000 nodes",
        "Custom scheduler configuration reduces latency",
        "Dedicated control plane nodes required at scale",
        "Monitoring overhead grows non-linearly",
        "Capacity planning requires predictive models"
      ],
      "topics": ["Kubernetes", "Scalability", "etcd", "Performance", "Architecture"]
    },
    {
      "video_id": "gitops002",
      "summary": "Compares Flux and Argo CD as GitOps continuous delivery tools, evaluating features, architecture, and production suitability. Discusses declarative deployment patterns, multi-cluster management, and integration with existing CI/CD pipelines. Provides decision framework for tool selection.",
      "key_points": [
        "Flux better for Helm-centric workflows",
        "Argo CD offers superior UI and visualization",
        "Both support multi-cluster deployments",
        "GitOps enables audit trails and rollback",
        "Tool selection depends on existing toolchain"
      ],
      "topics": ["GitOps", "Flux", "Argo CD", "Continuous Delivery", "Kubernetes"]
    },
    {
      "video_id": "k8s003",
      "summary": "Explores Cilium as an eBPF-based networking solution for Kubernetes, covering performance benefits, observability capabilities, and network policy enforcement. Demonstrates how eBPF technology provides deep visibility into network traffic and enables efficient packet processing without traditional iptables overhead.",
      "key_points": [
        "eBPF eliminates iptables performance bottlenecks",
        "Cilium provides network-layer observability",
        "Identity-based security policies more scalable",
        "Hubble UI visualizes service dependencies",
        "Network policies enforce zero-trust architecture"
      ],
      "topics": ["Cilium", "Kubernetes", "Networking", "eBPF", "Observability"]
    }
  ],
  "stats": {
    "total_talks": 3,
    "years_active": {
      "first": 2024,
      "latest": 2025,
      "span": 1
    },
    "total_speaking_minutes": 105,
    "most_active_year": 2025,
    "average_talk_length_minutes": 35
  }
}
```

### Example 2: Specialized Speaker

**Input:**
```json
{
  "talks": [
    {
      "video_id": "obs001",
      "title": "OpenTelemetry in Production",
      "date": "2025-09-12",
      "duration": 1920,
      "transcript": "...implementing distributed tracing at scale...",
      "description": "OpenTelemetry adoption journey"
    },
    {
      "video_id": "obs002",
      "title": "Prometheus Query Optimization",
      "date": "2025-05-18",
      "duration": 1680,
      "transcript": "...optimizing PromQL queries for large datasets...",
      "description": "Performance tuning for Prometheus"
    },
    {
      "video_id": "obs003",
      "title": "Building Observability Culture",
      "date": "2024-08-22",
      "duration": 2520,
      "transcript": "...organizational practices for effective observability...",
      "description": "Cultural and organizational aspects"
    }
  ]
}
```

**Output:**
```json
{
  "expertise_areas": [
    {
      "area": "Observability",
      "context": "Distributed tracing, metrics collection, monitoring best practices, and organizational culture",
      "talk_count": 3,
      "evidence": [
        "OpenTelemetry production deployment",
        "Prometheus query optimization",
        "SLO/SLI definition",
        "Observability-driven development",
        "Cross-team instrumentation standards"
      ]
    }
  ],
  "cncf_projects": [
    {
      "name": "OpenTelemetry",
      "talk_count": 1,
      "usage_context": "Distributed tracing and telemetry collection at scale",
      "first_mention": "2025-09",
      "latest_mention": "2025-09"
    },
    {
      "name": "Prometheus",
      "talk_count": 1,
      "usage_context": "Metrics collection and query performance optimization",
      "first_mention": "2025-05",
      "latest_mention": "2025-05"
    }
  ],
  "recurring_themes": [
    "Observability-driven development",
    "Production monitoring at scale",
    "Building data-driven engineering culture"
  ],
  "talk_summaries": [
    {
      "video_id": "obs001",
      "summary": "Documents the journey of implementing OpenTelemetry for distributed tracing across a microservices architecture. Covers instrumentation strategies, data volume management, sampling techniques, and integration with existing monitoring tools. Shares practical lessons from migrating from proprietary tracing to OpenTelemetry.",
      "key_points": [
        "Automatic instrumentation reduces adoption friction",
        "Tail-based sampling controls data volume",
        "Context propagation requires cross-team coordination",
        "OpenTelemetry Collector provides flexibility",
        "Migration from existing tools requires phased approach"
      ],
      "topics": ["OpenTelemetry", "Distributed Tracing", "Observability", "Microservices"]
    },
    {
      "video_id": "obs002",
      "summary": "Explores techniques for optimizing Prometheus query performance when dealing with large-scale time-series data. Covers recording rules, query patterns to avoid, storage considerations, and federation strategies. Provides actionable recommendations for reducing query latency and resource consumption.",
      "key_points": [
        "Recording rules pre-compute expensive queries",
        "Avoid high-cardinality labels in metrics",
        "Query splitting reduces memory pressure",
        "Remote read enables federation at scale",
        "Alert queries need separate optimization"
      ],
      "topics": ["Prometheus", "Performance Optimization", "Metrics", "Observability"]
    },
    {
      "video_id": "obs003",
      "summary": "Discusses organizational and cultural practices for building effective observability capabilities. Focuses on team collaboration, instrumentation standards, on-call practices, and using observability data to drive technical decisions. Emphasizes the importance of cross-functional buy-in and continuous improvement.",
      "key_points": [
        "Observability requires cross-team standards",
        "SLOs align engineering and business goals",
        "Instrumentation should be default, not optional",
        "Postmortems drive observability improvements",
        "Developer experience impacts adoption"
      ],
      "topics": ["Observability", "Culture", "SRE", "Team Practices", "SLO"]
    }
  ],
  "stats": {
    "total_talks": 3,
    "years_active": {
      "first": 2024,
      "latest": 2025,
      "span": 1
    },
    "total_speaking_minutes": 104,
    "most_active_year": 2025,
    "average_talk_length_minutes": 35
  }
}
```

## Quality Guidelines

### Expertise Area Identification
- **Minimum 2 talks** for expertise claim (or 1 deep technical talk)
- **Evidence-based:** List specific subtopics demonstrating depth
- **Avoid over-generalization:** "Kubernetes" not "Cloud Computing"
- **Context matters:** Explain how expertise manifests

### CNCF Project Tracking
- **Use official names:** "Argo CD" not "ArgoCD"
- **Accurate context:** Describe actual usage, not generic descriptions
- **Timeline precision:** Use YYYY-MM format from talk dates
- **Prioritize by frequency:** Order by talk_count descending

### Recurring Theme Detection
- **Higher-level concepts:** Not specific tools, but patterns/practices
- **Consistent across talks:** Appears in multiple presentations
- **Concise phrasing:** 5-8 words max
- **Actionable or descriptive:** Clear meaning

### Talk Summary Quality
- **Length:** 50-150 words (strict)
- **Factual:** Based on transcript/description content
- **Specific:** Concrete topics, not vague overviews
- **Key points:** 3-5 actionable takeaways
- **Topics:** 3-5 specific subject areas

### Statistics Accuracy
- **Count carefully:** Verify total_talks matches input length
- **Date parsing:** Handle various date formats
- **Duration conversion:** Seconds to minutes, rounded
- **Most active year:** Handle ties (use most recent)

## Common Pitfalls to Avoid

### ❌ Claiming Expertise Without Evidence

**Bad:**
```json
{
  "area": "Cloud Native Architecture",
  "context": "General cloud-native knowledge",
  "talk_count": 1,
  "evidence": []
}
```
**Why:** Too broad, insufficient evidence

**Good:**
```json
{
  "area": "Service Mesh Architecture",
  "context": "Istio implementation, sidecar patterns, traffic management",
  "talk_count": 2,
  "evidence": ["Istio deployment strategies", "mTLS configuration", "Traffic routing patterns"]
}
```

### ❌ Incorrect Project Names

**Bad:** "ArgoCD", "K8s", "OTel"

**Good:** "Argo CD", "Kubernetes", "OpenTelemetry"

### ❌ Vague Usage Context

**Bad:**
```json
{
  "name": "Prometheus",
  "usage_context": "Used for monitoring"
}
```

**Good:**
```json
{
  "name": "Prometheus",
  "usage_context": "Metrics collection, query optimization, large-scale time-series data management"
}
```

### ❌ Too Many Themes

**Bad:** 15 themes for 5 talks (over-segmented)

**Good:** 4-6 major themes that genuinely recur

### ❌ Summary Too Long or Too Short

**Bad (too short):** "This talk is about Kubernetes networking."

**Bad (too long):** 300-word detailed description

**Good:** 75-100 word focused summary with key insights

### ❌ Incorrect Statistics

**Bad:** Claiming 10 talks when input has 8

**Good:** Count matches input array length exactly

### ❌ Missing Evidence for Expertise

**Bad:**
```json
{
  "area": "Security",
  "evidence": []
}
```

**Good:**
```json
{
  "area": "Security",
  "evidence": ["Zero-trust architecture", "mTLS implementation", "RBAC policies", "Secrets management"]
}
```

## Important Notes

- This skill feeds into `presenter-profile-generation` skill
- Statistics drive the stats table in presenter profiles
- Expertise areas and themes become profile narrative content
- Talk summaries populate the "Talk Highlights" section
- CNCF project data identifies presenter's technical focus
- Quality here determines profile depth and accuracy

## Validation Checklist

Before returning output, verify:

- [ ] All expertise areas have 2+ talks (or 1 deep talk)
- [ ] Evidence array populated for each expertise area
- [ ] CNCF project names use official capitalization
- [ ] Project timelines use YYYY-MM format
- [ ] Projects ordered by talk_count descending
- [ ] Recurring themes are higher-level concepts
- [ ] Each theme appears in 3+ talks (or 2+ major talks)
- [ ] Talk summaries are 50-150 words each
- [ ] Key points are 3-5 per talk
- [ ] Topics are 3-5 per talk
- [ ] total_talks matches input array length
- [ ] years_active span is calculated correctly
- [ ] total_speaking_minutes is sum of durations / 60
- [ ] most_active_year is year with most talks
- [ ] average_talk_length is total_minutes / total_talks
- [ ] All statistics are integers (rounded)
