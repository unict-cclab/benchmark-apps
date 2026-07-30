# Online Boutique template

Go `text/template` manifest for Online Boutique, node-pinned gateways, and one
optional autoscaler implementation.

## Parameters

| Parameter | Type | Description |
| --- | --- | --- |
| `group` | string | Identifier used in labels and selectors |
| `schedulerName` | string | Scheduler used by application and gateway Pods |
| `minReplicas` | int | Initial replicas for application Deployments |
| `cpuRequest` | string | CPU request shared by all application microservices |
| `memoryRequest` | string | Memory request shared by all application microservices |
| `proxyNodes` | list | Nodes hosting gateway Deployments |
| `proxyNodePort` | int | Fixed gateway NodePort; `0` requests automatic allocation |
| `autoscaler.hpa.config` | map | HPA configuration rendered and validated by this template |
| `autoscaler.cpa.plugin` | string | Plugin name passed to the CPA container |
| `autoscaler.cpa.config` | map | CPA renderer configuration |

The HPA config requires `minReplicas`, `maxReplicas`, and a native Kubernetes
`metrics` list. Its optional `targets` list overrides the application-specific
default workloads.

The renderer supports the `sophos` and `polaris` CPA plugins. Both use a flat
camelCase schema and share `image`, `imagePullPolicy`, `intervalMillis`,
`minReplicas`, `maxReplicas`, `prometheusURL`, `targetResponseTimeMillis`,
`targetPercentage`, `timeRange`, and optional `targets` fields.

The Sophos config additionally requires `redisImage`, `redisHost`, `kp`, `ki`,
`kd`, `downscaleStabilizationSeconds`, and `marginRatio`, and supports
`excludeOutboundResponseTime`. More completely, it requires `image`,
`intervalMillis`, `minReplicas`, `maxReplicas`, `prometheusURL`,
`targetResponseTimeMillis`, `targetPercentage`, `timeRange`, `redisImage`,
`redisHost`, `kp`, `ki`, `kd`, `downscaleStabilizationSeconds`, and
`marginRatio`. `excludeOutboundResponseTime` defaults to `false`,
`imagePullPolicy` defaults to `IfNotPresent`, and `targets` can override the
default workloads.

The renderer validates these fields, serializes the complete camelCase object
as `config.json` in a ConfigMap, and mounts it into every CPA container. Plugins
consume that object directly; plugin settings are not rendered as environment
variables. The CPA `spec.config` contains only the operator's `interval`,
`minReplicas`, and `maxReplicas` settings.

The Polaris config requires `downscaleStabilizationSeconds` and deliberately
does not support `excludeOutboundResponseTime`: its metric is the inbound
service latency. `targetPercentage` and `timeRange` default to `0.95` and `1m`.
Its evaluator applies the latency-SLO proportional strategy described in the
[Polaris publication](https://dsg.tuwien.ac.at/~sd/papers/ICFEC_2022_T_Pusztai_High_Level.pdf).

```yaml
autoscaler:
  cpa:
    plugin: polaris
    config:
      image: ghcr.io/unict-cclab/custom-pod-autoscaler:latest
      imagePullPolicy: IfNotPresent
      intervalMillis: 15000
      minReplicas: 2
      maxReplicas: 10
      prometheusURL: http://prometheus.observability:9090/api/v1/query
      targetResponseTimeMillis: 250
      downscaleStabilizationSeconds: 300
```

The renderer rejects multiple autoscaler implementations, unknown
implementations, unsupported CPA plugins, missing fields, invalid numeric
ranges, and invalid replica bounds. See
[`values.example.yaml`](values.example.yaml) for a complete Sophos input.
