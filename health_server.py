"""
Health check HTTP 서버
Koyeb health check를 위한 간단한 HTTP 엔드포인트
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import logging

logger = logging.getLogger(__name__)


class HealthCheckHandler(BaseHTTPRequestHandler):
    """Health check 요청 핸들러"""

    def do_GET(self):
        """GET 요청 처리"""
        if self.path == '/health' or self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'OK')
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        """로그 출력 억제"""
        pass


def start_health_server(port=8000):
    """백그라운드에서 health check 서버 시작"""
    try:
        server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        logger.info(f"Health check server started on port {port}")
        return server
    except Exception as e:
        logger.warning(f"Failed to start health check server: {e}")
        return None
