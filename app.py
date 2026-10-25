"""Punto de entrada de DataConnect para Flask y servidores WSGI."""
from dataconnect import create_app

app = create_app()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
