# Skill: reference-architecture-generation

**Version:** 1.0.0  
**Purpose:** Generate comprehensive 10-section reference architecture content from deep analysis and diagram specifications for CNCF TAB submission.

---

## Overview

This skill transforms deep technical analysis and diagram specifications into a complete reference architecture document suitable for submission to the CNCF Technical Advisory Board (TAB).

### Key Differences from case-study-generation

| Aspect | Case Study | Reference Architecture |
|--------|------------|----------------------|
| **Sections** | 5 sections | 10 sections |
| **Length per section** | 100-300 words | 400-800 words |
| **Total length** | 500-1500 words | 2000-5000 words |
| **Audience** | Business leaders, marketing | Engineers, architects |
| **Tone** | Business-focused, benefits | Technical, instructional |
| **CNCF Projects** | 2+ projects | 5+ projects |
| **Technical depth** | High-level | Implementation-level |
| **Diagrams** | Optional | Required (with descriptions) |
| **Integration patterns** | Mentioned | Detailed explanation |
| **TAB submission** | No | Yes (with metadata) |

---

## Input Format

```json
{
  "deep_analysis": {
    "cncf_projects": [
      {
        "name": "Kubernetes",
        "category": "Orchestration & Management",
        "usage_context": "Primary container orchestration platform",
        "version": "v1.26",
        "configuration_details": "Three production clusters with Calico CNI"
      }
    ],
    "architecture_components": {
      "infrastructure_layer": [
        {
          "component": "Kubernetes Clusters",
          "description": "Three production clusters (us-east-1, us-west-2, eu-west-1)"
        }
      ],
      "platform_layer": [
        {
          "component": "Istio Service Mesh",
          "description": "Traffic management and observability"
        }
      ],
      "application_layer": [
        {
          "component": "Microservices",
          "description": "200+ microservices deployed across clusters"
        }
      ]
    },
    "integration_patterns": [
      {
        "pattern": "Service Mesh Integration",
        "description": "Istio provides traffic management between Kubernetes services",
        "projects_involved": ["Kubernetes", "Istio"]
      }
    ],
    "technical_metrics": [
      {
        "metric_name": "API Latency (p95)",
        "before_value": "500ms",
        "after_value": "50ms",
        "improvement_factor": "10x",
        "business_impact": "Enabled 200% user growth",
        "transcript_quote": "We reduced our p95 API latency from 500 milliseconds down to just 50 milliseconds"
      }
    ],
    "sections": {
      "background": "200-400 words: Company context from transcript...",
      "technical_challenge": "400-600 words: Specific problems faced...",
      "architecture_overview": "500-700 words: High-level design...",
      "implementation_details": "700-900 words: Step-by-step process...",
      "results_and_impact": "400-600 words: Outcomes and metrics...",
      "lessons_learned": "400-600 words: Reflections and advice..."
    },
    "screenshot_opportunities": [
      {
        "timestamp_seconds": 120,
        "description": "Kubernetes dashboard showing cluster overview",
        "section": "architecture_overview"
      }
    ],
    "key_quotes": [
      {
        "quote": "Moving to Kubernetes allowed us to scale from 50 to 500 microservices",
        "speaker": "CTO",
        "relevance": "Business impact of architecture decision"
      }
    ]
  },
  "diagram_specifications": {
    "diagrams": [
      {
        "title": "High-Level Architecture",
        "diagram_type": "system_context",
        "description": "Shows external users, load balancers, Kubernetes clusters, and databases",
        "components": ["Users", "AWS ALB", "EKS Clusters", "RDS", "S3"],
        "relationships": [
          {"from": "Users", "to": "AWS ALB", "type": "HTTPS requests"},
          {"from": "AWS ALB", "to": "EKS Clusters", "type": "Routes traffic"}
        ]
      }
    ]
  },
  "company_info": {
    "name": "Example Corp",
    "url": "https://example.com",
    "industry": "E-commerce",
    "verified_membership": true,
    "company_size": "500-1000 employees"
  },
  "video_metadata": {
    "title": "Example Corp's Journey to Cloud Native with Kubernetes and Istio - John Doe & Jane Smith, Example Corp",
    "url": "https://youtube.com/watch?v=VIDEO_ID",
    "duration_seconds": 1234,
    "duration_string": "20:34",
    "publication_date": "2026-01-15",
    "speakers": "John Doe & Jane Smith"
  }
}
```

---

## Output Format

```json
{
  "metadata": {
    "title": "Reference Architecture: E-commerce Platform on Kubernetes with Istio Service Mesh",
    "subtitle": "Multi-region, multi-cluster architecture for high-traffic e-commerce workloads",
    "company_name": "Example Corp",
    "company_url": "https://example.com",
    "industry": "E-commerce",
    "video_url": "https://youtube.com/watch?v=VIDEO_ID",
    "video_title": "Example Corp's Journey to Cloud Native with Kubernetes and Istio - John Doe & Jane Smith, Example Corp",
    "duration_string": "20:34",
    "speakers": "John Doe & Jane Smith",
    "publication_date": "2026-02-09",
    "word_count": 3500,
    "estimated_read_time": "18 minutes",
    "tab_metadata": {
      "project_maturity": "graduated",
      "architectural_significance": "Demonstrates multi-cluster Kubernetes with service mesh at scale for e-commerce",
      "primary_patterns": ["microservices", "service-mesh", "multi-cluster"]
    }
  },
  "sections": {
    "executive_summary": "200-300 words: Concise overview of the architecture, problem solved, and key outcomes...",
    "background": "300-400 words: Company context, industry, business requirements...",
    "technical_challenge": "400-600 words: Specific technical problems faced (scalability, reliability, etc.)...",
    "architecture_overview": "500-700 words: High-level architecture description with layers...",
    "architecture_diagrams": "300-400 words: Descriptions of each diagram with references...",
    "cncf_projects": "500-700 words: Detailed usage of each CNCF project...",
    "integration_patterns": "400-600 words: How projects integrate (e.g., Kubernetes + Istio)...",
    "implementation_details": "700-900 words: Step-by-step implementation process with commands/configs...",
    "deployment_architecture": "400-600 words: Multi-cluster, multi-region deployment setup...",
    "observability_operations": "400-600 words: Monitoring, logging, alerting, operations...",
    "results_and_impact": "400-600 words: Quantitative results and business impact...",
    "lessons_learned": "400-600 words: What worked, what didn't, recommendations...",
    "conclusion": "200-300 words: Summary and future directions..."
  },
  "cncf_project_list": [
    {
      "name": "Kubernetes",
      "category": "Orchestration & Management",
      "usage_summary": "Primary container orchestration platform across three production clusters"
    },
    {
      "name": "Istio",
      "category": "Service Mesh",
      "usage_summary": "Traffic management, security, and observability for microservices"
    }
  ],
  "key_metrics_summary": [
    {
      "metric": "API Latency (p95)",
      "improvement": "500ms → 50ms (10x improvement)",
      "business_impact": "Enabled 200% user growth"
    }
  ]
}
```

---

## Execution Instructions

### CRITICAL: Professional Formatting Requirements

**ALL sections must follow these formatting rules:**

