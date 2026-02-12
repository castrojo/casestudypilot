# Skill: architecture-diagram-specification

**Version:** 1.0.0  
**Purpose:** Generate textual specifications for architecture diagrams that can be used to create visual diagrams or guide screenshot extraction. Focuses on component diagrams, data flow diagrams, and deployment diagrams.

**Note:** This skill generates **textual descriptions** of diagrams, not actual diagram code (Mermaid/PlantUML). Future versions may include diagram code generation.

---

## Input Format

```json
{
  "deep_analysis": {
    "cncf_projects": [...],
    "architecture_components": {...},
    "integration_patterns": [...],
    "company_name": "Company Name"
  },
  "diagram_types": ["component", "data-flow", "deployment"]
}
```

**Input Requirements:**
- `deep_analysis`: Output from `transcript-deep-analysis` skill
- `diagram_types`: List of diagram types to generate (1-3 types)
  - **component**: Shows architectural components and their relationships
  - **data-flow**: Shows how data flows through the system
  - **deployment**: Shows how components are deployed (clusters, regions, etc.)

---

## Output Format

```json
{
  "diagrams": [
    {
      "type": "component|data-flow|deployment",
      "title": "Diagram title",
      "description": "1-2 sentence overview of what this diagram shows",
      "components": [
        {
          "id": "unique-id",
          "label": "Component Name",
          "type": "service|database|message-queue|load-balancer|api-gateway|cluster|other",
          "layer": "infrastructure|platform|application",
          "cncf_projects": ["Kubernetes", "Istio"],
          "description": "What this component does"
        }
      ],
      "connections": [
        {
          "from_id": "component-1",
          "to_id": "component-2",
          "type": "http|grpc|tcp|async|data-flow|deployment",
          "label": "Connection description",
          "bidirectional": false,
          "protocol": "HTTP/2|gRPC|TCP|Kafka|etc.",
          "notes": "Additional details about this connection"
        }
      ],
      "annotations": [
        {
          "component_id": "component-1",
          "text": "Key callout or metric (e.g., 'Handles 10K req/sec')",
          "position": "top|bottom|left|right"
        }
      ],
      "layout_hints": {
        "orientation": "horizontal|vertical",
        "groupings": [
          {
            "group_name": "Frontend Services",
            "component_ids": ["api-gateway", "web-app"]
          }
        ]
      }
    }
  ]
}
```

**Output Requirements:**
- Minimum 2 diagrams (typically component + data-flow or component + deployment)
- Each diagram must have at least 4 components
- Each diagram must have at least 3 connections
- All component IDs must be unique within a diagram
- All connections must reference valid component IDs

---

## Execution Instructions

### FACT-GROUNDING RULE

Diagram specifications must only include components, connections, and annotations that are grounded in the deep analysis (which itself must be grounded in the transcript). Do NOT add:
- Components not described in the deep analysis
- Connections or protocols not discussed by the speakers
- Annotations with metrics or capacities not from the transcript
- Standard architecture components "that are typically used" but were not mentioned

If the deep analysis has limited component data, produce simpler diagrams rather than inventing components to make them look comprehensive.

### Step 1: Understand the Architecture from Deep Analysis

**Objective:** Comprehend the full architecture before creating diagram specifications.

1. Read the `architecture_components` from deep analysis
2. Review the `integration_patterns` to understand component interactions
3. Identify the primary architectural patterns:
   - **Microservices**: Many services communicating via APIs
   - **Service Mesh**: Services communicate through proxies
   - **Event-Driven**: Services communicate via message queues
   - **Multi-Cluster**: Multiple Kubernetes clusters
   - **Hybrid Cloud**: On-prem + cloud components
4. Determine which diagrams will best illustrate the architecture

**Decision Tree:**
- If architecture has many services → Create **component diagram** (required)
- If architecture shows data processing pipeline → Create **data-flow diagram**
- If architecture is multi-region/multi-cluster → Create **deployment diagram**

**Quality Check:**
- Can you describe the architecture in 2-3 sentences?
- Do you understand how components interact?
- Have you identified the key architectural patterns?

---

### Step 2: Generate Component Diagram Specification

**Objective:** Create a component diagram showing architectural components and their relationships.

**Component Diagram Purpose:**
- Shows the major components of the system
- Shows relationships between components
- Shows which CNCF projects are used where
- Organized by architectural layers (infrastructure, platform, application)

#### Step 2.1: Identify Components

