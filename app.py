from flask import Flask, request, jsonify
import socket
import datetime

app = Flask(__name__)

@app.route('/')
def index():
    return 'Flask is live!'

@app.route('/api/check-device', methods=['POST'])
def check_device():
    data = request.json
    ip = data.get('ip')
    port = data.get('port', 80)  # default to port 80 (HTTP)

    if not ip:
        return jsonify({"error": "IP is required"}), 400

    try:
        socket.setdefaulttimeout(3)  # timeout in seconds
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((ip, port))
        s.close()
        status = "online"
    except Exception:
        status = "offline"

    hostname = socket.getfqdn(ip)

    return jsonify({
        "status": status,
        "ip": ip,
        "hostname": hostname,
        "port": port,
        "timestamp": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)