```
1. Paragraph Structure:
   - NEVER generate text as one continuous blob
   - ALWAYS break content into multiple paragraphs (2-5 sentences each)
   - Add blank line between paragraphs in markdown
   - Each paragraph should have ONE clear focus
   
2. Markdown Table Formatting:
   - Tables MUST have proper markdown syntax:
     | Column 1 | Column 2 | Column 3 |
     |----------|----------|----------|
     | Row 1    | Data     | Data     |
     | Row 2    | Data     | Data     |
   
   - ALWAYS include header separator row with dashes: |----------|
   - Ensure each row has same number of columns as header
   - No missing pipes (|) at start/end of rows
   - Test table structure: count pipes in header vs data rows
   
3. Professional Tone:
   - Minimize bold formatting (use only for project names on first mention)
   - NO emojis anywhere in the content
   - NO marketing language or buzzwords
   - Use formal technical writing style
   - Avoid excessive formatting (bold, italics, caps)
   
4. Section Organization:
   - Use clear subsection headers (###) when needed
   - Group related content logically
   - Use numbered lists for sequential steps
   - Use bullet lists for non-sequential items
   
5. Bad Example (DO NOT DO THIS):
   "CERN's architecture leverages six CNCF projects each serving a specific purpose in the overall system Kubernetes CNCF Graduated serves as the primary container orchestration platform hosting Keycloak pods across multiple clusters in different availability zones The migration from VM-based infrastructure to Kubernetes occurred in September 2023 moving from puppet-managed VMs to operator-managed containers The multi-cluster approach treats each Kubernetes cluster as cattle rather than pets clusters are replaceable and zone failures are handled gracefully..."
   
   Why bad: One massive paragraph, no breaks, unreadable
   
6. Good Example (DO THIS):
   "[CERN](https://home.cern)'s architecture leverages six CNCF projects, each serving a specific purpose in the overall system.
   
   **[Kubernetes](https://kubernetes.io)** (CNCF Graduated) serves as the primary container orchestration platform, hosting Keycloak pods across multiple clusters in different availability zones. The migration from VM-based infrastructure to Kubernetes occurred in September 2023, moving from puppet-managed VMs to operator-managed containers.
   
   The multi-cluster approach treats each Kubernetes cluster as cattle rather than pets. Clusters are replaceable and zone failures are handled gracefully without manual intervention. This design choice enables automatic failover and reduces operational burden."
   
   Why good: Multiple paragraphs, clear breaks, readable structure, proper linking

7. Screenshot Management (CRITICAL):
   - EACH screenshot MUST be used EXACTLY ONCE in the document
   - Track used screenshots to prevent duplicates
   - Screenshots are numbered 1-6 (screenshot-1.jpg through screenshot-6.jpg)
   - Once a screenshot is embedded, mark it as USED
   - NEVER reference the same screenshot number twice
   - If you need to refer to a diagram again, use text reference: "As shown in the architecture diagram above..."
   - Screenshot format: [![Description](images/slug/screenshot-N.jpg)](VIDEO_URL&t=XXXs)
   - Each screenshot should appear in the most relevant section based on deep_analysis.screenshot_opportunities
   - Distribute screenshots across 3-4 major sections (not all in one place)
   - Example: screenshot-1 in Background, screenshot-2 in Architecture Overview, screenshot-3 in Implementation, etc.
```

Follow these steps to generate the reference architecture:

### Step 1: Extract and Validate Inputs

Read all input data and validate structure:

```
1. Load deep_analysis from input
2. Load diagram_specifications from input
3. Load company_info from input
4. Load video_metadata from input
5. Verify all required fields are present
6. Verify deep_analysis has 5+ CNCF projects
7. Verify all 3 architecture layers are present
```

### Step 2: Generate Metadata

Create metadata for the reference architecture:

```
1. Generate title:
   - Format: "Reference Architecture: [Problem Domain] on [Primary CNCF Project] with [Secondary Projects]"
   - Example: "Reference Architecture: E-commerce Platform on Kubernetes with Istio Service Mesh"
   - Keep title under 100 characters
   - Make it descriptive and specific

2. Generate subtitle:
   - One-line description of the architecture's purpose
   - Format: "[Architecture pattern] for [use case]"
   - Example: "Multi-region, multi-cluster architecture for high-traffic e-commerce workloads"
   - Keep subtitle under 150 characters

3. Extract company_name and company_url from company_info:
   - company_name: from company_info.name
   - company_url: from company_info.url

4. Extract video metadata:
   - video_url: from video_metadata.url
   - video_title: from video_metadata.title (full title with speakers)
   - duration_string: from video_metadata.duration_string (format: "MM:SS" or "HH:MM:SS")
   - speakers: from video_metadata.speakers (extracted from title, format: "Name1 & Name2")

5. Calculate word_count:
   - Sum word counts from all sections
   - Target: 2500-4000 words (acceptable: 2000-5000)

6. Calculate estimated_read_time:
   - Formula: word_count / 200 (words per minute)
   - Round to nearest minute

7. Generate TAB metadata:
   a. project_maturity:
      - Check CNCF project maturity levels
      - Use highest maturity level among primary projects
      - Values: "graduated", "incubating", "sandbox"
   
   b. architectural_significance:
      - One sentence explaining why this architecture is significant
      - Focus on: scale, complexity, novel patterns, lessons learned
      - Example: "Demonstrates multi-cluster Kubernetes with service mesh at scale for e-commerce"
   
   c. primary_patterns:
      - List 2-4 architectural patterns used
      - Examples: "microservices", "service-mesh", "multi-cluster", "gitops", "event-driven"
      - Extract from deep_analysis.integration_patterns and architecture description

6. Set publication_date to current date (ISO format: YYYY-MM-DD)

7. Copy company_name, industry, video_url from inputs
```

### Step 2.5: Markdown Linking Conventions (CRITICAL)

**IMPORTANT:** All reference architectures must follow the same linking conventions as case studies for consistency.

```
Linking Rules (apply throughout ALL sections):

1. Company Name Linking:
   - ALWAYS link company name: [Company Name](https://company-url.com)
   - Link company name in EVERY section where it appears
   - Example: "[CERN](https://home.cern)" NOT "CERN"
   - Use company_url from company_info.url

2. CNCF Project Linking:
   - ALWAYS link CNCF projects with bold formatting: **[Project Name](https://project-url)**
   - Link on FIRST mention in each major section
   - Examples:
     - **[Kubernetes](https://kubernetes.io)**
     - **[Keycloak](https://www.keycloak.org)**
     - **[Argo CD](https://argoproj.github.io/cd/)**
     - **[Prometheus](https://prometheus.io)**
     - **[Istio](https://istio.io)**
   - Use official project URLs (kubernetes.io, istio.io, etc.)
   - Subsequent mentions in same section can be unlinked

3. CNCF Glossary Term Linking:
   - Link cloud-native terminology to CNCF glossary: [term](https://glossary.cncf.io/term/)
   - Common terms to link:
     - [cloud-native](https://glossary.cncf.io/cloud-native-tech/)
     - [microservices](https://glossary.cncf.io/microservices-architecture/)
     - [container orchestration](https://glossary.cncf.io/container-orchestration/)
     - [service mesh](https://glossary.cncf.io/service-mesh/)
     - [observability](https://glossary.cncf.io/observability/)
     - [GitOps](https://glossary.cncf.io/gitops/)
     - [progressive delivery](https://glossary.cncf.io/progressive-delivery/)
     - [canary deployment](https://glossary.cncf.io/canary-deployment/)
   - Link on first mention in each major section
   - Use kebab-case URLs (service-mesh, not servicemesh)

4. Project URL Reference List:
   Kubernetes: https://kubernetes.io
   Keycloak: https://www.keycloak.org
   Argo CD: https://argoproj.github.io/cd/
   Argo Rollouts: https://argoproj.github.io/rollouts/
   Prometheus: https://prometheus.io
   Grafana: https://grafana.com
   Istio: https://istio.io
   Envoy: https://www.envoyproxy.io
   Helm: https://helm.sh
   Fluent Bit: https://fluentbit.io
   Fluentd: https://www.fluentd.org
   Jaeger: https://www.jaegertracing.io
   Podman: https://podman.io
   Containerd: https://containerd.io
   
   (If project not listed, use format: https://projectname.io or https://github.com/cncf/projectname)

Example paragraph with proper linking:

"[CERN](https://home.cern) operates a multi-cluster **[Kubernetes](https://kubernetes.io)** architecture 
across multiple availability zones. The team uses **[Keycloak](https://www.keycloak.org)** for identity 
management with **[Argo CD](https://argoproj.github.io/cd/)** for [GitOps](https://glossary.cncf.io/gitops/)-based 
deployments. This [cloud-native](https://glossary.cncf.io/cloud-native-tech/) approach enables 
[CERN](https://home.cern) to manage 200,000 users with high availability. Monitoring is handled by 
**[Prometheus](https://prometheus.io)** and **[Grafana](https://grafana.com)**."

Quality Checks:
- [ ] Company name linked in every section
- [ ] All CNCF projects linked with bold on first mention per section
- [ ] Cloud-native terms linked to glossary on first mention per section
- [ ] URLs are correct and follow official project domains
- [ ] No broken links or placeholder URLs
```

