---
name: biography-extraction
description: Extracts and synthesizes biographical information from multiple sources
version: 1.0.0
---

# Biography Extraction Skill

## Purpose

Extract and synthesize biographical information from multiple sources (GitHub profile, video descriptions, transcript excerpts) to create accurate, factual presenter profiles. This skill ensures all biographical claims are traceable to source data and avoids speculation.

## Input Format

```json
{
  "github_profile": {
    "name": "Jeffrey Sica",
    "bio": "Kubernetes & OSS Advocate",
    "location": "Minneapolis, MN",
    "organizations": ["cncf", "kubernetes", "kubernetes-sigs"],
    "followers": 159,
    "company": "CNCF",
    "blog": "https://jeefy.dev",
    "twitter_username": "jeefy"
  },
  "video_descriptions": [
    "Jeffrey Sica discusses Kubernetes community management...",
    "Speaker: Jeffrey Sica, CNCF Ambassador..."
  ],
  "transcript_excerpts": [
    "I'm Jeffrey, I work on Kubernetes contributor experience...",
    "My role at CNCF involves community management..."
  ]
}
```

**Field Descriptions:**

- `github_profile` (object): GitHub API profile data
  - `name` (string): Display name
  - `bio` (string): GitHub bio text
  - `location` (string): Geographic location
  - `organizations` (array): GitHub organization memberships
  - `followers` (number): Follower count
  - `company` (string, optional): Company name
  - `blog` (string, optional): Personal website URL
  - `twitter_username` (string, optional): Twitter handle
- `video_descriptions` (array of strings): YouTube video descriptions mentioning the presenter
- `transcript_excerpts` (array of strings): Self-introductions and role descriptions from transcripts

## Output Format

```json
{
  "full_name": "Jeffrey Sica",
  "current_role": "Kubernetes & OSS Advocate at CNCF",
  "location": "Minneapolis, MN",
  "biography": "Jeffrey Sica is a Kubernetes and open source advocate at the Cloud Native Computing Foundation (CNCF). Based in Minneapolis, Minnesota, he focuses on improving contributor experience and building sustainable open source communities.\n\nWith deep expertise in Kubernetes ecosystem development, Jeffrey works closely with maintainers and contributors to enhance project governance and community engagement. His work spans multiple aspects of the Kubernetes project, including special interest groups (SIGs) and community management initiatives.\n\nAs an active member of the CNCF community, Jeffrey regularly presents at conferences and meetups, sharing insights on cloud-native technologies, community best practices, and sustainable open source development.",
  "organizations": ["CNCF", "Kubernetes", "Kubernetes SIGs"],
  "github_username": "jeefy",
  "followers": 159,
  "social_profiles": {
    "github": "https://github.com/jeefy",
    "website": "https://jeefy.dev",
    "twitter": "https://twitter.com/jeefy"
  }
}
```

**Field Descriptions:**

- `full_name` (string): Complete name (prefer GitHub name over transcript mentions)
- `current_role` (string): Current job title and organization
- `location` (string): Geographic location (city, state/country)
- `biography` (string): 2-3 paragraph narrative biography (300-500 words)
- `organizations` (array of strings): List of affiliated organizations
- `github_username` (string): GitHub username
- `followers` (number): GitHub follower count (from input github_profile)
- `social_profiles` (object): Dictionary of social media URLs
  - Keys: "github", "website", "twitter", "linkedin", etc.
  - Values: Full URLs

## Execution Instructions

### Step 1: Extract Factual Information

Review all input sources and create a fact list:

**From GitHub Profile:**
- Full name (use `name` field)
- Current role (from `bio` field)
- Location (exact string from `location` field)
- Company affiliation (from `company` field)
- Social media links (from `blog`, `twitter_username`)
- Organization memberships (from `organizations` array)

**From Video Descriptions:**
- Job titles mentioned
- Company/organization affiliations
- Role descriptions
- Achievements or credentials

**From Transcript Excerpts:**
- Self-described roles
- Work responsibilities
- Project involvement
- Team or organizational context

**Critical Rule:** Only extract information explicitly stated in sources. Do NOT infer, guess, or extrapolate.

### Step 2: Resolve Conflicts

If sources provide conflicting information:

1. **Prioritize GitHub profile** for current role and location (most up-to-date)
2. **Use most recent video** for role descriptions (check dates)
3. **Cross-reference multiple sources** for consistency
4. **When uncertain:** Use the most conservative claim

**Example Conflict:**
- GitHub bio: "Kubernetes Advocate at CNCF"
- Video description (2024): "Senior Developer at Company X"
- Transcript (2025): "I work at CNCF on Kubernetes"

**Resolution:** Use "Kubernetes Advocate at CNCF" (most recent + consistent)

### Step 3: Synthesize Biography

Write a 2-3 paragraph biography (300-500 words) following this structure:

**Paragraph 1: Current Role and Focus**
- Introduce presenter with full name
- State current role and organization
- Describe primary responsibilities or focus areas
- Mention geographic location

