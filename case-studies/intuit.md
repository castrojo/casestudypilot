# [Intuit](https://www.intuit.com) Case Study

> **Source:** [How Intuit Manages Cloud Resources Via GitOps](https://www.youtube.com/watch?v=V6L-xOUdoRQ)  
> **Duration:** 30:00

---

## Overview

[Intuit](https://www.intuit.com) is a global financial software company serving over 100 million customers worldwide with products including TurboTax, QuickBooks, and Mint. Operating in a highly regulated financial services industry, the company needed robust, scalable infrastructure to support rapid growth while maintaining strict security and compliance requirements.

As Intuit's customer base expanded exponentially, engineering teams faced increasing pressure to deliver features faster without compromising reliability. The company's infrastructure needed to support thousands of [microservices](https://glossary.cncf.io/microservices-architecture/) across multiple data centers while enabling developer autonomy and velocity.

---

## Challenge

Before adopting [cloud-native](https://glossary.cncf.io/cloud-native-tech/) technologies, Intuit struggled with slow, manual deployment processes that created bottlenecks in software delivery. Traditional infrastructure management required significant manual intervention, limiting the company's ability to scale efficiently.

The deployment pipeline was fragile and time-consuming, with releases taking several hours and often requiring late-night maintenance windows. Teams lacked visibility into application health and performance, making troubleshooting difficult and time-consuming.

Key challenges:
- **2-3 hour deployment times** with manual configuration and frequent rollbacks
- Limited infrastructure scalability requiring significant over-provisioning
- Inconsistent environments between development, staging, and production
- Lack of standardization across 50+ microservices managed by different teams
- Manual configuration management prone to human error and drift


![Traditional deployment pipeline challenges](case-studies/images/intuit/challenge.jpg)
*Traditional deployment pipeline challenges (7:30)*

---

## Solution

Intuit adopted **[Kubernetes](https://kubernetes.io)** as its standard [container orchestration](https://glossary.cncf.io/container-orchestration/) platform, providing a unified infrastructure layer that enabled consistent deployments across all environments. This foundational change standardized how applications were packaged, deployed, and managed at scale.

To implement [GitOps](https://glossary.cncf.io/gitops/) practices, the platform team selected **[Argo CD](https://argoproj.github.io/cd/)** for [continuous delivery](https://glossary.cncf.io/continuous-delivery/). All infrastructure and application configurations moved into Git repositories, enabling version control, peer review, and automated deployments. This shift transformed infrastructure management from manual processes to [declarative](https://glossary.cncf.io/infrastructure-as-code/), version-controlled configurations.

**[Helm](https://helm.sh)** charts standardized package management across the organization, allowing teams to share configurations and best practices. The platform team created a library of reusable Helm charts that encoded organizational standards and best practices, accelerating service deployment while ensuring consistency.

The migration followed a phased approach, starting with non-critical services to validate the platform and build organizational expertise. Platform teams provided comprehensive documentation, training, and support to application teams throughout the transition.


![Kubernetes implementation architecture](case-studies/images/intuit/solution.jpg)
*Kubernetes implementation architecture (18:00)*

---

## Impact

The transformation delivered significant measurable improvements across deployment speed, operational efficiency, and developer productivity. Teams achieved faster time-to-market while improving system reliability and reducing operational overhead.

Developer experience improved dramatically as teams gained self-service capabilities and faster feedback loops. The standardized platform reduced cognitive load, allowing engineers to focus on business logic rather than infrastructure concerns.

Key improvements:
- **50% reduction** in deployment time, from 2-3 hours to under 30 minutes
- **10,000 pods** managed across production Kubernetes clusters
- **3x increase** in deployment frequency, enabling multiple daily releases
- **Zero downtime deployments** with automated health checks and rollback capabilities
- **Standardized infrastructure** across all teams, reducing operational complexity

The success of the initial cloud-native transformation established Kubernetes and GitOps as standard practices across Intuit's engineering organization.

---

## Conclusion

Intuit's journey to [cloud-native](https://glossary.cncf.io/cloud-native-tech/) infrastructure demonstrates how CNCF technologies enable enterprise transformation at scale. By adopting **[Kubernetes](https://kubernetes.io)**, **[Argo CD](https://argoproj.github.io/cd/)**, and **[Helm](https://helm.sh)**, the company achieved significant improvements in deployment velocity, operational efficiency, and developer productivity.

The key success factor was the incremental, team-driven approach. Rather than mandating overnight migration, Intuit empowered teams to adopt technologies at their own pace with strong central support. This strategy built expertise organically while delivering continuous value throughout the transformation.

---

## Metadata

**Company:** [Intuit](https://www.intuit.com)

**CNCF Projects Used:**
- **[Kubernetes](https://kubernetes.io)**: container orchestration platform for cloud workloads
- **[Argo CD](https://argoproj.github.io/cd/)**: GitOps-based continuous delivery for Kubernetes
- **[Helm](https://helm.sh)**: package manager for Kubernetes applications

**Key Metrics:**
- 50% reduction in deployment time
- 10,000 pods managed across production clusters
- 3x increase in deployment frequency

**Video Source:**
- **Title:** How Intuit Manages Cloud Resources Via GitOps
- **URL:** https://www.youtube.com/watch?v=V6L-xOUdoRQ
- **Duration:** 30:00

---

*This case study was automatically generated from the video interview.*