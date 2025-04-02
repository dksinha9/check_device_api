from flask import Flask, request, jsonify
from flask_cors import CORS  # ✅ Add this
import socket
import datetime
from requests.auth import HTTPBasicAuth
import requests

app = Flask(__name__)
CORS(app)  # ✅ This enables CORS for all routes

@app.route('/')
def index():
    return 'Flask is live!'

@app.route('/api/check-device', methods=['POST'])
def check_device():
    data = request.json
    ip = data.get('ip')
    port = data.get('port', 80)

    if not ip:
        return jsonify({"error": "IP is required"}), 400

    try:
        socket.setdefaulttimeout(3)
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

@app.route('/api/router-info', methods=['POST'])
def get_router_info():
    data = request.json
    ip = data.get('ip')
    username = data.get('username')
    password = data.get('password')

    if not ip or not username:
        return jsonify({"error": "IP and username are required"}), 400

    url = f"https://{ip}/rest/system/resource"

    try:
        response = requests.get(
            url,
            auth=HTTPBasicAuth(username, password),
            verify=False  # Accept self-signed certs (for MikroTik)
        )
        return jsonify(response.json())

    except Exception as e:
        return jsonify({"error": "Failed to fetch router info", "details": str(e)}), 500


def find_user_id(ip, username, password, user_name):
    """Helper function to find a user by name and return their .id"""
    query_url = f"https://{ip}/rest/user-manager/user/print"
    query_payload = {
        ".query": [f"=name={user_name}"]
    }

    try:
        response = requests.post(
            query_url,
            auth=HTTPBasicAuth(username, password),
            json=query_payload,
            verify=False  # Allow self-signed cert
        )

        users = response.json()

        # Loop through and find exact name match
        for user in users:
            if user.get("name") == user_name:
                return user.get(".id")
        return None

    except Exception as e:
        print("Error finding user:", e)
        return None


@app.route("/api/enable-internet", methods=["POST"])
def enable_internet():
    data = request.json
    ip = data.get("ip")
    username = data.get("username")
    password = data.get("password")
    user_name = data.get("user_name")

    if not all([ip, username, password, user_name]):
        return jsonify({"error": "Missing required fields"}), 400

    user_id = find_user_id(ip, username, password, user_name)
    if not user_id:
        return jsonify({"error": "User not found"}), 404

    try:
        enable_url = f"https://{ip}/rest/user-manager/user/enable"
        payload = {".id": user_id}

        response = requests.post(
            enable_url,
            auth=HTTPBasicAuth(username, password),
            json=payload,
            verify=False
        )

        return jsonify({
            "status": "enabled",
            "user_id": user_id
        })

    except Exception as e:
        return jsonify({"error": "Enable failed", "details": str(e)}), 500


@app.route("/api/disable-internet", methods=["POST"])
def disable_internet():
    data = request.json
    ip = data.get("ip")
    username = data.get("username")
    password = data.get("password")
    user_name = data.get("user_name")

    if not all([ip, username, password, user_name]):
        return jsonify({"error": "Missing required fields"}), 400

    user_id = find_user_id(ip, username, password, user_name)
    if not user_id:
        return jsonify({"error": "User not found"}), 404

    try:
        disable_url = f"https://{ip}/rest/user-manager/user/disable"
        payload = {".id": user_id}

        response = requests.post(
            disable_url,
            auth=HTTPBasicAuth(username, password),
            json=payload,
            verify=False
        )

        return jsonify({
            "status": "disabled",
            "user_id": user_id
        })

    except Exception as e:
        return jsonify({"error": "Disable failed", "details": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)