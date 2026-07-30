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

The Sophos CPA config uses a flat camelCase schema. It requires `image`,
`intervalMillis`, `minReplicas`, `maxReplicas`, `prometheusURL`,
`targetResponseTimeMillis`, `targetPercentage`, `timeRange`, `redisImage`,
`redisHost`, `kp`, `ki`, `kd`, `downscaleStabilizationSeconds`, and
`marginRatio`. `excludeOutboundResponseTime` defaults to `false`,
`imagePullPolicy` defaults to `IfNotPresent`, and `targets` can override the
default workloads.

The renderer validates these fields and translates them to the uppercase
configuration names consumed internally by the Sophos container. Environment
variable names are therefore not part of the public template contract.

The renderer rejects multiple autoscaler implementations, unknown
implementations, unsupported CPA plugins, missing fields, invalid numeric
ranges, and invalid replica bounds. See
[`values.example.yaml`](values.example.yaml) for a complete Sophos input.
