# System Pomiaru Czasów Produkcji

Aplikacja webowa do pomiaru i zarządzania czasami procesów produkcyjnych przy indywidualnych zleceniach.

## Funkcjonalności

### 🔐 System Uwierzytelniania
- Logowanie użytkowników z bezpiecznym hashowaniem haseł
- Zarządzanie sesjami
- Role użytkowników: Admin, Projektant, Pracownik, Kierownik
- Kontrola dostępu oparta na rolach (RBAC)

### 👤 Panel Administratora (nowy!)
- Zarządzanie użytkownikami (dodawanie, usuwanie)
- Przypisywanie ról do użytkowników
- Przypisywanie wielu procesów/etapów do pracowników
- Przeglądanie listy użytkowników z ich rolami i uprawnieniami
- Zarządzanie procesami produkcyjnymi

### Panel Projektanta
- Tworzenie nowych zleceń produkcyjnych
- Generowanie kodów QR dla zleceń
- Pobieranie i wyświetlanie kodów QR
- Przeglądanie listy wszystkich zleceń
- **Dostęp**: Admin, Projektant

### Panel Pracownika
- Skanowanie kodów QR zleceń (kamerą lub ręcznie)
- Rozpoczynanie pracy (start) na wybranym etapie produkcji
- Kończenie pracy (stop) z automatycznym obliczaniem czasu
- Wyświetlanie aktywnych sesji pracy
- Wybór z przypisanych etapów produkcji
- **Dostęp**: Admin, Pracownik (tylko przypisane etapy)

### Panel Kierownika/Inżyniera Procesów
- Raport czasów zleceń (z możliwością filtrowania)
- Raport wydajności pracowników
- Raport efektywności etapów produkcji
- Eksport danych w formacie tabelarycznym
- **Dostęp**: Admin, Kierownik

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

3. Pierwsze uruchomienie utworzy domyślne konto administratora:
   - **Nazwa użytkownika**: `admin`
   - **Hasło**: `admin123`
   
   ⚠️ **WAŻNE**: Zmień hasło administratora po pierwszym logowaniu!

4. Otwórz przeglądarkę i przejdź do:
```
http://localhost:5000
```

5. Zaloguj się używając powyższych danych dostępowych

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

**Uwagi dotyczące skanowania kamerą**:
- Wymaga przeglądarki z obsługą dostępu do kamery (HTTPS w produkcji lub localhost w rozwoju)
- Wymaga połączenia z internetem do załadowania biblioteki skanowania (cdn.jsdelivr.net)
- Jeśli biblioteka się nie załaduje, użyj ręcznego wprowadzania kodów QR
- Możliwe przyczyny błędu ładowania: firewall, blokada reklam, brak internetu

### Rozwiązywanie problemów z kamerą

**Błąd: "NotReadableError: Could not start video source"**

Ten błąd występuje gdy:
1. **Kamera jest już używana** - Zamknij inne aplikacje/karty przeglądarki używające kamery
2. **Brak uprawnień** - Sprawdź ustawienia kamery w przeglądarce:
   - Chrome: Kliknij ikonę kłódki obok URL → Ustawienia witryny → Kamera
   - Firefox: Kliknij ikonę informacji obok URL → Uprawnienia → Kamera
3. **Problemy ze sterownikami** - Sprawdź czy kamera działa w innych aplikacjach
4. **Konflikty sprzętowe** - Spróbuj odłączyć i podłączyć ponownie kamerę USB

**Inne problemy**:
- **"Permission denied"** - Zezwól na dostęp do kamery w wyskakującym oknie przeglądarki
- **"Requested device not found"** - Sprawdź czy kamera jest podłączona i wykryta przez system
- **Kamera się nie uruchamia** - Odśwież stronę (Ctrl+F5) lub kliknij przycisk "Rozpocznij skanowanie"

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

- ✅ System uwierzytelniania z bezpiecznym hashowaniem haseł (PBKDF2)
- ✅ Kontrola dostępu oparta na rolach (RBAC)
- ✅ Sesje użytkowników z bezpiecznym SECRET_KEY
- Aplikacja automatycznie generuje losowy `SECRET_KEY` dla każdej sesji
- W produkcji ustaw zmienną środowiskową `SECRET_KEY` na stałą wartość
- Tryb debug jest domyślnie wyłączony; włącz przez `FLASK_DEBUG=true` tylko dla rozwoju
- Używaj HTTPS w środowisku produkcyjnym
- Zmień domyślne hasło administratora po pierwszym uruchomieniu

## Zmienne środowiskowe

- `SECRET_KEY` - Klucz sesji Flask (wymagane w produkcji)
- `FLASK_DEBUG` - Ustaw na 'true' aby włączyć tryb debug (tylko dla rozwoju)
- `FLASK_HOST` - Host do bindowania (domyślnie: 127.0.0.1, użyj 0.0.0.0 dla dostępu zewnętrznego)
- `FLASK_PORT` - Port aplikacji (domyślnie: 5000)

## Licencja

Projekt studencki - dozwolone użycie edukacyjne.