**For Each Component:**
1. Extract from `architecture_components` in deep analysis
2. Assign unique ID (kebab-case: `api-gateway`, `postgres-db`, `istio-mesh`)
3. Assign human-readable label (title case: "API Gateway", "PostgreSQL Database")
4. Categorize type (service, database, message-queue, etc.)
5. Assign layer (infrastructure, platform, application)
6. List CNCF projects used in this component
7. Write 1-sentence description

**Component Types:**
- **service**: Microservice, API, application
- **database**: SQL, NoSQL, cache
- **message-queue**: Kafka, RabbitMQ, NATS
- **load-balancer**: Nginx, Envoy, cloud LB
- **api-gateway**: Kong, Envoy, custom gateway
- **cluster**: Kubernetes cluster
- **other**: Anything else

**Example:**
```json
{
  "id": "order-service",
  "label": "Order Service",
  "type": "service",
  "layer": "application",
  "cncf_projects": [],
  "description": "Processes customer orders and manages order lifecycle"
}
```

```json
{
  "id": "istio-service-mesh",
  "label": "Istio Service Mesh",
  "type": "service",
  "layer": "platform",
  "cncf_projects": ["Istio", "Envoy"],
  "description": "Manages service-to-service communication with mTLS, traffic routing, and observability"
}
```

**Quality Checks:**
- Are all major components from deep analysis included?
- Are IDs unique and descriptive?
- Are components organized by layer?
- Are CNCF projects correctly associated?

#### Step 2.2: Define Connections

**For Each Connection:**
1. Identify source component ID (`from_id`)
2. Identify destination component ID (`to_id`)
3. Determine connection type:
   - **http**: HTTP/REST API calls
   - **grpc**: gRPC calls
   - **tcp**: Raw TCP connections
   - **async**: Asynchronous messaging (Kafka, queues)
   - **data-flow**: Data pipeline connections
   - **deployment**: Deployment relationships
4. Write connection label (e.g., "Fetches product data", "Publishes order events")
5. Determine if bidirectional (request-response = false, pub-sub = true)
6. Specify protocol (HTTP/2, gRPC, TCP, Kafka, etc.)
7. Add notes if connection has special characteristics

**Connection Patterns:**

**API Call (Synchronous):**
```json
{
  "from_id": "frontend-service",
  "to_id": "api-gateway",
  "type": "http",
  "label": "REST API calls",
  "bidirectional": false,
  "protocol": "HTTP/2",
  "notes": "Rate limited to 1000 req/sec per client"
}
```

**Message Queue (Asynchronous):**
```json
{
  "from_id": "order-service",
  "to_id": "kafka-cluster",
  "type": "async",
  "label": "Publishes order.created events",
  "bidirectional": false,
  "protocol": "Kafka",
  "notes": "Events partitioned by customer_id"
}
```

**Service Mesh (Mediated):**
```json
{
  "from_id": "order-service",
  "to_id": "istio-service-mesh",
  "type": "http",
  "label": "All outbound traffic",
  "bidirectional": true,
  "protocol": "HTTP/2",
  "notes": "Envoy sidecar intercepts all traffic"
}
```

**Quality Checks:**
- Do all connections reference valid component IDs?
- Are connection types appropriate (http vs. async)?
- Are bidirectional flags correct?
- Do connections match integration patterns from deep analysis?
- **Sourcing:** Only include protocols, data volumes, and rate limits that appear in the deep analysis. If the speakers did not describe a protocol for a connection, use a generic label like "communicates with" rather than inventing "gRPC" or "HTTP/2."

#### Step 2.3: Add Annotations

**Annotations Purpose:**
- Highlight key metrics (throughput, latency, scale)
- Call out important architectural decisions
- Note CNCF project usage

**For Each Annotation:**
1. Select component to annotate
2. Write concise text (max 10 words)
3. Choose position (top, bottom, left, right)

**Examples:**
```json
{
  "component_id": "api-gateway",
  "text": "Handles 100K req/sec peak",
  "position": "top"
}
```

```json
{
  "component_id": "istio-service-mesh",
  "text": "mTLS + circuit breaking",
  "position": "right"
}
```

**Quality Checks:**
- Are annotations concise and informative?
- Do annotations add value (not redundant with component description)?
- Are annotations positioned to avoid overlap?
- **Sourcing:** Only include metrics and capacities that appear in the deep analysis with transcript quotes. Do NOT invent throughput numbers, storage sizes, or request rates.

#### Step 2.4: Provide Layout Hints

**Layout Hints Purpose:**
- Suggest how diagram should be visually organized
- Group related components
- Suggest orientation (horizontal vs. vertical flow)

