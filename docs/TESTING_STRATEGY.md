# Stratégie de Tests - Spoke TTS API

## Table des matières

1. [Introduction](#1-introduction)
2. [Politique de Tests](#2-politique-de-tests)
3. [Types de Tests](#3-types-de-tests)
4. [Outils et Frameworks](#4-outils-et-frameworks)
5. [Stratégie d'Assurance Qualité (QA)](#5-stratégie-dassurance-qualité-qa)
6. [Accessibilité](#6-accessibilité)
7. [Exécution et CI/CD](#7-exécution-et-cicd)
8. [Métriques et Couverture](#8-métriques-et-couverture)
9. [Historique des Corrections](#9-historique-des-corrections)

---

## 1. Introduction

### 1.1 Contexte du Projet

Spoke TTS est une API REST de synthèse vocale émotionnelle basée sur StyleTTS 2. Le système permet de :
- Générer de la parole à partir de texte avec 21 émotions différentes
- Utiliser 107 voix de speakers différents
- Gérer un marketplace de voix premium via Supabase

### 1.2 Objectifs de la Stratégie de Tests

| Objectif | Description |
|----------|-------------|
| **Fiabilité** | Garantir que l'API répond correctement à toutes les requêtes valides |
| **Performance** | S'assurer que le système supporte la charge attendue |
| **Sécurité** | Protéger contre les vulnérabilités courantes (OWASP Top 10) |
| **Qualité** | Maintenir un code propre et maintenable |
| **Accessibilité** | Respecter les normes WCAG pour l'interface utilisateur |

### 1.3 Périmètre des Tests

**In Scope :**
- API REST (endpoints Flask)
- Logique métier (emotion routing, voice matching, marketplace)
- Intégration avec Supabase
- Performance sous charge

**Out of Scope :**
- Modèles de ML StyleTTS2 (pré-entraînés, non modifiables)
- Infrastructure Cloudflare/hébergement

---

## 2. Politique de Tests

### 2.1 Principes Directeurs

1. **Test-First Mindset** : Écrire les tests avant ou pendant le développement
2. **Automatisation** : Tous les tests doivent être automatisés et reproductibles
3. **Isolation** : Chaque test doit être indépendant des autres
4. **Rapidité** : Les tests unitaires doivent s'exécuter en < 1 seconde chacun
5. **Couverture** : Objectif minimum de 80% de couverture de code

### 2.2 Niveaux de Tests

```
┌─────────────────────────────────────────┐
│           Tests E2E (End-to-End)        │  <- Peu nombreux, lents
├─────────────────────────────────────────┤
│        Tests d'Intégration              │  <- Modérés
├─────────────────────────────────────────┤
│          Tests Unitaires                │  <- Nombreux, rapides
└─────────────────────────────────────────┘
        Pyramide des Tests
```

### 2.3 Critères d'Acceptation

Un test est considéré comme passant si :
- ✅ Il s'exécute sans erreur
- ✅ Les assertions sont toutes validées
- ✅ Le temps d'exécution est dans les limites acceptables
- ✅ Aucun effet de bord n'est détecté

### 2.4 Gestion des Environnements

| Environnement | Usage | Base de données |
|---------------|-------|-----------------|
| **Local** | Développement | SQLite mock / Supabase dev |
| **CI** | Tests automatisés | Mocks |
| **Staging** | Tests d'intégration | Supabase staging |
| **Production** | Smoke tests uniquement | Supabase prod |

---

## 3. Types de Tests

### 3.1 Tests Unitaires

**Objectif** : Tester les fonctions et classes isolément

**Composants testés :**
- `emotion_router.py` : Mapping émotions → modèles
- `voice_matcher.py` : Algorithme de matching vocal
- `marketplace.py` : Logique de gestion des voix

**Exemple de scénarios :**

| ID | Scénario | Entrée | Sortie attendue |
|----|----------|--------|-----------------|
| UT-01 | Emotion valide | `get_model("anger")` | Chemin vers le modèle |
| UT-02 | Emotion invalide | `get_model("invalid")` | `ValueError` |
| UT-03 | Mapping joy→amusement | `EMOTION_MAPPING["joy"]` | `"amusement"` |
| UT-04 | Voice matching male | `match_voices("male voice")` | Liste de speakers masculins |
| UT-05 | User init | `init_user("user123")` | Voix 1-4 attribuées |

### 3.2 Tests d'Intégration

**Objectif** : Tester l'interaction entre les composants et l'API

**Endpoints testés :**

| ID | Endpoint | Méthode | Scénario |
|----|----------|---------|----------|
| IT-01 | `/ping` | GET | Retourne status success |
| IT-02 | `/health` | GET | Retourne healthy |
| IT-03 | `/synthesize` | POST | Génère un audio WAV valide |
| IT-04 | `/synthesize` | POST | Erreur 400 si paramètre manquant |
| IT-05 | `/synthesize` | POST | Erreur 403 si voix non possédée |
| IT-06 | `/random_voice` | POST | Retourne un speaker du bon genre |
| IT-07 | `/marketplace/catalog` | GET | Retourne la liste des voix |
| IT-08 | `/marketplace/purchase` | POST | Achat réussi |
| IT-09 | `/voices/owned` | GET | Retourne les voix de l'utilisateur |

### 3.3 Tests de Charge (Performance)

**Objectif** : Valider la performance sous charge

**Scénarios de charge :**

| ID | Scénario | Utilisateurs | Durée | Critère de succès |
|----|----------|--------------|-------|-------------------|
| LT-01 | Charge normale | 10 users | 5 min | Temps réponse < 2s (hors synthèse) |
| LT-02 | Pic de charge | 50 users | 2 min | Pas d'erreur 5xx |
| LT-03 | Endurance | 5 users | 30 min | Pas de memory leak |

**Métriques surveillées :**
- Temps de réponse moyen (p50, p95, p99)
- Taux d'erreur
- Utilisation CPU/RAM
- Throughput (requêtes/seconde)

### 3.4 Tests de Sécurité

**Objectif** : Identifier les vulnérabilités

**Vérifications :**

| ID | Catégorie | Test |
|----|-----------|------|
| ST-01 | Injection | SQL injection dans user_id |
| ST-02 | Injection | Command injection dans text |
| ST-03 | XSS | Scripts dans les paramètres |
| ST-04 | Auth | Accès sans user_id valide |
| ST-05 | CORS | Vérification des origines autorisées |
| ST-06 | Rate Limiting | Protection contre le spam |
| ST-07 | Dépendances | Vulnérabilités connues (CVE) |

### 3.5 Tests E2E (End-to-End)

**Objectif** : Valider le parcours utilisateur complet

**Scénarios :**

| ID | Parcours |
|----|----------|
| E2E-01 | Nouvel utilisateur → obtient voix classiques → génère audio |
| E2E-02 | Utilisateur → achète voix premium → utilise la voix |
| E2E-03 | Utilisateur → demande voix random → génère audio |

---

## 4. Outils et Frameworks

### 4.1 Choix des Outils

| Outil | Usage | Justification |
|-------|-------|---------------|
| **pytest** | Tests unitaires & intégration | Standard Python, fixtures puissantes, plugins riches |
| **pytest-cov** | Couverture de code | Intégration native avec pytest |
| **requests** | Tests API HTTP | Simple, bien documenté |
| **locust** | Tests de charge | Python-native, UI web, scriptable |
| **bandit** | Analyse sécurité statique | Détecte les failles de sécurité courantes |
| **safety** | Audit dépendances | Vérifie les CVE dans requirements.txt |
| **black** | Formatage code | Style cohérent |
| **flake8** | Linting | Détecte les erreurs de style |

### 4.2 Justification des Choix

#### pytest vs unittest
- **pytest** : Syntaxe plus simple, fixtures réutilisables, meilleure sortie
- **unittest** : Plus verbeux, moins de plugins

→ **Choix : pytest** pour sa simplicité et son écosystème riche

#### locust vs JMeter vs k6
- **locust** : Python-native (cohérent avec le projet), facile à scripter
- **JMeter** : Plus complet mais complexe, Java-based
- **k6** : JavaScript, excellent mais langue différente

→ **Choix : locust** pour rester en Python et faciliter la maintenance

#### bandit vs SonarQube
- **bandit** : Léger, spécifique Python, gratuit
- **SonarQube** : Plus complet mais nécessite un serveur

→ **Choix : bandit** pour sa simplicité d'intégration CI

### 4.3 Structure des Fichiers de Tests

```
tests/
├── __init__.py
├── conftest.py              # Fixtures partagées
├── pytest.ini               # Configuration pytest
│
├── unit/                    # Tests unitaires
│   ├── __init__.py
│   ├── test_emotion_router.py
│   ├── test_voice_matcher.py
│   └── test_marketplace.py
│
├── integration/             # Tests d'intégration
│   ├── __init__.py
│   ├── test_api_endpoints.py
│   └── test_synthesis.py
│
├── load/                    # Tests de charge
│   └── locustfile.py
│
└── security/                # Tests de sécurité
    └── test_security.py
```

---

## 5. Stratégie d'Assurance Qualité (QA)

### 5.1 Processus QA

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   Develop    │───>│   Commit     │───>│   CI Tests   │───>│   Review     │
└──────────────┘    └──────────────┘    └──────────────┘    └──────────────┘
                                               │
                                               ▼
                           ┌─────────────────────────────────┐
                           │  Si échec : Fix → Re-commit     │
                           └─────────────────────────────────┘
```

### 5.2 Critères de Qualité

| Critère | Seuil | Outil de mesure |
|---------|-------|-----------------|
| Couverture de code | ≥ 80% | pytest-cov |
| Complexité cyclomatique | < 10 | radon |
| Vulnérabilités critiques | 0 | bandit, safety |
| Tests passants | 100% | pytest |
| Temps de build CI | < 10 min | GitHub Actions |

### 5.3 Revue de Code

**Checklist de revue :**
- [ ] Tests ajoutés/mis à jour pour les changements
- [ ] Pas de code commenté ou debug
- [ ] Documentation mise à jour si nécessaire
- [ ] Pas de secrets/credentials dans le code
- [ ] Gestion des erreurs appropriée
- [ ] Nommage clair des variables/fonctions

### 5.4 Gestion des Bugs

**Processus :**
1. Bug détecté (test ou production)
2. Création d'un ticket/issue GitHub
3. Écriture d'un test reproduisant le bug
4. Correction du code
5. Vérification que le test passe
6. Code review
7. Merge

---

## 6. Accessibilité

### 6.1 Normes Appliquées

Le projet respecte les **WCAG 2.1 niveau AA** pour l'interface utilisateur (frontend).

### 6.2 Critères d'Accessibilité

| Critère WCAG | Description | Application |
|--------------|-------------|-------------|
| 1.1.1 | Alternatives textuelles | Alt text pour les images |
| 1.4.3 | Contraste | Ratio minimum 4.5:1 |
| 2.1.1 | Clavier | Navigation complète au clavier |
| 2.4.1 | Contourner les blocs | Skip links |
| 3.1.1 | Langue de la page | `lang="fr"` ou `lang="en"` |
| 4.1.2 | Nom, rôle, valeur | ARIA labels appropriés |

### 6.3 Tests d'Accessibilité

**Outils utilisés :**
- **axe-core** : Audit automatisé
- **Lighthouse** : Score d'accessibilité
- **NVDA/VoiceOver** : Tests manuels avec lecteur d'écran

### 6.4 Spécificités Audio

Pour une application TTS, l'accessibilité inclut :
- Sous-titres/transcriptions du texte généré
- Contrôles audio accessibles (play/pause/volume)
- Feedback visuel de l'état de génération
- Temps de génération annoncé pour les utilisateurs

---

## 7. Exécution et CI/CD

### 7.1 Exécution Locale

```bash
# Installer les dépendances de test
pip install pytest pytest-cov requests locust bandit safety

# Lancer tous les tests
pytest tests/ -v

# Lancer avec couverture
pytest tests/ --cov=server --cov-report=html

# Lancer les tests unitaires uniquement
pytest tests/unit/ -v

# Lancer les tests d'intégration
pytest tests/integration/ -v

# Lancer l'analyse de sécurité
bandit -r server/
safety check -r requirements.txt

# Lancer les tests de charge
locust -f tests/load/locustfile.py --host=http://localhost:5000
```

### 7.2 Pipeline CI/CD (GitHub Actions)

```yaml
# .github/workflows/tests.yml
name: Tests

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov bandit safety

      - name: Run unit tests
        run: pytest tests/unit/ -v --cov=server

      - name: Run integration tests
        run: pytest tests/integration/ -v

      - name: Security scan
        run: |
          bandit -r server/ -ll
          safety check -r requirements.txt

      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

### 7.3 Fréquence d'Exécution

| Type de test | Déclencheur | Environnement |
|--------------|-------------|---------------|
| Unitaires | Chaque commit | CI |
| Intégration | Chaque PR | CI |
| Charge | Hebdomadaire | Staging |
| Sécurité | Chaque commit + quotidien | CI |

---

## 8. Métriques et Couverture

### 8.1 Objectifs de Couverture

| Module | Couverture cible |
|--------|------------------|
| `server/server.py` | ≥ 85% |
| `server/emotion_router.py` | ≥ 90% |
| `server/voice_matcher.py` | ≥ 80% |
| `server/marketplace.py` | ≥ 80% |
| **Global** | **≥ 80%** |

### 8.2 Rapport de Couverture

```bash
# Générer le rapport HTML
pytest tests/ --cov=server --cov-report=html

# Voir le rapport
open htmlcov/index.html
```

### 8.3 Métriques de Performance

| Endpoint | Temps de réponse cible |
|----------|------------------------|
| `/ping` | < 50ms |
| `/health` | < 50ms |
| `/random_voice` | < 100ms |
| `/marketplace/catalog` | < 200ms |
| `/voices/owned` | < 200ms |
| `/synthesize` | < 30s (dépend du texte) |

---

## 9. Historique des Corrections

### 9.1 Suivi des Corrections

Toutes les corrections issues des tests sont tracées via :
- **Commits Git** avec messages descriptifs
- **Issues GitHub** pour les bugs
- **Pull Requests** avec référence aux tests

### 9.2 Format des Commits

```
type(scope): description

[optional body]

Fixes #issue_number
```

Types : `fix`, `feat`, `test`, `docs`, `refactor`

### 9.3 Exemple d'Historique

| Date | Commit | Description | Tests liés |
|------|--------|-------------|------------|
| 2025-01-15 | `fix(api): handle missing emotion parameter` | Ajout validation | IT-04 |
| 2025-01-16 | `fix(security): sanitize user input` | Protection injection | ST-02 |
| 2025-01-20 | `test(unit): add emotion_router tests` | Nouveaux tests | UT-01, UT-02 |

---

## Annexes

### A. Commandes Utiles

```bash
# Lancer un test spécifique
pytest tests/unit/test_emotion_router.py::test_valid_emotion -v

# Lancer avec verbose et stop au premier échec
pytest tests/ -v -x

# Générer rapport JUnit (pour CI)
pytest tests/ --junitxml=report.xml
```

### B. Configuration pytest.ini

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_functions = test_*
addopts = -v --tb=short
filterwarnings =
    ignore::DeprecationWarning
```

### C. Contacts

- **Responsable Tests** : [Nom]
- **Responsable QA** : [Nom]
- **DevOps** : [Nom]

---

*Document créé le 30/01/2025 - Version 1.0*
*Dernière mise à jour : 30/01/2025*