### Step 3: Generate Executive Summary (200-300 words)

Write a concise overview of the entire architecture:

```
Paragraph 1: Problem and Context (50-75 words)
- Company name and industry
- Business challenge or requirement
- Why cloud native was needed
- Example: "Example Corp, a leading e-commerce platform, needed to scale from 50 to 500 microservices while maintaining sub-100ms API latency for millions of daily users."

Paragraph 2: Solution Overview (75-100 words)
- High-level architecture description
- Primary CNCF projects used
- Key architectural patterns
- Example: "The team implemented a multi-region Kubernetes architecture spanning three AWS regions, with Istio service mesh for traffic management and Prometheus/Grafana for observability."

Paragraph 3: Key Results (50-75 words)
- Top 3-4 quantitative improvements
- Business impact
- Example: "The new architecture reduced API latency by 10x (500ms → 50ms), improved deployment frequency from weekly to 50+ times per day, and enabled the platform to handle 200% user growth."

Paragraph 4: Significance (25-50 words)
- Why this architecture is relevant to other organizations
- What makes it noteworthy
- Example: "This reference architecture demonstrates how to operate Kubernetes at scale across multiple regions while maintaining high availability and performance."

Quality checks:
- Total word count: 200-300 words
- No marketing language or buzzwords
- Includes specific metrics with numbers
- Mentions 3-5 CNCF projects by name
```

### Step 4: Generate Background (300-400 words)

Provide company and business context:

```
Paragraph 1: Company Overview (75-100 words)
- Company name, industry, size
- Core business and products
- Target market and scale
- Extract from deep_analysis.sections.background and company_info
- Example: "Example Corp is a global e-commerce platform serving 10 million monthly active users across 30 countries. Founded in 2015, the company processes over $500M in annual transactions through its web and mobile applications."

Paragraph 2: Previous Architecture (100-125 words)
- What they were using before (monolith, legacy systems, etc.)
- Technical limitations of old approach
- Specific pain points
- Extract from deep_analysis.sections.background and technical_challenge
- Example: "Prior to 2024, Example Corp ran on a monolithic Rails application deployed on EC2 instances behind an ELB. As the platform grew, they encountered several critical limitations: deploys took 45 minutes and required downtime, scaling required manual intervention, and debugging production issues was difficult due to lack of observability."

Paragraph 3: Business Drivers (75-100 words)
- Why change was necessary
- Business goals and requirements
- Growth projections or competitive pressure
- Extract from deep_analysis.sections.background and key_quotes
- Example: "The company's ambitious growth plans required a more scalable architecture. The CTO stated: 'We needed to move from deploying once a week to multiple times per day to keep pace with customer demands.' Additionally, expanding to new regions required geographic distribution of services."

Paragraph 4: Decision to Adopt Cloud Native (50-75 words)
- Why they chose Kubernetes and CNCF projects
- Evaluation process or alternatives considered
- Key decision factors
- Example: "After evaluating managed services, serverless, and Kubernetes, the team chose Kubernetes for its flexibility and community support. The decision to adopt Istio came later when the team realized they needed more sophisticated traffic management and observability."

Quality checks:
- Total word count: 300-400 words
- Provides sufficient context for technical decisions
- Includes company-specific details (not generic)
- No fabricated information (only from transcript)
```

### Step 5: Generate Technical Challenge (400-600 words)

Detail the specific technical problems faced:

```
Paragraph 1: Core Technical Problem (100-150 words)
- Specific technical issues (not business issues)
- Why existing architecture couldn't solve it
- Technical constraints and requirements
- Extract from deep_analysis.sections.technical_challenge
- Use technical vocabulary (latency, throughput, consistency, etc.)
- Example: "The monolithic architecture presented three critical technical challenges: First, the application's synchronous request-response pattern created cascading failures when downstream services experienced latency. A slow database query could block an entire worker process, degrading performance across the entire application. Second, the team lacked visibility into service dependencies, making it difficult to debug production issues..."

Paragraph 2: Scalability Challenges (100-150 words)
- Specific scalability issues
- Performance bottlenecks
- Resource utilization problems
- Include metrics from deep_analysis.technical_metrics
- Example: "The platform's traffic patterns showed 10x spikes during flash sales and promotional events. The monolith could not horizontally scale individual components—scaling the checkout service meant scaling the entire application, wasting resources. During peak traffic, API latency (p95) reached 500ms, causing cart abandonment. The team estimated they needed to handle 50,000 requests per second during peak periods..."

Paragraph 3: Reliability and Availability Challenges (100-150 words)
- Downtime issues
- Failure scenarios
- Disaster recovery limitations
- Example: "Deployments required a maintenance window and caused 15-30 minutes of downtime. In 2023, the platform experienced three major outages totaling 8 hours of downtime, costing an estimated $2M in lost revenue. The monolithic architecture lacked regional redundancy—if the us-east-1 region went down, the entire platform went down. Additionally, database failures caused complete service outages..."

Paragraph 4: Operational Challenges (100-150 words)
- Deployment and CI/CD limitations
- Monitoring and debugging difficulties
- Team velocity and developer experience
- Example: "The ops team spent 40% of their time on manual deployment tasks and troubleshooting production issues. The lack of structured logging and distributed tracing made debugging difficult—engineers would spend hours correlating logs across multiple servers. Deployment frequency averaged once per week, limiting the team's ability to iterate quickly. Rollbacks required reverting database migrations, a risky and time-consuming process..."

Quality checks:
- Total word count: 400-600 words
- Focuses on technical problems (not business problems)
- Includes specific metrics and numbers
- Each paragraph has a clear focus
- Problems are concrete and specific (not vague)
- Connects to why cloud native was chosen
```

### Step 6: Generate Architecture Overview (500-700 words)

Describe the high-level architecture design:

```
Paragraph 1: Architecture Vision (75-100 words)
- High-level architecture approach
- Key design principles
- Overall architecture style (microservices, event-driven, etc.)
- Example: "Example Corp adopted a microservices architecture running on Kubernetes across three AWS regions. The design prioritizes fault isolation, independent scaling, and regional autonomy. Services communicate via HTTP/gRPC through an Istio service mesh, with asynchronous events handled by Kafka for eventually-consistent operations."

Paragraph 2: Infrastructure Layer (150-200 words)
- Physical/cloud infrastructure
- Kubernetes clusters (how many, where, why)
- Networking setup
- Extract from deep_analysis.architecture_components.infrastructure_layer
- Include specific configuration details
- Example: "The infrastructure layer consists of six Kubernetes clusters: three production clusters (us-east-1, us-west-2, eu-west-1), two staging clusters (us-east-1, eu-west-1), and one shared services cluster for monitoring and CI/CD. Each production cluster runs on Amazon EKS with 20-50 m5.2xlarge nodes using Kubernetes v1.26 and Calico CNI for network policies. Multi-region setup enables 99.99% availability SLA and sub-50ms latency for users worldwide. AWS Network Load Balancers distribute traffic to Istio ingress gateways in each region, with Route53 providing geo-aware DNS routing..."

Paragraph 3: Platform Layer (150-200 words)
- Service mesh, API gateway, message broker
- Platform services (observability, logging, etc.)
- Security and policy enforcement
- Extract from deep_analysis.architecture_components.platform_layer
- Example: "The platform layer provides cross-cutting concerns for all applications. Istio v1.18 service mesh handles traffic management, with Envoy sidecars automatically injected into all pods. Istio provides mutual TLS between services, circuit breaking, retries, and traffic shifting for canary deployments. Prometheus scrapes metrics from Envoy proxies and application endpoints, while Grafana provides dashboards and alerting. The ELK stack (Elasticsearch, Logstash, Kibana) centralizes logs from all services with structured JSON logging. ArgoCD implements GitOps for declarative deployments, with applications automatically synced from Git repositories..."

Paragraph 4: Application Layer (150-200 words)
- Microservices organization
- Service boundaries and responsibilities
- Data storage and state management
- Extract from deep_analysis.architecture_components.application_layer
- Example: "The application layer consists of 200+ microservices organized into 12 bounded contexts aligned with business domains (Catalog, Cart, Checkout, Orders, Payments, Inventory, Recommendations, etc.). Each domain team owns 10-20 services deployed independently. Services expose REST APIs and gRPC endpoints through Istio virtual services. State is stored in domain-specific databases (PostgreSQL for transactional data, DynamoDB for session data, Redis for caching, Elasticsearch for search). Services follow the Outbox pattern for reliable event publishing to Kafka, ensuring eventual consistency across domains..."

Quality checks:
- Total word count: 500-700 words
- Describes all 3 architecture layers clearly
- Includes specific technologies and versions
- Explains WHY design decisions were made (not just what)
- Provides enough detail for engineers to understand the architecture
- References diagram(s) if available
```

### Step 7: Generate Architecture Diagrams (300-400 words)

Describe the architecture diagrams with textual explanations:

```
Introduction (50 words):
- How many diagrams are included
- Purpose of each diagram type
- Example: "This reference architecture includes three diagrams that illustrate different aspects of the system: a high-level system context diagram, a detailed deployment architecture diagram, and a service interaction diagram showing request flow."

For each diagram from diagram_specifications.diagrams:

Diagram N: [Title] (75-125 words)
- Diagram type and purpose
- Main components shown
- Key relationships and data flows
- What this diagram reveals about the architecture
- Extract from diagram_specifications.diagrams[N]
- Example: 
  "Diagram 1: High-Level Architecture
  
  This system context diagram shows how external users interact with the platform across multiple regions. Users make HTTPS requests to Route53, which performs geographic routing to the nearest regional load balancer (AWS Network Load Balancer). Each region hosts an independent Kubernetes cluster with full application stack, ensuring regional autonomy. The diagram illustrates the data flow from user request through load balancer, Istio ingress gateway, microservices, and databases. Cross-region components include the shared monitoring cluster, CI/CD cluster, and centralized Elasticsearch for log aggregation."

Reference to diagrams in other sections:
- "See Diagram 1 for the complete system overview"
- "Refer to Diagram 2 for details on service-to-service communication"
- Encourage readers to use diagrams to understand the text

Quality checks:
- Total word count: 300-400 words
- Describes each diagram clearly without the diagram present
- Helps reader understand what they'll see in the visual
- Connects diagrams to architectural decisions
- If no diagram_specifications provided, explain that diagrams would enhance understanding and list what diagrams would be useful
```

### Step 8: Generate CNCF Projects (500-700 words)

Detail how each CNCF project is used:

```
CRITICAL: This section often becomes an unreadable blob. MUST use subsections and paragraph breaks.

Introduction (50-75 words):
- Brief paragraph listing all CNCF projects
- One sentence per project explaining its role
- Example: "This architecture leverages five graduated CNCF projects. **[Kubernetes](https://kubernetes.io)** provides container orchestration, **[Istio](https://istio.io)** handles service mesh capabilities, **[Prometheus](https://prometheus.io)** collects metrics, **[Argo CD](https://argoproj.github.io/cd/)** enables GitOps deployments, and **[Helm](https://helm.sh)** manages package definitions."

For each project in deep_analysis.cncf_projects:

### [Project Name] ([Category])

Write 3-4 SHORT paragraphs (NOT one long blob):

Paragraph 1 - Purpose (2-3 sentences):
[Why this project was chosen and its primary role]

Paragraph 2 - Implementation (3-4 sentences):
[Version, configuration, deployment details]

Paragraph 3 - Features (2-3 sentences + bullet list):
[Introduction sentence, then bulleted list of 3-5 features]

Paragraph 4 - Operations (2-3 sentences):
[How it's operated, monitored, maintained]

Example (CORRECT FORMATTING):

### Kubernetes (Orchestration & Management)

[Kubernetes](https://kubernetes.io) serves as the foundational container orchestration platform, managing all microservices across six clusters in three regions. The team selected Kubernetes for its maturity, extensive ecosystem, and proven scalability at enterprise scale.

The team deployed Kubernetes v1.26 using Amazon EKS in three AWS regions. Each production cluster runs 20-50 m5.2xlarge nodes with Cluster Autoscaler for dynamic scaling. All clusters use Calico CNI for network policies and identical configurations managed through Git.

Key features utilized include:
- Deployments with rolling updates (maxSurge: 25%, maxUnavailable: 0)
- StatefulSets for Kafka and Elasticsearch clusters
- DaemonSets for monitoring agents (Prometheus Node Exporter, Fluentd)
- Horizontal Pod Autoscaler targeting 70% CPU utilization
- Network Policies for service-to-service security
- RBAC for team-based access control

Node pools are segmented by workload type (general compute, memory-intensive, GPU). Cluster upgrades follow a rolling approach: dev clusters first, then staging, then production regions sequentially.

Quality checks:
- Total word count: 500-700 words (80-140 words per project)
- Covers 5+ CNCF projects with proper paragraph structure
- Each project has 3-4 SHORT paragraphs (NOT one blob)
- Includes version numbers and specific configurations
- Explains WHY each project was chosen
- Uses subsection headers (###) for each project
```

### Step 9: Generate Integration Patterns (400-600 words)

Explain how CNCF projects integrate and work together:

```
Introduction (50-75 words):
- What integration patterns exist in this architecture
- Why integration between projects is important
- Example: "The architecture's success depends on seamless integration between CNCF projects. Three primary integration patterns enable this: service mesh observability integration, GitOps continuous deployment, and unified monitoring and alerting."

For each pattern in deep_analysis.integration_patterns (100-150 words each):

Pattern N: [Pattern Name]

**Projects Involved:** [List projects]
- Extract from integration_patterns[N].projects_involved

**Description:**
- How the pattern works
- Technical implementation details
- Extract from integration_patterns[N].description
- Include specific configuration or code examples

**Benefits:**
- What this integration enables
- Performance or operational improvements

**Implementation Challenges:**
- Difficulties encountered
- Solutions applied
- Extract from deep_analysis.sections.lessons_learned if relevant

Example:

Pattern 1: Service Mesh Observability Integration

**Projects Involved:** Kubernetes, Istio, Prometheus, Grafana

**Description:** Istio's Envoy sidecars automatically generate detailed metrics for all service-to-service communication without requiring application code changes. Prometheus scrapes these metrics every 15 seconds from each Envoy proxy using Kubernetes Service Discovery. The team configured Istio to export additional custom metrics for business-level monitoring (requests by product category, checkout completion rate). Grafana dashboards visualize service latency, error rates, and traffic patterns in real-time. The integration provides automatic RED metrics (Rate, Errors, Duration) for every service.

**Benefits:** This integration provides zero-instrumentation observability—new services automatically get monitoring without developer effort. The team reduced mean time to detection (MTTD) from 15 minutes to 2 minutes by alerting on Envoy proxy metrics. Service owners can identify downstream dependencies and latency sources through distributed tracing integration with Jaeger.

**Implementation Challenges:** The team initially encountered high cardinality issues when exporting metrics with too many labels (service, version, pod, cluster), causing Prometheus memory issues. Solution: reduced label cardinality by removing pod-level labels and using recording rules to pre-aggregate common queries.

Quality checks:
- Total word count: 400-600 words
- Describes 2-4 integration patterns in detail
- Shows how projects work together (not in isolation)
- Includes technical implementation details
- Mentions configuration specifics
- Explains benefits AND challenges
```

### Step 10: Generate Implementation Details (700-900 words)

Provide step-by-step implementation guidance:

```
Introduction (75-100 words):
- Overview of implementation approach
- Timeline (how long it took)
- Team size and organization
- Extract from deep_analysis.sections.implementation_details
- Example: "The implementation occurred in four phases over six months, led by a platform team of 8 engineers. The team followed a phased rollout approach: infrastructure first, platform services second, application migration third, and optimization fourth. Each phase included validation in staging before production rollout."

Phase 1: [Phase Name] (150-200 words)
**Duration:** [Timeframe]

**Objectives:**
- What was accomplished in this phase
- Why this phase was first

**Steps:**
1. [Detailed step with commands or configurations]
2. [Detailed step with commands or configurations]
3. [Continue...]

**Challenges and Solutions:**
- Problem encountered
- How it was resolved
- Lesson learned

**Validation:**
- How success was measured
- Tests performed

Example:

Phase 1: Infrastructure Foundation (6 weeks)

**Duration:** January 1 - February 15, 2024

**Objectives:** Establish the base Kubernetes infrastructure across three regions with core platform services. This phase focused on cluster provisioning, networking setup, and security configuration.

**Steps:**
1. Provisioned three EKS clusters using eksctl with the following configuration:
   ```yaml
   apiVersion: eksctl.io/v1alpha5
   kind: ClusterConfig
   metadata:
     name: prod-us-east-1
     region: us-east-1
   nodeGroups:
     - name: general
       instanceType: m5.2xlarge
       desiredCapacity: 20
       maxSize: 50
   ```

2. Deployed Calico CNI for network policy enforcement:
   ```bash
   kubectl apply -f https://docs.projectcalico.org/manifests/calico.yaml
   ```

3. Configured cluster autoscaling with target metrics (CPU: 70%, Memory: 80%)

4. Established VPC peering between regions for cross-region communication

5. Deployed shared services (DNS, NTP, certificate management)

**Challenges and Solutions:**
- **Problem:** Initial node group sizing was too small, causing pod evictions during load testing.
- **Solution:** Increased min nodes from 10 to 20 per cluster and tuned HPA thresholds.
- **Lesson:** Load test infrastructure before application migration.

**Validation:**
- Created test deployments in each cluster
- Verified cross-cluster networking (5ms latency between regions)
- Stress tested node autoscaling (scaled from 20 to 45 nodes in 10 minutes)

[Continue with Phase 2, Phase 3, Phase 4...]

Quality checks:
- Total word count: 700-900 words
- Divided into 3-4 clear phases
- Each phase has specific timeline
- Includes actual commands, configs, or code snippets
- Describes challenges encountered (not just successes)
- Shows practical implementation details engineers can follow
- Extract all details from deep_analysis.sections.implementation_details
```

### Step 11: Generate Deployment Architecture (400-600 words)

Describe multi-cluster, multi-region deployment setup:

```
Paragraph 1: Deployment Strategy Overview (100-125 words)
- Multi-region vs. single-region rationale
- Active-active vs. active-passive
- Traffic routing approach
- Example: "Example Corp operates an active-active multi-region deployment across three AWS regions: us-east-1 (primary), us-west-2 (secondary), and eu-west-1 (for European users). Each region runs an independent, fully-functional copy of the entire application stack. Route53 performs geographic routing, directing users to the nearest region for optimal latency. If a region fails, Route53 health checks automatically route traffic to healthy regions within 30 seconds."

Paragraph 2: Cluster Organization (100-125 words)
- How many clusters, where, and why
- Cluster sizing and node groups
- Separation of concerns (prod/staging/shared services)
- Example: "The architecture uses six Kubernetes clusters: three production (one per region), two staging (us-east-1 and eu-west-1), and one shared services cluster for CI/CD and monitoring. Production clusters run 20-50 nodes each, while staging runs 10-15 nodes. Shared services cluster runs 5 nodes for ArgoCD, Jenkins, Prometheus (cross-cluster monitoring), and Grafana. This separation ensures that CI/CD failures don't impact production and monitoring remains available during regional outages."

Paragraph 3: Deployment Pipeline (100-125 words)
- CI/CD approach
- GitOps workflow
- Deployment frequency and process
- Extract from implementation details if available
- Example: "The team uses ArgoCD for GitOps-based deployments. Service code lives in application repositories; Kubernetes manifests live in a separate config repository. When developers merge to main, Jenkins builds Docker images, pushes to ECR, and updates the config repository with new image tags. ArgoCD detects changes and automatically syncs to dev cluster within 1 minute. After automated testing passes, developers promote to staging manually. Production deploys require approval and follow a phased rollout: 10% traffic → 25% → 50% → 100% over 2 hours with automatic rollback on errors."

Paragraph 4: Regional Coordination and Data Consistency (100-125 words)
- How regions coordinate
- Data replication strategy
- Handling cross-region traffic
- Example: "Each region maintains its own PostgreSQL RDS databases with cross-region replication for read replicas. Writes go to the regional primary; reads can use local replicas for lower latency. For globally-consistent data (user accounts, product catalog), DynamoDB Global Tables provide multi-region active-active replication with eventual consistency. Session data is stored in regional ElastiCache clusters with session replication disabled—if a user fails over to another region, they re-authenticate. This design optimizes for performance over strict consistency."

Quality checks:
- Total word count: 400-600 words
- Explains deployment strategy clearly
- Includes specific technologies (ArgoCD, Jenkins, etc.)
- Describes data replication and consistency approach
- Shows regional organization and traffic routing
```

### Step 12: Generate Observability and Operations (400-600 words)

Describe monitoring, logging, alerting, and operational practices:

```
Paragraph 1: Observability Stack Overview (100-125 words)
- Three pillars: metrics, logs, traces
- Tools used for each
- Why observability is critical for this architecture
- Example: "Observability is central to operating 200+ microservices across three regions. The architecture implements the three pillars of observability: metrics (Prometheus + Grafana), logs (ELK stack), and distributed tracing (Jaeger). Istio service mesh provides automatic instrumentation for service-to-service communication without application code changes. The centralized observability stack runs in the shared services cluster, collecting telemetry from all regions."

Paragraph 2: Metrics and Monitoring (100-125 words)
- What metrics are collected
- How alerting works
- Key dashboards
- Example: "Prometheus collects metrics every 15 seconds from three sources: Envoy sidecars (service mesh metrics), application /metrics endpoints (business metrics), and Kubernetes API (cluster metrics). Grafana dashboards provide real-time visibility into service health, latency percentiles (p50, p95, p99), error rates, and traffic patterns. The platform team maintains 30+ dashboards organized by domain (infrastructure, platform, applications). PagerDuty integration alerts on-call engineers for critical issues (API latency p95 > 100ms, error rate > 1%, pod crash loops)."

Paragraph 3: Logging and Debugging (100-125 words)
- Log aggregation approach
- Structured logging
- How engineers debug issues
- Example: "All services emit structured JSON logs to stdout, which Fluentd DaemonSets collect and forward to Elasticsearch. The ELK stack indexes 5TB of logs daily with 30-day retention. Engineers use Kibana to search logs across all services and regions, correlating requests using trace IDs. The team standardized on common log fields (timestamp, severity, service, trace_id, user_id) enabling cross-service queries. During incidents, engineers query Elasticsearch for error patterns, then use Jaeger to visualize the complete request trace across 10+ services."

Paragraph 4: Operational Runbooks and Incident Response (100-125 words)
- How incidents are handled
- Runbooks and automation
- On-call rotation and escalation
- Example: "The team maintains runbooks for 20 common failure scenarios (node failures, pod evictions, database failovers, certificate expiration). Runbooks include symptoms, investigation steps, and remediation procedures. On-call engineers use a three-tier escalation: L1 (first responders, 15-minute response time), L2 (service owners, 30-minute response time), L3 (senior engineers, 1-hour response time). Post-incident reviews occur within 48 hours with blameless postmortems documenting timeline, root cause, and action items. The team averages 2-3 SEV-1 incidents per month with MTTR of 25 minutes."

Quality checks:
- Total word count: 400-600 words
- Covers metrics, logs, and traces
- Describes operational practices
- Includes specific tools and configurations
- Explains how engineers debug and respond to issues
```

### Step 13: Generate Results and Impact (400-600 words)

Present quantitative results and business impact:

```
Introduction (50-75 words):
- Overview of improvements achieved
- How success is measured
- Example: "The cloud native architecture delivered significant improvements across performance, reliability, and operational efficiency. The team tracks 15 key metrics comparing pre-migration (baseline from Q4 2023) to post-migration (Q2 2024 after stabilization). All metrics show substantial improvement, validating the architectural decisions."

For each metric in deep_analysis.technical_metrics:

**[Metric Name]**
- **Before:** [before_value]
- **After:** [after_value]
- **Improvement:** [improvement_factor]
- **Business Impact:** [business_impact]
- **Supporting Evidence:** "[transcript_quote]"

Example:

**Performance Metrics:**

**API Latency (p95)**
- **Before:** 500ms
- **After:** 50ms
- **Improvement:** 10x improvement
- **Business Impact:** Reduced cart abandonment rate by 15%, contributing to $5M additional annual revenue
- **Supporting Evidence:** "We reduced our p95 API latency from 500 milliseconds down to just 50 milliseconds, which had a direct impact on conversion rates."

**Request Throughput**
- **Before:** 5,000 requests/second
- **After:** 50,000 requests/second
- **Improvement:** 10x improvement
- **Business Impact:** Supported 200% user growth without infrastructure cost increases
- **Supporting Evidence:** "We can now handle ten times the traffic we could before, with better performance."

**Reliability Metrics:**

**Uptime / Availability**
- **Before:** 99.5% (3.6 hours downtime/month)
- **After:** 99.99% (4 minutes downtime/month)
- **Improvement:** 50x improvement in availability
- **Business Impact:** Eliminated $2M annual revenue loss from outages
- **Supporting Evidence:** "Our availability went from three nines to four nines, virtually eliminating customer-facing outages."

**Operational Metrics:**

**Deployment Frequency**
- **Before:** Weekly (1 deploy/week)
- **After:** Multiple daily (50+ deploys/day)
- **Improvement:** 350x improvement
- **Business Impact:** Accelerated feature delivery and reduced time-to-market by 80%
- **Supporting Evidence:** "We went from deploying once a week with a maintenance window to deploying 50 times a day with zero downtime."

Summary (75-100 words):
- Total business impact
- ROI if available
- Overall assessment
- Example: "Over six months, the cloud native architecture delivered measurable improvements across all key metrics. The platform now serves 10M monthly users across 30 countries with sub-100ms latency. Infrastructure costs decreased by 30% despite 200% traffic growth, due to efficient resource utilization and autoscaling. The $2M investment in migration and training paid for itself within 8 months through increased revenue and reduced operational costs. Most importantly, the architecture positions the company for continued growth."

Quality checks:
- Total word count: 400-600 words
- Every metric has before/after/improvement numbers
- Every metric has a transcript quote (no fabrication!)
- Business impact is quantified where possible
- Metrics are grouped logically (performance, reliability, operational)
- Summary ties results to business value
```

### Step 14: Generate Lessons Learned (400-600 words)

Share reflections, recommendations, and advice:

```
Introduction (50-75 words):
- Purpose of lessons learned section
- Tone: honest and practical
- Example: "Migrating to cloud native was transformative but challenging. This section shares key lessons learned during the 6-month implementation, organized into what worked well, what didn't work as expected, and recommendations for other teams considering similar migrations."

What Worked Well (125-175 words):
- 3-4 decisions or approaches that were successful
- Why they worked
- Extract from deep_analysis.sections.lessons_learned
- Example: 
  "**Phased Migration Approach:** The decision to migrate incrementally (infrastructure first, then platform, then applications) reduced risk and allowed learning between phases. Each phase included validation before proceeding, catching issues early.
  
  **Investment in Observability Early:** Deploying Prometheus, Grafana, and ELK stack before migrating applications was critical. When issues occurred, the team had visibility to debug quickly. This decision reduced MTTR significantly.
  
  **Cross-Functional Platform Team:** Creating a dedicated 8-person platform team with expertise in Kubernetes, networking, and security accelerated implementation. The team unblocked application developers and maintained consistency across services.
  
  **GitOps for Configuration Management:** Using ArgoCD to manage all Kubernetes manifests in Git provided auditability, rollback capabilities, and declarative deployments. Configuration drift became impossible."

What Didn't Work as Expected (125-175 words):
- 2-3 challenges or mistakes
- What went wrong and why
- How the team recovered
- Example:
  "**Underestimating State Migration Complexity:** Migrating stateful services (databases, caches) was harder than anticipated. The team initially planned 2 weeks but required 6 weeks due to data consistency validation and testing. Lesson: allocate 3x time for state migration.
  
  **Istio Resource Overhead:** Envoy sidecar proxies consumed more CPU and memory than expected (200-500MB per pod). Smaller services needed resource limit increases. The team adjusted cluster sizing and implemented horizontal pod autoscaling to compensate.
  
  **Team Training Gaps:** Application developers struggled with Kubernetes concepts initially. The platform team held weekly workshops and created runbooks, but adoption was slower than expected. In retrospect, more upfront training would have accelerated migration."

Recommendations for Other Teams (125-175 words):
- 3-5 actionable recommendations
- Based on experience from this project
- Tone: practical and specific
- Example:
  "**Start with Observability:** Deploy monitoring and logging infrastructure before migrating applications. You can't fix what you can't measure.
  
  **Invest in Platform Team:** Don't expect application teams to become Kubernetes experts. A dedicated platform team provides golden path patterns and reduces friction.
  
  **Plan for 2x Timeline:** Cloud native migrations always take longer than expected. Budget extra time for state migration, testing, and stabilization.
  
  **Adopt GitOps from Day 1:** Managing Kubernetes with kubectl is error-prone. GitOps provides guardrails and auditability from the start.
  
  **Validate in Production-like Staging:** Staging environments must mirror production (cluster size, traffic patterns, data volume). Many issues only appear under production load."

Quality checks:
- Total word count: 400-600 words
- Honest about challenges (not just successes)
- Specific and actionable recommendations
- Based on real experience (not generic advice)
- Organized into clear sections
- Extract from deep_analysis.sections.lessons_learned
```