**Orientation:**
- **horizontal**: Left-to-right flow (typical for web request flow)
- **vertical**: Top-to-bottom flow (typical for layered architecture)

**Groupings:**
- Group components by function (frontend, backend, data)
- Group components by layer (infrastructure, platform, application)
- Group components by deployment location (cluster-1, cluster-2)

**Example:**
```json
{
  "orientation": "horizontal",
  "groupings": [
    {
      "group_name": "Frontend Services",
      "component_ids": ["web-app", "mobile-api", "api-gateway"]
    },
    {
      "group_name": "Backend Services",
      "component_ids": ["order-service", "inventory-service", "payment-service"]
    },
    {
      "group_name": "Data Layer",
      "component_ids": ["postgres-db", "redis-cache", "kafka-cluster"]
    }
  ]
}
```

**Quality Checks:**
- Does orientation match typical flow (requests, data, etc.)?
- Are groupings logical and non-overlapping?
- Do all component IDs in groupings exist?

#### Step 2.5: Assemble Component Diagram

**Combine all pieces:**
```json
{
  "type": "component",
  "title": "Microservices Architecture with Service Mesh",
  "description": "Shows 50+ microservices communicating through Istio service mesh with centralized observability",
  "components": [...],
  "connections": [...],
  "annotations": [...],
  "layout_hints": {...}
}
```

**Quality Checks:**
- Title is descriptive and specific
- Description summarizes what the diagram shows
- All required fields present
- At least 4 components, 3 connections

---

### Step 3: Generate Data Flow Diagram Specification (Optional)

**Objective:** Create a data flow diagram showing how data moves through the system.

**When to Create Data Flow Diagram:**
- Architecture processes data pipelines (ETL, streaming)
- Data flows through multiple stages (ingestion → processing → storage → visualization)
- Important to show data transformations

**Data Flow Diagram Purpose:**
- Shows how data enters the system
- Shows data transformations and processing stages
- Shows data storage and export
- Emphasizes data path, not service architecture

#### Step 3.1: Identify Data Sources

**Data Sources:**
- External APIs
- User input (web, mobile)
- IoT sensors
- File uploads
- Database replication
- Message queues

**For Each Data Source:**
```json
{
  "id": "customer-web-app",
  "label": "Customer Web App",
  "type": "service",
  "layer": "application",
  "cncf_projects": [],
  "description": "Source of customer order data"
}
```

#### Step 3.2: Identify Data Processing Stages

**Processing Stages:**
- Data ingestion (API endpoints, message consumers)
- Data validation and enrichment
- Data transformation (ETL)
- Data aggregation (analytics)
- Data storage (databases, data lakes)

**For Each Processing Stage:**
```json
{
  "id": "order-processor",
  "label": "Order Processing Pipeline",
  "type": "service",
  "layer": "application",
  "cncf_projects": [],
  "description": "Validates, enriches, and transforms order data"
}
```

#### Step 3.3: Identify Data Sinks

**Data Sinks:**
- Databases (PostgreSQL, MongoDB, etc.)
- Data lakes (S3, GCS)
- Analytics systems (data warehouses)
- Monitoring systems (Prometheus, Grafana)
- External APIs (partners, webhooks)

**For Each Data Sink:**
```json
{
  "id": "orders-database",
  "label": "Orders Database (PostgreSQL)",
  "type": "database",
  "layer": "platform",
  "cncf_projects": [],
  "description": "Persistent storage for order data"
}
```

#### Step 3.4: Define Data Flow Connections

**Data Flow Connections:**
- Use `type: "data-flow"` for all connections
- Label should describe what data is flowing
- Add notes about data format, volume, frequency

**Example:**
```json
{
  "from_id": "customer-web-app",
  "to_id": "api-gateway",
  "type": "data-flow",
  "label": "Order submission (JSON)",
  "bidirectional": false,
  "protocol": "HTTP/2",
  "notes": "10K orders/hour peak, ~5KB per order"
}
```

```json
{
  "from_id": "order-processor",
  "to_id": "orders-database",
  "type": "data-flow",
  "label": "Validated order data",
  "bidirectional": false,
  "protocol": "PostgreSQL",
  "notes": "Batch inserts every 5 seconds"
}
```

#### Step 3.5: Assemble Data Flow Diagram

```json
{
  "type": "data-flow",
  "title": "Order Processing Data Pipeline",
  "description": "Shows how customer orders flow from web app through validation and processing to persistent storage",
  "components": [...],
  "connections": [...],
  "annotations": [...],
  "layout_hints": {
    "orientation": "horizontal",
    "groupings": [...]
  }
}
```

