from flask import Flask, request
import threading

app = Flask(__name__)

@app.post("/set_departure")
def set_departure():
    time = request.json.get("time")
    print(f"[API] Departure time set to: {time}")
    return {"status": "ok"}

def start_api():
    thread = threading.Thread(target=lambda: app.run(host="0.0.0.0", port=5000))
    thread.daemon = True
    thread.start()
