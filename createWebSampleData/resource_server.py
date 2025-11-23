import http.server
import socketserver
import os

class ResourceHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=os.getcwd(), **kwargs)

    def do_GET(self):
        if self.path.startswith('/assets/'):
            self.path = self.path[1:]  # Remove leading '/'
        elif self.path.startswith('/temp/'):
            self.path = self.path[1:] # Remove leading '/'
        
        # Fallback to default behavior for other paths like index.html
        return http.server.SimpleHTTPRequestHandler.do_GET(self)

def run_server(port, web_dir):
    os.chdir(web_dir)
    Handler = ResourceHandler
    httpd = socketserver.TCPServer(("", port), Handler)
    print(f"Serving at http://localhost:{port}")
    httpd.serve_forever()