**Quality Checks:**
- Does diagram show complete data path (source → processing → sink)?
- Are data volumes/frequencies annotated?
- Are data formats specified?
- Does diagram focus on data (not services)?

---

### Step 4: Generate Deployment Diagram Specification (Optional)

**Objective:** Create a deployment diagram showing how components are deployed across infrastructure.

**When to Create Deployment Diagram:**
- Multi-region deployment
- Multi-cluster deployment
- Hybrid cloud (on-prem + cloud)
- Complex deployment topology

**Deployment Diagram Purpose:**
- Shows physical/logical deployment topology
- Shows clusters, regions, availability zones
- Shows network boundaries and connectivity
- Emphasizes deployment strategy, not data flow

#### Step 4.1: Identify Deployment Targets

**Deployment Targets:**
- Cloud regions (us-east-1, eu-west-1)
- Kubernetes clusters (prod-us, prod-eu, staging)
- Availability zones (AZ-A, AZ-B, AZ-C)
- On-premises data centers
- Edge locations

**For Each Deployment Target:**
```json
{
  "id": "k8s-cluster-us-east",
  "label": "Production Cluster (US East)",
  "type": "cluster",
  "layer": "infrastructure",
  "cncf_projects": ["Kubernetes"],
  "description": "Primary production cluster handling 60% of traffic"
}
```

#### Step 4.2: Identify Deployed Components

**For Each Deployed Component:**
- Show component as deployed (e.g., "Order Service (10 replicas)")
- Indicate which deployment target it's on
- Show scaling characteristics

**Example:**
```json
{
  "id": "order-service-us-east",
  "label": "Order Service (10 replicas)",
  "type": "service",
  "layer": "application",
  "cncf_projects": [],
  "description": "Order processing service deployed in US East cluster"
}
```

#### Step 4.3: Define Deployment Connections

**Deployment Connections:**
- Use `type: "deployment"` for deployment relationships
- Show cross-cluster communication
- Show database replication
- Show traffic routing (DNS, load balancers)

**Example:**
```json
{
  "from_id": "k8s-cluster-us-east",
  "to_id": "order-service-us-east",
  "type": "deployment",
  "label": "Deploys to",
  "bidirectional": false,
  "protocol": "Kubernetes",
  "notes": "Managed by Argo CD"
}
```

```json
{
  "from_id": "order-service-us-east",
  "to_id": "order-service-eu-west",
  "type": "http",
  "label": "Cross-region replication",
  "bidirectional": true,
  "protocol": "gRPC",
  "notes": "Active-active replication with conflict resolution"
}
```

#### Step 4.4: Assemble Deployment Diagram

```json
{
  "type": "deployment",
  "title": "Multi-Region Kubernetes Deployment",
  "description": "Shows five production clusters across three regions with active-active replication",
  "components": [...],
  "connections": [...],
  "annotations": [...],
  "layout_hints": {
    "orientation": "horizontal",
    "groupings": [
      {
        "group_name": "US Region",
        "component_ids": ["k8s-cluster-us-east", "k8s-cluster-us-west"]
      },
      {
        "group_name": "EU Region",
        "component_ids": ["k8s-cluster-eu-west"]
      }
    ]
  }
}
```

**Quality Checks:**
- Does diagram show deployment topology clearly?
- Are clusters/regions identified?
- Are cross-cluster connections shown?
- Are scaling characteristics annotated?

---

### Step 5: Validate and Finalize

**Objective:** Ensure all diagram specifications are complete and consistent.

**Validation Checklist:**

1. **Structural Validation:**
   - [ ] At least 2 diagrams generated
   - [ ] Each diagram has at least 4 components
   - [ ] Each diagram has at least 3 connections
   - [ ] All component IDs are unique within their diagram
   - [ ] All connection IDs reference valid components

2. **Content Validation:**
   - [ ] Diagrams reflect architecture from deep analysis
   - [ ] CNCF projects correctly associated with components
   - [ ] Connection types are appropriate (http, async, etc.)
   - [ ] Annotations add value (metrics, decisions)

3. **Consistency Validation:**
   - [ ] Component names consistent with deep analysis
   - [ ] Integration patterns from deep analysis represented
   - [ ] Layers (infrastructure, platform, application) used consistently

4. **Completeness Validation:**
   - [ ] All major components from deep analysis included
   - [ ] All integration patterns from deep analysis represented
   - [ ] Diagrams tell complete architectural story

