"""Acciones y sondas (probes) personalizadas para Chaos Toolkit."""
import os, signal, subprocess, time, requests
HERE = os.path.dirname(os.path.abspath(__file__))
def _pidfile(port): return f"/tmp/core_{port}.pid"

def start_node(port: int):
    p = subprocess.Popen(["python3", os.path.join(HERE, "core_node.py"), str(port), f"core-{port}"],
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    open(_pidfile(port), "w").write(str(p.pid))
    for _ in range(50):
        try:
            requests.get(f"http://127.0.0.1:{port}/health", timeout=0.3); return {"started": port}
        except Exception: time.sleep(0.1)
    return {"started": port, "warning": "no responde"}

def kill_node(port: int):
    pid = int(open(_pidfile(port)).read())
    os.kill(pid, signal.SIGKILL)
    return {"killed": port, "pid": pid}

def inject_latency(port: int, ms: int):
    return requests.post(f"http://127.0.0.1:{port}/chaos/latency/{ms}", timeout=2).json()

def success_ratio(samples: int = 20, max_ms: int = 1000) -> float:
    """Porcentaje de operaciones de usuario exitosas y rápidas (< max_ms) a través del gateway."""
    ok = 0
    for i in range(samples):
        s = time.time()
        try:
            r = requests.get("http://127.0.0.1:8000/saldo/u1", timeout=5) if i % 2 == 0 \
                else requests.post("http://127.0.0.1:8000/transferir", timeout=5)
            if r.ok and (time.time() - s) * 1000 < max_ms: ok += 1
        except Exception:
            pass
    return round(ok / samples, 3)
