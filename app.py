from flask import Flask, request, jsonify
import os
import platform
import datetime
import socket

app = Flask(__name__)

@app.route('/')
def index():
    return 'Flask is live!'

@app.route('/api/check-device', methods=['POST'])
def check_device():
    data = request.json
    ip = data.get('ip')
    if not ip:
        return jsonify({"error": "IP is required"}), 400

    try:
        param = "-n" if platform.system().lower() == "windows" else "-c"
        response = os.system(f"ping {param} 1 {ip}")
        status = "online" if response == 0 else "offline"
        hostname = socket.getfqdn(ip)
    except Exception as e:
        status = "error"
        hostname = str(e)

    return jsonify({
        "status": status,
        "ip": ip,
        "hostname": hostname,
        "timestamp": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)