### Step 15: Generate Conclusion (200-300 words)

Summarize and look forward:

```
Paragraph 1: Summary of Journey (75-100 words)
- Recap the transformation
- From-to narrative
- Key achievement
- Example: "Example Corp's transformation from a monolithic Rails application to a cloud native microservices architecture on Kubernetes represents a fundamental shift in how the company builds and operates software. Over six months, the team migrated 200+ microservices to Kubernetes across three regions, achieving 10x performance improvements and 50x reliability improvements while reducing infrastructure costs by 30%."

Paragraph 2: Current State and Continued Evolution (75-100 words)
- Where things stand today
- Ongoing optimization
- Adoption and maturity
- Example: "As of Q2 2024, the architecture is fully operational and stable. The team continues to optimize: implementing automated capacity planning, fine-tuning Istio traffic policies, and expanding observability with distributed tracing. Developer productivity has improved—teams now deploy multiple times daily with confidence. The platform team has shifted focus from migration to innovation, exploring service mesh federation and multi-cluster management."

Paragraph 3: Future Directions (50-75 words)
- What's next for this architecture
- Planned improvements or expansions
- Emerging technologies being considered
- Example: "Looking forward, the team plans to implement cross-region failover automation using Istio's multi-cluster capabilities, reducing RTO from 30 seconds to sub-second. Additional regions in APAC and South America are planned for 2025. The team is evaluating WebAssembly for edge computing and eBPF for advanced networking and security capabilities."

Quality checks:
- Total word count: 200-300 words
- Ties back to original problem and solution
- Shows current state and ongoing work
- Forward-looking (not just retrospective)
- Ends on positive, forward-looking note
```

### Step 16: Generate CNCF Project List

Create summary table of all CNCF projects:

```
Extract all unique CNCF projects from deep_analysis.cncf_projects

For each project, create entry:
{
  "name": "Project Name",
  "category": "CNCF category (e.g., 'Orchestration & Management')",
  "usage_summary": "One-sentence summary of how project is used (50-75 characters)"
}

Requirements:
- List projects in order of importance (primary projects first)
- Keep usage_summary brief but specific
- Ensure category names match official CNCF categories

Example:
[
  {
    "name": "Kubernetes",
    "category": "Orchestration & Management",
    "usage_summary": "Primary container orchestration platform across three production clusters"
  },
  {
    "name": "Istio",
    "category": "Service Mesh",
    "usage_summary": "Traffic management, security, and observability for microservices"
  },
  {
    "name": "Prometheus",
    "category": "Observability and Analysis",
    "usage_summary": "Metrics collection and alerting for infrastructure and applications"
  },
  {
    "name": "Argo CD",
    "category": "Continuous Integration & Delivery",
    "usage_summary": "GitOps-based continuous deployment to all Kubernetes clusters"
  },
  {
    "name": "Helm",
    "category": "Application Definition & Image Build",
    "usage_summary": "Package management for Kubernetes application deployments"
  }
]
```

### Step 17: Generate Key Metrics Summary

Create summary table of top improvements:

```
Extract top 5-7 metrics from deep_analysis.technical_metrics

For each metric, create entry:
{
  "metric": "Metric Name (with units)",
  "improvement": "Before → After (X improvement)",
  "business_impact": "One-sentence business impact"
}

Requirements:
- Select most impactful metrics (largest improvements or business value)
- Format consistently: "Before → After (Xx improvement)"
- Keep business_impact to one sentence (under 100 characters)
- Include mix of performance, reliability, and operational metrics

Example:
[
  {
    "metric": "API Latency (p95)",
    "improvement": "500ms → 50ms (10x improvement)",
    "business_impact": "Reduced cart abandonment by 15%, added $5M annual revenue"
  },
  {
    "metric": "Deployment Frequency",
    "improvement": "1 per week → 50 per day (350x improvement)",
    "business_impact": "Accelerated feature delivery and reduced time-to-market by 80%"
  },
  {
    "metric": "Availability",
    "improvement": "99.5% → 99.99% (50x improvement)",
    "business_impact": "Eliminated $2M annual revenue loss from outages"
  },
  {
    "metric": "Infrastructure Cost Efficiency",
    "improvement": "N/A → 30% reduction",
    "business_impact": "Saved $1.2M annually despite 200% traffic growth"
  }
]
```

### Step 18: Final Validation and Quality Check

Before outputting the final JSON, validate all requirements:

```
Validation Checklist:

Word Count:
- [ ] Total word count is between 2000-5000 words
- [ ] Each section meets target word count ranges
- [ ] Executive summary: 200-300 words
- [ ] Background: 300-400 words
- [ ] Technical challenge: 400-600 words
- [ ] Architecture overview: 500-700 words
- [ ] Architecture diagrams: 300-400 words
- [ ] CNCF projects: 500-700 words
- [ ] Integration patterns: 400-600 words
- [ ] Implementation details: 700-900 words
- [ ] Deployment architecture: 400-600 words
- [ ] Observability operations: 400-600 words
- [ ] Results and impact: 400-600 words
- [ ] Lessons learned: 400-600 words
- [ ] Conclusion: 200-300 words

Content Quality:
- [ ] All sections are present (10 required sections)
- [ ] 5+ CNCF projects documented
- [ ] Each project has detailed usage description
- [ ] Integration patterns between projects described
- [ ] Includes specific commands, configs, or code snippets
- [ ] All metrics have before/after/improvement values
- [ ] All metrics have transcript quotes (no fabrication)
- [ ] Technical terminology used correctly
- [ ] Tone is technical and instructional (not marketing)
- [ ] Company name is consistent throughout
- [ ] No placeholder text like [COMPANY] or [PROJECT]

Metadata:
- [ ] Title is descriptive and under 100 characters
- [ ] Subtitle is clear and under 150 characters
- [ ] TAB metadata includes project maturity, architectural significance, primary patterns
- [ ] Publication date is in ISO format (YYYY-MM-DD)
- [ ] Word count calculated correctly
- [ ] Estimated read time calculated (word_count / 200)

CNCF Project List:
- [ ] All projects from content are listed
- [ ] Each project has name, category, usage_summary
- [ ] Projects ordered by importance

Key Metrics Summary:
- [ ] Top 5-7 metrics included
- [ ] Each metric has consistent format
- [ ] Business impact statements are clear

If any validation fails:
- Fix the issue immediately
- Re-validate before proceeding
- Do NOT output incomplete or invalid JSON
```

