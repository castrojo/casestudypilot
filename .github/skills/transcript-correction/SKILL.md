---
name: transcript-correction
description: Corrects common errors in YouTube auto-generated transcripts
version: 1.0.0
---

# Transcript Correction Skill

## Purpose

Fix speech-to-text errors in YouTube auto-generated captions, focusing on:
- CNCF project name capitalization
- Technical term spelling
- Common acronyms and abbreviations

## Critical Rules

1. **Do NOT rephrase** - Only fix errors, preserve original wording
2. **Preserve speaker intent** - Don't change meaning
3. **Fix systematic errors** - Focus on repeated mistakes
4. **Maintain flow** - Keep sentence structure intact

## CNCF Projects to Correct

Always fix capitalization for these CNCF projects:

| Incorrect | Correct |
|-----------|---------|
| kubernetes | Kubernetes |
| prometheus | Prometheus |
| argo cd, argocd | Argo CD |
| helm | Helm |
| istio | Istio |
| cilium | Cilium |
| envoy | Envoy |
| linkerd | Linkerd |
| fluentd | Fluentd |
| jaeger | Jaeger |
| harbor | Harbor |
| falco | Falco |
| flux | Flux |
| rook | Rook |
| etcd | etcd (lowercase correct) |
| grpc | gRPC |
| containerd | containerd (lowercase correct) |
| knative | Knative |

## Common Technical Errors

### Command-line Tools
- cueectl, cube ctl, cube control → kubectl
- docker compose → Docker Compose
- git hub → GitHub

### Technical Terms
- micro services → microservices
- git ops → GitOps
- dev ops → DevOps
- dev sec ops → DevSecOps
- cloud native → cloud-native (when adjective)
- continuous integration → CI (if clearly abbreviated)
- continuous delivery → CD (if clearly abbreviated)

### Cloud Providers
- aws, amazon web services → AWS
- gcp, google cloud → Google Cloud
- azure → Azure

### Programming Concepts
- api → API
- rest api → REST API
- yaml → YAML
- json → JSON
- http → HTTP
- https → HTTPS

## Processing Guidelines

1. **Read entire transcript first** - Understand context
2. **Fix CNCF projects** - Highest priority
3. **Fix technical terms** - Second priority
4. **Preserve ambiguity** - If unsure, leave as-is
5. **Maintain punctuation** - Don't add or remove

## What NOT to Fix

- Speaker names (even if misspelled)
- Company names (even if informal)
- Informal language ("gonna", "wanna")
- Filler words ("um", "uh", "like")
- Grammatical errors in speech
- Regional pronunciations

## Quality Checklist

Before returning corrected transcript, verify:

- [ ] All CNCF project names capitalized correctly
- [ ] kubectl spelled correctly (common error)
- [ ] GitOps, DevOps, DevSecOps capitalized
- [ ] Cloud provider names capitalized
- [ ] No sentences rephrased
- [ ] Original meaning preserved
- [ ] Technical accuracy maintained

## Example Input

```
in our company we use kubernetes for container orchestration
we deployed prometheus for monitoring and argo cd for gitops
we also use helm charts and the cueectl command line tool
```

## Example Output

```
in our company we use Kubernetes for container orchestration
we deployed Prometheus for monitoring and Argo CD for GitOps
we also use Helm charts and the kubectl command line tool
```

## Notes

- This skill handles **correction only**, not content analysis
- Next skill (transcript-analysis) will extract structured data
- Correction quality directly impacts analysis accuracy
- When in doubt, preserve original text
