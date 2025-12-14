# Workly 2.0 - System Zarządzania Projektami

Workly 2.0 to nowoczesny system do zarządzania projektami i zadaniami, zbudowany na Django i Tailwind CSS.

## 🚀 Szybki Start

### Wymagania
- Python 3.8+
- Node.js 16+ (dla frontendu)
- npm lub yarn

### Instalacja

1. **Sklonuj repozytorium:**
```bash
git clone <repo-url>
cd Workly2.0
```

2. **Zainstaluj zależności Python:**
```bash
pip install -r requirements.txt
```

3. **Zainstaluj zależności Node.js:**
```bash
npm install
```

4. **Zbuduj pliki CSS:**
```bash
npm run build-css
```

5. **Uruchom migracje (jeśli potrzebne):**
```bash
python manage.py migrate
```

6. **Uruchom serwer Django:**
```bash
python manage.py runserver
```

7. **Otwórz przeglądarkę:**
```
http://127.0.0.1:8000/
```

## 📊 Baza Demo

**Baza danych SQLite jest już wypełniona danymi demo!** Po uruchomieniu serwera możesz od razu zalogować się jednym z kont:

| Username | Hasło | Email |
|----------|-------|-------|
| `anna_kowalska` | `1` | anna.kowalska@workly.demo |
| `piotr_nowak` | `1` | piotr.nowak@workly.demo |
| `maria_wisniewska` | `1` | maria.wisniewska@workly.demo |

Baza zawiera:
- 3 użytkowników demo
- 5 projektów z realistycznymi nazwami
- 50 zadań (po 10 zadań na projekt) z różnymi statusami, datami i przypisaniami

Zobacz `README_DEMO.md` dla szczegółów.

## 📚 Dokumentacja

- **`QUICK_START.md`** - Szybki przewodnik startowy
- **`README_DEMO.md`** - Dokumentacja bazy demo
- **`README_FRONTEND.md`** - Dokumentacja frontendu
- **`README_TESTS.md`** - Dokumentacja testów i raportów

## 🧪 Testy i raporty

**Uruchom testy:**
```bash
python manage.py test
```

**Wygeneruj raport HTML z pokryciem kodu:**
```bash
python generate_test_report.py
```

Zobacz `README_TESTS.md` dla szczegółów.

## 🛠️ Funkcjonalności

### ✅ Zaimplementowane:
- Dashboard z podsumowaniem projektów i zadań
- Zarządzanie projektami (tworzenie, edycja, usuwanie)
- Zarządzanie zadaniami (tworzenie, edycja, usuwanie)
- Filtrowanie projektów i zadań
- System zależności między zadaniami
- Wizualizacja harmonogramu (Gantt chart - w przygotowaniu)
- Responsywny design (mobile-friendly)
- Przełącznik motywów (Synthwave / Jasny)
- API REST z dokumentacją Swagger

### 🔄 W przygotowaniu:
- Pełna integracja z biblioteką Gantta
- Powiadomienia
- Eksport danych (CSV/PDF)
- Komentarze do zadań

## 🎨 Technologie

### Backend:
- **Django 5.2+** - Framework webowy
- **Django REST Framework** - API REST
- **SQLite** - Baza danych (z danymi demo)

### Frontend:
- **Tailwind CSS 3.4+** - Utility-first CSS framework
- **DaisyUI 4.4+** - Komponenty UI dla Tailwind
- **Vanilla JavaScript** - Do komunikacji z API

## 📁 Struktura projektu

```
Workly2.0/
├── accounts/          # Aplikacja użytkowników
├── projects/          # Aplikacja projektów
├── tasks/             # Aplikacja zadań
├── dashboard/         # Dashboard API
├── gantt/             # Gantt chart API
├── frontend/          # Widoki frontendu
├── static/            # Pliki statyczne (CSS, JS, obrazy)
├── templates/         # Szablony HTML
└── db.sqlite3         # Baza danych (z danymi demo)
```

## 🔐 Uwagi bezpieczeństwa

⚠️ **To jest projekt demo/rozwojowy.** W środowisku produkcyjnym:
- Zmień `SECRET_KEY` w `settings.py`
- Ustaw `DEBUG = False`
- Użyj silnej bazy danych (PostgreSQL, MySQL)
- Skonfiguruj HTTPS
- Użyj silnych haseł dla użytkowników

## 📝 Licencja

[Określ licencję]

## 👥 Autorzy

Katarzyna Bąk

