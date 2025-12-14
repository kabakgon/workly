# Baza Demo - Workly 2.0

## Opis

Baza demo zawiera przykładowe dane do testowania aplikacji Workly 2.0. Zawiera:
- 3 użytkowników demo (z hasłem `1`)
- 5 projektów z realistycznymi nazwami
- 50 zadań (po 10 zadań na projekt) z różnymi statusami, datami i przypisaniami

## Baza danych w repozytorium

**Baza danych SQLite (`db.sqlite3`) jest już zawarta w repozytorium** z wypełnionymi danymi demo. Po sklonowaniu repozytorium i uruchomieniu serwera Django, możesz od razu zalogować się jednym z kont demo (patrz sekcja "Użytkownicy demo" poniżej).

## Odtworzenie bazy demo (opcjonalnie)

Jeśli chcesz odtworzyć bazę demo od zera, uruchom następującą komendę:

```bash
python manage.py setup_demo_data
```

Lub jeśli używasz `py`:

```bash
py manage.py setup_demo_data
```

**Uwaga:** Ta komenda usunie wszystkie istniejące projekty i zadania przed utworzeniem nowych danych demo.

## Użytkownicy demo

Po uruchomieniu komendy, możesz zalogować się jednym z następujących kont:

| Username | Hasło | Email |
|----------|-------|-------|
| `anna_kowalska` | `1` | anna.kowalska@workly.demo |
| `piotr_nowak` | `1` | piotr.nowak@workly.demo |
| `maria_wisniewska` | `1` | maria.wisniewska@workly.demo |

## Co robi komenda?

1. **Dodaje 3 użytkowników demo** - jeśli użytkownicy już istnieją, aktualizuje ich hasła na `1`
2. **Usuwa wszystkie istniejące projekty i zadania** - czyści bazę danych przed dodaniem danych demo
3. **Tworzy 5 projektów demo** z realistycznymi nazwami:
   - System Zarządzania Projektami
   - Aplikacja Mobilna E-Commerce
   - Portal Klienta B2B
   - System Analizy Danych
   - Migracja do Chmury
4. **Dodaje po 10 zadań do każdego projektu** z:
   - Różnymi statusami (todo, in_progress, review, done, blocked)
   - Różnymi datami rozpoczęcia i zakończenia
   - Różnymi przypisaniami (lub bez przypisania)
   - Różnymi wartościami postępu (0-100%)

## Uwagi

- **Istniejący użytkownicy są zachowywani** - komenda nie usuwa istniejących użytkowników, tylko dodaje nowych
- **Wszystkie projekty i zadania są usuwane** - przed dodaniem danych demo, wszystkie istniejące projekty i zadania są usuwane
- **Zależności są usuwane automatycznie** - wraz z zadaniami są usuwane również wszystkie zależności między zadaniami

## Przykładowe użycie

```bash
# Aktywuj środowisko wirtualne (jeśli używasz)
source venv/bin/activate  # Linux/Mac
# lub
venv\Scripts\activate  # Windows

# Uruchom komendę
python manage.py setup_demo_data
```

Po uruchomieniu komendy zobaczysz szczegółowe informacje o utworzonych danych.

