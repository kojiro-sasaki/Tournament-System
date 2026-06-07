# Tournament Management System

## Opis projektu

Tournament Management System to aplikacja z graficznym interfejsem użytkownika (GUI), służąca do organizacji i prowadzenia turniejów drużynowych. System umożliwia rejestrację drużyn, zarządzanie turniejami oraz śledzenie wyników rozgrywek.

## Cel projektu

Celem projektu jest stworzenie systemu wspomagającego organizację turniejów esportowych oraz automatyzującego proces zarządzania rozgrywkami.

## Planowane dyscypliny

System będzie umożliwiał organizację turniejów dla różnych dyscyplin esportowych.

Planowane dyscypliny:

- Counter-Strike 2
- Dota 2

Każdy turniej będzie przypisany do jednej wybranej dyscypliny.

## Role użytkowników

### Administrator

Administrator odpowiada za:

* tworzenie turniejów,
* ustawianie harmonogramu meczów,
* zarządzanie przebiegiem turnieju,
* wprowadzanie wyników,
* generowanie drabinki turniejowej.

### Drużyna

Drużyna posiada własne konto i może:

* zarejestrować konto drużyny,
* zalogować się do systemu,
* edytować informacje o drużynie,
* zapisać się do turnieju,
* przeglądać wyniki i drabinki.

## Informacje o drużynie

Drużyna może podać:

* nazwę drużyny,
* region,
* opis drużyny.

## Funkcjonalności systemu

### Zarządzanie drużynami

* rejestracja drużyn,
* logowanie,
* edycja danych drużyny.

### Zarządzanie turniejami

* tworzenie turniejów,
* wybór dyscypliny,
* rejestracja drużyn,
* rozpoczęcie turnieju,
* zarządzanie meczami.

### System rozgrywek

* automatyczne losowanie drużyn do drabinki,
* obsługa od 8 do 16 drużyn,
* generowanie kolejnych rund,
* automatyczne przesuwanie zwycięzców dalej,
* obsługa trybu Single Elimination.

### Mecze

* ustawianie czasu meczu,
* zapisywanie wyników,
* wyłanianie zwycięzców.

## Ograniczenia projektu

* aplikacja posiada GUI,
* liczba drużyn w turnieju: 8–16,
* wyniki meczów wprowadza administrator.

## Technologie

* Python
* GUI Framework (do ustalenia)
* SQLite
* pytest
* GitHub Actions
* Git + GitHub

## Organizacja pracy

* Scrum
* Feature Branch Workflow
* Pull Requests
* Code Review
* Continuous Integration
