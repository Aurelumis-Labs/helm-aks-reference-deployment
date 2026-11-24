# helm-aks-reference-deployment

A small, complete reference for deploying a containerized Flask service to Kubernetes with Helm: one chart, per-environment values, health probes, safe rolling updates, rollback, and a CI pipeline for AKS.

> Status: learning and reference project. Everything here uses synthetic names. The chart has not been validated against a production cluster.

## What this demonstrates

- Packaging an application as a Helm chart with helpers, labels and per-environment values (`values-dev.yaml`, `values-prod.yaml`).
- Safe rollouts: rolling update with `maxUnavailable: 0`, readiness and liveness probes, resource requests and limits, PodDisruptionBudget.
- Container hardening: non-root user, read-only root filesystem, dropped capabilities.
- Release safety: `helm upgrade --install --atomic`, `helm history`, `helm rollback`.
- A CI path (GitHub Actions for lint and render; Azure Pipelines for build, push to ACR and deploy to AKS).

## Layout

```text
app/                  Flask service, Dockerfile
chart/                Helm chart (templates, values, dev and prod overrides)
kind-config.yaml      local cluster (kind) with a host port mapping
azure-pipelines.yml   build to ACR, deploy to AKS with helm --atomic
.github/workflows/    chart lint and render, image build
docs/architecture.md  diagram and design decisions
docs/adr/0005-...     decision record: Helm chart with per-environment values
```

## Run it locally (Docker Desktop and kind)

Install kind, kubectl and helm first (Windows: `winget install Kubernetes.kind Kubernetes.kubectl Helm.Helm`).

```bash
kind create cluster --name lab --config kind-config.yaml
docker build -t hello-flask:1.0.0 app/
kind load docker-image hello-flask:1.0.0 --name lab

helm lint chart
helm template hello chart -f chart/values-dev.yaml     # read the generated YAML
helm install hello chart -f chart/values-dev.yaml
kubectl get pods,svc
curl http://localhost:8080/                             # version and environment
```

## Upgrade, break, roll back

```bash
docker build -t hello-flask:1.1.0 app/ && kind load docker-image hello-flask:1.1.0 --name lab
helm upgrade hello chart -f chart/values-dev.yaml --set image.tag=1.1.0
helm history hello

# deploy a broken image on purpose; --atomic restores the previous release
helm upgrade hello chart -f chart/values-dev.yaml --set image.tag=does-not-exist --atomic --timeout 60s
helm rollback hello 1
```

## Environments

```bash
helm upgrade hello chart -f chart/values-prod.yaml --set image.tag=1.1.0
kubectl get pods   # three replicas and a PodDisruptionBudget
```

## Deploy to AKS from Azure DevOps

`azure-pipelines.yml` builds the image with ACR Tasks and deploys with `helm upgrade --install --atomic`. Replace the placeholders (`<your-acr-name>`, service connection, resource group, cluster) before use, and gate production with an Azure DevOps environment approval.

## License

MIT
