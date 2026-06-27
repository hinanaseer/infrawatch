from flask import Flask, jsonify, render_template
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import platform, socket, time, random, os

app = Flask(__name__)

REQUEST_COUNT = Counter("app_requests_total", "Total HTTP requests", ["method", "endpoint", "status"])
REQUEST_LATENCY = Histogram("app_request_latency_seconds", "Request latency", ["endpoint"])

def get_system_info():
    return {
        "hostname":    socket.gethostname(),
        "platform":    platform.system(),
        "python":      platform.python_version(),
        "environment": os.getenv("APP_ENV", "production"),
        "version":     os.getenv("APP_VERSION", "1.0.0"),
        "cloud":       os.getenv("CLOUD_PROVIDER", "local"),
    }

def mock_services():
    services = [
        {"name": "Database",      "icon": "🗄️"},
        {"name": "Cache (Redis)", "icon": "⚡"},
        {"name": "Message Queue", "icon": "📨"},
        {"name": "Auth Service",  "icon": "🔐"},
        {"name": "Storage (S3)",  "icon": "🪣"},
        {"name": "CDN",           "icon": "🌐"},
    ]
    for svc in services:
        svc["status"]  = random.choice(["healthy", "healthy", "healthy", "degraded"])
        svc["latency"] = round(random.uniform(2, 120), 1)
        svc["uptime"]  = round(random.uniform(99.1, 99.99), 2)
    return services

@app.route("/")
def index():
    start    = time.time()
    info     = get_system_info()
    services = mock_services()
    healthy  = sum(1 for s in services if s["status"] == "healthy")
    duration = round((time.time() - start) * 1000, 2)
    REQUEST_COUNT.labels("GET", "/", "200").inc()
    return render_template("index.html", info=info, services=services,
                           healthy=healthy, total=len(services), response_time=duration)

@app.route("/health")
def health():
    return jsonify({"status": "healthy", "version": os.getenv("APP_VERSION", "1.0.0")})

@app.route("/api/status")
def api_status():
    return jsonify({"system": get_system_info(), "services": mock_services()})

@app.route("/metrics")
def metrics():
    return generate_latest(), 200, {"Content-Type": CONTENT_TYPE_LATEST}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8888, debug=True)