**Final Output:**
```json
{
  "diagrams": [
    {
      "type": "component",
      "title": "...",
      "description": "...",
      "components": [...],
      "connections": [...],
      "annotations": [...],
      "layout_hints": {...}
    },
    {
      "type": "data-flow",
      "title": "...",
      "description": "...",
      "components": [...],
      "connections": [...],
      "annotations": [...],
      "layout_hints": {...}
    }
  ]
}
```

---

## Quality Guidelines

### Diagram Clarity

1. **Component Naming:**
   - IDs: kebab-case, descriptive (`order-service`, not `svc1`)
   - Labels: title case, human-readable ("Order Service", not "orderSvc")
   - Avoid abbreviations unless industry-standard (API, DB, K8s)

2. **Connection Clarity:**
   - Labels describe what flows (data, requests, events)
   - Protocols specified for technical accuracy
   - Notes provide context (volume, frequency, special behavior)

3. **Annotation Clarity:**
   - Concise (max 10 words)
   - Quantitative when possible ("100K req/sec", not "high traffic")
   - Position to avoid overlap

4. **Layout Clarity:**
   - Orientation matches natural flow (left-to-right for requests)
   - Groupings logical and non-overlapping
   - Layers organized vertically (top = application, bottom = infrastructure)

### Technical Accuracy

1. **CNCF Projects:**
   - Only list projects actually used in the component
   - Don't invent project usage not in deep analysis
   - Use correct project names (Kubernetes, not K8s in formal names)

2. **Connection Types:**
   - `http`: Synchronous HTTP/REST API calls
   - `grpc`: Synchronous gRPC calls
   - `tcp`: Raw TCP connections (databases, caches)
   - `async`: Asynchronous messaging (Kafka, queues)
   - `data-flow`: Data pipeline connections
   - `deployment`: Deployment relationships

3. **Component Types:**
   - Use specific types (service, database, message-queue)
   - Avoid generic "other" unless truly necessary
   - Match types to actual component function

### Consistency with Deep Analysis

1. **Component Consistency:**
   - All components from `architecture_components` in deep analysis should appear
   - Component descriptions should match deep analysis
   - CNCF project associations should match deep analysis

2. **Pattern Consistency:**
   - Integration patterns from deep analysis should be visible in connections
   - If deep analysis mentions "service mesh", diagram should show mesh connections
   - If deep analysis mentions "multi-cluster", deployment diagram should show clusters

3. **Metric Consistency:**
   - Annotations should use metrics from deep analysis
   - Don't fabricate metrics not in deep analysis
   - Use exact values from deep analysis

---

## Examples

### Example 1: E-commerce Microservices Component Diagram

**Input:**
```json
{
  "deep_analysis": {
    "cncf_projects": [
      {"name": "Kubernetes", "category": "orchestration", ...},
      {"name": "Istio", "category": "service-mesh", ...},
      {"name": "Prometheus", "category": "observability", ...}
    ],
    "architecture_components": {
      "infrastructure_layer": [
        {"component": "AWS VPC", "description": "Network isolation", "cncf_projects": []}
      ],
      "platform_layer": [
        {"component": "Kubernetes", "description": "Container orchestration", "cncf_projects": ["Kubernetes"]},
        {"component": "Istio Service Mesh", "description": "Traffic management", "cncf_projects": ["Istio", "Envoy"]}
      ],
      "application_layer": [
        {"component": "Order Service", "description": "Order processing", "cncf_projects": []},
        {"component": "Inventory Service", "description": "Inventory management", "cncf_projects": []}
      ]
    },
    "integration_patterns": [
      {"pattern_name": "Service Mesh Integration", "projects_involved": ["Istio", "Envoy"], ...}
    ],
    "company_name": "ShopFlow"
  },
  "diagram_types": ["component"]
}
```

