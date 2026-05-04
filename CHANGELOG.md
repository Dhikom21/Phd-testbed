# Changelog

## [0.1.0] - 2026-05-04

### Added
- Verification layer with HTTP API (`/verify`, `/health`)
- Static policy engine: protected-resource block, namespace allow-list
- Kubernetes RBAC (Layer 5) for agent-sandbox namespace
- JSONL action audit log
- Docker image: phd-testbed/verification:0.1.0
- kind multi-node cluster + KWOK mirror cluster
- Prometheus + Grafana stack deployed (instrumentation pending)
- All policy paths tested via curl: ALLOW, BLOCK-protected, BLOCK-namespace


### Notes
- Observability stack runs but does not yet scrape application metrics
  
