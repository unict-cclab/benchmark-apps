# LocalAI Cluster Template

Template Kubernetes per la creazione di un cluster **LocalAI** composto da:

- **1 Master**
- **N Worker**
- **1 Gateway NGINX dedicato** (uno per ogni master/cluster)

Il template utilizza la sintassi **Go `text/template`** (stile Helm), ad esempio:

```gotemplate
{{ .group }}
{{ .portbind }}
```

> **Nota:** il Gateway **non utilizza Istio**. Ogni cluster dispone di un reverse proxy **NGINX dedicato**, con rapporto **1:1** tra **Master** e **Gateway**, seguendo la stessa logica di `generateGatewayYAML`.

---

## Variabili del template

| Variabile | Tipo | Descrizione |
|-----------|------|-------------|
| `.group` | string | Identificativo univoco del cluster (es. `cluster-3`). |
| `.portbind` | int | Porta P2P/gRPC del Master (es. `8080`). |
| `.p2pToken` | string | Token P2P generato tramite `generateP2PToken`. |
| `.masterHostname` | string | Hostname del nodo su cui schedulare il Master. Se vuoto, viene utilizzato lo scheduler Kubernetes. |
| `.schedulerName` | string | Nome dello scheduler Kubernetes da utilizzare. |
| `.useGPU` | bool | Abilita o meno le risorse GPU. |
| `.workerBasePort` | int | Porta iniziale dei Worker. Il worker `i` utilizza `workerBasePort + i`. Segue lo stesso schema di `basePort` in `handleScaleWorkers` (`19000 + SeqID * 100`). |
| `.numWorker` | int | Numero di Worker da creare (una Deployment per ciascuno). |
| `.workerNodeName` | string | Hostname del nodo su cui schedulare i Worker (opzionale). |
| `.workerMemoryLimitGi` | int | Limite di memoria per ciascun Worker, espresso in Gi (opzionale). |
| `.gatewayNodePort` | int | `NodePort` fisso del Gateway (opzionale). |
| `.proxyNode` | map | |
---

## Requisiti

Il motore **Go `text/template`** deve registrare nel `FuncMap` le funzioni utilizzate dal template per generare i Worker:

```go
funcMap := template.FuncMap{
    "until": func(n int) []int {
        s := make([]int, n)
        for i := range s {
            s[i] = i
        }
        return s
    },
    "add": func(a, b int) int {
        return a + b
    },
}

tmpl := template.Must(
    template.New("cluster").
        Funcs(funcMap).
        Parse(tplStr),
)
```

Le funzioni vengono utilizzate principalmente per:

- iterare sulla creazione dei Worker (`until`)
- calcolare le porte incrementali (`add`)

---

## Architettura

```text
                +----------------------+
                |     Gateway NGINX    |
                |  (1 per ogni Master) |
                +----------+-----------+
                           |
                           |
                    +------+------+
                    |    Master    |
                    +------+------+
                           |
          +----------------+----------------+
          |                |                |
      +---+---+        +---+---+        +---+---+
      |Worker0|        |Worker1|   ...  |WorkerN|
      +-------+        +-------+        +-------+
```

Ogni cluster è completamente indipendente ed è composto da:

- un Master
- uno o più Worker
- un Gateway NGINX dedicato