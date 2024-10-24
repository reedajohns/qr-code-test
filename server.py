# server.py
from flask import Flask, render_template, request, jsonify
from datetime import datetime
import os
import json
import threading
import time
import requests
import platform
import socket
import uuid
import re

app = Flask(__name__)

CONFIG_FILE = 'config.json'
HEARTBEAT_INTERVAL = 5  # Default interval in seconds
heartbeat_thread = None
heartbeat_event = threading.Event()
config = {}
last_heartbeat_status = None
last_heartbeat_time = None

# Load configuration from file if it exists
def load_config():
    global config
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
            print("Loaded configuration from file.")

def save_config():
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f)
    print("Configuration saved to file.")

def get_system_info():
    system_info = {}
    try:
        system_info["platform"] = platform.system()
        system_info["platform_release"] = platform.release()
        system_info["platform_version"] = platform.version()
        system_info["architecture"] = platform.machine()
        system_info["hostname"] = socket.gethostname()
        system_info["ip_address"] = socket.gethostbyname(socket.gethostname())
        system_info["mac_address"] = ":".join(re.findall("..", "%012x" % uuid.getnode()))
        system_info["processor"] = platform.processor()
    except Exception as e:
        print(f"Error getting system info: {e}")
    return system_info

def send_healthcheck():
    global config, last_heartbeat_status, last_heartbeat_time
    system_info = get_system_info()
    current_time = int(time.time())

    healthcheck = {
        "timestamp": time.time(),
        "timezone": time.tzname[0],
        "system_info": system_info,
        "device_id": config.get("DEVICE_ID", ""),
        "name": config.get("DEVICE_NAME", ""),
        "timestamp": current_time,
        "timezone": "UTC",
        "type": "NVIDIA Jetson",
        "owner": "",
        "container": {
            "id": config.get("DEVICE_ID", ""),
            "name": config.get("DEVICE_ID", ""),
            "status": "running",
            "inference_server_version": "",
            "last_inference_timestamp": current_time
        }
    }

    try:
        response = requests.post(
            url=f"{config.get('ROBOFLOW_API_BASE_URL')}/device-healthcheck-v2?api_key={config.get('ROBOFLOW_API_KEY')}",
            json=healthcheck,
            timeout=5,
        )
        response.raise_for_status()
        print("Sent healthcheck", response.json())
        last_heartbeat_status = "Success"
    except Exception as e:
        print(f"Error sending healthcheck: {e}")
        last_heartbeat_status = f"Error: {e}"
    finally:
        last_heartbeat_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def heartbeat_task():
    global HEARTBEAT_INTERVAL, heartbeat_event
    while not heartbeat_event.is_set():
        send_healthcheck()
        heartbeat_event.wait(HEARTBEAT_INTERVAL)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process_qr', methods=['POST'])
def process_qr():
    global config, heartbeat_thread, heartbeat_event
    data = request.get_json()
    print(f"Received data: {data}")  # Debugging statement
    qr_data = data.get('data', '')
    print(f"Received QR data: {qr_data}")  # Debugging statement
    try:
        # Assuming the QR code data is a JSON string
        config = json.loads(qr_data)
        save_config()

        # Restart the heartbeat thread
        if heartbeat_thread and heartbeat_thread.is_alive():
            heartbeat_event.set()
            heartbeat_thread.join()

        heartbeat_event.clear()
        heartbeat_thread = threading.Thread(target=heartbeat_task, daemon=True)
        heartbeat_thread.start()

        return jsonify({'status': 'success', 'data': config})
    except json.JSONDecodeError:
        return jsonify({'status': 'error', 'message': 'Invalid QR code data'}), 400

@app.route('/get_state', methods=['GET'])
def get_state():
    global config, HEARTBEAT_INTERVAL, last_heartbeat_status, last_heartbeat_time
    state = {
        'config': config,
        'heartbeat_interval': HEARTBEAT_INTERVAL,
        'last_heartbeat_status': last_heartbeat_status,
        'last_heartbeat_time': last_heartbeat_time,
    }
    return jsonify(state)

@app.route('/set_heartbeat_interval', methods=['POST'])
def set_heartbeat_interval():
    global HEARTBEAT_INTERVAL, heartbeat_event, heartbeat_thread
    data = request.get_json()
    interval = data.get('interval', HEARTBEAT_INTERVAL)
    try:
        interval = float(interval)
        if interval <= 0:
            raise ValueError("Interval must be positive")
        HEARTBEAT_INTERVAL = interval

        # Restart the heartbeat thread with new interval
        if heartbeat_thread and heartbeat_thread.is_alive():
            heartbeat_event.set()
            heartbeat_thread.join()

        heartbeat_event.clear()
        heartbeat_thread = threading.Thread(target=heartbeat_task, daemon=True)
        heartbeat_thread.start()

        return jsonify({'status': 'success', 'interval': HEARTBEAT_INTERVAL})
    except ValueError as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

@app.route('/clear_config', methods=['POST'])
def clear_config():
    global config, heartbeat_event, heartbeat_thread
    config = {}
    if os.path.exists(CONFIG_FILE):
        os.remove(CONFIG_FILE)
        print("Configuration file deleted.")

    # Stop the heartbeat thread
    if heartbeat_thread and heartbeat_thread.is_alive():
        heartbeat_event.set()
        heartbeat_thread.join()

    return jsonify({'status': 'success'})

if __name__ == '__main__':
    # Load existing configuration if available
    load_config()

    # Start heartbeat if config is available
    if config:
        heartbeat_event.clear()
        heartbeat_thread = threading.Thread(target=heartbeat_task, daemon=True)
        heartbeat_thread.start()

    # Run the Flask app with SSL
    from werkzeug.serving import make_ssl_devcert
    import ssl

    # Ensure SSL certificate exists
    cert_path = os.path.join('certs', 'cert')
    key_path = os.path.join('certs', 'key')

    context = (cert_path + '.pem', key_path + '.pem')
    app.run(host='0.0.0.0', port=8000, ssl_context=context)
