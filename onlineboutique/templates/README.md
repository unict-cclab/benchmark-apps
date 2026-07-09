# Online Boutique manifest template

`manifest.yaml.tmpl` is a Go `text/template` manifest intended for the
experiment executor. It accepts this input:

```yaml
schedulerName: scheduler-plugins-scheduler
group: onlineboutique-a
proxyNodes:
  - ctx-cluster-01-app-01
  - ctx-cluster-01-app-02
```

- `schedulerName` is required and is assigned to every application and node
  proxy Pod.
- `group` is required and must be a valid Kubernetes label value. It identifies
  one tenant in metrics and resource selectors.
- `proxyNodes` is a required, non-empty list of Kubernetes node names. The
  template creates one node-pinned proxy Deployment for every entry.
- `hpa.enabled` optionally renders `autoscaling/v2` HorizontalPodAutoscaler
  resources for the core Deployments.
- `cpa.enabled` optionally renders CustomPodAutoscaler resources for the
  request-serving core Deployments plus a shared Redis instance for controller
  state. The CPA mode expects the Custom Pod Autoscaler operator CRD to already
  be installed and `cpa.image` to point at the autoscaler image.
- The template creates `minAvailable: 1` PodDisruptionBudgets for the core
  application Deployments. Single-replica Deployments will therefore be
  protected from voluntary descheduler evictions until they are scaled above
  one replica.

The executor should render templates with Go's `missingkey=error` option and
validate all three inputs before rendering. Node names must also be usable in a
Kubernetes resource name after the `gateway-` prefix.

Tenants with different groups must be installed in different namespaces. The
group changes labels and selectors, but application resource and Service names
remain stable so that the Online Boutique services can resolve one another.
The node proxy consequently forwards to the namespace-local `frontend`
Service.

The proxy Service uses a Kubernetes-assigned NodePort, avoiding cluster-wide
port collisions between tenants. After applying the manifest, the executor can
read it from `service/node-proxy`.

The template also creates Istio `DestinationRule` resources for the internal
application Services. They enable locality-aware `LEAST_REQUEST` balancing so
Envoy prefers endpoints in the caller's locality when Istio sidecars are
injected. Nodes should be labeled with Kubernetes locality labels such as
`topology.kubernetes.io/region` and `topology.kubernetes.io/zone`; map those
labels to the network-cost groups used by the experiment.
