"""Nodo 'core' simulado: servicio transaccional de una billetera digital."""
import sys, time, threading
from flask import Flask, jsonify, request
app = Flask(__name__)
NODE = sys.argv[2] if len(sys.argv) > 2 else "core"
state = {"latency_ms": 0}
saldos = {"u1": 150000}
lock = threading.Lock()

def lag():
    if state["latency_ms"]:
        time.sleep(state["latency_ms"] / 1000)

@app.get("/health")
def health():
    return jsonify(status="ok", node=NODE)

@app.get("/saldo/<u>")
def saldo(u):
    lag()
    return jsonify(usuario=u, saldo=saldos.get(u, 0), node=NODE)

@app.post("/transferir")
def transferir():
    lag()
    with lock:
        saldos["u1"] = saldos.get("u1", 0)  # operación simulada
    return jsonify(estado="aprobada", node=NODE)

@app.post("/chaos/latency/<int:ms>")
def set_latency(ms):
    state["latency_ms"] = ms
    return jsonify(latency_ms=ms)

if __name__ == "__main__":
    import logging; logging.getLogger("werkzeug").setLevel(logging.ERROR)
    app.run(port=int(sys.argv[1]), threaded=True)