---

## Common Mistakes to Avoid

### 1. Fabricating Technical Details

**❌ Wrong:**
```
"The team deployed Kubernetes v1.28 with custom CNI plugins..."
```
(If transcript doesn't mention v1.28 or custom CNI)

**✅ Correct:**
```
"The team deployed Kubernetes for container orchestration across multiple regions..."
```
(Only state what's in the transcript)

### 2. Using Marketing Language

**❌ Wrong:**
```
"The revolutionary cloud native platform transformed the business, leveraging cutting-edge technologies to achieve unprecedented scalability..."
```

**✅ Correct:**
```
"The Kubernetes-based architecture improved API latency by 10x (500ms to 50ms) and supported 200% user growth without proportional infrastructure cost increases."
```

### 3. Generic Implementation Details

**❌ Wrong:**
```
"The team implemented microservices and deployed them to Kubernetes clusters."
```

**✅ Correct:**
```
"The team deployed 200+ microservices organized into 12 bounded contexts to three EKS clusters (us-east-1, us-west-2, eu-west-1) using eksctl with m5.2xlarge nodes and Calico CNI for network policies."
```

### 4. Missing Technical Specificity

**❌ Wrong:**
```
"Services communicate with each other through the service mesh."
```

**✅ Correct:**
```
"Services communicate via HTTP/2 and gRPC through Istio v1.18 service mesh, with Envoy sidecar proxies automatically injected into all pods using the istio-injection=enabled namespace label. Mutual TLS is enforced for all service-to-service communication."
```

### 5. Copying from Other Reference Architectures

**❌ Wrong:**
```
[Copying sections from another Kubernetes reference architecture]
```

**✅ Correct:**
```
[Generate unique content based on THIS company's deep_analysis and transcript]
```

### 6. Inconsistent Company Names

**❌ Wrong:**
```
Paragraph 1: "Example Corp deployed..."
Paragraph 2: "The company deployed..."
Paragraph 3: "They deployed..."
```

**✅ Correct:**
```
Paragraph 1: "Example Corp deployed..."
Paragraph 2: "Example Corp deployed..."
Paragraph 3: "Example Corp deployed..."
```
(Consistent company name usage throughout)

### 7. Wrong Word Count Ranges

**❌ Wrong:**
```
Executive Summary: 500 words (should be 200-300)
Background: 150 words (should be 300-400)
```

**✅ Correct:**
```
Executive Summary: 250 words ✓
Background: 350 words ✓
```

### 8. Missing Transcript Quotes for Metrics

**❌ Wrong:**
```json
{
  "metric": "API Latency (p95)",
  "improvement": "500ms → 50ms (10x improvement)",
  "business_impact": "Improved user experience"
  // Missing transcript_quote!
}
```

**✅ Correct:**
```json
{
  "metric": "API Latency (p95)",
  "improvement": "500ms → 50ms (10x improvement)",
  "business_impact": "Reduced cart abandonment by 15%",
  "transcript_quote": "We reduced our p95 API latency from 500 milliseconds down to just 50 milliseconds"
}
```

---

## Quality Guidelines

### Technical Depth

Reference architectures must demonstrate implementation-level detail:

- ✅ Include specific version numbers (Kubernetes v1.26, Istio v1.18)
- ✅ Include actual commands (`kubectl apply`, `helm install`)
- ✅ Include configuration snippets (YAML, JSON)
- ✅ Explain architectural decisions with rationale
- ✅ Describe integration patterns between projects
- ✅ Include performance tuning details
- ✅ Describe operational practices

### Technical Accuracy

All technical details must be accurate and verifiable:

- ✅ Extract from deep_analysis and transcript ONLY
- ✅ Do NOT fabricate version numbers, metrics, or configurations
- ✅ If transcript doesn't mention specifics, stay high-level
- ✅ Verify CNCF project names are correct
- ✅ Use correct technical terminology

### Target Audience: Engineers

Write for technical readers, not business audiences:

- ✅ Use technical vocabulary (sidecars, ingress controllers, CRDs)
- ✅ Assume Kubernetes knowledge (no need to explain what a pod is)
- ✅ Focus on "how" not "why" (implementation over benefits)
- ✅ Include practical details engineers can use
- ✅ Avoid marketing language and buzzwords

### Completeness

All required sections and data:

- ✅ All 10 sections present
- ✅ Word counts within target ranges
- ✅ 5+ CNCF projects documented
- ✅ Integration patterns described
- ✅ Metrics have before/after/improvement/quote
- ✅ TAB metadata completed

---

## Example Output (Abbreviated)

```json
{
  "metadata": {
    "title": "Reference Architecture: E-commerce Platform on Kubernetes with Istio Service Mesh",
    "subtitle": "Multi-region, multi-cluster architecture for high-traffic e-commerce workloads",
    "company_name": "Example Corp",
    "industry": "E-commerce",
    "video_url": "https://youtube.com/watch?v=VIDEO_ID",
    "publication_date": "2026-02-09",
    "word_count": 3500,
    "estimated_read_time": "18 minutes",
    "tab_metadata": {
      "project_maturity": "graduated",
      "architectural_significance": "Demonstrates multi-cluster Kubernetes with service mesh at scale for e-commerce, processing 50K requests/second with sub-50ms latency",
      "primary_patterns": ["microservices", "service-mesh", "multi-cluster", "gitops"]
    }
  },
  "sections": {
    "executive_summary": "Example Corp, a leading e-commerce platform serving 10 million monthly users, needed to scale from 50 to 500 microservices while maintaining sub-100ms API latency. Their monolithic Rails application couldn't meet these requirements...",
    "background": "Example Corp is a global e-commerce platform founded in 2015, processing over $500M in annual transactions. The company serves customers in 30 countries through web and mobile applications...",
    ...
  },
  "cncf_project_list": [
    {
      "name": "Kubernetes",
      "category": "Orchestration & Management",
      "usage_summary": "Primary container orchestration platform across three production clusters"
    },
    ...
  ],
  "key_metrics_summary": [
    {
      "metric": "API Latency (p95)",
      "improvement": "500ms → 50ms (10x improvement)",
      "business_impact": "Reduced cart abandonment by 15%, added $5M annual revenue"
    },
    ...
  ]
}
```

---

## Testing Your Output

After generating the reference architecture, verify:

1. **Run validate-reference-architecture CLI tool:**
   ```bash
   python -m casestudypilot validate-reference-architecture reference_architecture.json
   ```
   - Should return exit code 0 (technical depth >= 0.70)
   - Or exit code 1 if score is 0.60-0.69 (acceptable but warn)
   - Should NOT return exit code 2 (score < 0.60 = failure)

2. **Manual quality check:**
   - Read through each section—does it flow logically?
   - Are technical details specific and accurate?
   - Are metrics supported by transcript quotes?
   - Is the tone technical and instructional (not marketing)?
   - Are all 10 sections present and within word count ranges?

3. **CNCF project validation:**
   - Are all project names correct?
   - Are categories accurate?
   - Is usage detailed and specific?

4. **Consistency check:**
   - Is company name consistent throughout?
   - Are CNCF project names spelled consistently?
   - Are version numbers consistent (if mentioned multiple times)?

---

## Version History

- **v1.0.0** (2026-02-09) - Initial skill specification
