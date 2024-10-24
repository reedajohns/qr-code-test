// static/index.js
const codeReader = new ZXing.BrowserQRCodeReader();
const videoElement = document.getElementById('qr-video');
const resultElement = document.getElementById('qr-result');
const scanButton = document.getElementById('btn-scan-qr');
const scannerContainer = document.getElementById('scanner-container');
const stateContainer = document.getElementById('state-container');
const configDataElement = document.getElementById('config-data');
const heartbeatIntervalElement = document.getElementById('heartbeat-interval');
const intervalInput = document.getElementById('interval-input');
const setIntervalButton = document.getElementById('set-interval');
const clearConfigButton = document.getElementById('clear-config');
const heartbeatStatusElement = document.getElementById('heartbeat-status');
const heartbeatTimeElement = document.getElementById('heartbeat-time');
let scanning = false;

function fetchState() {
    fetch('/get_state')
        .then(response => response.json())
        .then(data => {
            if (Object.keys(data.config).length > 0) {
                stateContainer.style.display = 'block';
                configDataElement.textContent = JSON.stringify(data.config, null, 2);
                heartbeatIntervalElement.textContent = data.heartbeat_interval;
                intervalInput.value = data.heartbeat_interval;

                // Update heartbeat status and time
                heartbeatStatusElement.textContent = data.last_heartbeat_status || 'N/A';
                heartbeatTimeElement.textContent = data.last_heartbeat_time || 'N/A';
            } else {
                stateContainer.style.display = 'none';
            }
        })
        .catch(error => {
            console.error('Error fetching state:', error);
        });
}

scanButton.addEventListener('click', () => {
    if (scanning) {
        stopScanning();
    } else {
        startScanning();
    }
});

function startScanning() {
    scanning = true;
    scanButton.textContent = 'Stop Scanning';
    scannerContainer.style.display = 'inline-block';
    codeReader.decodeOnceFromVideoDevice(undefined, 'qr-video')
        .then(result => {
            console.log(result);
            resultElement.textContent = `QR Code Data Received`;
            sendQRData(result.text);
            stopScanning();
        })
        .catch(err => {
            console.error(err);
            resultElement.textContent = `Error: ${err}`;
            stopScanning();
        });
}

function stopScanning() {
    scanning = false;
    scanButton.textContent = 'Scan QR Code';
    scannerContainer.style.display = 'none';
    codeReader.reset();
}

function sendQRData(qrData) {
    fetch('/process_qr', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        },
        body: JSON.stringify({ data: qrData })
    })
    .then(response => response.json())
    .then(data => {
        console.log('Server Response:', data);
        if (data.status === 'success') {
            fetchState();
        } else {
            resultElement.textContent = `Error: ${data.message}`;
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

setIntervalButton.addEventListener('click', () => {
    const interval = intervalInput.value;
    fetch('/set_heartbeat_interval', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        },
        body: JSON.stringify({ interval: interval })
    })
    .then(response => response.json())
    .then(data => {
        console.log('Heartbeat interval set:', data);
        if (data.status === 'success') {
            heartbeatIntervalElement.textContent = data.interval;
        } else {
            alert(`Error: ${data.message}`);
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
});

clearConfigButton.addEventListener('click', () => {
    if (confirm('Are you sure you want to clear the configuration?')) {
        fetch('/clear_config', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            console.log('Configuration cleared:', data);
            fetchState();
        })
        .catch(error => {
            console.error('Error:', error);
        });
    }
});

// Fetch state on page load
fetchState();
// Fetch state every 5 seconds
setInterval(fetchState, 5000);
