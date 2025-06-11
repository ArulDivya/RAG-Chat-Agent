import socket
from contextlib import closing

def check_port(port):
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        return s.connect_ex(('localhost', port)) == 0

if check_port(11434):
    print("⚠️ Ollama already running - connecting to existing instance")
else:
    print("➡️ Starting new Ollama instance")
    import subprocess
    subprocess.Popen(["ollama", "serve"])