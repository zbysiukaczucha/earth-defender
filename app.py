from flask import Flask, send_from_directory, request, jsonify, render_template
from flasgger import Swagger
import sqlite3
import os

app = Flask(__name__)
swagger = Swagger(app)  # Automatyczna dokumentacja API

# Konfiguracja bazy danych
DB_NAME = "scores.db"


def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                score INTEGER NOT NULL
            )
        ''')
        conn.commit()


# --- ROUTING (Strony WWW) ---

@app.route('/')
def play_game():
    """
    Serwuje plik index.html wygenerowany przez Pygbag.
    Gra znajduje się w folderze static/game_build.
    """
    # Flask domyślnie szuka w templates, ale my serwujemy statyczny build Pygbaga
    return send_from_directory('static/game_build', 'index.html')


# Flask musi wiedzieć, jak serwować pliki .wasm i .apk
@app.route('/<path:filename>')
def serve_game_files(filename):
    return send_from_directory('static/game_build', filename)


@app.route('/leaderboard')
def leaderboard_page():
    """Wyświetla prostą tabelę HTML z wynikami."""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name, score FROM scores ORDER BY score DESC LIMIT 10")
        scores = cursor.fetchall()

    # Prosty HTML wewnątrz kodu (możesz przenieść do templates/leaderboard.html)
    html = """
    <html>
    <head>
        <title>Top 10 Graczy</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body class="container mt-5">
        <h1>Najlepsi Obrońcy Ziemi</h1>
        <table class="table table-striped">
            <thead><tr><th>Gracz</th><th>Wynik</th></tr></thead>
            <tbody>
    """
    for name, score in scores:
        html += f"<tr><td>{name}</td><td>{score}</td></tr>"

    html += """
            </tbody>
        </table>
        <a href="/" class="btn btn-primary">Zagraj Ponownie</a>
    </body>
    </html>
    """
    return html


# --- API (Backend) ---

@app.route('/api/score', methods=['POST'])
def add_score():
    """
    Zapisuje nowy wynik.
    ---
    tags:
      - Wyniki
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            name:
              type: string
            score:
              type: integer
    responses:
      200:
        description: Wynik zapisany pomyślnie
    """
    data = request.json
    name = data.get('name', 'Anonim')
    score = data.get('score', 0)

    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO scores (name, score) VALUES (?, ?)", (name, score))
        conn.commit()

    return jsonify({"message": "Saved", "status": "success"}), 201


if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)