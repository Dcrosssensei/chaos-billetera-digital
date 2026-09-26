#!/bin/bash
# Ejecuta cada experimento contra cada arquitectura con tráfico de fondo.
cd "$(dirname "$0")"; mkdir -p results; export PYTHONPATH=$PWD
run() { arch=$1; exp=$2; tag=${arch}_${exp}
  pkill -f "[c]ore_node.py 900"; pkill -f "python3 [g]ateway"; sleep 1
  python3 -c "import chaoslab; chaoslab.start_node(9001); chaoslab.start_node(9002)"
  python3 gateway.py $arch >/dev/null 2>&1 & sleep 1.5
  curl -s localhost:8000/saldo/u1 >/dev/null
  python3 load.py results/$tag.csv 45 & LP=$!
  sleep 5
  chaos --log-file results/$tag.log run $exp.json --journal-path results/$tag.journal.json > results/$tag.out 2>&1
  wait $LP
  pkill -f "[c]ore_node.py 900"; pkill -f "python3 [g]ateway"; sleep 1
  echo "$tag: $(python3 -c "import json;j=json.load(open('results/$tag.journal.json'));print(j['status'], j['deviated'])")"
}
for arch in monolitico resiliente; do for exp in E1_caida_nodo E2_latencia; do run $arch $exp; done; done
run monolitico E3_caida_total; run resiliente E3_caida_total
