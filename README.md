# README: Setting Up the Device Heartbeat Monitor Server on Mac

This README provides step-by-step instructions to set up the Device Heartbeat Monitor server on your Mac. The server allows you to scan QR codes using your iPhone, process the data, and send heartbeat messages to a specified API endpoint.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Project Structure](#project-structure)
- [Setup Instructions](#setup-instructions)
  - [1. Clone the Repository](#1-clone-the-repository)
  - [2. Create a Virtual Environment](#2-create-a-virtual-environment)
  - [3. Activate the Virtual Environment](#3-activate-the-virtual-environment)
  - [4. Install Required Python Packages](#4-install-required-python-packages)
  - [5. Generate SSL Certificates](#5-generate-ssl-certificates)
  - [6. Prepare the QR Code](#6-prepare-the-qr-code)
  - [7. Running the Server](#7-running-the-server)
- [Accessing the Web Interface](#accessing-the-web-interface)
- [Testing the Application](#testing-the-application)
  - [1. Scan the QR Code](#1-scan-the-qr-code)
  - [2. View and Adjust Heartbeat Settings](#2-view-and-adjust-heartbeat-settings)
  - [3. Clear Configuration](#3-clear-configuration)
- [Troubleshooting](#troubleshooting)
- [Security Considerations](#security-considerations)
- [Next Steps](#next-steps)
- [License](#license)

---

## Prerequisites

- **Mac Computer**: Running macOS.
- **Python 3.9**: Ensure you have Python 3.9 installed. You can check your Python version by running `python3 --version` in the terminal.
- **iPhone with Safari**: For testing the QR code scanning functionality.

## Project Structure

The project directory should have the following structure:

```
device-heartbeat-monitor/
├── certs/
│   ├── cert.pem
│   └── key.pem
├── config.json          # Created at runtime
├── server.py
├── templates/
│   └── index.html
├── static/
    └── index.js
```

- **`certs/`**: Contains SSL certificate and key for HTTPS.
- **`config.json`**: Stores configuration data (created at runtime).
- **`server.py`**: The Flask server script.
- **`templates/index.html`**: The web interface HTML page.
- **`static/index.js`**: JavaScript code for the web interface.

---

## Setup Instructions

### 1. Clone the Repository

First, create a directory for the project and navigate to it:

```bash
mkdir device-heartbeat-monitor
cd device-heartbeat-monitor
```

Alternatively, if you have the project in a Git repository, clone it:

```bash
git clone <repository_url> .
```

### 2. Create a Virtual Environment

Create a virtual environment named `venv`:

```bash
python3.9 -m venv venv
```

### 3. Activate the Virtual Environment

Activate the virtual environment:

```bash
source venv/bin/activate
```

### 4. Install Required Python Packages

Upgrade `pip` and install the necessary packages:

```bash
pip install --upgrade pip
pip install flask requests pyopenssl
```

### 5. Generate SSL Certificates

Safari on iOS requires HTTPS for camera access. Generate a self-signed SSL certificate.

#### Create the `certs` Directory

```bash
mkdir certs
cd certs
```

#### Generate the Certificate and Key

Run the following command to generate a self-signed certificate:

```bash
openssl req -x509 -newkey rsa:2048 -keyout key.pem -out cert.pem -days 365 -nodes
```

- When prompted, enter the information requested. For testing purposes, you can leave them blank or enter dummy data.
- This will create `cert.pem` and `key.pem` in the `certs` directory.

#### Return to Project Directory

```bash
cd ..
```

### 6. Prepare the QR Code

The QR code should contain a JSON payload with your device configuration. Ensure the JSON is properly formatted.

#### Example QR Code Payload

```json
{
  "DEVICE_ID": "edge_dev",
  "DEVICE_NAME": "edge_dev",
  "ROBOFLOW_API_BASE_URL": "https://api.roboflow.com",
  "ROBOFLOW_API_KEY": "YOUR_API_KEY_HERE"
}
```

**Important**: Replace `"YOUR_API_KEY_HERE"` with your actual API key.

#### Generate the QR Code

Use an online QR code generator or a tool to create a QR code with the JSON payload.

- **Online Generator**: [QRCode Monkey](https://www.qrcode-monkey.com/)
- **Ensure**: The entire JSON string is included in the QR code.

### 7. Running the Server

Ensure you're in your project directory and your virtual environment is activated.

#### Start the Flask Server

```bash
python server.py
```

You should see output indicating that the server is running on `https://0.0.0.0:8000`.

---

## Accessing the Web Interface

### Find Your Mac's IP Address

You need your Mac's local IP address to access the server from your iPhone.

```bash
ipconfig getifaddr en0
```

- Replace `en0` with the correct network interface if necessary (e.g., `en1`, `en2`).
- Note the IP address (e.g., `192.168.1.10`).

### Connect Your iPhone to the Same Network

Ensure your iPhone is connected to the same Wi-Fi network as your Mac.

### Access the Web Page from Safari on Your iPhone

1. Open Safari on your iPhone.
2. Navigate to: `https://<Your_Mac_IP_Address>:8000`
   - Replace `<Your_Mac_IP_Address>` with your actual IP address (e.g., `192.168.1.10`).

### Bypass the SSL Warning

Since we're using a self-signed certificate, Safari will display a warning:

1. **"This Connection Is Not Private"** message appears.
2. Tap **"Show Details"**.
3. Tap **"Visit This Website"**.
4. Confirm by tapping **"Visit Website"**.
5. If prompted, enter your passcode to trust the certificate.

---

## Testing the Application

### 1. Scan the QR Code

- On the web page, tap the **"Scan QR Code"** button.
- Safari will prompt you to allow camera access. Tap **"Allow"**.
- Point your iPhone's camera at the QR code you generated.
- Once scanned, the data will be processed, and the configuration will be saved.

### 2. View and Adjust Heartbeat Settings

- **Current State**: The web page will display the current configuration and heartbeat interval.
- **Heartbeat Interval**: Adjust the interval (in seconds) using the input field and click **"Set Interval"**.
- **Heartbeat Status**: The page will display the last heartbeat status and timestamp.
- **Auto-Refresh**: The heartbeat status updates every 5 seconds.

### 3. Clear Configuration

- To clear the configuration and stop the heartbeat, click **"Clear Configuration"**.
- Confirm the action when prompted.
- The page will prompt you to scan the QR code again.

---

## Troubleshooting

- **Camera Access Issues**:
  - Ensure Safari has permission to access the camera.
  - Go to **Settings > Safari > Camera** and set it to **Allow**.

- **SSL Certificate Errors**:
  - If Safari doesn't allow you to bypass the SSL warning, you may need to install the certificate on your iPhone.

- **Network Connectivity**:
  - Ensure both devices are on the same network.
  - Check your Mac's firewall settings to allow incoming connections on port `8000`.

- **Invalid QR Code Error**:
  - Verify that your QR code contains valid JSON.
  - Use a JSON validator like [jsonlint.com](https://jsonlint.com/) to check the payload.

- **401 Unauthorized Error**:
  - Ensure the `ROBOFLOW_API_KEY` is correct and has the necessary permissions.
  - Update the QR code with the valid API key if necessary.

---

## Security Considerations

- **API Keys**:
  - Keep your API keys secure.
  - Do not expose API keys in publicly accessible places.

- **SSL Certificates**:
  - For production environments, use a certificate from a trusted Certificate Authority (CA).
  - Self-signed certificates are acceptable for testing purposes.

- **Sensitive Data**:
  - Be cautious about storing sensitive data in `config.json`.
  - Consider encrypting the configuration file or implementing authentication.

---

## Next Steps

- **Deploy on NVIDIA Jetson**:
  - Once validated on your Mac, you can deploy the application on your NVIDIA Jetson device.

- **Enhance the User Interface**:
  - Customize the styling and appearance of the web page as desired.

- **Implement Additional Features**:
  - Add logging and monitoring capabilities.
  - Implement authentication mechanisms for added security.

---

## License

This project is for personal or internal use. Ensure compliance with any licenses or terms of use associated with third-party libraries or APIs.

---

**Enjoy using your Device Heartbeat Monitor! If you have any questions or need further assistance, feel free to reach out.**