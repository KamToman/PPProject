# System Pomiaru Czasów Produkcji

Aplikacja webowa do pomiaru i zarządzania czasami procesów produkcyjnych przy indywidualnych zleceniach.

## Funkcjonalności

### Panel Projektanta
- Tworzenie nowych zleceń produkcyjnych
- Generowanie kodów QR dla zleceń
- Pobieranie i wyświetlanie kodów QR
- Przeglądanie listy wszystkich zleceń

### Panel Pracownika
- Skanowanie kodów QR zleceń
- Rozpoczynanie pracy (start) na wybranym etapie produkcji
- Kończenie pracy (stop) z automatycznym obliczaniem czasu
- Wyświetlanie aktywnych sesji pracy
- Wybór etapu produkcji

### Panel Kierownika/Inżyniera Procesów
- Raport czasów zleceń (z możliwością filtrowania)
- Raport wydajności pracowników
- Raport efektywności etapów produkcji
- Eksport danych w formacie tabelarycznym

## Technologie

- **Backend**: Flask (Python)
- **Baza danych**: SQLite (SQLAlchemy ORM)
- **Frontend**: HTML, CSS, JavaScript
- **Kody QR**: qrcode, Pillow

## Instalacja

1. Zainstaluj zależności:
```bash
pip install -r requirements.txt
```

2. Uruchom aplikację:
```bash
python app.py
```

3. Otwórz przeglądarkę i przejdź do:
```
http://localhost:5000
```

## Demo

Aby zobaczyć demonstrację funkcjonalności aplikacji:

1. Upewnij się, że aplikacja jest uruchomiona (`python app.py`)
2. W nowym terminalu uruchom:
```bash
pip install requests  # jeśli jeszcze nie zainstalowane
python demo.py
```

Demo automatycznie:
- Utworzy nowe zlecenie
- Rozpocznie i zakończy pracę na różnych etapach produkcji
- Wyświetli raporty z czasami pracy

## Struktura bazy danych

### Tabela: Orders (Zlecenia)
- `id` - ID zlecenia
- `order_number` - Numer zlecenia (unikalny)
- `description` - Opis zlecenia
- `created_at` - Data utworzenia

### Tabela: ProductionStages (Etapy produkcji)
- `id` - ID etapu
- `name` - Nazwa etapu
- `description` - Opis etapu

Domyślne etapy:
1. Projektowanie
2. Cięcie
3. Montaż
4. Kontrola jakości
5. Pakowanie

### Tabela: TimeLogs (Logi czasów pracy)
- `id` - ID logu
- `order_id` - ID zlecenia
- `stage_id` - ID etapu produkcji
- `worker_name` - Imię i nazwisko pracownika
- `start_time` - Czas rozpoczęcia
- `end_time` - Czas zakończenia
- `status` - Status (in_progress, completed)

## Użycie

### Tworzenie zlecenia (Projektant)
1. Przejdź do Panelu Projektanta
2. Wprowadź numer zlecenia i opcjonalny opis
3. Kliknij "Utwórz zlecenie"
4. Pobierz lub wyświetl wygenerowany kod QR
5. Nanieś kod QR na dokumentację projektu

### Rejestracja czasu pracy (Pracownik)
1. Przejdź do Panelu Pracownika
2. Wprowadź swoje imię i nazwisko
3. Wybierz etap produkcji, na którym pracujesz
4. Skanuj kod QR na jeden z dwóch sposobów:
   - **Kamera PC/telefonu**: Kliknij "📷 Skanuj kamerą" i zezwól na dostęp do kamery
   - **Ręczne wprowadzenie**: Wpisz kod QR ręcznie w pole tekstowe
5. Kliknij "Start pracy" aby rozpocząć
6. Kliknij "Stop pracy" aby zakończyć pracę na tym zleceniu

**Uwaga**: Skanowanie kamerą wymaga przeglądarki z obsługą dostępu do kamery (HTTPS w produkcji lub localhost w rozwoju)

### Przeglądanie raportów (Kierownik)
1. Przejdź do Panelu Kierownika
2. Wybierz interesujący raport z zakładek:
   - Czasy zleceń
   - Wydajność pracowników
   - Efektywność etapów
3. Użyj filtrów (jeśli dostępne)
4. Kliknij "Wczytaj raport"

## API Endpoints

### Orders
- `POST /api/orders` - Utwórz nowe zlecenie
- `GET /api/orders/<order_id>/qrcode` - Pobierz kod QR zlecenia

### Worker
- `POST /api/scan` - Przetwórz skanowanie kodu QR (start/stop)
- `GET /api/worker/active-sessions` - Pobierz aktywne sesje pracownika

### Reports
- `GET /api/reports/order-times` - Raport czasów zleceń
- `GET /api/reports/worker-productivity` - Raport wydajności pracowników
- `GET /api/reports/stage-efficiency` - Raport efektywności etapów

### Stages
- `GET /api/stages` - Pobierz wszystkie etapy produkcji
- `POST /api/stages` - Utwórz nowy etap produkcji

## Bezpieczeństwo

- Aplikacja automatycznie generuje losowy `SECRET_KEY` dla każdej sesji
- W produkcji ustaw zmienną środowiskową `SECRET_KEY` na stałą wartość
- Tryb debug jest domyślnie wyłączony; włącz przez `FLASK_DEBUG=true` tylko dla rozwoju
- Rozważ dodanie uwierzytelniania użytkowników
- Używaj HTTPS w środowisku produkcyjnym

## Zmienne środowiskowe

- `SECRET_KEY` - Klucz sesji Flask (wymagane w produkcji)
- `FLASK_DEBUG` - Ustaw na 'true' aby włączyć tryb debug (tylko dla rozwoju)
- `FLASK_HOST` - Host do bindowania (domyślnie: 127.0.0.1, użyj 0.0.0.0 dla dostępu zewnętrznego)
- `FLASK_PORT` - Port aplikacji (domyślnie: 5000)

## Licencja

Projekt studencki - dozwolone użycie edukacyjne.
