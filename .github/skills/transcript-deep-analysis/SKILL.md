# Skill: transcript-deep-analysis

**Version:** 1.0.0  
**Purpose:** Deep technical analysis of video transcripts to extract architectural patterns, CNCF projects, integration patterns, and technical implementation details for reference architecture generation.

**Difference from transcript-analysis:** This skill performs deeper technical extraction (architectural patterns, integration patterns, technical metrics) required for reference architectures. Extract only what is explicitly stated in the transcript — quality and accuracy over quantity.

---

## Input Format

```json
{
  "transcript": "Full corrected transcript text from transcript-correction skill",
  "video_title": "Video title from youtube-data",
  "video_description": "Video description from youtube-data (optional)",
  "duration_seconds": 1234,
  "company_name": "Verified company name from validate-company"
}
```

**Input Requirements:**
- `transcript`: Must be at least 2000 characters (enforced by validate-transcript)
- `video_title`: Required for context
- `company_name`: Must be exact match from CNCF companies list
- `duration_seconds`: Used for timestamp validation

---

## Output Format

```json
{
  "cncf_projects": [
    {
      "name": "Kubernetes",
      "category": "orchestration|networking|storage|observability|security|service-mesh|ci-cd|other",
      "usage_context": "How the project is used, in the speaker's own words",
      "integration_pattern": "sidecar|operator|plugin|extension|native|custom",
      "confidence": "high"
    }
  ],
  "architecture_components": {
    "infrastructure_layer": [
      {
        "component": "Component name",
        "description": "What it does",
        "cncf_projects": ["Kubernetes", "Envoy"]
      }
    ],
    "platform_layer": [
      {
        "component": "Component name",
        "description": "What it does",
        "cncf_projects": ["Argo CD", "Prometheus"]
      }
    ],
    "application_layer": [
      {
        "component": "Component name",
        "description": "What it does",
        "cncf_projects": ["Linkerd", "Jaeger"]
      }
    ]
  },
  "integration_patterns": [
    {
      "pattern_name": "Service Mesh Integration",
      "description": "How services communicate",
      "projects_involved": ["Istio", "Envoy"],
      "technical_details": "Specific implementation details"
    }
  ],
  "technical_metrics": [
    {
      "metric_name": "Deployment Frequency",
      "before_value": "weekly",
      "after_value": "10x per day",
      "measurement_unit": "deployments",
      "source_confidence": "explicit|paraphrased",
      "transcript_quote": "Exact quote from transcript supporting this metric"
    }
  ],
  "sections": {
    "background": "2-3 paragraphs: Company context, industry, scale, business model",
    "technical_challenge": "2-3 paragraphs: Specific technical problems, why existing solutions failed, constraints",
    "architecture_overview": "3-4 paragraphs: High-level architecture description, key design decisions, why this approach",
    "implementation_details": "4-5 paragraphs: How components were integrated, technical challenges solved, lessons learned",
    "results_and_impact": "2-3 paragraphs: Technical outcomes, performance improvements, business impact",
    "lessons_learned": "2-3 paragraphs: What worked, what didn't, advice for others"
  },
  "key_quotes": [
    {
      "quote": "Exact quote from transcript",
      "speaker_role": "CTO|Engineer|Manager|Other",
      "context": "Why this quote is significant",
      "section": "background|technical_challenge|architecture_overview|implementation_details|results_and_impact|lessons_learned"
    }
  ],
  "screenshot_opportunities": [
    {
      "timestamp_seconds": 123,
      "description": "What should be visible in screenshot",
      "type": "architecture-diagram|dashboard|code|terminal|ui|other",
      "priority": "high|medium|low",
      "recommended_caption": "Caption for the screenshot"
    }
  ]
}
```

