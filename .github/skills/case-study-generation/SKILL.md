---
name: case-study-generation
description: Generates polished case study sections
version: 1.0.0
---

# Case Study Generation Skill

## Purpose

Generate publication-ready case study content in CNCF style using analyzed transcript data.

## Style Guidelines

**Tone:** Professional, technical, factual
**Voice:** Third-person narrative
**Tense:** Past tense for actions, present for current state
**Length:** 500-1500 words total
**Paragraphs:** 3-5 sentences each
**Formatting:** Markdown with bold metrics

## Section Specifications

### Overview (2-3 paragraphs, 150-300 words)

**Purpose:** Introduce the company and set context

**Content to include:**
- Company name, industry, and size
- Business context and market
- Why cloud-native matters to them
- High-level technology landscape

**Style:**
- Start with company introduction
- Build context progressively
- End with transition to challenge

**Example:**
```markdown
Intuit is a global financial software company serving over 100 million customers
worldwide. Operating in a highly regulated industry, the company needed robust,
scalable infrastructure to support its flagship products including TurboTax,
QuickBooks, and Mint.

As Intuit's customer base grew exponentially, the engineering teams faced
increasing pressure to deliver features faster while maintaining security and
compliance. Traditional deployment processes couldn't keep pace with business
demands, creating bottlenecks that impacted product velocity.
```

### Challenge (2-3 paragraphs + bullet list, 200-400 words)

**Purpose:** Describe specific problems faced

**Content to include:**
- Technical limitations
- Business pressures
- Scale/complexity issues
- Pain points for teams

**Structure:**
```markdown
[Paragraph describing context]

[Paragraph detailing specific problems]

Key challenges:
- Specific challenge 1
- Specific challenge 2
- Specific challenge 3
- Specific challenge 4
```

**Style:**
- Be specific and concrete
- Quantify problems when possible
- Use bullet points for clarity
- Lead naturally into solution

**Example:**
```markdown
Before adopting cloud-native technologies, Intuit's deployment process was
slow and error-prone. Release cycles took weeks, and deployments often
required manual intervention and late-night maintenance windows.

The existing infrastructure couldn't scale elastically, leading to
over-provisioning and wasted resources. Teams lacked visibility into
application health and performance, making troubleshooting difficult.

Key challenges:
- **2-3 hour deployment times** with frequent rollback failures
- Manual configuration management across 50+ microservices
- Inconsistent environments between development and production
- Limited observability into distributed application behavior
```

### Solution (3-4 paragraphs, 300-500 words)

**Purpose:** Explain how CNCF technologies solved problems

**Content to include:**
- CNCF projects adopted (bold project names)
- Implementation approach
- Architecture decisions
- Integration with existing systems

**Style:**
- Lead with technology choices
- Explain rationale for selections
- Describe implementation phases
- Highlight key integrations
- Bold CNCF project names

**Example:**
```markdown
Intuit adopted **Kubernetes** as its container orchestration platform,
providing a unified infrastructure layer across all environments. The
platform standardized deployments and enabled elastic scaling based on
actual demand.

To implement GitOps practices, the team chose **Argo CD** for continuous
delivery. All infrastructure and application configurations moved to Git
repositories, enabling version control, code review, and automated
deployments. **Helm** charts standardized package management across teams.

The architecture incorporated **Prometheus** for metrics collection and
**Jaeger** for distributed tracing. This observability stack gave teams
real-time visibility into application behavior and performance bottlenecks.

Integration with existing CI/CD pipelines was gradual. Teams migrated
services incrementally, validating each migration before proceeding. This
phased approach minimized risk while building organizational knowledge.
```

### Impact (2-3 paragraphs + bullet list, 200-400 words)

**Purpose:** Showcase results and improvements

**Content to include:**
- Quantitative metrics (bold them!)
- Business outcomes
- Team benefits
- Future plans

**Structure:**
```markdown
[Paragraph describing overall transformation]

[Paragraph on team/business impact]

Key improvements:
- **Bold metric 1** with context
- **Bold metric 2** with context
- **Bold metric 3** with context
```

**Style:**
- Lead with strongest metrics
- Bold all numbers
- Connect metrics to business value
- End with forward-looking statement

**Example:**
```markdown
The impact of Intuit's cloud-native transformation was substantial and
measurable. Deployment frequency increased dramatically while reliability
improved, enabling teams to deliver value faster and more safely.

Developer productivity soared as teams gained self-service capabilities
and faster feedback loops. The observability improvements reduced mean
time to resolution for incidents, improving customer experience.

Key improvements:
- **50% reduction** in deployment time, from 2 hours to 15 minutes
- **10,000 pods** managed across production clusters
- **Zero downtime deployments** with automated rollback capabilities
- **3x increase** in deployment frequency, from weekly to multiple daily releases

The success of the initial implementation prompted Intuit to expand
adoption across additional teams and workloads.
```

### Conclusion (1-2 paragraphs, 100-200 words)

**Purpose:** Summarize and provide takeaways

**Content to include:**
- Key success factors
- Lessons learned
- Recommendations for others
- Future direction

**Style:**
- Synthesize main points
- Offer insights
- End positively

**Example:**
```markdown
Intuit's journey demonstrates how CNCF technologies can transform enterprise
infrastructure. By adopting **Kubernetes**, **Argo CD**, and complementary
tools, the company achieved both technical excellence and business agility.

The key to success was the incremental, team-driven approach. Rather than
mandating a big-bang migration, Intuit empowered teams to adopt technologies
at their own pace with central support. This built expertise organically
while delivering value continuously.
```

## Quality Checklist

Before returning generated content, verify:

- [ ] All sections present (Overview, Challenge, Solution, Impact, Conclusion)
- [ ] Word count in range (500-1500 total)
- [ ] CNCF project names bolded
- [ ] Metrics bolded and contextualized
- [ ] Bullet lists formatted correctly
- [ ] Professional tone maintained
- [ ] No marketing fluff or superlatives
- [ ] Technical accuracy preserved
- [ ] Smooth narrative flow
- [ ] Markdown syntax correct

## Output Format

Return JSON with each section:

```json
{
  "overview": "Markdown content...",
  "challenge": "Markdown content...",
  "solution": "Markdown content...",
  "impact": "Markdown content...",
  "conclusion": "Markdown content..."
}
```

## Important Notes

- Base content on transcript analysis, don't invent details
- Preserve factual accuracy - only use stated information
- If transcript lacks detail for a section, keep it brief but accurate
- Quality over length - better to be concise than to pad content
- This content goes into the Jinja2 template for final assembly

## Reference Case Studies

Study these CNCF case studies for style and tone:
- https://www.cncf.io/case-studies/intuit/
- https://www.cncf.io/case-studies/adobe/
- https://www.cncf.io/case-studies/spotify/
- https://www.cncf.io/case-studies/adidas/

## Common Mistakes to Avoid

- ❌ Marketing language ("revolutionary", "game-changing")
- ❌ Vague statements without metrics
- ❌ Over-technical implementation details
- ❌ Ignoring business context
- ❌ Forgetting to bold metrics
- ❌ Writing in first person
- ❌ Using future tense for past events
- ❌ Missing bullet lists in Challenge/Impact sections
