---
name: presenter-profile-generation
description: Generates polished presenter profile content in professional narrative style
version: 1.0.0
---

# Presenter Profile Generation Skill

## Purpose

Generate publication-ready presenter profile content using biographical data and talk aggregation analysis. Produces professional narrative sections that showcase the presenter's expertise, contributions, and impact in the cloud-native community.

## Style Guidelines

**Tone:** Professional, factual, respectful  
**Voice:** Third-person narrative  
**Tense:** Present tense for current activities, past tense for completed talks  
**Length:** 1000-2000 words total across all sections  
**Paragraphs:** 3-5 sentences each  
**Formatting:** Markdown with bold emphasis, bullet lists, proper headers  

## Input Format

The input combines outputs from `biography-extraction` and `talk-aggregation` skills:

```json
{
  "biography": {
    "full_name": "Jeffrey Sica",
    "current_role": "Kubernetes & OSS Advocate at CNCF",
    "location": "Minneapolis, MN",
    "biography": "Jeffrey Sica is a Kubernetes and open source advocate...",
    "organizations": ["CNCF", "Kubernetes", "Kubernetes SIGs"],
    "github_username": "jeefy",
    "social_profiles": {
      "github": "https://github.com/jeefy",
      "website": "https://jeefy.dev"
    }
  },
  "aggregation": {
    "expertise_areas": [
      {
        "area": "Kubernetes",
        "context": "Deep community involvement, contributor experience",
        "talk_count": 5,
        "evidence": ["Container orchestration", "Kubernetes governance"]
      }
    ],
    "cncf_projects": [
      {
        "name": "Kubernetes",
        "talk_count": 5,
        "usage_context": "Container orchestration, community governance",
        "first_mention": "2022-05",
        "latest_mention": "2025-10"
      }
    ],
    "recurring_themes": [
      "Open source community sustainability",
      "Scalable infrastructure patterns"
    ],
    "talk_summaries": [
      {
        "video_id": "abc123",
        "title": "Kubernetes Community Deep Dive",
        "date": "2025-10-15",
        "summary": "Explores best practices...",
        "key_points": ["Point 1", "Point 2"],
        "topics": ["Kubernetes", "Community"]
      }
    ],
    "stats": {
      "total_talks": 8,
      "years_active": {"first": 2022, "latest": 2025, "span": 3},
      "total_speaking_minutes": 272,
      "most_active_year": 2025,
      "average_talk_length_minutes": 34
    }
  }
}
```

## Output Format

```json
{
  "overview": "Markdown content introducing the presenter (200-400 words)...",
  "expertise": "Markdown content describing expertise areas (300-500 words)...",
  "talk_highlights": "Markdown content with chronological talk list (400-600 words)...",
  "key_themes": "Markdown content discussing recurring themes (200-400 words)...",
  "stats_table": {
    "total_talks": "8 presentations",
    "years_active": "2022 - 2025 (3 years)",
    "top_technology": "Kubernetes (5 talks)",
    "primary_focus": "Community Management & GitOps",
    "github_followers": "159",
    "organizations": "CNCF, Kubernetes, Kubernetes SIGs",
    "total_speaking_time": "4 hours 32 minutes"
  }
}
```

## Section Specifications

### Overview Section (200-400 words)

**Purpose:** Introduce the presenter, their role, and community presence

**Content to include:**
- Full name and current role
- Geographic location
- Primary organizational affiliations
- Community involvement overview
- Speaking activity summary (high-level)

**Structure:**
```markdown
## Overview

[Paragraph 1: Introduction and current role]
[Paragraph 2: Community involvement and contributions]
[Paragraph 3: Speaking activity and reach]
```

**Style:**
- Start with biographical introduction
- Incorporate biography text naturally
- Mention speaking activity scale
- End with community impact statement

