"""Generador de tráfico: simula usuarios consultando saldo y transfiriendo. Registra cada petición en CSV."""
import sys, time, csv, random, threading, requests
out, dur = sys.argv[1], float(sys.argv[2])
t0 = time.time(); open(out + ".t0", "w").write(str(t0)); rows = []; lk = threading.Lock()
def worker():
    while time.time() - t0 < dur:
        op = "saldo" if random.random() < 0.6 else "transferir"
        s = time.time()
        try:
            r = requests.get("http://127.0.0.1:8000/saldo/u1", timeout=10) if op == "saldo" \
                else requests.post("http://127.0.0.1:8000/transferir", timeout=10)
            code = r.status_code; deg = int(op == "saldo" and r.ok and r.json().get("degradado", False))
        except Exception:
            code, deg = 0, 0
        with lk: rows.append((round(s - t0, 3), op, code, round((time.time() - s) * 1000, 1), deg))
        time.sleep(0.1)
ths = [threading.Thread(target=worker) for _ in range(4)]
[t.start() for t in ths]; [t.join() for t in ths]
with open(out, "w", newline="") as f:
    w = csv.writer(f); w.writerow(["t", "op", "status", "lat_ms", "degradado"]); w.writerows(sorted(rows))
