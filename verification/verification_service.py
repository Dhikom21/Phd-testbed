import json, os, subprocess, time, uuid
from flask import Flask, request, jsonify
from policies import decide

app = Flask(__name__)
LOG_FILE = os.environ.get("LOG_FILE", "/app/logs/action_log.jsonl")
KUBE_CONTEXT = os.environ.get("KUBE_CONTEXT", "kind-testbed")

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})

@app.route("/verify", methods=["POST"])
def verify():
    action = request.get_json(force=True)
    action_id = str(uuid.uuid4())[:8]
    timestamp = time.time()

    print(f"[AGENT  ] {action_id}  {action.get('verb'):>6}  {action.get('resource')}", flush=True)
    decision = decide(action)
    mark = "ALLOW" if decision["status"] == "ALLOWED" else "BLOCK"
    print(f"[VERIF  ] {action_id}  {mark}  ({decision['reason']})", flush=True)

    real_outcome = None
    if decision["status"] == "ALLOWED":
        real_outcome = execute_against_cluster(action)
        if real_outcome:
            print(f"[CLUSTER] {action_id}  exit={real_outcome.get('exit_code')}", flush=True)

    record = {"action_id": action_id, "timestamp": timestamp, "action": action,
              "decision": decision, "real_outcome": real_outcome}
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(record) + "\n")

    return jsonify({"action_id": action_id, "decision": decision, "real_outcome": real_outcome})


def execute_against_cluster(action):
    cmd = ["kubectl", "--context", KUBE_CONTEXT, action["verb"], action["resource"]]
    if action.get("namespace"):
        cmd.extend(["-n", action["namespace"]])
    if action.get("verb") == "scale":
        replicas = action.get("params", {}).get("replicas")
        if replicas:
            cmd.append(f"--replicas={replicas}")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        return {"exit_code": result.returncode,
                "stdout": result.stdout[:500],
                "stderr": result.stderr[:500]}
    except subprocess.TimeoutExpired:
        return {"error": "timeout"}
    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    print("=== Verification service starting on :5000 ===", flush=True)
    print(f"Log file: {LOG_FILE}", flush=True)
    print(f"Kube context: {KUBE_CONTEXT}", flush=True)
    app.run(host="0.0.0.0", port=5000)