**Paragraph 2: Expertise and Involvement**
- Describe technical expertise areas
- Highlight specific projects or technologies
- Mention organizational involvement (SIGs, working groups)
- Describe scope of work (what they work on)

**Paragraph 3: Community Presence**
- Mention speaking engagements or presentations
- Describe contribution to the community
- Note areas of advocacy or thought leadership
- Connect to broader impact or mission

**Tone Guidelines:**
- Third-person narrative ("Jeffrey Sica is..." not "I am...")
- Professional and factual
- Present tense for current activities
- Avoid marketing language or superlatives
- Use concrete, verifiable statements

### Step 4: Compile Metadata

**Organizations:**
- Normalize organization names (proper capitalization)
- Include all affiliations mentioned in sources
- Order by prominence (primary employer first)

**GitHub Data:**
- Extract `github_username` from input profile
- Extract `followers` count directly from input profile (pass through as-is)

**Social Profiles:**
- Construct full URLs from usernames
- GitHub: `https://github.com/{username}`
- Twitter: `https://twitter.com/{username}` (if available)
- Website: Use exact URL from GitHub blog field
- Only include profiles explicitly mentioned in sources

### Step 5: Validate Output

Before returning, verify:

- [ ] Full name matches GitHub profile
- [ ] Current role is from most recent source
- [ ] Location is exact string from GitHub
- [ ] Biography is 300-500 words
- [ ] Biography uses third-person voice
- [ ] All organizations are properly capitalized
- [ ] GitHub username is correct
- [ ] Followers count matches input (pass-through)
- [ ] All social profile URLs are valid
- [ ] No speculative or inferred information

## Examples

### Example 1: Complete Profile

**Input:**
```json
{
  "github_profile": {
    "name": "Sarah Chen",
    "bio": "Cloud Native Engineer at Acme Corp",
    "location": "San Francisco, CA",
    "organizations": ["kubernetes", "cncf"],
    "followers": 342,
    "company": "Acme Corp",
    "blog": "https://sarahchen.dev"
  },
  "video_descriptions": [
    "Sarah Chen from Acme Corp discusses service mesh adoption",
    "Sarah Chen, Cloud Native Engineer, shares insights on Istio"
  ],
  "transcript_excerpts": [
    "I'm Sarah, I work on cloud infrastructure at Acme Corp",
    "In my role, I focus on service mesh and observability"
  ]
}
```

**Output:**
```json
{
  "full_name": "Sarah Chen",
  "current_role": "Cloud Native Engineer at Acme Corp",
  "location": "San Francisco, CA",
  "biography": "Sarah Chen is a Cloud Native Engineer at Acme Corp, based in San Francisco, California. She specializes in cloud infrastructure, service mesh architectures, and observability solutions for distributed systems.\n\nWith deep expertise in CNCF technologies, Sarah focuses on implementing and scaling service mesh solutions like Istio in production environments. Her work involves designing resilient architectures that enable teams to build and operate cloud-native applications with confidence.\n\nSarah is an active member of the Kubernetes and CNCF communities, regularly sharing her experiences with service mesh adoption and observability best practices at conferences and meetups.",
  "organizations": ["Acme Corp", "Kubernetes", "CNCF"],
  "github_username": "sarahchen",
  "social_profiles": {
    "github": "https://github.com/sarahchen",
    "website": "https://sarahchen.dev"
  }
}
```

### Example 2: Minimal Profile

**Input:**
```json
{
  "github_profile": {
    "name": "Alex Kumar",
    "bio": "DevOps Engineer",
    "location": "London, UK",
    "organizations": ["prometheus"],
    "followers": 87
  },
  "video_descriptions": [
    "Alex Kumar presents monitoring strategies"
  ],
  "transcript_excerpts": [
    "I work on observability and monitoring solutions"
  ]
}
```

**Output:**
```json
{
  "full_name": "Alex Kumar",
  "current_role": "DevOps Engineer",
  "location": "London, UK",
  "biography": "Alex Kumar is a DevOps Engineer based in London, United Kingdom, with expertise in observability and monitoring solutions. He focuses on building robust monitoring infrastructure for cloud-native applications.\n\nAlex is actively involved in the Prometheus community, contributing to observability practices and tooling. His work centers on helping teams implement effective monitoring strategies for distributed systems.\n\nThrough conference presentations and community engagement, Alex shares practical insights on observability patterns and monitoring best practices with the broader cloud-native community.",
  "organizations": ["Prometheus"],
  "github_username": "alexkumar",
  "social_profiles": {
    "github": "https://github.com/alexkumar"
  }
}
```

### Example 3: Multiple Organizations