**Output Requirements:**
- **cncf_projects**: Only projects explicitly named in the transcript (no minimum — report what's there)
- **architecture_components**: Include layers discussed in the transcript (note gaps with disclosure)
- **integration_patterns**: Include patterns described in the transcript
- **technical_metrics**: All metrics must have `transcript_quote` for validation
- **sections**: Each section should cover what the transcript discusses (shorter is acceptable)
- **screenshot_opportunities**: Minimum 6 opportunities (for reference architecture needs)

---

## Execution Instructions

### Step 1: Read and Understand the Transcript

**Objective:** Comprehend the full technical context before extraction.

1. Read the entire transcript at least twice
2. Identify the speaker roles (CTO, engineer, architect, etc.)
3. Note timestamps where technical details are discussed
4. Mark sections with architecture diagrams or visual aids
5. Identify the company's technical maturity level (startup, enterprise, etc.)

**Quality Check:**
- Can you explain the company's technical journey in 2-3 sentences?
- Have you identified all speakers and their roles?

---

### Step 2: Extract CNCF Projects (Transcript-Only)

**Objective:** Identify all CNCF projects **explicitly mentioned by name** in the transcript. Do NOT infer or imply projects.

**CRITICAL RULE: Transcript-only extraction.** If a speaker says "service mesh" but never names Istio, Linkerd, or Envoy, do NOT add any of those projects. Record the generic term in the usage context of the component that mentions it, but do not fabricate a specific project name.

**Method:**
1. Search for explicit project mentions by name: "Kubernetes", "Prometheus", "Envoy", "Argo CD", etc.
2. For each explicitly named project:
   - Categorize (orchestration, networking, storage, etc.)
   - Extract usage context **using the speaker's own words**
   - Identify integration patterns **only if described in the transcript**
3. Do NOT add projects that were never mentioned by name
4. Do NOT map generic terms to specific projects (e.g., "CI/CD" does not mean "Argo CD")

**Quality Checks:**
- Is every project explicitly mentioned by name in the transcript?
- Is the usage context derived from what the speaker actually said?
- Could you point to the exact moment in the transcript where each project was named?

**Example:**
```json
{
  "name": "Kubernetes",
  "category": "orchestration",
  "usage_context": "Container orchestration platform for running Keycloak pods across multiple clusters",
  "integration_pattern": "native",
  "confidence": "high"
}
```

**Anti-Pattern (DO NOT DO):**
```json
{
  "name": "Calico",
  "category": "networking",
  "usage_context": "CNI plugin for network policies",
  "integration_pattern": "plugin",
  "confidence": "low"
}
```
Why wrong: If the speaker never said "Calico," do not include it — even if Kubernetes typically uses a CNI plugin.

---

### Step 3: Map Architecture Components (3 Layers)

**Objective:** Create a layered architecture map showing how components relate.

**Infrastructure Layer (Bottom):**
- Cloud providers (AWS, GCP, Azure)
- Container runtimes (containerd, CRI-O)
- Networking infrastructure (CNI plugins, load balancers)
- Storage systems (persistent volumes, object storage)

**Platform Layer (Middle):**
- Kubernetes and orchestration
- Service mesh (Istio, Linkerd)
- Observability (Prometheus, Grafana, Jaeger)
- CI/CD (Argo CD, Tekton)
- Security (OPA, Falco)

**Application Layer (Top):**
- Microservices and applications
- API gateways
- Application-level patterns (circuit breakers, retries)

**For Each Component:**
1. Extract component name from transcript
2. Write 1-2 sentence description
3. List CNCF projects used in this component
4. Note if component is custom-built or CNCF-based

**Quality Checks:**
- Are the layers populated with components **actually mentioned in the transcript**?
- If the transcript does not discuss a layer, note: "The presentation did not discuss [layer] components."
- Do NOT invent components to fill layers. Report only what was described.
- Are CNCF projects correctly associated with components?
- Does the architecture flow logically (bottom to top)?

**Example:**
```json
{
  "infrastructure_layer": [
    {
      "component": "Container Runtime",
      "description": "Runs containerized workloads using containerd as the runtime engine across all clusters",
      "cncf_projects": ["containerd"]
    }
  ]
}
```

---

### Step 4: Extract Integration Patterns (Minimum 2)

**Objective:** Document how CNCF projects integrate with each other and custom systems.

**Common Integration Patterns:**
1. **Service Mesh Integration**: How services communicate (e.g., Istio + Envoy)
2. **Observability Stack**: How metrics/logs/traces are collected (e.g., Prometheus + Grafana + Jaeger)
3. **GitOps Pipeline**: How deployments happen (e.g., Argo CD + Flux)
4. **Security Policy Enforcement**: How policies are enforced (e.g., OPA + Falco)
5. **Multi-Cluster Management**: How multiple clusters are managed
6. **Hybrid Cloud Integration**: How on-prem and cloud integrate

**For Each Pattern:**
1. Name the pattern (be specific)
2. Write 2-3 sentence description
3. List all projects involved
4. Extract technical details from transcript:
   - Configuration specifics
   - Custom integrations
   - Challenges overcome
   - Performance characteristics

**Quality Checks:**
- Are there at least 2 patterns identified?
- Do patterns show how projects work together (not just individual tools)?
- Are technical details specific (not generic)?
- Are details traceable to transcript?

**Example:**
```json
{
  "pattern_name": "Service Mesh Integration with Observability",
  "description": "Istio service mesh integrated with Prometheus for metrics and Jaeger for distributed tracing. Custom Envoy filters added for business-specific telemetry.",
  "projects_involved": ["Istio", "Envoy", "Prometheus", "Jaeger"],
  "technical_details": "Configured Istio to emit custom metrics via statsD, with 15-second scrape intervals. Added custom Envoy filter for request tracing with sampling rate of 1%. Integrated with existing Grafana dashboards showing golden signals (latency, traffic, errors, saturation)."
}
```

---

### Step 5: Extract Technical Metrics (With Transcript Quotes)

**Objective:** Extract quantitative improvements with supporting evidence.

**Metric Categories:**
1. **Performance**: Latency, throughput, response times
2. **Reliability**: Uptime, error rates, MTTR
3. **Scalability**: Request volume, concurrent users, data processed
4. **Development Velocity**: Deployment frequency, lead time, change fail rate
5. **Cost**: Infrastructure costs, operational savings
6. **Security**: Vulnerabilities fixed, incident response time

**For Each Metric:**
1. Extract metric name (be specific: "API latency", not "performance")
2. Extract before value (with units)
3. Extract after value (with units)
4. Note measurement unit (ms, requests/sec, dollars, etc.)
5. Determine source confidence:
   - **explicit**: Directly stated in transcript with specific numbers
   - **paraphrased**: Speaker described the improvement qualitatively (e.g., "much faster") — record their exact words in transcript_quote, do NOT convert to a number

   **CRITICAL:** Do NOT include "implied" or "estimated" metrics. If the speaker did not state a metric, it does not exist. If they said "much less operational burden," record that quote — do NOT convert it to "70% reduction."
6. **CRITICAL**: Extract exact quote from transcript supporting this metric

**Quality Checks:**
- Does each metric have a before and after value?
- Are units consistent and clear?
- Is the transcript quote an exact match (for validation)?
- Are improvements realistic (not exaggerated)?

**Example:**
```json
{
  "metric_name": "API Response Time (p95)",
  "before_value": "500",
  "after_value": "50",
  "measurement_unit": "milliseconds",
  "source_confidence": "explicit",
  "transcript_quote": "We reduced our p95 API response time from 500 milliseconds down to 50 milliseconds after implementing Istio with connection pooling."
}
```

**Anti-Pattern (DO NOT DO):**
```json
{
  "metric_name": "Performance",
  "before_value": "slow",
  "after_value": "fast",
  "measurement_unit": "speed",
  "source_confidence": "implied",
  "transcript_quote": ""  // WRONG: No quote = fabrication risk
}
```

---

### Step 6: Generate Section Content (6 Sections)

**Objective:** Write comprehensive technical sections for the reference architecture.

**CRITICAL: Transcript-only content.** Every claim, fact, number, timeline, and technical detail in every section must come from the transcript. If the transcript does not discuss a topic for a given section, write a brief section covering only what was said, followed by: "The presentation did not cover [topic] in detail."

**Do NOT:**
- Infer version numbers, configurations, or team sizes not mentioned in the transcript
- Add implementation steps that were not described by the speakers
- Fill sections with generic cloud-native best practices
- Extrapolate timelines, costs, or staffing details
- Write about topics the speakers did not discuss

**DO:**
- Use the speakers' own words and phrasing where possible
- Quote the transcript directly when describing results or metrics
- Write shorter sections when the transcript has less detail on that topic
- Clearly disclose when a topic was not covered: "The presentation did not cover [topic] in detail."

**Section 1: Background (200-400 words)**

**Content Requirements:**
- Company name, industry, and business model
- Company scale (employees, customers, revenue if mentioned)
- Technical maturity level (startup, mid-size, enterprise)
- Business context: What does the company do?
- Why is this architecture significant? (innovative, large-scale, etc.)

**Tone:** Professional, factual, sets context without jargon
- **Sourcing:** Every fact must come from the transcript. If the transcript does not provide information for a bullet point above, omit it rather than fabricate it.

**Example Opening:**
> "[Company] is a [industry] company that provides [product/service] to [customer base]. Founded in [year], the company has grown to [scale metrics] and processes [technical scale]. As the business scaled, their infrastructure needed to evolve from [before] to [after] to meet [business requirement]."

---

**Section 2: Technical Challenge (300-500 words)**

**Content Requirements:**
- Specific technical problems faced (not vague "performance issues")
- Why existing solutions failed or were inadequate
- Technical constraints (budget, timeline, team size, legacy systems)
- Business impact of the problem (downtime, lost revenue, customer complaints)

**Tone:** Problem-focused, technical, creates urgency
- **Sourcing:** Every fact must come from the transcript. If the transcript does not provide information for a bullet point above, omit it rather than fabricate it.

**Structure:**
1. Paragraph 1: Primary technical problem with specific symptoms
2. Paragraph 2: Why traditional solutions didn't work, constraints faced
3. Paragraph 3: Business impact and urgency to solve

**Example:**
> "The platform was experiencing cascading failures during peak traffic, with API response times spiking from 200ms to 5+ seconds. Traditional load balancing couldn't prevent these failures because services had no circuit breakers or retry logic. The engineering team tried implementing custom retry logic in each service, but this led to inconsistent behavior and increased development time by 40%. With 50% YoY traffic growth projected, the existing architecture would not scale."

---

**Section 3: Architecture Overview (400-600 words)**

**Content Requirements:**
- High-level description of the new architecture
- Key design decisions and rationale
- Why this approach over alternatives
- How it addresses the technical challenge
- Overview of CNCF projects used and their roles

**Tone:** Technical but accessible, architectural thinking
- **Sourcing:** Every fact must come from the transcript. If the transcript does not provide information for a bullet point above, omit it rather than fabricate it.

**Structure:**
1. Paragraph 1: High-level architecture description (3-4 key components)
2. Paragraph 2: Design decisions and trade-offs
3. Paragraph 3: CNCF projects selected and why
4. Paragraph 4: How architecture solves the challenge

**Example:**
> "The team adopted a service mesh architecture using Istio to handle traffic management, observability, and security at the infrastructure level rather than in application code. This approach separated infrastructure concerns from business logic, allowing developers to focus on features while the mesh handled resilience patterns. Istio was selected over alternatives like Linkerd because the team needed fine-grained traffic routing for canary deployments and had existing Envoy expertise. The mesh integrated with Prometheus for metrics and Jaeger for distributed tracing, creating a comprehensive observability stack."

---

**Section 4: Implementation Details (600-800 words)**

**Content Requirements:**
- Step-by-step implementation approach (phases)
- How components were integrated
- Technical challenges encountered and solutions
- Configuration specifics (without exposing secrets)
- Custom code or extensions built
- Migration strategy (if applicable)

**Tone:** Deep technical, instructional, lessons learned
- **Sourcing:** Every fact must come from the transcript. If the transcript does not provide information for a bullet point above, omit it rather than fabricate it.

**Structure:**
1. Paragraph 1: Implementation approach and phases
2. Paragraph 2: Integration of first major component
3. Paragraph 3: Integration of additional components
4. Paragraph 4: Technical challenges and solutions
5. Paragraph 5: Lessons learned during implementation

**Example:**
> "Implementation occurred in three phases over six months. Phase 1 focused on deploying Istio to a single dev cluster and proving the service mesh concept with 10 non-critical services. The team wrote custom Helm charts to deploy Istio with their specific configuration: mTLS in permissive mode initially, then strict after validation. Phase 2 migrated 50 services to production with incremental rollout using Istio's VirtualService resources for canary deployments. This revealed a critical issue: Istio's default resource limits caused CPU throttling under high load. The team increased CPU limits from 500m to 2 cores per Envoy proxy and implemented horizontal pod autoscaling. Phase 3 integrated observability: Prometheus scraped mesh metrics every 15 seconds, and Grafana dashboards visualized golden signals per service."

---

**Section 5: Results and Impact (300-500 words)**

**Content Requirements:**
- Quantitative technical outcomes (use metrics from Step 5)
- Performance improvements
- Operational improvements
- Developer productivity improvements
- Business impact (revenue, customer satisfaction, cost savings)

**Tone:** Results-focused, data-driven, celebratory but factual
- **Sourcing:** Every fact must come from the transcript. If the transcript does not provide information for a bullet point above, omit it rather than fabricate it.

**Structure:**
1. Paragraph 1: Primary technical results (performance, reliability)
2. Paragraph 2: Operational and developer productivity improvements
3. Paragraph 3: Business impact and ROI

**Example:**
> "The new architecture delivered significant technical improvements. API response time (p95) dropped from 500ms to 50ms, and incident response time decreased from 2 hours to 15 minutes due to improved observability. The service mesh handled 1M requests per second during peak traffic without cascading failures, compared to the previous limit of 200K requests per second. Developer productivity improved measurably: deployment frequency increased from weekly to 10x per day, and the time to add circuit breakers to a service dropped from 3 days of development to 5 minutes of configuration. The business impact was substantial: the platform supported 200% user growth without additional infrastructure costs, and customer-reported incidents decreased by 75%."

---

**Section 6: Lessons Learned (300-500 words)**

**Content Requirements:**
- What worked well (technical and organizational)
- What didn't work or required adjustment
- Surprises encountered
- Advice for others attempting similar architecture
- Future improvements planned

**Tone:** Reflective, honest, instructional
- **Sourcing:** Every fact must come from the transcript. If the transcript does not provide information for a bullet point above, omit it rather than fabricate it.

**Structure:**
1. Paragraph 1: What worked well and why
2. Paragraph 2: What was challenging or didn't work initially
3. Paragraph 3: Advice for others and future improvements

**Example:**
> "Several decisions proved critical to success. Starting with a small pilot in the dev environment allowed the team to learn Istio without production risk. Investing in comprehensive observability early (Prometheus, Grafana, Jaeger) paid dividends during troubleshooting. The decision to run Istio in permissive mTLS mode initially avoided breaking existing services while migrating incrementally. However, the team underestimated resource requirements: Istio's control plane and Envoy proxies consumed 30% more CPU than anticipated, requiring infrastructure upgrades. Documentation was initially insufficient, causing onboarding friction for new developers unfamiliar with service mesh concepts. For others considering service mesh adoption: start small, invest in observability first, and expect a 3-6 month learning curve. The team plans to explore multi-cluster mesh topologies and ambient mesh mode in the next architecture evolution."

---

### Step 7: Identify Key Quotes (Minimum 6)

**Objective:** Extract impactful quotes that support the reference architecture narrative.

**Selection Criteria:**
- Quote is verbatim from transcript (exact words)
- Quote adds credibility or insight
- Quote shows technical depth or business impact
- Quote is from a named speaker with clear role

**For Each Quote:**
1. Extract exact quote (with proper punctuation)
2. Identify speaker role (CTO, Engineer, Manager, etc.)
3. Write 1 sentence explaining why this quote matters
4. Assign quote to appropriate section

**Quality Checks:**
- Are quotes verbatim (not paraphrased)?
- Are there quotes for all 6 sections?
- Do quotes add substance (not filler)?

**Example:**
```json
{
  "quote": "We were spending 40% of our engineering time fighting infrastructure fires instead of building features. The service mesh changed that calculus completely.",
  "speaker_role": "CTO",
  "context": "Demonstrates business impact of infrastructure problems and why architecture change was necessary",
  "section": "technical_challenge"
}
```

---

### Step 8: Identify Screenshot Opportunities (Minimum 6)

**Objective:** Mark timestamps where visual content would enhance the reference architecture.

**Screenshot Types:**
1. **architecture-diagram**: System diagrams, component relationships
2. **dashboard**: Grafana, Prometheus, monitoring dashboards
3. **code**: Configuration files, YAML, code snippets
4. **terminal**: CLI commands, kubectl output
5. **ui**: Application interfaces, user flows
6. **other**: Presentation slides, whiteboard drawings

**For Each Screenshot:**
1. Note exact timestamp in seconds
2. Describe what should be visible
3. Categorize screenshot type
4. Assign priority (high, medium, low)
5. Write recommended caption

**Prioritization:**
- **high**: Architecture diagrams, key metrics dashboards, critical code
- **medium**: Supporting dashboards, configuration examples
- **low**: Supplementary UI, presentation slides

**Quality Checks:**
- Are there at least 6 screenshots identified?
- Are priorities justified?
- Are captions descriptive?
- Are timestamps accurate?

**Example:**
```json
{
  "timestamp_seconds": 847,
  "description": "Architecture diagram showing three-layer architecture with Istio service mesh connecting microservices, Prometheus collecting metrics, and Jaeger tracing requests",
  "type": "architecture-diagram",
  "priority": "high",
  "recommended_caption": "Figure 1: Service mesh architecture with Istio handling traffic management and observability across 500+ microservices"
}
```

---

## Quality Guidelines

### Technical Depth Standards

Reference architectures require higher technical depth than case studies:

1. **CNCF Project Coverage:**
   - Only projects explicitly named in the transcript (no minimum)
   - Each project must have clear usage context from the speaker's words
   - Do NOT infer projects from generic terms

2. **Architecture Detail:**
   - Document layers discussed in the transcript (note gaps with disclosure)
   - Describe integration patterns the speakers mentioned
   - Include only configuration details from the transcript (not generic knowledge)

3. **Technical Metrics:**
   - All metrics must have transcript quotes (for fabrication prevention)
   - Metrics must be quantitative (numbers, not adjectives)
   - Before/after values required for comparison

4. **Section Depth:**
   - Each section: 200-800 words (longer than case studies)
   - Technical specificity: Commands, configurations, architecture decisions
   - Implementation details: How things were done, not just what was done

### Validation Requirements

Your output will be validated by `validate-deep-analysis` CLI tool:

**Validation Checks:**
1. All CNCF projects are explicitly named in the transcript
2. Architecture layers present reflect what was discussed
3. All technical metrics have non-empty `transcript_quote`
4. `len(screenshot_opportunities) >= 6` - Minimum screenshots
5. Sections cover transcript content (shorter is acceptable for sparse topics)

**Exit Codes:**
- 0: PASS - All validations passed
- 1: WARNING - Minor issues (e.g., 4 projects instead of 5)
- 2: CRITICAL - Major issues (e.g., missing architecture layers, no transcript quotes)

If validation returns exit code 2, the agent will stop and post an error to the GitHub issue. Ensure your output meets all requirements.

---

## Examples

### Example 1: E-commerce Company Scaling with CNCF Stack

**Input:**
```json
{
  "transcript": "We're an e-commerce platform processing 10 million orders per month... [5000+ word transcript about implementing Kubernetes, Istio, Prometheus, Argo CD, and OPA]...",
  "video_title": "How We Scaled to 10M Orders/Month with Cloud Native Technologies",
  "video_description": "Technical deep dive into our architecture transformation",
  "duration_seconds": 2400,
  "company_name": "ShopFlow"
}
```

**Output (Abbreviated):**
```json
{
  "cncf_projects": [
    {
      "name": "Kubernetes",
      "category": "orchestration",
      "usage_context": "Primary orchestration platform managing 200 microservices across 5 production clusters (US-East, US-West, EU-West, Asia-Pacific, DR)",
      "integration_pattern": "native",
      "confidence": "high"
    },
    {
      "name": "Istio",
      "category": "service-mesh",
      "usage_context": "Service mesh handling traffic routing, circuit breaking, and mTLS between services. Used for canary deployments with automated rollback based on error rate metrics",
      "integration_pattern": "sidecar",
      "confidence": "high"
    },
    {
      "name": "Prometheus",
      "category": "observability",
      "usage_context": "Metrics collection with 15-second scrape interval. Stores 90 days of metrics data for capacity planning and incident analysis",
      "integration_pattern": "native",
      "confidence": "high"
    },
    {
      "name": "Argo CD",
      "category": "ci-cd",
      "usage_context": "GitOps deployment tool synchronizing 200+ applications from Git to Kubernetes. Implements progressive delivery with automated rollback",
      "integration_pattern": "operator",
      "confidence": "high"
    },
    {
      "name": "Open Policy Agent",
      "category": "security",
      "usage_context": "Policy enforcement for admission control (resource limits, security contexts, registry restrictions) and runtime authorization",
      "integration_pattern": "native",
      "confidence": "high"
    },
    {
      "name": "Envoy",
      "category": "networking",
      "usage_context": "Data plane proxy as part of Istio service mesh. Handles L7 load balancing, retries, timeouts, circuit breaking",
      "integration_pattern": "sidecar",
      "confidence": "high"
    }
  ],
  "architecture_components": {
    "infrastructure_layer": [
      {
        "component": "Multi-Region Kubernetes Clusters",
        "description": "Five production Kubernetes clusters (v1.26) deployed across AWS regions with cross-region failover capability",
        "cncf_projects": ["Kubernetes"]
      },
      {
        "component": "Container Networking",
        "description": "Calico CNI providing network policy enforcement and encrypted pod-to-pod communication",
        "cncf_projects": ["Calico"]
      }
    ],
    "platform_layer": [
      {
        "component": "Service Mesh",
        "description": "Istio service mesh with Envoy proxies managing all service-to-service communication, including traffic routing, circuit breaking, and mTLS",
        "cncf_projects": ["Istio", "Envoy"]
      },
      {
        "component": "Observability Stack",
        "description": "Prometheus for metrics, Grafana for visualization, and Jaeger for distributed tracing, providing complete visibility into system behavior",
        "cncf_projects": ["Prometheus", "Grafana", "Jaeger"]
      },
      {
        "component": "GitOps Deployment Pipeline",
        "description": "Argo CD managing declarative deployments from Git with automated sync and rollback capabilities",
        "cncf_projects": ["Argo CD"]
      },
      {
        "component": "Policy Enforcement",
        "description": "Open Policy Agent enforcing security policies at admission control and runtime authorization",
        "cncf_projects": ["Open Policy Agent"]
      }
    ],
    "application_layer": [
      {
        "component": "Microservices",
        "description": "200+ microservices handling order processing, inventory, payments, recommendations, and customer service",
        "cncf_projects": []
      },
      {
        "component": "API Gateway",
        "description": "Envoy-based API gateway with rate limiting, authentication, and request routing to internal services",
        "cncf_projects": ["Envoy"]
      }
    ]
  },
  "integration_patterns": [
    {
      "pattern_name": "Service Mesh with Progressive Delivery",
      "description": "Istio service mesh integrated with Argo Rollouts for automated canary deployments with traffic shaping and automated rollback",
      "projects_involved": ["Istio", "Envoy", "Argo CD", "Prometheus"],
      "technical_details": "Argo Rollouts controls Istio VirtualServices to implement canary deployments. Traffic shifts from 10% → 50% → 100% over 30 minutes with automated rollback if Prometheus metrics (error rate > 1% or latency p95 > 200ms) exceed thresholds. Custom Envoy filters emit business metrics (orders/sec, cart-to-order conversion) for rollback decisions."
    },
    {
      "pattern_name": "Unified Observability with Correlation",
      "description": "Prometheus, Grafana, and Jaeger integrated to correlate metrics, logs, and traces for rapid incident diagnosis",
      "projects_involved": ["Prometheus", "Grafana", "Jaeger", "Istio"],
      "technical_details": "Istio automatically propagates trace context headers. Prometheus scrapes mesh metrics with trace IDs as labels, allowing Grafana dashboards to link from high error rate metrics directly to failing traces in Jaeger. Custom Grafana dashboards show golden signals (latency, traffic, errors, saturation) per service with drill-down to traces."
    },
    {
      "pattern_name": "Policy-as-Code with OPA",
      "description": "Open Policy Agent enforces security and operational policies across admission control and runtime",
      "projects_involved": ["Open Policy Agent", "Kubernetes"],
      "technical_details": "OPA Gatekeeper validates all Kubernetes resources at admission time: resource limits required, only approved container registries allowed, no privileged containers, security contexts enforced. OPA also provides runtime authorization for service-to-service communication based on JWT claims, integrated with Istio's authorization policies."
    }
  ],
  "technical_metrics": [
    {
      "metric_name": "API Latency (p95)",
      "before_value": "800",
      "after_value": "120",
      "measurement_unit": "milliseconds",
      "source_confidence": "explicit",
      "transcript_quote": "Our p95 API latency dropped from 800 milliseconds to 120 milliseconds after implementing Istio's connection pooling and circuit breakers."
    },
    {
      "metric_name": "Deployment Frequency",
      "before_value": "2",
      "after_value": "50",
      "measurement_unit": "deployments per day",
      "source_confidence": "explicit",
      "transcript_quote": "We went from deploying twice a week to 50 deployments per day across our 200 services using Argo CD."
    },
    {
      "metric_name": "Incident MTTR",
      "before_value": "3",
      "after_value": "0.25",
      "measurement_unit": "hours",
      "source_confidence": "explicit",
      "transcript_quote": "Mean time to resolution dropped from 3 hours to 15 minutes because Jaeger showed us exactly which service was causing the problem."
    }
  ],
  "sections": {
    "background": "ShopFlow is an e-commerce platform serving 5 million customers across North America and Europe...[400 words]",
    "technical_challenge": "As order volume grew from 1 million to 10 million per month, the monolithic architecture began to fail...[500 words]",
    "architecture_overview": "The team adopted a cloud-native architecture built on Kubernetes with Istio service mesh...[600 words]",
    "implementation_details": "Implementation occurred in four phases over eight months. Phase 1 established Kubernetes clusters...[800 words]",
    "results_and_impact": "The new architecture delivered dramatic improvements across technical and business metrics...[500 words]",
    "lessons_learned": "Several key decisions contributed to success. Starting with a pilot program...[400 words]"
  },
  "key_quotes": [
    {
      "quote": "We were drowning in incidents. Every week we'd have at least one major outage affecting thousands of customers.",
      "speaker_role": "VP of Engineering",
      "context": "Illustrates the severity of technical challenges before architecture transformation",
      "section": "technical_challenge"
    },
    {
      "quote": "Istio gave us superpowers. We could implement circuit breakers, retries, and timeouts for all 200 services without touching a single line of application code.",
      "speaker_role": "Principal Engineer",
      "context": "Demonstrates the value of service mesh for infrastructure-level resilience patterns",
      "section": "architecture_overview"
    }
  ],
  "screenshot_opportunities": [
    {
      "timestamp_seconds": 420,
      "description": "Architecture diagram showing five Kubernetes clusters with Istio mesh spanning clusters, Prometheus federation for metrics, and Argo CD managing deployments",
      "type": "architecture-diagram",
      "priority": "high",
      "recommended_caption": "Figure 1: Multi-region cloud-native architecture with service mesh and observability"
    },
    {
      "timestamp_seconds": 890,
      "description": "Grafana dashboard showing service-level golden signals (latency, traffic, errors, saturation) with drill-down links to Jaeger traces",
      "type": "dashboard",
      "priority": "high",
      "recommended_caption": "Figure 2: Unified observability dashboard correlating metrics with distributed traces"
    }
  ]
}
```

---

## Common Mistakes to Avoid

### Mistake 1: Insufficient CNCF Projects

**Wrong:**
```json
{
  "cncf_projects": [
    {"name": "Kubernetes", "category": "orchestration", "usage_context": "Container orchestration", "integration_pattern": "native", "confidence": "high"},
    {"name": "Docker", "category": "runtime", "usage_context": "Containers", "integration_pattern": "native", "confidence": "high"}
  ]
}
```

**Why Wrong:**
- Only 2 projects (need minimum 5)
- Docker is not a CNCF project (it's containerd)
- Usage contexts are vague

**Fix:**
```json
{
  "cncf_projects": [
    {"name": "Kubernetes", "category": "orchestration", "usage_context": "Primary orchestration platform managing 200 microservices", "integration_pattern": "native", "confidence": "high"},
    {"name": "Istio", "category": "service-mesh", "usage_context": "Traffic management and mTLS for service-to-service communication", "integration_pattern": "sidecar", "confidence": "high"},
    {"name": "Prometheus", "category": "observability", "usage_context": "Metrics collection with 15-second scrape interval", "integration_pattern": "native", "confidence": "high"},
    {"name": "Argo CD", "category": "ci-cd", "usage_context": "GitOps deployment tool", "integration_pattern": "operator", "confidence": "high"},
    {"name": "Open Policy Agent", "category": "security", "usage_context": "Admission control policy enforcement", "integration_pattern": "native", "confidence": "high"}
  ]
}
```

---

### Mistake 2: Missing Transcript Quotes for Metrics

**Wrong:**
```json
{
  "metric_name": "Performance",
  "before_value": "slow",
  "after_value": "fast",
  "measurement_unit": "speed",
  "source_confidence": "implied",
  "transcript_quote": ""
}
```

**Why Wrong:**
- No transcript quote (will fail validation)
- Vague metric name ("Performance")
- Non-quantitative values ("slow", "fast")
- Meaningless unit ("speed")

**Fix:**
```json
{
  "metric_name": "API Response Time (p95)",
  "before_value": "500",
  "after_value": "50",
  "measurement_unit": "milliseconds",
  "source_confidence": "explicit",
  "transcript_quote": "We reduced our p95 API response time from 500 milliseconds down to 50 milliseconds after implementing Istio with connection pooling."
}
```

---

### Mistake 3: Missing Architecture Layers

**Wrong:**
```json
{
  "architecture_components": {
    "platform_layer": [
      {"component": "Kubernetes", "description": "Orchestration", "cncf_projects": ["Kubernetes"]}
    ]
  }
}
```

**Why Wrong:**
- Only 1 layer (need all 3)
- Will fail validation

**Fix:**
```json
{
  "architecture_components": {
    "infrastructure_layer": [
      {"component": "AWS VPC", "description": "Network isolation", "cncf_projects": []},
      {"component": "Calico CNI", "description": "Pod networking", "cncf_projects": ["Calico"]}
    ],
    "platform_layer": [
      {"component": "Kubernetes", "description": "Container orchestration", "cncf_projects": ["Kubernetes"]},
      {"component": "Istio", "description": "Service mesh", "cncf_projects": ["Istio"]}
    ],
    "application_layer": [
      {"component": "Microservices", "description": "Business logic", "cncf_projects": []}
    ]
  }
}
```

---

### Mistake 4: Vague Section Content

**Wrong (Technical Challenge section):**
> "The company had performance problems and scalability issues. Things were slow and customers complained. They needed a better solution."

**Why Wrong:**
- No specific technical details
- Vague problems ("slow", "issues")
- No quantitative impact

**Fix:**
> "The platform experienced cascading failures during peak traffic, with API response times spiking from 200ms to 5+ seconds. Traditional load balancing couldn't prevent these failures because services lacked circuit breakers or retry logic. The engineering team attempted to implement custom retry logic in each of 50+ services, but this increased development time by 40% and led to inconsistent behavior. With 50% YoY traffic growth projected, the existing architecture would not scale without significant re-architecture."

---

## Success Criteria

Your output is successful if:

1. ✅ Validates successfully with `validate-deep-analysis` (exit code 0)
2. ✅ Contains only CNCF projects explicitly named in the transcript
3. ✅ Documents architecture layers discussed in the transcript (gaps disclosed)
4. ✅ Integration patterns are grounded in what speakers described
5. ✅ All metrics have supporting transcript quotes
6. ✅ Each section covers transcript content faithfully (shorter is acceptable)
7. ✅ Identifies at least 6 screenshot opportunities with clear descriptions
8. ✅ Output is strictly based on transcript content (no fabrication, no inference)

---

**Version History:**
- 1.0.0 (2026-02-09): Initial skill definition for reference architecture generation

**Related Skills:**
- `transcript-correction`: Input preparation (corrects transcript before deep analysis)
- `reference-architecture-generation`: Downstream consumer (uses this analysis)

**Related CLI Tools:**
- `validate-transcript`: Validates transcript quality before analysis
- `validate-deep-analysis`: Validates this skill's output
- `validate-company`: Validates company name input
