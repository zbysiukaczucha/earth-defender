## Space Invaders - Gra Przeglądarkowa
Klasyczna gra Space Invaders napisana w **Pygame**, 
skompilowana do **WebAssembly (WASM)** i zintegrowana
z backendem **Flask**.

## Technologie

* **Frontend**: Python, Pygame CE, Pygbag (WebAssembly)
(https://github.com/pygame-web/pygbag)
* **Backend:** Python, Flask, SQLite
* **API Dokumentacja**: Swagger (Flasgger) dostępny pod `/apidocs`

## Instalacja (dla deweloperów)

1.  **Sklonuj repozytorium:**
    ```bash
    git clone [https://github.com/TWOJ_NICK/space-invaders.git](https://github.com/TWOJ_NICK/space-invaders.git)
    cd space-invaders
    ```

2.  **Stwórz środowisko wirtualne:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # Linux/Mac
    venv\Scripts\activate     # Windows
    ```

3.  **Zainstaluj zależności:**
    ```bash
    pip install -r requirements.txt
    ```
    
4.  **Skompiluj grę (jeśli wprowadziłeś zmiany w main.py):**
    ```bash
    pygbag --build main.py
    # Skopiuj zawartość build/web do static/game_build/
    ```

5.  **Uruchom serwer:**
    ```bash
    python app.py
    ```

6.  **Otwórz w przeglądarce:**
    Wejdź na adres `http://127.0.0.1:5000`

## Dokumentacja

Szczegółowa dokumentacja znajduje się w folderze `/docs`:
* [Instrukcja dla Gracza](docs/user_guide.md)
* [Dokumentacja Techniczna API](docs/api.md)