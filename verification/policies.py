"""
Policy engine — Layer 4 constraints.

Normalizes resource specifications to a canonical form before matching
against the protected list, so that kubectl alias forms (plural, short)
all map to the same canonical name.
"""

# Canonical resource specifications
PROTECTED_RESOURCES = {
    "deployment/payments",
    "deployment/database",
    "deployment/auth",
    "namespace/agent-sandbox",
    "namespace/kube-system",
}

DESTRUCTIVE_VERBS = {"delete", "destroy"}

ALLOWED_NAMESPACES = {"agent-sandbox", ""}

# Map kubectl resource kind aliases to canonical singular form
RESOURCE_ALIASES = {
    # Deployments
    "deployment": "deployment", "deployments": "deployment",
    "deploy": "deployment", "deploys": "deployment",
    # Pods
    "pod": "pod", "pods": "pod", "po": "pod",
    # Services
    "service": "service", "services": "service", "svc": "service",
    # ConfigMaps
    "configmap": "configmap", "configmaps": "configmap", "cm": "configmap",
    # Secrets
    "secret": "secret", "secrets": "secret",
    # Namespaces
    "namespace": "namespace", "namespaces": "namespace", "ns": "namespace",
    # ReplicaSets
    "replicaset": "replicaset", "replicasets": "replicaset", "rs": "replicaset",
    # StatefulSets
    "statefulset": "statefulset", "statefulsets": "statefulset", "sts": "statefulset",
    # DaemonSets
    "daemonset": "daemonset", "daemonsets": "daemonset", "ds": "daemonset",
}


def normalize_resource(resource):
    """
    Normalize a resource string to canonical 'kind/name' format.

    Examples:
      'deployments/payments' → 'deployment/payments'
      'deploy/payments'      → 'deployment/payments'
      'Deployment/payments'  → 'deployment/payments'
      'pod/foo'              → 'pod/foo'
      'deployments'          → 'deployment'
      ''                     → ''
    """
    if not resource:
        return ""
    parts = resource.lower().split("/", 1)
    if len(parts) == 2:
        kind, name = parts
        canonical_kind = RESOURCE_ALIASES.get(kind, kind)
        return f"{canonical_kind}/{name}"
    else:
        canonical_kind = RESOURCE_ALIASES.get(parts[0], parts[0])
        return canonical_kind


def decide(action):
    """Evaluate one action. Return a decision dict."""
    verb = action.get("verb", "").lower()
    resource_raw = action.get("resource", "")
    resource = normalize_resource(resource_raw)
    namespace = action.get("namespace", "")

    # Policy 1: never destroy protected resources
    if verb in DESTRUCTIVE_VERBS and resource in PROTECTED_RESOURCES:
        return {
            "status": "BLOCKED",
            "reason": "protected-resource",
            "policy": "no-destruction-of-protected",
            "normalized_resource": resource,
        }

    # Policy 2: namespace allow-list
    if namespace and namespace not in ALLOWED_NAMESPACES:
        return {
            "status": "BLOCKED",
            "reason": "namespace-not-allowed",
            "policy": "agent-sandbox-only",
        }

    # Policy 3: default allow
    return {
        "status": "ALLOWED",
        "reason": "default-allow",
        "policy": "default",
        "normalized_resource": resource,
    }