**Example:**
```markdown
## Overview

Jeffrey Sica is a Kubernetes and open source advocate at the Cloud Native Computing Foundation (CNCF), based in Minneapolis, Minnesota. He focuses on improving contributor experience and building sustainable open source communities.

With deep expertise in Kubernetes ecosystem development, Jeffrey works closely with maintainers and contributors to enhance project governance and community engagement. His work spans multiple aspects of the Kubernetes project, including special interest groups (SIGs) and community management initiatives.

Over the past three years, Jeffrey has delivered 8 presentations at major cloud-native conferences and events, sharing insights on community management, Kubernetes governance, and sustainable open source development. His talks have reached audiences at KubeCon, CloudNativeCon, and community meetups, establishing him as a recognized voice in the CNCF ecosystem.
```

### Expertise Section (300-500 words)

**Purpose:** Detail the presenter's technical expertise and areas of focus

**Content to include:**
- Expertise areas from aggregation data
- Specific evidence of expertise
- CNCF projects associated with expertise
- Context for how expertise manifests
- Evolution of expertise over time (if applicable)

**Structure:**
```markdown
## Areas of Expertise

[Introductory paragraph: Overview of expertise landscape]

### [Expertise Area 1]
[2-3 sentences describing this area with evidence]

### [Expertise Area 2]
[2-3 sentences describing this area with evidence]

[Closing paragraph: Integration or cross-cutting themes]
```

**Style:**
- Use H3 headers for each major expertise area
- Bold CNCF project names
- Include specific evidence from talks
- Connect expertise to practical applications
- Mention talk counts to show depth

**Example:**
```markdown
## Areas of Expertise

Jeffrey's technical expertise spans multiple dimensions of cloud-native computing, with particular depth in community management, Kubernetes operations, and GitOps practices.

### Kubernetes and Container Orchestration

Jeffrey demonstrates deep expertise in **Kubernetes** architecture and operations, having delivered 5 presentations on topics including container orchestration patterns, cluster scalability, and contributor experience improvements. His knowledge extends to Kubernetes governance models, special interest group management, and community sustainability practices. He has addressed both technical implementation challenges and organizational aspects of Kubernetes adoption.

### Open Source Community Management

With 3 talks focused on community sustainability and governance, Jeffrey brings significant expertise to open source project management. His insights cover contributor onboarding, maintainer support systems, building inclusive communities, and establishing sustainable governance models. This expertise is particularly evident in his work with Kubernetes SIGs and CNCF community initiatives.

### GitOps and Continuous Delivery

Jeffrey's expertise in GitOps workflows includes practical experience with **Argo CD** and **Flux**, having presented on continuous delivery patterns, declarative deployment strategies, and GitOps best practices. He addresses both technical implementation details and organizational adoption challenges.

These expertise areas intersect in Jeffrey's holistic approach to cloud-native development, where technical excellence, community sustainability, and operational best practices converge to create resilient, scalable systems.
```

### Talk Highlights Section (400-600 words)

**Purpose:** Showcase individual talks with summaries and key takeaways

**Content to include:**
- Chronological list of talks (most recent first)
- Talk title and date
- Event name (if available)
- 50-100 word summary for each talk
- Key topics covered
- Notable insights or unique value

**Structure:**
```markdown
## Talk Highlights

[Introductory paragraph: Overview of speaking portfolio]

### "[Talk Title]" (Month YYYY)
*[Event name if available]*

[2-3 sentence summary]

**Key Topics:** [Topic 1, Topic 2, Topic 3]

### "[Talk Title 2]" (Month YYYY)
...
```

**Style:**
- List talks in reverse chronological order (newest first)
- Bold talk titles or use quotes
- Include date in (Month YYYY) format
- Italicize event names
- Keep summaries concise (2-3 sentences)
- Use "Key Topics" to list 3-5 main subjects

