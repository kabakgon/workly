# Quick Start - Workly 2.0

## Szybki start z frontendem

### 1. Zainstaluj zależności Node.js
```bash
npm install
```

### 2. Zbuduj pliki CSS
```bash
npm run build-css
```

### 3. Uruchom serwer Django
```bash
python manage.py runserver
```

### 4. Otwórz przeglądarkę
```
http://127.0.0.1:8000/
```

### 5. Zaloguj się
- **Baza demo jest już wypełniona danymi!** Możesz od razu zalogować się jednym z kont demo:
  - `anna_kowalska` / hasło: `1`
  - `piotr_nowak` / hasło: `1`
  - `maria_wisniewska` / hasło: `1`
- Lub użyj konta administratora Django (utwórz przez `/admin/`)

### 6. (Opcjonalnie) Odtwórz bazę demo
Jeśli chcesz odtworzyć bazę demo od zera:
```bash
python manage.py setup_demo_data
```

To utworzy 3 użytkowników demo (hasło: `1`), 5 projektów i 50 zadań.
Zobacz `README_DEMO.md` dla szczegółów.

## Struktura URL

- `/` - Dashboard
- `/projects/` - Lista projektów
- `/projects/{id}/` - Szczegóły projektu
- `/projects/{id}/gantt/` - Diagram Gantta
- `/tasks/` - Lista zadań
- `/admin/` - Panel administracyjny Django
- `/api/docs/` - Dokumentacja API (Swagger)

## Tryb deweloperski (watch mode)

Aby automatycznie odświeżać CSS podczas edycji:
```bash
npm run watch-css
```

Uruchom to w osobnym terminalu podczas pracy nad stylami.

## Rozwiązywanie problemów

### CSS nie działa
- Upewnij się, że uruchomiłeś `npm run build-css`
- Sprawdź czy plik `static/css/output.css` istnieje i ma zawartość

### Błędy 404 na API
- Sprawdź czy serwer Django działa
- Sprawdź czy jesteś zalogowany (wymagane dla większości endpointów)

### Błędy CSRF
- Upewnij się, że jesteś zalogowany przez Django
- Sprawdź czy cookies są włączone w przeglądarce

