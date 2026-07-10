# LocalAI template

Go `text/template` manifest for one LocalAI master, optional workers, and one
NGINX gateway per proxy node.

## Parameters

| Parameter | Type | Description |
| --- | --- | --- |
| `group` | string | Cluster identifier used in names and labels |
| `namespace` | string | Kubernetes namespace |
| `schedulerName` | string | Scheduler used by generated Pods |
| `portbind` | int | Master P2P/gRPC port |
| `p2pToken` | string | Token shared by master and workers |
| `masterHostname` | string | Optional node hosting the master |
| `useGPU` | bool | Requests GPU resources for the master |
| `numWorker` | int | Number of worker Deployments |
| `workerBasePort` | int | Port of worker 0; incremented for each worker |
| `workerNodeName` | string | Optional node hosting all workers |
| `workerMemoryLimitGi` | int | Optional worker memory limit in GiB |
| `models_pvc` | string | Models PVC name |
| `backend_pvc` | string | Backend PVC name |
| `proxyNodes` | list | Nodes hosting gateway Deployments |
| `proxyNodePort` | int | Fixed gateway NodePort; `0` requests automatic allocation |

The renderer must provide the `until` and `add` template functions. See
[`values.example.yaml`](values.example.yaml) for a complete input.
