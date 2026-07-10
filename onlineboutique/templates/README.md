# Online Boutique template

Go `text/template` manifest for Online Boutique, node-pinned gateways, and
optional HPA or Custom Pod Autoscaler resources.

## Parameters

| Parameter | Type | Description |
| --- | --- | --- |
| `group` | string | Identifier used in labels and selectors |
| `schedulerName` | string | Scheduler used by application and gateway Pods |
| `minReplicas` | int | Initial replicas for application Deployments |
| `proxyNodes` | list | Nodes hosting gateway Deployments |
| `proxyNodePort` | int | Fixed gateway NodePort; `0` requests automatic allocation |
| `hpa.enabled` | bool | Generates HorizontalPodAutoscalers |
| `hpa.minReplicas` | int | HPA minimum replicas |
| `hpa.maxReplicas` | int | HPA maximum replicas |
| `hpa.targetCPUUtilizationPercentage` | int | HPA CPU target |
| `cpa.enabled` | bool | Generates CustomPodAutoscalers and Redis |
| `cpa.image` | string | Autoscaler image |
| `cpa.imagePullPolicy` | string | Autoscaler image pull policy |
| `cpa.intervalMillis` | int | Control interval in milliseconds |
| `cpa.minReplicas` | int | CPA minimum replicas |
| `cpa.maxReplicas` | int | CPA maximum replicas |
| `cpa.prometheusURL` | string | Prometheus query endpoint |
| `cpa.targetResponseTimeMillis` | number | Target response time |
| `cpa.targetPercentage` | number | Target percentile |
| `cpa.timeRange` | string | Prometheus query range |
| `cpa.redisImage` | string | Redis image |
| `cpa.redisHost` | string | Redis Service hostname |
| `cpa.kp`, `cpa.ki`, `cpa.kd` | number | PID coefficients |
| `cpa.downscaleStabilization` | int | Downscale stabilization in seconds |

Do not enable HPA and CPA together. See
[`values.example.yaml`](values.example.yaml) for a complete input.
