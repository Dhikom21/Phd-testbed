PROTECTED_RESOURCES = {
    "deployment/payments",
    "deployment/database",
    "deployment/auth",
    "namespace/agent-sandbox",
    "namespace/kube-system",
}
DESTRUCTIVE_VERBS = {"delete", "destroy"}
ALLOWED_NAMESPACES = {"agent-sandbox", ""}

def decide(action):
    verb = action.get("verb", "").lower()
    resource = action.get("resource", "")
    namespace = action.get("namespace", "")

    if verb in DESTRUCTIVE_VERBS and resource in PROTECTED_RESOURCES:
        return {"status": "BLOCKED", "reason": "protected-resource",
                "policy": "no-destruction-of-protected"}

    if namespace and namespace not in ALLOWED_NAMESPACES:
        return {"status": "BLOCKED", "reason": "namespace-not-allowed",
                "policy": "agent-sandbox-only"}

    return {"status": "ALLOWED", "reason": "default-allow", "policy": "default"}