**Output:**
```json
{
  "diagrams": [
    {
      "type": "component",
      "title": "ShopFlow Microservices Architecture with Service Mesh",
      "description": "Shows core microservices communicating through Istio service mesh with centralized observability",
      "components": [
        {
          "id": "api-gateway",
          "label": "API Gateway",
          "type": "api-gateway",
          "layer": "application",
          "cncf_projects": ["Envoy"],
          "description": "Entry point for all customer traffic with rate limiting and authentication"
        },
        {
          "id": "order-service",
          "label": "Order Service",
          "type": "service",
          "layer": "application",
          "cncf_projects": [],
          "description": "Processes customer orders and manages order lifecycle"
        },
        {
          "id": "inventory-service",
          "label": "Inventory Service",
          "type": "service",
          "layer": "application",
          "cncf_projects": [],
          "description": "Manages product inventory and availability"
        },
        {
          "id": "payment-service",
          "label": "Payment Service",
          "type": "service",
          "layer": "application",
          "cncf_projects": [],
          "description": "Handles payment processing with third-party integrations"
        },
        {
          "id": "istio-mesh",
          "label": "Istio Service Mesh",
          "type": "service",
          "layer": "platform",
          "cncf_projects": ["Istio", "Envoy"],
          "description": "Manages all service-to-service communication with mTLS, circuit breaking, and traffic routing"
        },
        {
          "id": "prometheus",
          "label": "Prometheus",
          "type": "service",
          "layer": "platform",
          "cncf_projects": ["Prometheus"],
          "description": "Collects and stores metrics from all services and mesh"
        },
        {
          "id": "postgres-db",
          "label": "PostgreSQL Database",
          "type": "database",
          "layer": "platform",
          "cncf_projects": [],
          "description": "Primary relational database for order and inventory data"
        },
        {
          "id": "k8s-cluster",
          "label": "Kubernetes Cluster",
          "type": "cluster",
          "layer": "infrastructure",
          "cncf_projects": ["Kubernetes"],
          "description": "Container orchestration platform running all services"
        }
      ],
      "connections": [
        {
          "from_id": "api-gateway",
          "to_id": "istio-mesh",
          "type": "http",
          "label": "Routes incoming requests",
          "bidirectional": false,
          "protocol": "HTTP/2",
          "notes": "API gateway is first entry point into mesh"
        },
        {
          "from_id": "istio-mesh",
          "to_id": "order-service",
          "type": "http",
          "label": "Forwards order requests",
          "bidirectional": true,
          "protocol": "HTTP/2",
          "notes": "Mesh handles mTLS, retries, circuit breaking"
        },
        {
          "from_id": "order-service",
          "to_id": "istio-mesh",
          "type": "http",
          "label": "Checks inventory",
          "bidirectional": false,
          "protocol": "HTTP/2",
          "notes": "All outbound traffic goes through mesh"
        },
        {
          "from_id": "istio-mesh",
          "to_id": "inventory-service",
          "type": "http",
          "label": "Inventory query",
          "bidirectional": true,
          "protocol": "HTTP/2",
          "notes": "Circuit breaker opens after 5 consecutive failures"
        },
        {
          "from_id": "order-service",
          "to_id": "postgres-db",
          "type": "tcp",
          "label": "Stores order data",
          "bidirectional": false,
          "protocol": "PostgreSQL",
          "notes": "Connection pooling with max 100 connections"
        },
        {
          "from_id": "istio-mesh",
          "to_id": "prometheus",
          "type": "http",
          "label": "Mesh metrics",
          "bidirectional": false,
          "protocol": "HTTP",
          "notes": "Scraped every 15 seconds"
        },
        {
          "from_id": "order-service",
          "to_id": "prometheus",
          "type": "http",
          "label": "Application metrics",
          "bidirectional": false,
          "protocol": "HTTP",
          "notes": "Custom business metrics (orders/sec, revenue)"
        },
        {
          "from_id": "k8s-cluster",
          "to_id": "istio-mesh",
          "type": "deployment",
          "label": "Runs control plane",
          "bidirectional": false,
          "protocol": "Kubernetes",
          "notes": "Istio control plane runs as K8s deployment"
        }
      ],
      "annotations": [
        {
          "component_id": "api-gateway",
          "text": "100K req/sec peak",
          "position": "top"
        },
        {
          "component_id": "istio-mesh",
          "text": "mTLS + circuit breaking",
          "position": "right"
        },
        {
          "component_id": "order-service",
          "text": "50 replicas, HPA enabled",
          "position": "bottom"
        },
        {
          "component_id": "postgres-db",
          "text": "5TB data, multi-AZ",
          "position": "bottom"
        }
      ],
      "layout_hints": {
        "orientation": "horizontal",
        "groupings": [
          {
            "group_name": "Application Services",
            "component_ids": ["api-gateway", "order-service", "inventory-service", "payment-service"]
          },
          {
            "group_name": "Platform Services",
            "component_ids": ["istio-mesh", "prometheus", "postgres-db"]
          },
          {
            "group_name": "Infrastructure",
            "component_ids": ["k8s-cluster"]
          }
        ]
      }
    }
  ]
}
```

---

### Example 2: Data Pipeline Data Flow Diagram