**Example:**
```markdown
## Talk Highlights

Jeffrey has delivered presentations at major cloud-native conferences and community events, consistently focusing on topics that bridge technical implementation and community sustainability. His talks provide actionable insights drawn from real-world experience managing large open source projects.

### "Kubernetes Community Management Best Practices" (October 2025)
*KubeCon North America 2025*

Explores best practices for managing large open source communities, focusing on contributor onboarding, maintainer support, and sustainable governance models. Draws from Kubernetes community experience to provide actionable insights for growing projects.

**Key Topics:** Community Management, Kubernetes, Governance, Contributor Experience, Sustainability

### "GitOps with Argo CD and Flux" (March 2025)
*CloudNativeCon Europe 2025*

Compares Flux and Argo CD as GitOps continuous delivery tools, evaluating features, architecture, and production suitability. Discusses declarative deployment patterns and multi-cluster management strategies.

**Key Topics:** GitOps, Argo CD, Flux, Continuous Delivery, Kubernetes

### "Scaling Kubernetes Contributor Experience" (November 2024)
*Kubernetes Community Day Minneapolis*

Documents approaches to improving contributor experience at scale, including automation tooling, documentation improvements, and mentorship programs. Shares lessons from Kubernetes SIG leadership.

**Key Topics:** Kubernetes, Contributor Experience, Automation, Mentorship, SIG Leadership

[Continue for all talks...]
```

### Key Themes Section (200-400 words)

**Purpose:** Identify and discuss recurring themes across the presenter's talks

**Content to include:**
- Recurring themes from aggregation data
- How themes manifest across multiple talks
- Connection between themes and expertise
- Impact or implications of these themes
- Forward-looking perspective (if applicable)

**Structure:**
```markdown
## Recurring Themes

[Introductory paragraph: Overview of thematic focus]

[Paragraph 2: Discussion of 2-3 major themes with examples]

[Paragraph 3: Integration or implications of these themes]
```

**Style:**
- Group related themes together
- Use bold for theme names on first mention
- Reference specific talks as examples
- Connect themes to broader community trends
- Avoid listing themes without discussion

**Example:**
```markdown
## Recurring Themes

Jeffrey's presentations consistently explore the intersection of technical excellence and community sustainability, revealing a cohesive philosophy about building resilient open source ecosystems.

A central theme across his work is **open source community sustainability**—the practices and governance structures that enable projects to thrive long-term. This appears in multiple talks, from community management best practices to contributor experience improvements. Jeffrey emphasizes that technical success depends on healthy community dynamics, including clear governance, maintainer support systems, and inclusive contributor pathways.

**Scalable infrastructure patterns** represent another recurring focus, particularly in his Kubernetes-related presentations. Jeffrey explores not just technical scalability (managing thousands of nodes or pods), but also organizational scalability—how teams and communities scale their operations effectively. This includes automation, self-service capabilities, and architectural patterns that enable growth without proportional increases in operational burden.

**GitOps workflows and best practices** emerge as a third major theme, reflecting the shift toward declarative, Git-based infrastructure management. Jeffrey's talks on Argo CD, Flux, and continuous delivery patterns demonstrate practical approaches to implementing GitOps at scale, including tool selection, multi-cluster management, and integration with existing workflows.

These themes underscore Jeffrey's holistic perspective: sustainable cloud-native success requires technical sophistication, healthy community practices, and modern operational patterns working in concert.
```

### Stats Table (Structured Data)

**Purpose:** Provide quick-reference statistics about the presenter's speaking activity

**Format:** Dictionary of key-value pairs (not markdown, just structured data)

**Fields to include:**

| Key | Format | Example |
|-----|--------|---------|
| `total_talks` | "{N} presentations" | "8 presentations" |
| `years_active` | "{first} - {latest} ({span} years)" | "2022 - 2025 (3 years)" |
| `top_technology` | "{project} ({count} talks)" | "Kubernetes (5 talks)" |
| `primary_focus` | "{area} & {area}" or "{area}, {area}, {area}" | "Community Management & GitOps" |
| `github_followers` | "{count}" | "159" |
| `organizations` | "{org}, {org}, {org}" | "CNCF, Kubernetes, Kubernetes SIGs" |
| `total_speaking_time` | "{hours} hours {minutes} minutes" | "4 hours 32 minutes" |

**Calculation Details:**

