from flask import Flask, send_from_directory, request, jsonify, render_template
from flasgger import Swagger
import sqlite3
import os

app = Flask(__name__)
swagger = Swagger(app)

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


@app.route('/')
def play_game():
    """
    Serwuje plik index.html wygenerowany przez Pygbag.
    Gra znajduje się w folderze static/game_build.
    """
    return render_template('index.html')


@app.route('/<path:filename>')
def serve_game_files(filename):
    return send_from_directory('static/game_build', filename)


@app.route('/leaderboard')
def leaderboard_page():
    """Wyświetla tabelę wyników używając szablonu HTML."""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name, score FROM scores ORDER BY score DESC LIMIT 10")
        scores = cursor.fetchall()

    return render_template('leaderboard.html', scores=scores)


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