**Input:**
```json
{
  "deep_analysis": {
    "cncf_projects": [
      {"name": "Kafka", "category": "streaming", ...},
      {"name": "Kubernetes", "category": "orchestration", ...}
    ],
    "architecture_components": {
      "application_layer": [
        {"component": "Event Ingestion API", "description": "Receives events", "cncf_projects": []},
        {"component": "Stream Processor", "description": "Processes events", "cncf_projects": []}
      ]
    },
    "company_name": "DataCorp"
  },
  "diagram_types": ["data-flow"]
}
```

**Output:**
```json
{
  "diagrams": [
    {
      "type": "data-flow",
      "title": "Real-Time Event Processing Pipeline",
      "description": "Shows how customer events flow from ingestion through processing to analytics and storage",
      "components": [
        {
          "id": "mobile-app",
          "label": "Mobile App",
          "type": "service",
          "layer": "application",
          "cncf_projects": [],
          "description": "Source of customer behavior events"
        },
        {
          "id": "ingestion-api",
          "label": "Event Ingestion API",
          "type": "service",
          "layer": "application",
          "cncf_projects": [],
          "description": "REST API for event submission with validation"
        },
        {
          "id": "kafka-raw",
          "label": "Kafka (Raw Events Topic)",
          "type": "message-queue",
          "layer": "platform",
          "cncf_projects": ["Kafka"],
          "description": "Durably stores raw events before processing"
        },
        {
          "id": "stream-processor",
          "label": "Stream Processor",
          "type": "service",
          "layer": "application",
          "cncf_projects": [],
          "description": "Validates, enriches, and aggregates events in real-time"
        },
        {
          "id": "kafka-processed",
          "label": "Kafka (Processed Events Topic)",
          "type": "message-queue",
          "layer": "platform",
          "cncf_projects": ["Kafka"],
          "description": "Stores processed events for downstream consumers"
        },
        {
          "id": "analytics-db",
          "label": "Analytics Database (ClickHouse)",
          "type": "database",
          "layer": "platform",
          "cncf_projects": [],
          "description": "Columnar database for fast analytical queries"
        },
        {
          "id": "s3-data-lake",
          "label": "S3 Data Lake",
          "type": "database",
          "layer": "platform",
          "cncf_projects": [],
          "description": "Long-term storage for all events (7 years retention)"
        }
      ],
      "connections": [
        {
          "from_id": "mobile-app",
          "to_id": "ingestion-api",
          "type": "data-flow",
          "label": "Customer events (JSON)",
          "bidirectional": false,
          "protocol": "HTTP/2",
          "notes": "50K events/sec peak, ~2KB per event, batched in 100-event chunks"
        },
        {
          "from_id": "ingestion-api",
          "to_id": "kafka-raw",
          "type": "data-flow",
          "label": "Raw events",
          "bidirectional": false,
          "protocol": "Kafka",
          "notes": "Async write with 3x replication, partitioned by user_id"
        },
        {
          "from_id": "kafka-raw",
          "to_id": "stream-processor",
          "type": "data-flow",
          "label": "Consumes raw events",
          "bidirectional": false,
          "protocol": "Kafka",
          "notes": "Consumer group with 20 parallel consumers"
        },
        {
          "from_id": "stream-processor",
          "to_id": "kafka-processed",
          "type": "data-flow",
          "label": "Enriched and aggregated events",
          "bidirectional": false,
          "protocol": "Kafka",
          "notes": "Added user metadata, sessionization, 5-min tumbling windows"
        },
        {
          "from_id": "kafka-processed",
          "to_id": "analytics-db",
          "type": "data-flow",
          "label": "Batch inserts every 10 seconds",
          "bidirectional": false,
          "protocol": "ClickHouse",
          "notes": "Micro-batches of 10K events, 90-day retention"
        },
        {
          "from_id": "kafka-processed",
          "to_id": "s3-data-lake",
          "type": "data-flow",
          "label": "Continuous archival (Parquet)",
          "bidirectional": false,
          "protocol": "S3",
          "notes": "Hourly Parquet files, partitioned by date, compressed with Snappy"
        }
      ],
      "annotations": [
        {
          "component_id": "kafka-raw",
          "text": "3-day retention",
          "position": "top"
        },
        {
          "component_id": "stream-processor",
          "text": "99.9% processing latency < 100ms",
          "position": "right"
        },
        {
          "component_id": "analytics-db",
          "text": "10B events, p99 query < 500ms",
          "position": "bottom"
        },
        {
          "component_id": "s3-data-lake",
          "text": "500TB total, 7-year retention",
          "position": "bottom"
        }
      ],
      "layout_hints": {
        "orientation": "horizontal",
        "groupings": [
          {
            "group_name": "Ingestion",
            "component_ids": ["mobile-app", "ingestion-api", "kafka-raw"]
          },
          {
            "group_name": "Processing",
            "component_ids": ["stream-processor", "kafka-processed"]
          },
          {
            "group_name": "Storage",
            "component_ids": ["analytics-db", "s3-data-lake"]
          }
        ]
      }
    }
  ]
}
```