- **total_talks:** From `stats.total_talks`
- **years_active:** From `stats.years_active` object
- **top_technology:** CNCF project with highest talk_count
- **primary_focus:** Top 2-3 expertise areas (by talk_count), joined with "&" or ","
- **github_followers:** From `biography.github_username` (fetch from GitHub API if available, otherwise omit)
- **organizations:** From `biography.organizations`, comma-separated
- **total_speaking_time:** Convert `stats.total_speaking_minutes` to hours and minutes
  - Hours: `minutes // 60`
  - Remaining minutes: `minutes % 60`

**Example:**
```json
{
  "total_talks": "8 presentations",
  "years_active": "2022 - 2025 (3 years)",
  "top_technology": "Kubernetes (5 talks)",
  "primary_focus": "Community Management & GitOps",
  "github_followers": "159",
  "organizations": "CNCF, Kubernetes, Kubernetes SIGs",
  "total_speaking_time": "4 hours 32 minutes"
}
```

## Execution Instructions

### Step 1: Prepare Context

Load and organize input data:

**From Biography:**
- Full name, current role, location
- Biography text (will be adapted, not copied verbatim)
- Organizations list
- Social profiles

**From Aggregation:**
- Expertise areas (ordered by talk_count descending)
- CNCF projects (ordered by talk_count descending)
- Recurring themes
- Talk summaries (with titles and dates - fetch from video metadata)
- Statistics

### Step 2: Generate Overview Section

