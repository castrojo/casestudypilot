"""Hyperlink mappings for case studies."""

# Company URLs (add more as needed)
COMPANY_URLS = {
    "Intuit": "https://www.intuit.com",
    "Adobe": "https://www.adobe.com",
    "Spotify": "https://www.spotify.com",
    "Adidas": "https://www.adidas.com",
    "Apple": "https://www.apple.com",
    "Netflix": "https://www.netflix.com",
}

# CNCF Project URLs
PROJECT_URLS = {
    "Kubernetes": "https://kubernetes.io",
    "Argo CD": "https://argoproj.github.io/cd/",
    "Argo Rollouts": "https://argoproj.github.io/rollouts/",
    "Argo Workflows": "https://argoproj.github.io/workflows/",
    "Helm": "https://helm.sh",
    "Prometheus": "https://prometheus.io",
    "Istio": "https://istio.io",
    "Envoy": "https://www.envoyproxy.io",
    "Fluentd": "https://www.fluentd.org",
    "Jaeger": "https://www.jaegertracing.io",
    "Linkerd": "https://linkerd.io",
    "Cilium": "https://cilium.io",
    "Falco": "https://falco.org",
    "Harbor": "https://goharbor.io",
    "etcd": "https://etcd.io",
    "CoreDNS": "https://coredns.io",
    "containerd": "https://containerd.io",
    "Datadog": "https://www.datadoghq.com",
    "Jenkins": "https://www.jenkins.io",
    "Traefik": "https://traefik.io",
}

# CNCF Glossary terms
GLOSSARY_TERMS = {
    "microservices": "https://glossary.cncf.io/microservices-architecture/",
    "cloud-native": "https://glossary.cncf.io/cloud-native-tech/",
    "cloud native": "https://glossary.cncf.io/cloud-native-tech/",
    "container orchestration": "https://glossary.cncf.io/container-orchestration/",
    "GitOps": "https://glossary.cncf.io/gitops/",
    "continuous delivery": "https://glossary.cncf.io/continuous-delivery/",
    "declarative": "https://glossary.cncf.io/infrastructure-as-code/",
    "infrastructure as code": "https://glossary.cncf.io/infrastructure-as-code/",
    "progressive delivery": "https://glossary.cncf.io/progressive-delivery/",
    "canary deployment": "https://glossary.cncf.io/canary-deployment/",
    "blue-green deployment": "https://glossary.cncf.io/blue-green-deployment/",
    "service mesh": "https://glossary.cncf.io/service-mesh/",
}


def add_hyperlinks(text: str, company_name: str = None) -> str:
    """Add hyperlinks to company names, CNCF projects, and glossary terms.

    Args:
        text: The markdown text to enhance
        company_name: The primary company name to link

    Returns:
        Text with hyperlinks added
    """
    import re

    # Add company URL if provided and not already linked
    if company_name and company_name in COMPANY_URLS:
        company_url = COMPANY_URLS[company_name]
        # Only link if not already markdown-linked
        pattern = rf"\b{re.escape(company_name)}\b(?![^\[]*\])"
        # Link first occurrence in each paragraph
        text = re.sub(pattern, f"[{company_name}]({company_url})", text, count=1)

    # Add CNCF project URLs
    for project, url in PROJECT_URLS.items():
        # Match bold project names **ProjectName** that aren't already linked
        pattern = rf"\*\*{re.escape(project)}\*\*(?!\()"
        text = re.sub(pattern, f"**[{project}]({url})**", text)

    # Add glossary terms (case insensitive)
    for term, url in GLOSSARY_TERMS.items():
        # Match term not already in markdown link or bold
        pattern = rf"\b{re.escape(term)}\b(?![^\[]*\])(?![^\*]*\*\*)"
        # Only replace first occurrence per paragraph to avoid over-linking
        paragraphs = text.split("\n\n")
        for i, para in enumerate(paragraphs):
            paragraphs[i] = re.sub(
                pattern, f"[{term}]({url})", para, count=1, flags=re.IGNORECASE
            )
        text = "\n\n".join(paragraphs)

    return text
