# Experimento de ingeniería del caos: billetera digital

Laboratorio para comparar cómo responden dos arquitecturas de una billetera digital cuando falla su backend transaccional. Las fallas se inyectan con [Chaos Toolkit](https://chaostoolkit.org/).

- **Monolítica**: un solo nodo core, sin timeouts ni conmutación. Es la arquitectura que se infiere del incidente.
- **Resiliente**: dos nodos core, timeout de 0,5 s, reintento con conmutación (failover), circuit breaker y degradación gradual (la consulta de saldo se sirve desde caché).

## Componentes

| Archivo | Descripción |
|---|---|
| `core_node.py` | Nodo core simulado (Flask): consulta de saldo, transferencias y un endpoint para inyectar latencia. |
| `gateway.py` | API Gateway en modo `monolitico` o `resiliente`. |
| `load.py` | Generador de tráfico: 4 usuarios concurrentes que consultan saldo (60 %) y transfieren (40 %). Registra cada petición en CSV. |
| `chaoslab.py` | Acciones y sondas personalizadas para Chaos Toolkit (levantar/matar nodos, inyectar latencia, medir la tasa de éxito). |
| `E1_caida_nodo.json` | E1: caída abrupta del nodo core principal. |
| `E2_latencia.json` | E2: latencia de 3 s en el nodo core principal. |
| `E3_caida_total.json` | E3: caída de ambos nodos core (peor caso). |
| `run_all.sh` | Corre los tres experimentos contra las dos arquitecturas con tráfico de fondo. |
| `analyze.py` | Calcula métricas antes, durante y después de la falla y las guarda en `results/metrics.json`. |
| `plots.py` | Genera las figuras del informe en `results/fig/`. |

## Hipótesis de estado estable

Los usuarios pueden consultar saldo y transferir: al menos el 95 % de las operaciones termina con éxito en menos de 1 s.

## Cómo ejecutarlo

Requiere Linux (o WSL), Python 3, `bash`, `curl` y `pkill`.

```bash
pip install -r requirements.txt
./run_all.sh          # tarda unos minutos; deja CSV, journals y salidas en results/
python3 analyze.py    # genera results/metrics.json
python3 plots.py      # genera las figuras en results/fig/
```

## Resultados

Disponibilidad y latencia p95 durante la ventana de falla (de `results/metrics.json`):

| Experimento | Arquitectura | Hipótesis | Operaciones exitosas | p95 |
|---|---|---|---|---|
| E1 · caída de un nodo | Monolítica | No se cumple | 0 % | 7 ms |
| E1 · caída de un nodo | Resiliente | Se cumple | 100 % | 8 ms |
| E2 · latencia de 3 s | Monolítica | No se cumple | 100 % | 3007 ms |
| E2 · latencia de 3 s | Resiliente | Se cumple | 100 % | 506 ms |
| E3 · caída total | Monolítica | No se cumple | 0 % | 6 ms |
| E3 · caída total | Resiliente | No se cumple | 61,3 % | 5 ms |

En E3 ninguna arquitectura puede transferir porque no queda backend, pero la resiliente sigue respondiendo las consultas de saldo desde caché (modo degradado).
