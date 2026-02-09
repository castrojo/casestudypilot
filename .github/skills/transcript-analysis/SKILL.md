---
name: transcript-analysis
description: Analyzes transcripts to extract structured data
version: 1.0.0
---

# Transcript Analysis Skill

## Purpose

Extract structured information from corrected video transcripts to enable case study generation:
- Identify CNCF projects used
- Extract quantitative metrics
- Classify content into sections

## Analysis Tasks

### 1. Identify CNCF Projects

Find all mentions of CNCF projects and understand their usage context.

**Common CNCF Projects:**
- Kubernetes, Prometheus, Envoy, CoreDNS, containerd
- Fluentd, Jaeger, Vitess, Helm, Argo CD, Flux
- Cilium, Linkerd, Istio, etcd, CRI-O, Harbor
- Falco, Dragonfly, Rook, TiKV, gRPC, CNI
- Knative, OpenTelemetry

**For each project found, extract:**
- Project name (exact capitalization)
- Usage context (what it's used for)
- Any specific features or benefits mentioned

**Example:**
```json
{
  "name": "Kubernetes",
  "usage_context": "container orchestration and workload scheduling"
}
```

### 2. Extract Quantitative Metrics

Find all measurable achievements and improvements.

**Metric Types:**

**Percentages:**
- "50% reduction in..."
- "3x increase in..."
- "99.9% uptime"

**Time Savings:**
- "from 2 hours to 15 minutes"
- "deployment time reduced by 30 minutes"
- "faster by 5x"

**Scale:**
- "10,000 pods in production"
- "1 million requests per second"
- "100 microservices"

**Cost:**
- "$100,000 saved annually"
- "reduced costs by 40%"
- "infrastructure costs decreased"

**Reliability:**
- "zero downtime deployments"
- "99.99% availability"
- "reduced incidents by 80%"

**Format for each metric:**
```json
{
  "value": "50%",
  "type": "percentage",
  "context": "reduction in deployment time",
  "full_statement": "We saw a 50% reduction in deployment time after adopting Argo CD"
}
```

### 3. Classify Content into Sections

Analyze the transcript and extract content for each section type.

**Section Types:**

**Background:**
- Company overview and industry
- Business context and scale
- Why they're using CNCF technologies
- Team size and structure

**Keywords:** "we are", "our company", "we work with", "our team", "in our industry"

**Challenge:**
- Problems they faced
- Pain points and limitations
- Technical debt or constraints
- Business pressures

**Keywords:** "the problem", "we faced", "difficulty", "challenge", "struggled", "couldn't"

**Solution:**
- CNCF technologies adopted
- Implementation approach
- Architecture changes
- How they solved problems

**Keywords:** "we implemented", "we adopted", "we deployed", "we chose", "solution", "approach"

**Impact:**
- Results achieved
- Metrics and improvements
- Business outcomes
- Lessons learned

**Keywords:** "we achieved", "we saw", "improvement", "results", "now we can", "benefit"

## Output Format

Return a JSON object with this structure:

```json
{
  "cncf_projects": [
    {
      "name": "Kubernetes",
      "usage_context": "container orchestration platform for microservices"
    },
    {
      "name": "Argo CD",
      "usage_context": "GitOps continuous delivery for Kubernetes"
    }
  ],
  "key_metrics": [
    {
      "value": "50%",
      "type": "percentage",
      "context": "reduction in deployment time",
      "full_statement": "We reduced deployment time by 50%"
    },
    {
      "value": "10,000",
      "type": "scale",
      "context": "pods managed in production",
      "full_statement": "We now manage over 10,000 pods in production"
    }
  ],
  "sections": {
    "background": "Relevant sentences and context...",
    "challenge": "Description of problems faced...",
    "solution": "How they implemented CNCF technologies...",
    "impact": "Results and improvements achieved..."
  }
}
```

## Processing Guidelines

1. **Read entire transcript** - Understand full context
2. **Identify all CNCF projects** - Case-insensitive search
3. **Extract metrics aggressively** - Don't miss quantitative data
4. **Classify by strongest signal** - Sentences can belong to multiple sections
5. **Preserve original wording** - Use actual quotes when possible
6. **Be comprehensive** - Include all relevant information

## Quality Checklist

- [ ] All CNCF projects identified (minimum 2)
- [ ] Usage context provided for each project
- [ ] At least 1 quantitative metric extracted
- [ ] All 4 section types have content
- [ ] Background explains company context
- [ ] Challenge describes specific problems
- [ ] Solution details CNCF implementation
- [ ] Impact includes measurable results

## Example Input

```
We're a financial services company with 5000 employees. We were struggling
with slow deployments that took 2-3 hours. We adopted Kubernetes for
orchestration and Argo CD for continuous delivery. Now our deployments
take only 15 minutes and we manage 10,000 pods across multiple clusters.
```

## Example Output

```json
{
  "cncf_projects": [
    {
      "name": "Kubernetes",
      "usage_context": "container orchestration"
    },
    {
      "name": "Argo CD",
      "usage_context": "continuous delivery"
    }
  ],
  "key_metrics": [
    {
      "value": "2-3 hours to 15 minutes",
      "type": "time_savings",
      "context": "deployment time",
      "full_statement": "deployments took 2-3 hours, now take only 15 minutes"
    },
    {
      "value": "10,000",
      "type": "scale",
      "context": "pods managed across clusters",
      "full_statement": "we manage 10,000 pods across multiple clusters"
    }
  ],
  "sections": {
    "background": "We're a financial services company with 5000 employees.",
    "challenge": "We were struggling with slow deployments that took 2-3 hours.",
    "solution": "We adopted Kubernetes for orchestration and Argo CD for continuous delivery.",
    "impact": "Now our deployments take only 15 minutes and we manage 10,000 pods across multiple clusters."
  }
}
```

## Important Notes

- This analysis feeds into the case-study-generation skill
- Quality here directly impacts final case study quality
- Be thorough - missing metrics or projects degrades output
- When unsure, include rather than exclude
- Preserve technical accuracy - don't interpret or guess