**Input:**
```json
{
  "github_profile": {
    "name": "Maria Garcia",
    "bio": "Principal Engineer @ TechCo | CNCF Ambassador",
    "location": "Barcelona, Spain",
    "organizations": ["cncf", "kubernetes", "helm", "argo"],
    "followers": 567,
    "company": "TechCo",
    "blog": "https://mariagarcia.io",
    "twitter_username": "mariagarcia"
  },
  "video_descriptions": [
    "Maria Garcia, CNCF Ambassador and Principal Engineer at TechCo",
    "Speaker: Maria Garcia discusses GitOps and continuous delivery"
  ],
  "transcript_excerpts": [
    "I'm Maria, Principal Engineer at TechCo and CNCF Ambassador",
    "I contribute to Argo CD and Helm projects",
    "My work involves GitOps adoption across enterprise teams"
  ]
}
```

**Output:**
```json
{
  "full_name": "Maria Garcia",
  "current_role": "Principal Engineer at TechCo | CNCF Ambassador",
  "location": "Barcelona, Spain",
  "biography": "Maria Garcia is a Principal Engineer at TechCo and a Cloud Native Computing Foundation (CNCF) Ambassador, based in Barcelona, Spain. She specializes in GitOps practices, continuous delivery, and enterprise adoption of cloud-native technologies.\n\nWith significant contributions to the Argo CD and Helm projects, Maria focuses on helping enterprise teams adopt GitOps workflows and modern deployment practices. Her technical expertise spans continuous delivery architectures, Kubernetes operations, and developer experience improvements for large-scale organizations.\n\nAs a CNCF Ambassador, Maria actively promotes cloud-native technologies and best practices through conference presentations, community engagement, and thought leadership. She regularly shares insights on GitOps adoption patterns, continuous delivery strategies, and lessons learned from enterprise cloud-native transformations.",
  "organizations": ["TechCo", "CNCF", "Kubernetes", "Helm", "Argo"],
  "github_username": "mariagarcia",
  "social_profiles": {
    "github": "https://github.com/mariagarcia",
    "website": "https://mariagarcia.io",
    "twitter": "https://twitter.com/mariagarcia"
  }
}
```

## Quality Guidelines

### Factual Accuracy
- **Every claim must be traceable** to input sources
- Use exact wording from sources when possible
- Do not infer relationships, roles, or expertise
- When sources conflict, use most recent and authoritative

### Biography Style
- **Length:** 300-500 words (2-3 paragraphs)
- **Voice:** Third-person narrative
- **Tense:** Present tense for current activities
- **Tone:** Professional, factual, respectful
- **Structure:** Role → Expertise → Community presence

### Metadata Completeness
- Include all organizations mentioned in sources
- Construct valid URLs for all social profiles
- Use exact location string from GitHub
- Normalize organization names (proper caps)

## Common Pitfalls to Avoid

### ❌ Speculation and Inference

**Bad:**
```
"Maria is likely one of the most influential voices in the GitOps community"
```
**Why:** Not stated in sources, speculative superlative

**Good:**
```
"Maria contributes to Argo CD and Helm projects and shares GitOps insights as a CNCF Ambassador"
```

### ❌ Marketing Language

**Bad:**
```
"Sarah is a rockstar engineer who revolutionized cloud infrastructure at Acme Corp"
```
**Why:** Hyperbolic, not factual

**Good:**
```
"Sarah Chen is a Cloud Native Engineer at Acme Corp, specializing in service mesh and observability"
```

### ❌ First-Person Voice

**Bad:**
```
"I work on Kubernetes contributor experience at CNCF"
```
**Why:** Biography should be third-person

**Good:**
```
"Jeffrey works on Kubernetes contributor experience at CNCF"
```

### ❌ Vague Descriptions

**Bad:**
```
"Alex does various things in the cloud-native space"
```
**Why:** Not specific or informative

**Good:**
```
"Alex focuses on observability and monitoring solutions for cloud-native applications"
```

### ❌ Unverifiable Claims

**Bad:**
```
"Maria is an expert in all CNCF projects and has contributed to dozens of repositories"
```
**Why:** Cannot be verified from input sources

**Good:**
```
"Maria contributes to Argo CD and Helm projects"
```

### ❌ Missing Source Priority

**Bad:** Using old video description role when GitHub profile shows current role

**Good:** Prioritize GitHub profile for current information

## Important Notes

- This skill feeds into `presenter-profile-generation` skill
- Biography quality directly impacts profile completeness
- Be conservative - better to omit than to speculate
- When sources are sparse, keep biography brief but accurate
- Organizations array feeds into stats table generation
- Social profiles enable user discovery and verification

## Validation Checklist

Before returning output, verify:

- [ ] Full name matches GitHub exactly
- [ ] Current role is most recent from sources
- [ ] Location string is exact match
- [ ] Biography is 300-500 words
- [ ] Biography has 2-3 paragraphs
- [ ] Third-person voice used throughout
- [ ] No speculative or marketing language
- [ ] All organizations properly capitalized
- [ ] GitHub username extracted correctly
- [ ] Social profile URLs are valid
- [ ] No information invented or inferred
- [ ] All claims traceable to input sources