**Opening Paragraph:**
- Adapt biography introduction (don't copy-paste verbatim)
- Include full name, role, location
- Mention primary organizations

**Middle Paragraph:**
- Summarize expertise focus (high-level)
- Mention community involvement
- Reference key contributions

**Closing Paragraph:**
- State speaking activity statistics (total talks, years active)
- Mention venue types (conferences, meetups)
- Make impact statement

**Length Target:** 200-400 words (3 paragraphs)

### Step 3: Generate Expertise Section

**Opening Paragraph:**
- Introduce expertise landscape
- Mention number of expertise areas
- Preview major themes

**Expertise Area Subsections:**
- Create H3 header for each top 3-5 expertise areas
- 2-3 sentences per area
- Include:
  - Description of expertise
  - Evidence from talks (specific topics)
  - Associated CNCF projects (bolded)
  - Talk count for credibility
  - Practical context (what they do with this expertise)

**Closing Paragraph:**
- Integrate expertise areas
- Show how they connect
- Mention holistic approach or philosophy

**Length Target:** 300-500 words

### Step 4: Generate Talk Highlights Section

**Opening Paragraph:**
- Describe speaking portfolio
- Mention venue diversity
- Preview thematic consistency

**Talk Entries:**
- Order talks reverse chronologically (newest first)
- For each talk:
  - H3 header: "Talk Title" (Date in Month YYYY format)
  - Italicized event name (if available)
  - 2-3 sentence summary (adapt from aggregation summary, don't copy verbatim)
  - "Key Topics:" line with 3-5 topics

**Number of Talks to Include:**
- All talks if ≤8 talks
- Most recent 10-12 if >8 talks
- Always include most recent year completely

**Length Target:** 400-600 words

### Step 5: Generate Key Themes Section

**Opening Paragraph:**
- Identify overarching pattern in themes
- Set up thematic discussion

**Body Paragraphs:**
- Discuss 2-4 major themes
- For each theme:
  - Bold theme name on first mention
  - Explain how it manifests across talks
  - Give 1-2 specific examples (reference talk titles)
  - Discuss why this theme matters

**Closing Paragraph:**
- Synthesize themes
- Show interconnections
- Make broader observation about presenter's perspective or philosophy

**Length Target:** 200-400 words

### Step 6: Generate Stats Table

Calculate each field:

**total_talks:** 
```
"{stats.total_talks} presentations"
```

**years_active:**
```
"{first} - {latest} ({span} years)"
Example: "2022 - 2025 (3 years)"
```

**top_technology:**
```
Find CNCF project with max talk_count
"{project.name} ({project.talk_count} talks)"
Example: "Kubernetes (5 talks)"
```

**primary_focus:**
```
Take top 2-3 expertise areas (by talk_count)
If 2 areas: "{area1} & {area2}"
If 3 areas: "{area1}, {area2}, & {area3}"
Example: "Community Management & GitOps"
```

**github_followers:**
```
"{biography.github_followers}" (if available)
Otherwise omit this field
```

**organizations:**
```
Join biography.organizations with ", "
Example: "CNCF, Kubernetes, Kubernetes SIGs"
```

**total_speaking_time:**
```
hours = stats.total_speaking_minutes // 60
minutes = stats.total_speaking_minutes % 60
"{hours} hours {minutes} minutes"
Example: "4 hours 32 minutes"
```

### Step 7: Validate Output

Before returning, verify:

**Overview:**
- [ ] 200-400 words
- [ ] 3 paragraphs
- [ ] Includes name, role, location
- [ ] Mentions speaking statistics
- [ ] Professional tone

**Expertise:**
- [ ] 300-500 words
- [ ] H3 headers for expertise areas
- [ ] CNCF projects bolded
- [ ] Evidence cited for each area
- [ ] Integration paragraph at end

**Talk Highlights:**
- [ ] 400-600 words
- [ ] Reverse chronological order
- [ ] All recent talks included
- [ ] Summaries are 2-3 sentences
- [ ] Key topics listed for each

**Key Themes:**
- [ ] 200-400 words
- [ ] Discusses 2-4 major themes
- [ ] Examples reference specific talks
- [ ] Synthesis paragraph at end

**Stats Table:**
- [ ] All required fields present
- [ ] Formatting matches specification
- [ ] Calculations are correct
- [ ] Units are included (talks, years, minutes)

**Overall:**
- [ ] Total length 1000-2000 words
- [ ] Third-person voice throughout
- [ ] No marketing language or superlatives
- [ ] Markdown formatting correct
- [ ] Professional, respectful tone

## Quality Checklist

Before returning generated content, verify:

- [ ] All sections present (Overview, Expertise, Talk Highlights, Key Themes, Stats Table)
- [ ] Total word count 1000-2000
- [ ] Third-person voice throughout
- [ ] Present tense for current activities, past for talks
- [ ] CNCF project names bolded
- [ ] Markdown syntax correct
- [ ] No marketing fluff or superlatives
- [ ] All statistics accurate and formatted correctly
- [ ] Talk order is reverse chronological
- [ ] Themes discussed with examples, not just listed
- [ ] Professional and respectful tone
- [ ] No speculation beyond input data

## Examples

### Example 1: Community-Focused Presenter

**Input Snippet:**
```json
{
  "biography": {
    "full_name": "Jeffrey Sica",
    "current_role": "Kubernetes & OSS Advocate at CNCF",
    "location": "Minneapolis, MN"
  },
  "aggregation": {
    "expertise_areas": [
      {"area": "Kubernetes", "talk_count": 5},
      {"area": "Community Management", "talk_count": 3}
    ],
    "cncf_projects": [
      {"name": "Kubernetes", "talk_count": 5}
    ],
    "recurring_themes": [
      "Open source community sustainability",
      "Contributor experience"
    ],
    "stats": {
      "total_talks": 8,
      "years_active": {"first": 2022, "latest": 2025, "span": 3},
      "total_speaking_minutes": 272
    }
  }
}
```

**Output Snippet (Overview Section):**
```markdown
## Overview

Jeffrey Sica is a Kubernetes and open source advocate at the Cloud Native Computing Foundation (CNCF), based in Minneapolis, Minnesota. He specializes in community management, contributor experience, and sustainable open source development practices.

With deep involvement in Kubernetes governance and community initiatives, Jeffrey focuses on building resilient, inclusive open source communities. His work with Kubernetes special interest groups (SIGs) and CNCF community programs has shaped contributor pathways and maintainer support systems that enable projects to thrive at scale.

Over the past three years, Jeffrey has delivered 8 presentations at major cloud-native conferences, community meetups, and virtual events, establishing himself as a recognized voice on community sustainability and Kubernetes ecosystem development. His talks consistently address the intersection of technical excellence and healthy community practices.
```

### Example 2: Technical-Focused Presenter

**Input Snippet:**
```json
{
  "biography": {
    "full_name": "Sarah Chen",
    "current_role": "Cloud Native Engineer at Acme Corp",
    "location": "San Francisco, CA"
  },
  "aggregation": {
    "expertise_areas": [
      {"area": "Service Mesh", "talk_count": 4},
      {"area": "Observability", "talk_count": 3}
    ],
    "cncf_projects": [
      {"name": "Istio", "talk_count": 3},
      {"name": "Prometheus", "talk_count": 2}
    ],
    "recurring_themes": [
      "Production reliability patterns",
      "Microservices architecture"
    ],
    "stats": {
      "total_talks": 7,
      "years_active": {"first": 2023, "latest": 2025, "span": 2},
      "total_speaking_minutes": 189
    }
  }
}
```

**Output Snippet (Expertise Section):**
```markdown
## Areas of Expertise

Sarah's technical expertise centers on production-grade microservices infrastructure, with particular depth in service mesh architectures and observability solutions.

### Service Mesh Architecture

Sarah demonstrates significant expertise in **Istio** and service mesh patterns, having delivered 4 presentations on topics including traffic management, security policies, and multi-cluster mesh configurations. Her knowledge spans both technical implementation details and operational best practices for running service meshes at scale in production environments.

### Observability and Monitoring

With 3 talks focused on observability, Sarah brings practical experience with **Prometheus**, distributed tracing, and monitoring strategies for microservices. Her expertise covers metrics collection, alerting strategies, and building observability-driven development cultures within engineering teams.

These expertise areas reflect Sarah's holistic approach to building resilient distributed systems where visibility, control, and reliability work together to enable confident operations.
```

## Common Mistakes to Avoid

### ❌ Copy-Pasting Biography Verbatim

**Bad:** Copying biography text directly into Overview

**Good:** Adapt and contextualize biography content for the overview

### ❌ Listing Instead of Discussing

**Bad (Key Themes section):**
```markdown
The key themes are:
- Community sustainability
- GitOps workflows
- Scalable architecture
```

**Good:**
```markdown
A central theme is community sustainability, appearing in multiple talks from best practices to contributor experience...
```

### ❌ Chronological Talk Order

**Bad:** Oldest talks first

**Good:** Newest talks first (reverse chronological)

### ❌ Missing CNCF Project Formatting

**Bad:** "Jeffrey discussed Kubernetes and Argo CD"

**Good:** "Jeffrey discussed **Kubernetes** and **Argo CD**"

### ❌ Marketing Language

**Bad:** "Jeffrey is a rockstar speaker revolutionizing community management"

**Good:** "Jeffrey focuses on community management practices and sustainable governance"

### ❌ First-Person Voice

**Bad:** "I work on Kubernetes at CNCF"

**Good:** "Jeffrey works on Kubernetes at CNCF"

### ❌ Incorrect Stats Formatting

**Bad:** `"total_talks": "8"` (missing "presentations")

**Good:** `"total_talks": "8 presentations"`

### ❌ Missing Evidence for Expertise

**Bad:** "Jeffrey is an expert in Kubernetes" (unsupported claim)

**Good:** "Jeffrey demonstrates deep expertise in Kubernetes, having delivered 5 presentations on orchestration patterns, governance, and community management"

## Important Notes

- This skill produces final content for presenter profiles
- Output quality determines profile professionalism and usefulness
- Content must be entirely based on input data (no invention)
- Stats table drives metadata display in profile templates
- Length targets ensure comprehensive but readable profiles
- Professional tone reflects well on both presenter and CNCF

## Reference Profiles

Study these speaker profiles for style and tone:
- CNCF Ambassador profiles
- Conference speaker bios
- Open source maintainer profiles
- Technical community leader pages

(Note: Profiles should be factual and professional, not promotional)
