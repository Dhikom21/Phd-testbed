# PhD Testbed: Verification Layer 

A research testbed for studying simulation-gated execution as a safety
mechanism for unconstrained AI agents acting on Kubernetes clusters.

## Status (v0.1.0)

| Component | Status |
|---|---|
| kind cluster (3 nodes) | Working |
| KWOK mirror cluster | Working |
| Verification HTTP service | Working |
| Static policy engine | Working |
| Kubernetes RBAC (Layer 5) | Working |
| Action audit log (JSONL) | Working |
| End-to-end ALLOWED + BLOCKED paths | Tested via curl |
| Prometheus + Grafana stack | Deployed (not yet instrumented) |
| OpenClaw container | Pending |
| KWOK simulation step | Pending |

## Architecture

Defense-in-depth across five layers:
1. Prompt rules — written into the LLM's system prompt
2. Output schema — forces JSON shape via guided decoding
3. Container hardening — non-root, read-only FS, no caps
4. Verification layer (this repo) — policy decisions; future: KWOK simulation
5. Kubernetes RBAC — cluster-enforced limits on the agent's identity

See `COMMANDS.md` for the operational command reference.

## Pending

- v0.2.0 — Prometheus metrics from verification service + Grafana dashboards
- v0.3.0 — OpenClaw container (LLM agent) integration
- v0.4.0 — KWOK simulation step in policy decisions (research contribution)
