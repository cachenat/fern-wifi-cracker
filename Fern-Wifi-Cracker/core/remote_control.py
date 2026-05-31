"""
Remote Control HTTP API for Fern-Wifi-Cracker.

Start with: python3 execute.py --remote-control [PORT]

Endpoints (all require X-API-Key header except /api/v1/health):
  GET  /api/v1/health
  GET  /api/v1/status
  POST /api/v1/scan/start   body: {"interface": "wlan0mon"}
  POST /api/v1/scan/stop
  GET  /api/v1/networks
  GET  /api/v1/database
"""

import os
import json
import sqlite3
import secrets
import threading
import subprocess
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse


class RemoteControlServer:
    def __init__(self, port=8765, get_interface=None):
        self.port = port
        self.api_key = secrets.token_hex(16)
        self._get_interface = get_interface or (lambda: '')
        self._lock = threading.Lock()
        self._scan_active = False
        self._httpd = None
        self._thread = None

    def start(self):
        handler = _make_handler(self)
        self._httpd = HTTPServer(('127.0.0.1', self.port), handler)
        self._thread = threading.Thread(target=self._httpd.serve_forever, daemon=True)
        self._thread.start()
        print('[Fern Remote Control] Listening on http://127.0.0.1:{}'.format(self.port))
        print('[Fern Remote Control] API Key: {}'.format(self.api_key))

    def stop(self):
        if self._httpd:
            self._httpd.shutdown()


def _make_handler(server):
    class _Handler(BaseHTTPRequestHandler):
        def log_message(self, fmt, *args):
            pass

        def _send(self, code, data):
            body = json.dumps(data).encode()
            self.send_response(code)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def _auth(self):
            return self.headers.get('X-API-Key', '') == server.api_key

        def _body(self):
            n = int(self.headers.get('Content-Length', 0))
            return json.loads(self.rfile.read(n)) if n else {}

        def do_GET(self):
            path = urlparse(self.path).path
            if path == '/api/v1/health':
                self._send(200, {'status': 'ok'})
            elif not self._auth():
                self._send(401, {'error': 'unauthorized'})
            elif path == '/api/v1/status':
                self._status()
            elif path == '/api/v1/networks':
                self._networks()
            elif path == '/api/v1/database':
                self._database()
            else:
                self._send(404, {'error': 'not found'})

        def do_POST(self):
            path = urlparse(self.path).path
            if not self._auth():
                self._send(401, {'error': 'unauthorized'})
            elif path == '/api/v1/scan/start':
                self._scan_start()
            elif path == '/api/v1/scan/stop':
                self._scan_stop()
            else:
                self._send(404, {'error': 'not found'})

        def _status(self):
            wep_count = wpa_count = 0
            combined_csv = _read_csv('/tmp/fern-log/WPA/zfern-wpa-01.csv')
            for line in combined_csv.splitlines():
                if 'WEP' in line:
                    wep_count += 1
                if 'WPA' in line or 'WPA2' in line:
                    wpa_count += 1
            with server._lock:
                active = server._scan_active
            self._send(200, {
                'interface': server._get_interface(),
                'scan_active': active,
                'wep_networks': wep_count,
                'wpa_networks': wpa_count,
            })

        def _networks(self):
            self._send(200, {
                'wep': _parse_csv(_read_csv('/tmp/fern-log/zfern-wep-01.csv')),
                'wpa': _parse_csv(_read_csv('/tmp/fern-log/WPA/zfern-wpa-01.csv')),
            })

        def _database(self):
            rows = []
            try:
                db_path = os.path.join(os.getcwd(), 'key-database', 'Database.db')
                conn = sqlite3.connect(db_path)
                for row in conn.execute(
                    'SELECT access_point, mac_address, encryption, key, channel FROM keys'
                ):
                    rows.append({
                        'access_point': row[0],
                        'mac_address': row[1],
                        'encryption': row[2],
                        'key': row[3],
                        'channel': row[4],
                    })
                conn.close()
            except Exception as exc:
                self._send(500, {'error': str(exc)})
                return
            self._send(200, {'entries': rows})

        def _scan_start(self):
            body = self._body()
            iface = body.get('interface', '') or server._get_interface()
            if not iface:
                self._send(400, {'error': 'interface required; pass {"interface": "wlan0mon"}'})
                return
            with server._lock:
                if server._scan_active:
                    self._send(409, {'error': 'scan already active'})
                    return
                server._scan_active = True
            subprocess.call(
                'killall airodump-ng',
                shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            )
            threading.Thread(
                target=_scan_worker, args=(iface, server), daemon=True,
            ).start()
            self._send(200, {'status': 'started', 'interface': iface})

        def _scan_stop(self):
            with server._lock:
                server._scan_active = False
            subprocess.call(
                'killall airodump-ng',
                shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            )
            self._send(200, {'status': 'stopped'})

    return _Handler


def _read_csv(path):
    try:
        with open(path, 'r', errors='ignore') as fh:
            return fh.read()
    except OSError:
        return ''


def _parse_csv(text):
    nets = []
    if not text:
        return nets
    try:
        ap_block = text[:text.index('Station MAC')]
        rows_text = ap_block[ap_block.index('Key'):].strip('Key\r\n')
        for row in rows_text.splitlines():
            cols = row.split(',')
            if len(cols) < 14:
                continue
            nets.append({
                'ssid': cols[13].strip(),
                'mac_address': cols[0].strip(),
                'channel': cols[3].strip(),
                'speed': cols[4].strip(),
                'power': cols[8].strip(),
            })
    except (ValueError, IndexError):
        pass
    return nets


def _scan_worker(iface, server):
    with open(os.devnull, 'w') as devnull:
        procs = [
            subprocess.Popen(
                ['airodump-ng', '--write', '/tmp/fern-log/zfern-wep',
                 '--output-format', 'csv', '--encrypt', 'wep', iface],
                stdout=devnull, stderr=devnull,
            ),
            subprocess.Popen(
                ['airodump-ng', '--write', '/tmp/fern-log/WPA/zfern-wpa',
                 '--output-format', 'csv', '--encrypt', 'wpa', iface],
                stdout=devnull, stderr=devnull,
            ),
        ]
        while True:
            with server._lock:
                if not server._scan_active:
                    break
            time.sleep(1)
        for proc in procs:
            try:
                proc.terminate()
            except Exception:
                pass
