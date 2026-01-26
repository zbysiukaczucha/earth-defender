# Dokumentacja API

Backend udostępnia REST API do komunikacji z grą.
Dokumentacja interaktywna (Swagger UI) dostępna jest pod adresem: `/apidocs`.

## Endpointy

### 1. Zapisanie wyniku
Zapisuje wynik gracza po zakończeniu gry.

* **URL:** `/api/score`
* **Metoda:** `POST`
* **Format danych:** JSON
* **Przykład Body:**
    ```json
    {
      "name": "SuperGracz",
      "score": 1500
    }
    ```
* **Odpowiedź Sukces:** 201 Created

### 2. Pobranie rankingu
Zwraca listę 10 najlepszych wyników.

* **URL:** `/api/leaderboard` (HTML view) lub API access (do implementacji)
...