"""API Gateway simulado.
Modo 'monolitico': un único nodo core, sin timeouts ni conmutación (arquitectura inferida del incidente).
Modo 'resiliente': dos nodos, timeout corto, reintento con conmutación (failover),
cortocircuito (circuit breaker) y degradación gradual (consulta de saldo desde caché)."""
import sys, time, threading, requests
from flask import Flask, jsonify
app = Flask(__name__)
MODE = sys.argv[1]
NODES = ["http://127.0.0.1:9001"] if MODE == "monolitico" else ["http://127.0.0.1:9001", "http://127.0.0.1:9002"]
TIMEOUT = 30 if MODE == "monolitico" else 0.5
cache = {}
breaker = {n: {"fails": 0, "open_until": 0.0} for n in NODES}
blk = threading.Lock()

def call(method, path):
    last = None
    for n in NODES:
        if MODE == "resiliente":
            with blk:
                if breaker[n]["open_until"] > time.time():
                    continue
        try:
            r = requests.request(method, n + path, timeout=TIMEOUT)
            r.raise_for_status()
            with blk: breaker[n]["fails"] = 0
            return r.json()
        except Exception as e:
            last = e
            if MODE == "resiliente":
                with blk:
                    breaker[n]["fails"] += 1
                    if breaker[n]["fails"] >= 3:
                        breaker[n]["open_until"] = time.time() + 2.0  # semiabierto a los 2 s
    raise RuntimeError(str(last))

@app.get("/health")
def health():
    return jsonify(status="ok", mode=MODE)

@app.get("/saldo/<u>")
def saldo(u):
    try:
        d = call("GET", f"/saldo/{u}"); cache[u] = d; return jsonify(d)
    except Exception:
        if MODE == "resiliente" and u in cache:
            return jsonify({**cache[u], "degradado": True}), 200
        return jsonify(error="servicio no disponible"), 503

@app.post("/transferir")
def transferir():
    try:
        return jsonify(call("POST", "/transferir"))
    except Exception:
        return jsonify(error="servicio no disponible"), 503

if __name__ == "__main__":
    import logging; logging.getLogger("werkzeug").setLevel(logging.ERROR)
    app.run(port=8000, threaded=True)
