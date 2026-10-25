from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.parse

# Tracking states using set data types
chess_members = set()
added_history = set()
removed_history = set()

class ClubManagerHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        self.end_headers()
        
        with open('index.html', 'r', encoding='utf-8') as file:
            html = file.read()
        
        if not chess_members:
            list_items = '<li class="empty">No members registered yet.</li>'
        else:
            list_items = "".join([f"<li>{member}</li>" for member in sorted(chess_members)])
        
       
        added_options = "".join(f"<option disabled>+ {m}</option>" for m in sorted(added_history)) or "<option disabled>None</option>"
        removed_options = "".join(f"<option disabled>- {m}</option>" for m in sorted(removed_history)) or "<option disabled>None</option>"
        
        
        html = html.replace('{{MEMBERS}}', list_items)
        html = html.replace('{{COUNT}}', str(len(chess_members)))
        html = html.replace('{{ADDED_OPTIONS}}', added_options)
        html = html.replace('{{REMOVED_OPTIONS}}', removed_options)
        
        self.wfile.write(html.encode('utf-8'))

    def do_POST(self):
        global chess_members, added_history, removed_history
        
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')
        params = urllib.parse.parse_qs(post_data)
        
        name = params.get('name', [''])[0].strip()
        action = params.get('action', [''])[0]
        
        if name:
            input_set = {name}
            
            if action == 'add':
                # Use set union (|) to add to current members and added log
                # Use set difference (-) to remove the name from the historical deletion log if re-added
                chess_members = chess_members | input_set
                added_history = added_history | input_set
                removed_history = removed_history - input_set
                
            elif action == 'remove':
                
                was_member = input_set & chess_members
                
                # Use set difference (-) to drop from active membership and addition logs
                # Use set union (|) to register into the deletion log
                chess_members = chess_members - input_set
                added_history = added_history - input_set
                removed_history = removed_history | was_member
                
        self.send_response(303)
        self.send_header('Location', '/')
        self.end_headers()

if __name__ == '__main__':
    server_address = ('', 8080)
    httpd = HTTPServer(server_address, ClubManagerHandler)
    print("🚀 Chess Club backend actively running at http://localhost:8080 ...")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server safely.")
        httpd.server_close()