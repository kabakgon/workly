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
- Użyj konta administratora Django lub utwórz nowe konto przez `/admin/`

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

