# Testy - Workly 2.0

## Jak uruchomić testy

### 1. Upewnij się, że środowisko wirtualne jest aktywne

**Windows:**
```bash
venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 2. Uruchom wszystkie testy

```bash
python manage.py test
```

Lub jeśli używasz `py`:
```bash
py manage.py test
```

### 3. Uruchom testy dla konkretnej aplikacji

```bash
# Testy dla projektów
python manage.py test projects

# Testy dla zadań
python manage.py test tasks

# Testy dla dashboardu
python manage.py test dashboard

# Testy dla Gantta
python manage.py test gantt
```

### 4. Uruchom konkretny plik testów

```bash
python manage.py test projects.tests
python manage.py test tasks.tests
python manage.py test dashboard.tests
python manage.py test gantt.tests
```

### 5. Uruchom konkretny test case

```bash
python manage.py test projects.tests.ProjectAPITestCase
python manage.py test tasks.tests.TaskAPITestCase
python manage.py test tasks.tests.DependencyAPITestCase
python manage.py test dashboard.tests.DashboardAPITestCase
python manage.py test gantt.tests.GanttAPITestCase
```

### 6. Uruchom konkretny test

```bash
python manage.py test projects.tests.ProjectAPITestCase.test_create_project
python manage.py test tasks.tests.TaskAPITestCase.test_list_tasks
```

### 7. Opcje dodatkowe

**Verbose output (szczegółowe informacje):**
```bash
python manage.py test --verbosity=2
```

**Zatrzymaj po pierwszym błędzie:**
```bash
python manage.py test --failfast
```

**Zachowaj bazę testową (do debugowania):**
```bash
python manage.py test --keepdb
```

**Pokaż wszystkie dostępne opcje:**
```bash
python manage.py test --help
```

## 📊 Generowanie raportów z testów

### 1. Raport pokrycia kodu (Coverage)

**Instalacja coverage:**
```bash
pip install coverage
```

**Uruchom testy z coverage:**
```bash
coverage run --source='.' manage.py test
```

**Wygeneruj raport tekstowy:**
```bash
coverage report
```

**Wygeneruj raport HTML (zalecane):**
```bash
coverage html
```

Raport HTML będzie dostępny w folderze `htmlcov/index.html`. Otwórz go w przeglądarce.

**Wygeneruj raport XML (dla CI/CD):**
```bash
coverage xml
```

### 2. Raport XML (JUnit format)

Django nie ma wbudowanego generatora XML, ale możesz użyć:

```bash
python manage.py test --verbosity=2 > test_results.txt
```

Lub użyć zewnętrznego narzędzia jak `pytest` z `pytest-django`:
```bash
pip install pytest pytest-django
pytest --junitxml=test_results.xml
```

### 3. Raport do pliku

**Zapisz output testów do pliku:**
```bash
python manage.py test --verbosity=2 > test_report.txt 2>&1
```

**Zapisz tylko błędy:**
```bash
python manage.py test --verbosity=2 2>&1 | grep -E "(FAIL|ERROR)" > test_errors.txt
```

### 4. Pełny raport z coverage (zalecane)

```bash
# 1. Uruchom testy z coverage
coverage run --source='.' manage.py test --verbosity=2

# 2. Wygeneruj raport HTML
coverage html

# 3. Otwórz raport w przeglądarce
# Windows:
start htmlcov/index.html
# Linux/Mac:
open htmlcov/index.html
# lub po prostu otwórz plik htmlcov/index.html w przeglądarce
```

## Struktura testów

### `projects/tests.py`
- `ProjectAPITestCase` - testy dla endpointów projektów
  - Listowanie, tworzenie, pobieranie, aktualizacja, usuwanie
  - Filtrowanie, wyszukiwanie, sortowanie
  - Uprawnienia (owner vs non-owner)

### `tasks/tests.py`
- `TaskAPITestCase` - testy dla endpointów zadań
  - Listowanie, tworzenie, pobieranie, aktualizacja, usuwanie
  - Kopiowanie zadań
  - Filtrowanie, wyszukiwanie
  - Uprawnienia (assignee vs project owner)
- `DependencyAPITestCase` - testy dla zależności
  - Tworzenie, aktualizacja, usuwanie
  - Walidacja (cykle, różne projekty)

### `dashboard/tests.py`
- `DashboardAPITestCase` - testy dla dashboard API
  - `/api/my/projects/` - lista projektów użytkownika
  - `/api/my/tasks/` - lista zadań użytkownika
  - `/api/my/summary/` - podsumowanie dashboardu
  - `/api/my/timeline/` - widok timeline
  - `/api/users/` - lista użytkowników

### `gantt/tests.py`
- `GanttAPITestCase` - testy dla Gantt API
  - `/api/projects/{id}/gantt/` - dane Gantta
  - Pola zadań i zależności
  - Filtrowanie zależności po projekcie

## Przykładowe uruchomienie

```bash
# Aktywuj środowisko wirtualne
venv\Scripts\activate  # Windows
# lub
source venv/bin/activate  # Linux/Mac

# Uruchom wszystkie testy
python manage.py test --verbosity=2

# Oczekiwany wynik:
# Creating test database for alias 'default'...
# System check identified no issues (0 silenced).
# ...................... (testy przechodzą)
# ----------------------------------------------------------------------
# Ran XX tests in X.XXXs
# OK
# Destroying test database for alias 'default'...
```

## Rozwiązywanie problemów

### Błąd: "ModuleNotFoundError: No module named 'django'"
- Upewnij się, że środowisko wirtualne jest aktywne
- Zainstaluj zależności: `pip install -r requirements.txt`

### Błąd: "Database locked"
- Zamknij wszystkie połączenia z bazą danych
- Uruchom testy ponownie

### Testy są wolne
- Użyj `--keepdb` aby nie tworzyć bazy za każdym razem
- Uruchom tylko testy dla konkretnej aplikacji

## Statystyki testów

Po uruchomieniu testów zobaczysz:
- Liczbę uruchomionych testów
- Czas wykonania
- Liczbę błędów (jeśli występują)
- Szczegóły błędów (z `--verbosity=2`)

## CI/CD

Testy można uruchomić w CI/CD pipeline:

```yaml
# Przykład dla GitHub Actions
- name: Run tests
  run: |
    python manage.py test --verbosity=2

- name: Generate coverage report
  run: |
    coverage run --source='.' manage.py test
    coverage xml
    coverage html
```

## Konfiguracja coverage

Możesz utworzyć plik `.coveragerc` w głównym katalogu projektu:

```ini
[run]
source = .
omit = 
    */migrations/*
    */tests/*
    */venv/*
    */env/*
    manage.py
    */settings.py

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise AssertionError
    raise NotImplementedError
    if __name__ == .__main__.:
    if TYPE_CHECKING:
    @abstractmethod
```
