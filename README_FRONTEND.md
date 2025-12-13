# Frontend Workly 2.0 - Instrukcja instalacji

## Wymagania

- Node.js (v16 lub nowszy)
- npm lub yarn

## Instalacja

1. **Zainstaluj zależności Node.js:**
```bash
npm install
```

2. **Zbuduj pliki CSS z Tailwind:**
```bash
npm run build-css
```

Dla trybu deweloperskiego (automatyczne odświeżanie):
```bash
npm run watch-css
```

3. **Uruchom serwer Django:**
```bash
python manage.py runserver
```

4. **Otwórz przeglądarkę:**
```
http://127.0.0.1:8000/
```

## Struktura frontendu

```
static/
├── src/
│   └── input.css          # Plik źródłowy Tailwind
├── css/
│   └── output.css         # Skompilowany CSS (generowany)
└── js/
    ├── main.js            # Główne funkcje API
    ├── projects.js        # Logika projektów
    └── tasks.js           # Logika zadań

templates/
├── base.html              # Główny layout z DaisyUI
└── frontend/
    ├── dashboard.html     # Strona główna
    ├── projects.html      # Lista projektów
    ├── project_detail.html # Szczegóły projektu
    ├── tasks.html         # Lista zadań
    └── gantt.html         # Diagram Gantta
```

## Funkcjonalności

### ✅ Zaimplementowane:
- Dashboard z podsumowaniem
- Lista projektów z filtrowaniem i wyszukiwaniem
- Tworzenie nowych projektów
- Szczegóły projektu
- Lista zadań użytkownika
- Podgląd danych Gantta
- Responsywny design (mobile-friendly)
- Integracja z API Django REST Framework

### 🔄 Do rozbudowy:
- Edycja projektów i zadań
- Usuwanie projektów i zadań
- Pełna integracja z biblioteką Gantta (dhtmlx-gantt, frappe-gantt)
- Drag & drop dla zadań
- Powiadomienia
- Eksport danych

## Technologie

- **Tailwind CSS 3.4+** - Utility-first CSS framework
- **DaisyUI 4.4+** - Komponenty UI dla Tailwind
- **Alpine.js** - Lekki framework JavaScript
- **Vanilla JavaScript** - Do komunikacji z API

## Dostosowywanie motywu

DaisyUI oferuje wiele gotowych motywów. Aby zmienić motyw, edytuj `data-theme` w `templates/base.html`:

```html
<html lang="pl" data-theme="dark">
```

Dostępne motywy: light, dark, cupcake, bumblebee, emerald, corporate, synthwave, retro, cyberpunk, valentine, halloween, garden, forest, aqua, lofi, pastel, fantasy, wireframe, black, luxury, dracula, cmyk, autumn, business, acid, lemonade, night, coffee, winter

## API Endpoints używane przez frontend

- `GET /api/my/summary/` - Podsumowanie dashboardu
- `GET /api/my/projects/` - Projekty użytkownika
- `GET /api/my/tasks/` - Zadania użytkownika
- `GET /api/projects/` - Lista projektów
- `POST /api/projects/` - Tworzenie projektu
- `GET /api/projects/{id}/` - Szczegóły projektu
- `GET /api/projects/{id}/gantt/` - Dane Gantta
- `GET /api/tasks/` - Lista zadań

## Uwagi

- Frontend wymaga zalogowania użytkownika (wszystkie widoki mają `@login_required`)
- Używa Session Authentication Django
- CSRF token jest automatycznie obsługiwany przez Django
- Wszystkie żądania API używają `credentials: 'same-origin'`

