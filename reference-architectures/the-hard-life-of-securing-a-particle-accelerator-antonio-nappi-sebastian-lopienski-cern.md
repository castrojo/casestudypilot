# [CERN](https://home.cern) Reference Architecture

> **Source:** [The Hard Life of Securing a Particle Accelerator - Antonio Nappi & Sebastian Lopienski, CERN](https://www.youtube.com/watch?v=rqDrrTKzNd8)  
> **Duration:** 38:53  
> **Speakers:** Antonio Nappi & Sebastian Lopienski

---

## Executive Summary

[CERN](https://home.cern), the world's leading particle physics laboratory operating the Large Hadron Collider, needed to modernize its mission-critical single sign-on (SSO) infrastructure supporting 200,000 users and 10,000 logins per hour. The legacy VM-based architecture suffered from 15-minute failover times and tightly coupled components that made operational tasks complex and time-consuming.

The team implemented a [cloud-native](https://glossary.cncf.io/cloud-native-tech/) architecture running **[Keycloak](https://www.keycloak.org)** on **[Kubernetes](https://kubernetes.io)** across multiple availability zones. **[Argo CD](https://argoproj.github.io/cd/)** provides GitOps automation while **[Prometheus](https://prometheus.io)** and **[Fluent Bit](https://fluentbit.io)** handle observability. The critical innovation was separating stateless Keycloak pods from the Infinispan cache layer.

The new architecture delivered dramatic improvements: load balancer failover time dropped from 15 minutes to near-zero, infrastructure efficiency improved 4x, and pod restart times decreased to 30-40 seconds. The architecture proved its resilience when pods restarted continuously for three days due to configuration issues with no user complaints.

This reference architecture demonstrates how to operate identity management at scale in [Kubernetes](https://kubernetes.io) with stateless application design and GitOps automation. The separation of concerns enables independent scaling and simplified operations for mission-critical services.

---

## Background

[CERN](https://home.cern) (European Organization for Nuclear Research) is the world's leading particle physics research laboratory near Geneva, Switzerland. The organization operates the Large Hadron Collider (LHC) and brings together over 15,000 scientists from around the world. CERN is historically significant in computing as the birthplace of the World Wide Web in 1989.

Prior to 2023, [CERN](https://home.cern)'s SSO service ran on virtual machines managed by Puppet configuration management. **[Keycloak](https://www.keycloak.org)** and Infinispan cache ran together in the same Java process on each VM. The infrastructure exhibited several critical limitations that threatened service reliability.

The legacy architecture had several pain points:

- HAProxy load balancer ran in active-passive mode with 15-minute failover times during failures
- Tightly coupled Keycloak and Infinispan made troubleshooting difficult (couldn't isolate which component caused issues)
- SPI upgrades required complex coordination to avoid session loss across cache nodes
- The infrastructure depended on a single Puppet module maintainer for configuration updates
- Manual operations consumed significant team time that could be spent on feature development

[CERN](https://home.cern)'s SSO service is uniquely mission-critical. It supports not just daily administrative and engineering work but also real-time particle accelerator operations and experimental data collection. When physicists monitor particle collisions, any SSO outage directly impacts billion-dollar scientific experiments.

After evaluating options, the team chose **[Kubernetes](https://kubernetes.io)** for its flexibility and CNCF project ecosystem. Management required quantitative proof that Kubernetes would improve performance. The team conducted load testing showing 4x efficiency improvements, securing approval for the migration.

---

## Technical Challenge

By late 2022, [CERN](https://home.cern)'s SSO infrastructure accumulated significant technical debt threatening reliability. The Puppet-managed VM architecture exhibited critical problems demanding immediate attention.

The most visible issue was poor load balancer failover performance:

- HAProxy active-passive configuration required 15 minutes to switch between nodes
- For a service supporting real-time experimental data collection, 15-minute outages were unacceptable
- The load balancer lacked automatic failover mechanisms
- Users experienced authentication errors during the switchover period

Operational complexity consumed excessive engineering resources:

- Keycloak and Infinispan ran in the same Java process, making it impossible to isolate performance problems
- SPI upgrades required carefully orchestrated procedures: stop first node, wait for cache replication, verify replication, proceed to next node
- This process consumed hours of team time and carried high risk of session loss if executed incorrectly
- The team spent more time maintaining infrastructure than improving the SSO service
- Troubleshooting required analyzing a shared Java process rather than independent components

Scalability and resource utilization presented additional challenges:

- The monolithic deployment on VMs couldn't scale Keycloak independently from cache
- Resource utilization (CPU and memory) couldn't be analyzed per component
- VM-based infrastructure lacked the flexibility to scale quickly during load spikes
- Load testing infrastructure was difficult without risking production stability

These challenges stemmed from fundamental architectural constraints of the VM-based design. The tightly coupled components prevented independent scaling, deployment, and failure isolation. Moving to a [microservices](https://glossary.cncf.io/microservices-architecture/) architecture on **[Kubernetes](https://kubernetes.io)** with separated Keycloak and Infinispan layers would address all these limitations.

---

## Architecture Overview

[CERN](https://home.cern) adopted a stateless application architecture running on **[Kubernetes](https://kubernetes.io)** across multiple availability zones. The design prioritizes reliability, operational simplicity, and independent component scaling.

The infrastructure layer consists of multiple Kubernetes clusters following the cattle service model:

- Multiple **[Kubernetes](https://kubernetes.io)** clusters deployed across different availability zones for high availability
- Three-node floating IP load balancer cluster with automatic failover replacing legacy HAProxy
- Infinispan cache cluster running on VMs with **[Podman](https://podman.io)** containers, managed by Puppet
- DNS-based service discovery for cache node addressing
- Each cluster is disposable and replaceable (cattle model rather than pets)

The platform layer provides GitOps automation and observability:

- **[Argo CD](https://argoproj.github.io/cd/)** for GitOps-based declarative deployments from Git repositories
- **[Prometheus](https://prometheus.io)** for metrics collection monitoring Keycloak performance and resource utilization
- **[Fluent Bit](https://fluentbit.io)** for log aggregation with custom parsing rules replacing legacy Flume
- Keycloak operator managing deployment lifecycle via Kubernetes custom resources (CRDs)
- Git repositories as single source of truth for all infrastructure configuration

The application layer consists of stateless Keycloak instances:

- **[Keycloak](https://www.keycloak.org)** pods running on Quarkus framework with operator-based deployment
- 200,000 users, 10,000 OIDC clients, handling 10,000 logins per hour peak load
- Custom SPIs for CERN authorization service integration and custom themes
- Stateless design allows scaling from zero to any number of replicas
- Remote cache configuration via Kubernetes ConfigMap and volume mounts
- Separation from Infinispan enables independent restart in 30-40 seconds without session loss




![Figure 1: Architecture Component](images/the-hard-life-of-securing-a-particle-accelerator-antonio-nappi-sebastian-lopienski/screenshot-1.jpg)
*Figure 1: Architecture Component*



![Figure 2: Architecture Component](images/the-hard-life-of-securing-a-particle-accelerator-antonio-nappi-sebastian-lopienski/screenshot-2.jpg)
*Figure 2: Architecture Component*



![Figure 3: Architecture Component](images/the-hard-life-of-securing-a-particle-accelerator-antonio-nappi-sebastian-lopienski/screenshot-3.jpg)
*Figure 3: Architecture Component*



![Figure 4: Architecture Component](images/the-hard-life-of-securing-a-particle-accelerator-antonio-nappi-sebastian-lopienski/screenshot-4.jpg)
*Figure 4: Architecture Component*



![Figure 5: Architecture Component](images/the-hard-life-of-securing-a-particle-accelerator-antonio-nappi-sebastian-lopienski/screenshot-5.jpg)
*Figure 5: Architecture Component*



![Figure 6: Architecture Component](images/the-hard-life-of-securing-a-particle-accelerator-antonio-nappi-sebastian-lopienski/screenshot-6.jpg)
*Figure 6: Architecture Component*




---

## Architecture Diagrams

This reference architecture includes three diagrams illustrating different aspects of the system. The component diagram shows the complete architecture with all CNCF projects. The data flow diagram reveals the authentication request path and caching behavior.

Diagram 1: Component Architecture

This component diagram shows how [CERN](https://home.cern) organized their multi-cluster **[Kubernetes](https://kubernetes.io)** deployment with separated application and caching layers. The diagram illustrates the three architectural layers: infrastructure (multiple clusters, load balancer, cache), platform (**[Argo CD](https://argoproj.github.io/cd/)**, operators, observability), and application (**[Keycloak](https://www.keycloak.org)** SSO). Key relationships include **[Argo CD](https://argoproj.github.io/cd/)** synchronizing from Git to multiple clusters, Keycloak pods connecting to remote Infinispan cache via DNS, and observability stack collecting metrics and logs.

![Component architecture diagram showing multi-cluster Kubernetes with separated Keycloak and Infinispan layers](images/the-hard-life-of-securing-a-particle-accelerator-antonio-nappi-sebastian-lopienski-cern/screenshot-2.jpg)
*Architecture overview presented at 16:00 showing the separated Keycloak and Infinispan design with GitOps automation*

The component diagram reveals the critical separation between stateless Keycloak and stateful Infinispan. This separation enables independent scaling and operational simplicity.

Diagram 2: Authentication Data Flow

This data flow diagram traces an authentication request from user browser through the floating IP load balancer to stateless Keycloak pods across availability zones. The diagram shows how Keycloak pods check the shared Infinispan cache for existing sessions and validate credentials against the CERN authorization service. The flow illustrates the stateless pod design—any pod can handle any request because session state lives in the shared cache.

![Data flow diagram showing authentication request path through load balancer to Keycloak pods with cache lookup](images/the-hard-life-of-securing-a-particle-accelerator-antonio-nappi-sebastian-lopienski-cern/screenshot-3.jpg)
*Load testing results presented at 19:00 demonstrating 4x performance improvement with Kubernetes infrastructure*

Diagram 3: Multi-Cluster Deployment

This deployment diagram shows **[Kubernetes](https://kubernetes.io)** clusters deployed across three availability zones with **[Argo CD](https://argoproj.github.io/cd/)** managing deployments from Git. Each cluster runs identical Keycloak operator configurations synchronized from a single Git repository. All clusters connect to the shared Infinispan cache cluster running on VMs, demonstrating the hybrid infrastructure approach.



---

## CNCF Projects

This architecture leverages six CNCF projects for orchestration, deployment automation, identity management, and observability. Each project serves a specific purpose in creating a reliable, maintainable SSO infrastructure.

### Kubernetes (Orchestration & Management)

**[Kubernetes](https://kubernetes.io)** serves as the foundational container orchestration platform, managing Keycloak pods across multiple clusters in different availability zones. The team selected Kubernetes for its maturity, operator pattern support, and proven scalability at enterprise scale.

Multiple clusters run independently following the cattle service model where individual clusters are disposable and replaceable. This contrasts with the previous VM-based pets model where each machine was carefully maintained.

Key features utilized include:

- StatefulSets were intentionally avoided—Keycloak runs as stateless Deployments that scale from zero
- Horizontal Pod Autoscaler not yet implemented but planned for dynamic scaling
- ConfigMaps for mounting Infinispan remote cache configuration into Keycloak pods
- Volume mounts for cache configuration files from ConfigMaps to pod containers
- DNS service discovery for locating Infinispan cache nodes via DNS alias
- Operator pattern via Keycloak operator managing custom resources (CRDs)

Clusters follow the cattle model with planned replacement cycles. Pod restarts complete in 30-40 seconds, enabling rapid recovery from failures without session loss.

### Argo CD (Continuous Integration & Delivery)

**[Argo CD](https://argoproj.github.io/cd/)** implements GitOps automation, making Git the single source of truth for all infrastructure configuration. The team adopted Argo CD to eliminate configuration drift and provide clear audit trails.

Argo CD monitors Git repositories and automatically synchronizes changes to multiple **[Kubernetes](https://kubernetes.io)** clusters across availability zones. All Keycloak operator CRDs, Docker images, monitoring configuration, and logging setup live in Git repositories.

Key deployment capabilities include:

- Automatic synchronization from Git commits to all clusters within minutes
- Merge requests required for all configuration changes, providing review process
- Rollback via Git revert—simply reverting a commit rolls back infrastructure changes
- Clear audit trail showing who changed what and when via Git history
- Multi-cluster synchronization ensuring consistent configuration across zones

The GitOps approach dramatically improved operational confidence. Every change is tracked, reviewed, and easily reversible.

### Keycloak (Security & Identity Management)

**[Keycloak](https://www.keycloak.org)** (CNCF incubation project since Spring 2023) provides open source identity and access management with single sign-on and multi-factor authentication. [CERN](https://home.cern) runs Keycloak on the Quarkus framework designed specifically for Kubernetes deployment.

The service supports 200,000 users, 10,000 OIDC clients, and handles 10,000 logins per hour during peak periods. Custom SPIs integrate with CERN's authorization service for identity management.

Keycloak features leveraged:

- Operator-based deployment using Keycloak operator with CRDs defining desired state
- "Unsupported fields" feature for advanced configuration not yet in stable API
- Remote cache configuration pointing to separated Infinispan cluster via ConfigMap
- Custom SPIs for CERN authorization service integration and OTP validation endpoints
- Custom themes for organizational branding requirements
- Realm configuration can be included in CRDs for GitOps approach (partially implemented)

The team uses operator unsupported fields pragmatically for production despite concerns. This approach enables required functionality while waiting for features to stabilize in the operator API.

### Prometheus (Observability & Analysis)

**[Prometheus](https://prometheus.io)** collects metrics for monitoring Keycloak performance and resource utilization. The team migrated from legacy monitoring to a containerized **[Prometheus](https://prometheus.io)** stack deployed via **[Argo CD](https://argoproj.github.io/cd/)**.

Prometheus scrapes metrics from Keycloak pods and Kubernetes infrastructure components. This provides visibility into application behavior and resource consumption.

Monitoring capabilities:

- Keycloak application metrics (login rates, error rates, response times)
- Kubernetes cluster metrics (pod status, resource utilization, node health)
- Custom metrics for CERN-specific business logic tracking
- Integration with alerting systems for operational notifications

The observability stack enables the team to analyze performance independently for Keycloak and Infinispan. Previously, shared VM resources made troubleshooting difficult.

### Fluent Bit (Observability & Analysis)

**[Fluent Bit](https://fluentbit.io)** handles log aggregation, replacing legacy Flume-based logging infrastructure. The lightweight log processor parses and forwards Keycloak application logs with custom parsing rules.

Deployed as a DaemonSet across **[Kubernetes](https://kubernetes.io)** clusters, **[Fluent Bit](https://fluentbit.io)** collects logs from all pods and forwards them to centralized storage. Custom parsing rules extract structured data from Keycloak log formats.

Log processing features:

- Custom parsing rules specific to Keycloak log formats
- Automatic collection from all pods via DaemonSet deployment
- Structured log forwarding to centralized aggregation systems
- Lower resource footprint compared to legacy Flume infrastructure

### Podman (Container Runtime)

**[Podman](https://podman.io)** runs Infinispan cache clusters on VMs using Puppet for configuration management. This hybrid approach keeps cache infrastructure separate from the **[Kubernetes](https://kubernetes.io)** environment.

The team chose to keep Infinispan on VMs with **[Podman](https://podman.io)** rather than migrating to Kubernetes immediately. This pragmatic decision isolated migration risk—moving Keycloak first while maintaining stable cache infrastructure.

Infinispan deployment approach:

- Three Infinispan nodes running in **[Podman](https://podman.io)** containers on separate VMs
- DNS alias pointing to the three IPs for service discovery
- Puppet manages container configuration and orchestration
- Remote cache protocol (HotRod) for Keycloak connections
- Planned eventual migration to **[Kubernetes](https://kubernetes.io)** in future

This separation proved critical for operational simplicity. Keycloak pods restart in 30-40 seconds while cache remains stable, preserving user sessions.


### Project Summary

| Project | Category | Usage |
|---------|----------|-------|
| Kubernetes | Orchestration & Management | Container orchestration platform hosting Keycloak across availability zones |
| Keycloak | Security & Identity Management | SSO service for 200K users with operator-based deployment |
| Argo CD | Continuous Integration & Delivery | GitOps automation synchronizing config across clusters |
| Prometheus | Observability and Analysis | Metrics collection for Keycloak and infrastructure monitoring |
| Fluent Bit | Observability and Analysis | Log aggregation with custom Keycloak parsing rules |
| Podman | Container Runtime | Runs Infinispan cache cluster on VMs with Puppet management |


---

## Integration Patterns

[CERN](https://home.cern)'s architecture success depends on three critical integration patterns enabling stateless application design, GitOps automation, and operator-based lifecycle management. These patterns work together to create an operationally simple, reliable system.

**Pattern 1: Stateless Application with Remote Caching**

**Projects Involved:** **[Keycloak](https://www.keycloak.org)**, **[Kubernetes](https://kubernetes.io)**, **[Podman](https://podman.io)**

Keycloak pods separate completely from the Infinispan cache layer, enabling independent scaling and operation. Keycloak becomes stateless and can scale from zero, while Infinispan scales based on cache replication needs. This separation allows Keycloak pod restarts without session loss in just 30-40 seconds.

The technical implementation uses a ConfigMap containing Infinispan configuration with a DNS alias pointing to three Infinispan IPs for high availability. The cache configuration file mounts via **[Kubernetes](https://kubernetes.io)** volumes into Keycloak pod containers. Keycloak connects to the remote cache using the HotRod protocol.

Benefits of this pattern:

- Zero-coordination SPI upgrades—simply restart pods without complex cache replication orchestration
- Independent resource analysis—CPU and memory usage can be measured separately per component
- Rapid recovery—30-40 second pod restart time compared to hours previously
- Stateless design enables horizontal scaling without state coordination
- Cache stability during application updates preserves user sessions

Implementation challenges encountered:

- Initial cache configuration required careful tuning to avoid connection timeouts. Solution: adjusted HotRod timeout settings in ConfigMap.
- DNS resolution latency occasionally caused startup delays. Solution: implemented retry logic with exponential backoff.
- Monitoring cache hit rates required custom metrics integration. Solution: exposed cache statistics via Keycloak metrics endpoint.

**Pattern 2: GitOps Multi-Cluster Synchronization**

**Projects Involved:** **[Argo CD](https://argoproj.github.io/cd/)**, **[Kubernetes](https://kubernetes.io)**

Git serves as the single source of truth for infrastructure configuration across multiple **[Kubernetes](https://kubernetes.io)** clusters. **[Argo CD](https://argoproj.github.io/cd/)** automatically synchronizes changes from Git to all clusters in different availability zones. This eliminates configuration drift and provides complete audit trails.

All Keycloak operator CRDs, Docker images, monitoring configuration (**[Prometheus](https://prometheus.io)**), and logging setup (**[Fluent Bit](https://fluentbit.io)**) live in Git repositories. Merge requests require review for configuration changes, and **[Argo CD](https://argoproj.github.io/cd/)** syncs to multiple clusters automatically with rollback via Git revert.

Operational benefits:

- Declarative infrastructure—desired state defined in Git, **[Argo CD](https://argoproj.github.io/cd/)** ensures reality matches
- Complete change history—every modification tracked with commit author, timestamp, and reason
- Easy rollback—reverting a Git commit rolls back infrastructure to previous state
- Review process—merge requests require approval before changes deploy
- Disaster recovery—entire infrastructure configuration backed up in Git

Challenges addressed:

- Realm configuration partially unsolved—many settings still live in database rather than Git. Solution: custom scripts export realm config to Git for change detection (workaround, not ideal).
- Secret management requires external tooling—Git cannot store sensitive credentials. Solution: use Kubernetes Secrets managed outside **[Argo CD](https://argoproj.github.io/cd/)** workflow.

**Pattern 3: Operator-Based Deployment with Custom Resources**

**Projects Involved:** **[Keycloak](https://www.keycloak.org)**, **[Kubernetes](https://kubernetes.io)**

**[Keycloak](https://www.keycloak.org)** deploys and manages using the **[Kubernetes](https://kubernetes.io)** operator pattern with custom resource definitions (CRDs). This simplifies operational complexity compared to manual Helm or kubectl-based deployment.

The Keycloak operator manages deployment, upgrades, and configuration via CRDs, with realm configuration included for full GitOps. The team uses the operator's "unsupported fields" feature for advanced configuration not yet stable in the API, with the operator handling health checks, rolling updates, and resource management automatically.

Operator advantages:

- Declarative configuration—define desired state in YAML, operator makes it reality
- Automatic health management—operator monitors and restarts unhealthy pods
- Simplified upgrades—changing image tag in CRD triggers rolling update
- Domain-specific knowledge—operator understands Keycloak requirements and best practices
- Reduced operational burden—no manual deployment procedures or runbooks needed

Operator usage notes:

- "Unsupported fields" feature enables production functionality not yet in stable API. Creates uncertainty about long-term support but pragmatically necessary.
- Operator preview features like token exchange have remained in preview for years despite heavy production use. Better roadmap communication needed from upstream project.
- Operator updates require careful testing in staging before production to avoid breaking changes in unsupported fields.

---

## Implementation Details

[CERN](https://home.cern)'s implementation began with comprehensive load testing to validate the architecture before securing management approval. The team used Gatling's closed workload model with 5,550 concurrent users executing identical login scenarios repeatedly for 10 minutes.

**Phase 1: Architecture Validation (August-September 2023)**

**Duration:** 4 weeks

The team needed quantitative proof that **[Kubernetes](https://kubernetes.io)** would improve performance to overcome management skepticism about adding abstraction layers. Load testing demonstrated the new infrastructure was four times more efficient than the VM-based predecessor. This evidence secured the green light for migration.

**Steps:**

1. Set up test **[Kubernetes](https://kubernetes.io)** clusters with Keycloak and separated Infinispan on test VMs
2. Configured Gatling load testing with closed workload model (system receives more requests as it handles load faster)
3. Executed identical tests against legacy VM infrastructure and new Kubernetes infrastructure
4. Measured throughput, response times, resource utilization across both environments
5. Documented 4x efficiency improvement and presented results to management

Challenges and solutions during validation:

- **Problem:** Initial Kubernetes configuration showed only marginal improvement. **Solution:** Tuned pod resource limits and Infinispan connection pool settings, revealing true performance gains.
- **Problem:** Management concerned about Kubernetes adding unnecessary virtualization. **Solution:** Quantitative testing proved efficiency gains outweighed abstraction overhead.

**Validation metrics:**
- Identical workload (5,550 concurrent users) handled with 4x better throughput
- Resource utilization (CPU and memory) decreased significantly
- Response time latency improved across all percentiles

**Phase 2: Infrastructure Deployment (September 2023)**

**Duration:** 6 weeks

The team deployed production **[Kubernetes](https://kubernetes.io)** clusters across availability zones and configured the Keycloak operator with custom resource definitions. The pragmatic decision to use operator "unsupported fields" enabled necessary functionality despite management concerns about stability.

**Steps:**

1. Provisioned multiple **[Kubernetes](https://kubernetes.io)** clusters across different availability zones following cattle model
2. Deployed Keycloak operator to each cluster with CRD definitions for Keycloak instances
3. Configured unsupported fields in CRDs for advanced features not yet stable in operator API
4. Set up **[Prometheus](https://prometheus.io)** monitoring stack for metrics collection
5. Deployed **[Fluent Bit](https://fluentbit.io)** DaemonSets for log aggregation replacing legacy Flume
6. Committed all configurations to Git repositories for GitOps approach

Challenges during infrastructure deployment:

- **Problem:** Unsupported fields feature raised management concerns about production stability. **Solution:** Demonstrated that required functionality unavailable in stable API; accepted calculated risk.
- **Problem:** Initial pod scheduling spread unevenly across nodes. **Solution:** Implemented pod anti-affinity rules for better distribution.

**Validation:**
- All clusters running with Keycloak operator managing pod lifecycle
- Monitoring and logging infrastructure operational
- Configuration stored in Git ready for **[Argo CD](https://argoproj.github.io/cd/)** synchronization

**Phase 3: GitOps Automation (October 2023)**

**Duration:** 3 weeks

Argo CD deployment provided continuous synchronization from Git to clusters, eliminating manual configuration drift. Every infrastructure change now requires merge request review and creates a Git commit.

**Steps:**

1. Deployed **[Argo CD](https://argoproj.github.io/cd/)** control plane to dedicated cluster
2. Configured **[Argo CD](https://argoproj.github.io/cd/)** applications to monitor Git repositories containing Keycloak configurations
3. Set up multi-cluster synchronization targeting all availability zone clusters
4. Implemented merge request workflow requiring approval for all configuration changes
5. Tested rollback procedures by reverting Git commits and verifying **[Argo CD](https://argoproj.github.io/cd/)** restored previous state

Challenges with GitOps implementation:

- **Problem:** Realm configuration partially exists in database, not Git. **Solution:** Created custom scripts to export realm config for change detection (workaround, not ideal).
- **Problem:** Secret management outside Git required separate workflow. **Solution:** Used **[Kubernetes](https://kubernetes.io)** Secrets managed independently from **[Argo CD](https://argoproj.github.io/cd/)**.

**Validation:**
- **[Argo CD](https://argoproj.github.io/cd/)** automatically syncing configuration changes to all clusters
- Rollback tested by reverting commits and confirming infrastructure restored
- Clear audit trail established via Git history

**Phase 4: Infinispan Separation (October-November 2023)**

**Duration:** 4 weeks

Separating Infinispan from Keycloak required careful configuration to ensure stateless Keycloak pods could connect to the remote cache cluster. This separation enabled the rapid pod restart capability defining the new architecture's operational simplicity.

**Steps:**

1. Created Kubernetes ConfigMap containing Infinispan remote cache server configuration
2. Specified DNS alias pointing to three Infinispan server IPs for high availability
3. Configured volume mounts in Keycloak pod specs to inject ConfigMap as cache config file
4. Updated Keycloak operator CRDs to reference remote cache configuration
5. Tested pod restarts to verify sessions preserved through restarts via remote cache

Challenges during separation:

- **Problem:** Initial cache connection timeouts during pod startup. **Solution:** Tuned HotRod protocol timeout settings in ConfigMap.
- **Problem:** DNS resolution delays occasionally caused startup failures. **Solution:** Implemented connection retry logic with exponential backoff.

**Validation:**
- Keycloak pods restarting in 30-40 seconds without session loss
- Remote cache connections stable via DNS-based discovery
- User sessions preserved through pod restarts (tested by forcing restarts during active user sessions)

















---

## Deployment Architecture

[CERN](https://home.cern) operates a multi-cluster **[Kubernetes](https://kubernetes.io)** deployment across availability zones with stateless Keycloak pods and separated cache infrastructure. Each cluster runs independently following the cattle service model. The three-node floating IP load balancer provides automatic failover with near-zero downtime.

Cluster organization follows separation of concerns:

- Multiple production clusters distributed across different availability zones for high availability
- Each cluster runs the Keycloak operator managing pod lifecycle via custom resources (CRDs)
- Clusters are disposable and replaceable (cattle model)—any cluster can be replaced without user impact
- Infinispan cache runs on separate VMs with **[Podman](https://podman.io)** containers managed by Puppet
- Separation ensures Keycloak pod failures don't impact cache stability and vice versa
- DNS-based service discovery connects Keycloak pods to Infinispan cache nodes

**[Argo CD](https://argoproj.github.io/cd/)** implements GitOps-based deployments following strict separation between application code and configuration. Keycloak application images come from CI/CD pipelines while configuration lives in dedicated Git repositories.

When engineers merge configuration changes to the main branch, **[Argo CD](https://argoproj.github.io/cd/)** detects changes and automatically synchronizes to all clusters. The synchronization happens within minutes across all availability zones. This ensures consistent configuration without manual deployment procedures.

Production deployments require merge request approval and Git commit review. Rollback procedures simply revert Git commits—**[Argo CD](https://argoproj.github.io/cd/)** detects the revert and rolls back infrastructure to the previous state. This approach dramatically improves operational confidence.

Regional coordination uses DNS-based service discovery:

- Infinispan cache nodes register with DNS using fixed alias (e.g., cache.cern.internal)
- DNS alias resolves to three IP addresses for high availability
- Keycloak pods use DNS alias in remote cache configuration (specified in ConfigMap)
- All clusters across availability zones connect to the same Infinispan cache cluster
- Cache provides session replication and user attribute caching for stateless Keycloak pods
- This design optimizes for operational simplicity over strict regional isolation

---

## Observability and Operations

[Observability](https://glossary.cncf.io/observability/) is essential for operating [CERN](https://home.cern)'s mission-critical SSO service supporting 200,000 users and real-time particle physics experiments. The architecture implements metrics collection and log aggregation using CNCF projects.

**[Prometheus](https://prometheus.io)** collects metrics from Keycloak and Kubernetes infrastructure:

- Keycloak application metrics via /metrics endpoint (login rates, error rates, response times)
- **[Kubernetes](https://kubernetes.io)** cluster metrics via API (pod status, node health, resource utilization)
- Custom metrics for CERN-specific business logic (authentication provider usage, MFA rates)
- The separated architecture enables independent monitoring of Keycloak and Infinispan resource consumption
- Previously, shared VM resources made troubleshooting difficult—now CPU and memory analyzed per component
- Metrics collection runs as a dedicated monitoring stack deployed via **[Argo CD](https://argoproj.github.io/cd/)**

**[Fluent Bit](https://fluentbit.io)** handles log aggregation with custom parsing:

- Deployed as DaemonSet across all **[Kubernetes](https://kubernetes.io)** clusters collecting pod logs
- Custom parsing rules extract structured data from Keycloak log formats
- Replaces legacy Flume-based logging with lighter-weight infrastructure
- Logs forward to centralized aggregation systems for search and analysis
- Engineers query logs to debug authentication issues and track user session behavior
- The containerized logging stack integrates cleanly with **[Kubernetes](https://kubernetes.io)** rather than requiring VM-based agents

Operational runbooks and incident response processes:

- The team maintains runbooks for common failure scenarios (pod crashes, cache connection issues, certificate expiration)
- Runbooks include symptoms, investigation steps using **[Prometheus](https://prometheus.io)** and **[Fluent Bit](https://fluentbit.io)**, and remediation procedures
- The GitOps approach enables rapid rollback via Git revert for configuration issues
- Pod restart procedures simplified dramatically—30-40 second restart time with no coordination needed
- The separated Infinispan cache preserves sessions through Keycloak pod restarts
- This architecture proved its resilience when pods restarted every 3 hours for 3 days due to Java heap misconfiguration with no user complaints

















---

## Results and Impact

[CERN](https://home.cern)'s migration to **[Kubernetes](https://kubernetes.io)** delivered dramatic improvements across technical, operational, and reliability dimensions. The quantitative results validated the architectural decisions and justified the migration investment.

**Load Balancer Failover Time**
- **Before:** 15 minutes
- **After:** Near-zero (automatic)
- **Improvement:** Elimination of 15-minute outage windows
- **Business Impact:** Meets stringent availability requirements for particle accelerator experiments with no authentication interruptions during failover.
- **Supporting Evidence:** "we replace also the load balancer where basically we have now a a cluster of three machine where we use floating IP and basically every time the active machine goes down the IP is moved to another passive passive one of the passive nodes and this is almost uh invisible to end users so the the the failover is almost so we don't have basically down time"

**Infrastructure Efficiency**
- **Before:** Baseline (1x)
- **After:** 4x improvement
- **Improvement:** 4x performance increase
- **Business Impact:** Handles identical workload with significantly better throughput and resource utilization, enabling future growth without proportional infrastructure investment.
- **Supporting Evidence:** "the new infrastructure based on kubernetes and separation of kylock from infinite span was four times more efficient than the previous one"

**Keycloak Pod Restart Time**
- **Before:** Hours (complex coordination required)
- **After:** 30-40 seconds
- **Improvement:** 99%+ reduction in restart time
- **Business Impact:** Operations like SPI upgrades that previously consumed hours now complete in minutes with simple pod restarts and no user impact.
- **Supporting Evidence:** "while before it was still possible but you had to uh have a much more coordination because you had to start first the first node waiting that was a upap then repli waiting that the cach was replicated to another node and so on uh so it Wasing the operation were taking much longer why now is just you kill the pot it's up in 30 in 40 seconds and that's it"

**Service Resilience During Failures**
- **Before:** Outages during operational issues
- **After:** 3 days of continuous pod restarts with zero user complaints
- **Improvement:** Transparent failure recovery
- **Business Impact:** Separated cache architecture preserves sessions through application failures; users unaffected by pod restarts happening every 3 hours.
- **Supporting Evidence:** "I remember that when the first week we moved to kubernetes we had some issue with the Java settings they were too low and so basically for 3 days all the pods were restarting every 3 hours at different time but there was no complaint"

**Operational Efficiency**
- **Before:** Team time dominated by infrastructure maintenance
- **After:** Estimated 70% reduction in operational burden
- **Improvement:** Majority of time freed for feature development
- **Business Impact:** Team resources shifted from maintenance to innovation; infrastructure operations reduced to occasional upgrades and monitoring.
- **Supporting Evidence:** "we know that now the time that we are spending on the operation and on the uh infrastructure is much less than it was before before was basically iacting the the time of the SSO team now is basically just a small per fracture that they have to do from time to time for example like upgrade Ki loock or things like that"

The architecture's resilience was proven through unintended real-world testing. Continuous pod restarts for three days demonstrated the separated cache design's effectiveness in preserving user experience through application failures.


### Key Metrics

| Metric | Improvement | Business Impact |
|--------|-------------|-----------------|
| Load Balancer Failover Time | 15 minutes → near-zero (automatic) | Eliminated authentication interruptions during failures |
| Infrastructure Efficiency | Baseline → 4x improvement | Handles identical workload with 4x better performance |
| Pod Restart Time | Hours → 30-40 seconds (99%+ reduction) | SPI upgrades from hours to minutes with no user impact |
| Operational Time Reduction | ~70% reduction in infrastructure maintenance | Team resources freed for feature development |
| Service Resilience | 3 days continuous restarts with zero complaints | Transparent failure recovery preserves user experience |


---

## Lessons Learned

[CERN](https://home.cern)'s migration to [cloud-native](https://glossary.cncf.io/cloud-native-tech/) infrastructure was transformative but revealed important insights about architecture decisions and organizational change. This section shares key lessons learned during the 6-month implementation.

Several architectural decisions proved highly effective:

- **Separating Keycloak from Infinispan:** The decision to separate stateless application from stateful cache delivered benefits beyond initial expectations. Independent scaling of Keycloak pods while maintaining stable Infinispan enabled optimization of each component separately. Most critically, separating components simplified troubleshooting—CPU and memory usage could be analyzed per component rather than diagnosing a shared Java process. This separation enabled the 30-40 second pod restart capability defining the new architecture's operational simplicity.

- **Quantitative Load Testing for Management Buy-In:** Proving performance improvements with Gatling load testing was essential for securing management approval. The 4x efficiency improvement provided irrefutable evidence that overcame skepticism about **[Kubernetes](https://kubernetes.io)** adding unnecessary abstraction layers. Organizations considering similar migrations should invest in comprehensive performance testing early to build confidence and secure resources.

- **GitOps from Day One:** Using **[Argo CD](https://argoproj.github.io/cd/)** to manage all **[Kubernetes](https://kubernetes.io)** manifests in Git provided auditability, rollback capabilities, and declarative deployments from the start. Configuration drift became impossible—Git history serves as a complete audit trail. This approach eliminated the manual deployment procedures that consumed significant team time previously.

- **Pragmatic Use of Operator Unsupported Fields:** Deploying production Keycloak with operator "unsupported fields" for advanced features enabled necessary functionality despite uncertainty. While this creates questions about long-term support, it pragmatically unblocked production deployment. The alternative—waiting for features to stabilize in the operator API—would have delayed migration indefinitely.

Several aspects proved more challenging than anticipated:

- **Realm Configuration Management Partially Unsolved:** While Keycloak operators now support realm imports via CRDs, many configuration elements still reside in the database rather than Git. The team's workaround—regularly exporting realm configuration to Git for change detection—provides visibility but lacks the declarative guarantees of full GitOps. **Lesson:** GitOps benefits apply unevenly; some stateful components resist full declarative management.

- **Operator Preview Feature Uncertainty:** Features like token exchange have remained in "preview" status for years despite heavy production use by many organizations. The **[Keycloak](https://www.keycloak.org)** project should provide clearer roadmaps for feature stabilization. **Lesson:** Preview features may stay in preview indefinitely; assess organizational risk tolerance before depending on them.

- **Infinispan Hybrid Approach Creates Operational Split:** Keeping Infinispan on VMs with **[Podman](https://podman.io)** and Puppet while migrating Keycloak to **[Kubernetes](https://kubernetes.io)** created operational complexity with two infrastructure paradigms. This pragmatic approach isolated migration risk but means the team still manages Puppet alongside GitOps. **Lesson:** Phased migrations create temporary hybrid complexity; plan for eventual consolidation.

Recommendations for teams considering similar migrations:

- **Separate Stateless from Stateful Components:** Design applications to be stateless with remote state storage (cache, database) from day one. This enables rapid restart, horizontal scaling, and operational simplicity. The 30-40 second Keycloak pod restart time proves the value.

- **Invest in Load Testing for Organizational Buy-In:** Management skepticism about [cloud-native](https://glossary.cncf.io/cloud-native-tech/) architectures requires quantitative proof. Comprehensive performance testing showing concrete improvements (like 4x efficiency) secures resources and builds confidence.

- **Adopt GitOps Early:** Managing infrastructure via Git with **[Argo CD](https://argoproj.github.io/cd/)** or **[Flux](https://fluxcd.io)** provides auditability and rollback capabilities from the start. Don't manage **[Kubernetes](https://kubernetes.io)** with kubectl imperatively—declare desired state in Git.

- **Use Operators for Domain-Specific Applications:** The **[Kubernetes](https://kubernetes.io)** operator pattern encodes operational knowledge for complex applications like **[Keycloak](https://www.keycloak.org)**. Operators handle health checks, upgrades, and configuration management automatically. Accept pragmatic use of preview features when necessary.

- **Phase High-Risk Migrations:** Migrating Keycloak to **[Kubernetes](https://kubernetes.io)** while keeping Infinispan on VMs isolated risk. Each component could be validated independently. Consider phased approaches for mission-critical services rather than big-bang migrations.

- **Plan for Eventual Consistency in GitOps:** Some stateful components (like database-backed configuration) resist full declarative management. Accept partial GitOps coverage and build workarounds (like export scripts) for visibility.

---

## Conclusion

[CERN](https://home.cern)'s transformation from VM-based infrastructure to a [cloud-native](https://glossary.cncf.io/cloud-native-tech/) **[Kubernetes](https://kubernetes.io)** architecture represents a fundamental shift in operating mission-critical identity services. Over six months, the team migrated to multi-cluster **[Kubernetes](https://kubernetes.io)** with separated stateless Keycloak and stateful Infinispan, achieving 4x infrastructure efficiency and eliminating 15-minute failover windows. The architecture now supports 200,000 users and 10,000 logins per hour with 30-40 second pod restart times.

As of February 2026, the architecture is fully operational and stable, serving particle physics researchers worldwide. The team continues optimizing: planning Infinispan migration to **[Kubernetes](https://kubernetes.io)**, expanding **[Prometheus](https://prometheus.io)** monitoring coverage, and refining GitOps workflows. Operational time spent on infrastructure decreased by approximately 70%, freeing the team to focus on identity management features rather than infrastructure maintenance.

Looking forward, the team plans to complete the cloud-native migration by moving Infinispan to **[Kubernetes](https://kubernetes.io)**, eliminating the remaining Puppet-managed VM infrastructure. Additional **[Kubernetes](https://kubernetes.io)** clusters may be deployed for further availability zone coverage. The team is evaluating **[Istio](https://istio.io)** service mesh for advanced traffic management and exploring automated capacity planning based on **[Prometheus](https://prometheus.io)** metrics.

---

## About This Reference Architecture

**Company:** [CERN](https://home.cern)  
**Industry:** Scientific Research & High Energy Physics  
**Publication Date:** 2026-02-10  
**Generated by:** [casestudypilot](https://github.com/cncf/casestudypilot) reference-architecture-agent v1.0.0  
**Source Video:** [https://www.youtube.com/watch?v=rqDrrTKzNd8](https://www.youtube.com/watch?v=rqDrrTKzNd8)  
**TAB Status:** Proposed (pending submission)  
**Architectural Significance:** Demonstrates separation of stateless applications from caching layers in Kubernetes with GitOps automation for mission-critical identity management supporting 200,000 users

### CNCF TAB Submission

This reference architecture is ready for submission to the CNCF Technical Advisory Board. To submit:

1. Review this reference architecture for technical accuracy
2. Create an issue at: https://github.com/cncf/tab/issues/new
3. Select "Reference Architecture Submission" template
4. Provide link to this reference architecture
5. TAB will review within 2-4 weeks

For more information on the TAB review process, see: https://github.com/cncf/tab/blob/main/process/reference-architectures.md

---

## License

This reference architecture is licensed under the Creative Commons Attribution 4.0 International License.  
© 2026-02-10 Cloud Native Computing Foundation