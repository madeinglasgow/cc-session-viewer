#!/usr/bin/env python3
"""
Custom HTTP server for the Claude Code session viewer.
Serves static files and provides an endpoint to save comments to session JSON files.

Usage: python server.py
Then open http://localhost:8000/viewer.html
"""

from http.server import HTTPServer, SimpleHTTPRequestHandler
import json
import os


class ViewerHandler(SimpleHTTPRequestHandler):
    """Handler that adds POST /save-comments endpoint to static file serving."""

    def do_POST(self):
        if self.path == '/save-comments':
            self._handle_save_comments()
        else:
            self.send_error(404, "Not Found")

    def _handle_save_comments(self):
        try:
            # Read request body
            content_length = int(self.headers.get('Content-Length', 0))
            body = json.loads(self.rfile.read(content_length))

            session_file = body.get('sessionFile')
            comments = body.get('comments', {})

            if not session_file:
                self.send_error(400, "Missing sessionFile")
                return

            # Security: ensure file is within current directory
            abs_path = os.path.abspath(session_file)
            cwd = os.getcwd()
            if not abs_path.startswith(cwd + os.sep) and abs_path != cwd:
                self.send_error(403, "Access denied - file outside allowed directory")
                return

            # Verify file exists and is a JSON file
            if not os.path.isfile(abs_path):
                self.send_error(404, "Session file not found")
                return

            if not abs_path.endswith('.json'):
                self.send_error(400, "Not a JSON file")
                return

            # Read existing session JSON
            with open(abs_path, 'r', encoding='utf-8') as f:
                session_data = json.load(f)

            # Merge in comments (or remove key if empty)
            if comments:
                session_data['comments'] = comments
            elif 'comments' in session_data:
                del session_data['comments']

            # Write back with nice formatting
            with open(abs_path, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, indent=2, ensure_ascii=False)

            # Send success response
            self._send_json_response(200, {"success": True})

        except json.JSONDecodeError as e:
            self.send_error(400, f"Invalid JSON: {e}")
        except Exception as e:
            self.send_error(500, f"Server error: {e}")

    def _send_json_response(self, status_code, data):
        """Send a JSON response with the given status code and data."""
        response = json.dumps(data).encode('utf-8')
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', len(response))
        self.end_headers()
        self.wfile.write(response)


def main():
    port = 8000
    server = HTTPServer(('localhost', port), ViewerHandler)
    print(f"Session Viewer server running at http://localhost:{port}")
    print(f"Open http://localhost:{port}/viewer.html to view sessions")
    print("Press Ctrl+C to stop")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped")


if __name__ == '__main__':
    main()
