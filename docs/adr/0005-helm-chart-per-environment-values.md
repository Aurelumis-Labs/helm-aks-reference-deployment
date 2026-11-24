# ADR-0005: Package services as one Helm chart with per-environment values and atomic releases

- **Status:** Proposed
- **Date:** 2026-11-23
- **Decision owner:** Avinash Padaki
- **Jira:** KAN-81
- **Repo / PR:** helm-aks-reference-deployment (PR pending)

## Context

Services deployed to Kubernetes need consistent packaging, environment-specific configuration, safe rollouts and reversible releases. Hand-edited manifests per environment drift, and a failed upgrade can leave a release half-deployed.

## Decision

1. Package each service as one Helm chart. Environments differ in data, not templates: `values.yaml` holds defaults and `values-dev.yaml` / `values-prod.yaml` override them.
2. Roll out with `RollingUpdate`, `maxUnavailable: 0` and `maxSurge: 1`, so capacity never drops during an update.
3. Define readiness and liveness probes on `/healthz`, set resource requests and limits, and run as a non-root user with a read-only root filesystem and all capabilities dropped.
4. Deploy with `helm upgrade --install --atomic` so a failed release rolls itself back.
5. Enable a PodDisruptionBudget in production so node drains cannot take the service below one available pod.

## Alternatives considered

- Raw manifests with Kustomize overlays: no templating language, but every shared change is repeated across overlays and there is no release history or rollback.
- One chart per environment: simple to read, but the charts drift apart.
- Helm without `--atomic`: failed releases need manual rollback and can stay half-deployed.
- A GitOps controller (Argo CD or Flux): stronger drift control, deferred as out of scope for this reference.

## Consequences

**Benefits:** One reviewed chart for every environment; failed releases recover without manual steps; release history and rollback come from Helm.

**Costs and risks:** Helm templating adds a layer to read and debug. `--atomic` rolls back on failure and can hide the root cause, so logs must be captured. A read-only root filesystem breaks applications that write to disk unless a writable volume is mounted. A PodDisruptionBudget on a single replica blocks node drains.

## Non-goals

Ingress and TLS, autoscaling, secrets management, GitOps, multi-cluster rollout.

## Validation criteria

`helm lint` and `helm template` pass for default, dev and prod values. On a local kind cluster, an upgrade succeeds, a deliberately broken image rolls back under `--atomic`, and `helm rollback` restores a previous revision. A node drain respects the PodDisruptionBudget.
