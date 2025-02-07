import webview
from app import app

def start_server():
    app.run(host='127.0.0.1', port=3000)

if __name__ == '__main__':
    import threading
    server = threading.Thread(target=start_server)
    server.daemon = True
    server.start()
    
    # Create a desktop window
    webview.create_window("Employify", "http://127.0.0.1:3000",
                         width=1200,
                         height=800,
                         resizable=True,
                         min_size=(800, 600),
                         background_color='#FFF')
    webview.start()
