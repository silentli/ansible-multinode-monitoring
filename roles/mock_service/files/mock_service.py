#!/usr/bin/env python3

import http.server
import socketserver
import json
import time
import os
import logging
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    
    handlers=[
        logging.StreamHandler(),  # Console output
        logging.FileHandler('/var/log/mock-service.log')  # File output
    ]
)
logger = logging.getLogger('mock-service')

class MockHTTPRequestHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests"""
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            response = {
                'service': 'mock-service',
                'status': 'running',
                'timestamp': datetime.now().isoformat(),
                'uptime': time.time(),
                'version': '1.0.0',
                'endpoints': {
                    '/': 'Service info',
                    '/health': 'Health check',
                    '/metrics': 'Basic metrics'
                }
            }
            
            self.wfile.write(json.dumps(response, indent=2).encode())
            logger.info(f"GET / - Service info requested from {self.client_address[0]}")
            
        elif self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            response = {
                'status': 'healthy',
                'timestamp': datetime.now().isoformat()
            }
            
            self.wfile.write(json.dumps(response).encode())
            logger.info(f"GET /health - Health check from {self.client_address[0]}")
            
        elif self.path == '/metrics':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            
            # Basic Prometheus-style metrics
            metrics = f"""# HELP mock_service_requests_total Total number of requests
# TYPE mock_service_requests_total counter
mock_service_requests_total {int(time.time())}

# HELP mock_service_uptime_seconds Service uptime in seconds
# TYPE mock_service_uptime_seconds gauge
mock_service_uptime_seconds {time.time()}

# HELP mock_service_info Service information
# TYPE mock_service_info gauge
mock_service_info{{version="1.0.0",service="mock-service"}} 1
"""
            self.wfile.write(metrics.encode())
            logger.debug(f"GET /metrics - Metrics requested from {self.client_address[0]}")
            
        else:
            self.send_response(404)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            response = {
                'error': 'Not found',
                'path': self.path,
                'timestamp': datetime.now().isoformat()
            }
            
            self.wfile.write(json.dumps(response).encode())
            logger.warning(f"GET {self.path} - 404 Not Found from {self.client_address[0]}")

    def do_POST(self):
        """Handle POST requests"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        response = {
            'message': 'POST request received',
            'timestamp': datetime.now().isoformat()
        }
        
        self.wfile.write(json.dumps(response).encode())
        logger.info(f"POST / - Echo request from {self.client_address[0]}")

    def log_message(self, format, *args):
        """Override to use logging instead of print"""
        logger.info(f"HTTP: {format % args}")

"""
Simple Mock HTTP Service
Simulates a basic web service for testing and monitoring purposes.
"""
def main():
    """Main function to start the server"""
    # Get port from environment variable or use default
    PORT = int(os.environ.get('MOCK_SERVICE_PORT', 8080))
    HOST = '0.0.0.0'
    
    try:
        with socketserver.TCPServer((HOST, PORT), MockHTTPRequestHandler) as httpd:
            logger.info(f"Mock service starting on {HOST}:{PORT}")
            logger.info("Available endpoints:")
            logger.info("  GET / - Service information")
            logger.info("  GET /health - Health check")
            logger.info("  GET /metrics - Prometheus metrics")
            logger.info("  POST / - Echo endpoint")
            httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info("Shutting down mock service...")
    except Exception as e:
        logger.error(f"Error starting server: {e}")
        exit(1)

if __name__ == '__main__':
    main()