---

## Common Mistakes to Avoid

### Mistake 1: Insufficient Components

**Wrong:**
```json
{
  "components": [
    {"id": "frontend", "label": "Frontend", "type": "service", "layer": "application", "cncf_projects": [], "description": "UI"},
    {"id": "backend", "label": "Backend", "type": "service", "layer": "application", "cncf_projects": [], "description": "API"},
    {"id": "database", "label": "Database", "type": "database", "layer": "platform", "cncf_projects": [], "description": "DB"}
  ]
}
```

**Why Wrong:**
- Only 3 components (need minimum 4)
- Too generic ("Frontend", "Backend")
- No CNCF projects shown
- Doesn't reflect architecture from deep analysis

**Fix:**
- Add more specific components (Order Service, Inventory Service, etc.)
- Include platform components (Kubernetes, Istio, Prometheus)
- Associate CNCF projects with components

---

### Mistake 2: Invalid Connection References

**Wrong:**
```json
{
  "connections": [
    {
      "from_id": "order-service",
      "to_id": "payment-api",  // Component "payment-api" doesn't exist
      "type": "http",
      "label": "Process payment",
      "bidirectional": false,
      "protocol": "HTTP",
      "notes": ""
    }
  ]
}
```

**Why Wrong:**
- Connection references non-existent component ID
- Will cause validation error

**Fix:**
- Ensure all connection IDs reference components defined in `components` array
- Double-check spelling of component IDs

---

### Mistake 3: Missing Connection Details

**Wrong:**
```json
{
  "from_id": "order-service",
  "to_id": "inventory-service",
  "type": "http",
  "label": "API call",  // Too vague
  "bidirectional": false,
  "protocol": "",  // Missing protocol
  "notes": ""  // No additional details
}
```

**Why Wrong:**
- Vague label ("API call" doesn't describe what flows)
- Missing protocol
- No notes about volume, frequency, or special behavior

**Fix:**
```json
{
  "from_id": "order-service",
  "to_id": "inventory-service",
  "type": "http",
  "label": "Checks product availability",
  "bidirectional": false,
  "protocol": "HTTP/2",
  "notes": "Synchronous call with 500ms timeout, circuit breaker opens after 5 failures"
}
```

---

### Mistake 4: Inconsistent with Deep Analysis

**Wrong (if deep analysis mentions Istio service mesh):**
```json
{
  "connections": [
    {
      "from_id": "order-service",
      "to_id": "inventory-service",  // Direct connection
      "type": "http",
      "label": "API call",
      "bidirectional": false,
      "protocol": "HTTP",
      "notes": ""
    }
  ]
}
```

**Why Wrong:**
- Deep analysis mentions Istio service mesh
- Diagram shows direct service-to-service communication
- Doesn't reflect actual architecture

**Fix:**
- Add Istio mesh component
- Show services connecting through mesh
- Match integration patterns from deep analysis

---

## Success Criteria

Your output is successful if:

1. ✅ Contains at least 2 diagrams (typically component + data-flow or component + deployment)
2. ✅ Each diagram has at least 4 components
3. ✅ Each diagram has at least 3 connections
4. ✅ All component IDs are unique within their diagram
5. ✅ All connection IDs reference valid components
6. ✅ CNCF projects correctly associated with components
7. ✅ Diagrams reflect architecture from deep analysis
8. ✅ Layout hints provide clear organization guidance
9. ✅ Annotations add value with metrics or key decisions
10. ✅ Diagram specifications are complete and usable

---

**Version History:**
- 1.0.0 (2026-02-09): Initial skill definition for diagram specification generation

**Related Skills:**
- `transcript-deep-analysis`: Provides input (architecture components, CNCF projects)
- `reference-architecture-generation`: Uses diagram specifications as context

**Related CLI Tools:**
- None (this skill has no dedicated validation tool; validation occurs in reference-architecture-generation context)

**Future Enhancements:**
- Generate Mermaid diagram code from specifications
- Generate PlantUML diagram code from specifications
- Support for sequence diagrams (showing request flows over time)
- Support for state diagrams (showing component state transitions)
