# Détection de fraude automatique
## 📄 Sommaire

- [❓ Contexte](#-contexte)
- [🎯 Objectifs du projet](#-objectifs-du-projet)
- [🏗️ Architecture globale](#️-architecture-globale)
- [📁 Structure du projet](#-structure-du-projet)
- [🛠️ Technologies](#️-technologies)
- [💻 Installation](#-installation)
- [🚀 Utilisation](#-utilisation)
- [🔄 Data Pipeline](#-data-pipeline)

---

## ❓ Contexte

La fraude représente un problème majeur pour les institutions financières. En 2019, la Banque centrale européenne estimait que les transactions frauduleuses par carte bancaire dans l'UE dépassaient le milliard d'euros ! 😮

L'IA peut contribuer à résoudre ce problème en détectant les paiements frauduleux avec une grande précision. Ce cas d'usage est d'ailleurs devenu l'un des plus populaires auprès des data scientists.

Cependant, malgré la puissance des algorithmes développés, le défi consiste désormais à les déployer en production. Il s'agit de prédire les paiements frauduleux en temps réel et d'y réagir de manière appropriée.

---

## 🎯 Objectifs du projet
Des clients ont fait appel à votre équipe pour une première version du projet qui a été réalisée. Elle leur permet d'être averti par une notification lorsqu'une fraude est détectée, et tous les matins ils peuvent vérifier les paiements et les fraudes survenus la veille.

Satisfaits de cette première version ils ont demandé d'améliorer les points suivants :

- Proposer un nouveau modèle de détection de fraude, plus performant que celui de la première version
- Enrichir les rapports de visualisation avec la possibilité de sélectionner des plages de date, et ajouter des diagrammes sur les catégories de transaction concernées par les fraudes
- intégrer une pipeline CICD afin que les développements réalisés par l'équipe technique n'impacte pas la stabilité de l'application en production.
- surveiller les performances du modèle et les détecter les éventuels drifts de données


---

## 🏗️ Architecture globale
![Schéma d'architecture](data/schéma_architecture.png)

---

## 📁 Structure du projet
```
BLOC4-CICD/
│
├── 📁 app/
│   ├── 🐳 Dockerfile
│   ├── 🐍 extract.py
│   ├── 🐍 load_model.py
│   ├── 🐍 load.py
│   ├── 📄 requirements.txt
│   ├── 🐍 run_pipeline.py
│   ├── 💻 run.sh
│   ├── 🐍 transform.py
│   └── 🐍 worker.py
│
├── 📁 data/
│   └── 📊 fraudTest.csv
│   └── 🏗️ schéma_architecture.png
│
├── 📁 mlflow/
│   ├── 📄 .gitattributes
│   ├── 🐍 app.py
│   ├── 🐳 Dockerfile
│   ├── 📖 README.md
│   └── 📄 requirements.txt
│
├── 📁 model_api/
│   ├── 🐍 app.py
│   ├── 🐳 Dockerfile
│   ├── 📖 README.md
│   └── 📄 requirements.txt
│
├── 📁 streamlit/
│   ├── 🐳 Dockerfile
│   └── 📄 requirements.txt
│
├── 📁 tests/
│   ├── 🐳 Dockerfile
│   ├── ⚙️ pytest.ini
│   ├── 📄 requirements.txt
│   ├── 🧪 test_extract.py
│   ├── 🧪 test_load_model.py
│   ├── 🧪 test_load.py
│   └── 🧪 test_transform.py
│
├── 📁 train/
│   └── 🐍 train.py
│
├── 🔐 .env
├── 📄 .gitignore
├── 📓 dataexplorer.ipynb
├── 📖 README.md
└── 📄 requirements.txt
```

---

## 🛠️ Technologies

### Pile de base
```python
Python 3.10            # Langage de programmation principal
SQLAlchemy             # Bibliothèque ORM base de données
Pandas                 # Bibliothèque pour manipulation Data
NumPy                  # Bibliothèque pour calcul scientifique
Requests               # Bibliothèque HTTP for appels API
Pytest                 # Bibliothèque pour tests automatisés
Evidently              # Bibliothèque pour surveillance du modèle
```

### Cloud & Base de données
- **AWS S3**: Stockage cloud pour données non structurées et fichiers
- **Neon DB**: Base de données PostgreSQL pour les données structurées

### APIs
- **Real time fraud API**: Données fictives de transactions bancaires
- **Fraud Detection**: Modèle de prédiction de fraude

### Development Tools
- **Jupyter Notebook**: Analyse exploratoire des données
- **VS Code**: IDE principal
- **Git**: Contrôle de version
- **Github**: pipeline CICD via github actions
- **Hugging Face Spaces** : Déploiement d'applications

---

## 💻 Installation

### Prérequis
- Python 3.10
- Compte AWS (pour S3)
- Compte Neon DB (compte gratuit disponible)
- Compte Docker Hub (https://hub.docker.com)
- Compte Hugging Face (https://huggingface.co)


### Etapes de configuration

1. **Cloner le dépôt git**
```bash
git clone https://github.com/Aurelie-R/bloc4-cicd.git
cd bloc4-cicd
```

2. **Créer un environnement virtuel et installer les dépendances**
```bash
python -m venv venv
source venv/bin/activate  # ou venv\Scripts\activate sur Windows
pip install -r requirements.txt
```

3. **Configurer les variables d'environnement**
```bash
cp config/.env.example .env
# Edit .env with your API keys and credentials
```

**Variables d'environnement requises:**
```env
# AWS S3
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
S3_BUCKET_NAME=your_bucket_name

# Neon DB
DATABASE_URL=postgresql://user:password@host/database
```

---

## 🚀 Utilisation
### 1. Création et déploiement du serveur mlflow sur Hugging Face Spaces
Le détail de l'installation est documenté dans le [fichier README](mlflow/README.md) du répertoire mlflow.

Les valeurs des variables d'envrionnement à renseigner dans les secrets du hugging face space sont les même que celles définies dans votre fichier .venv

Une fois le container déployé, vérifier que l'on accède bien au serveur mlflow sur https://VOTRE_USERNAME-VOTRE_SPACE_NAME.hf.space 

### 2. Entrainement du modèle de ML
```bash
python train/train.py 

```
Une fois l'entrainement terminé, aller sur la console mlflow (disponible sous votre hugging face space), cliquer sur le menu "Models" du bandeau du haut, puis sur le modèle "fraud_detector_RF" et ajouter l'alias "production" à une des versions du modèle.

### 3. Lancement de la pipeline d'ingestion de données
```bash
python app/worker.py 

```
### 4. Création et déploiement de l'application streamlit pour visualisation des données (sur Huggigng Face Spaces)
Le détail de l'installation est documenté dans le [fichier README](streamlit/README.md) du répertoire streamlit.

Les valeurs des variables d'envrionnement à renseigner dans les secrets du hugging face space sont les même que celles définies dans votre fichier .venv


### 5. Visualisation des données
Une fois le container streamlit déployé, l'application de visualisation des données est disponible sur https://VOTRE_USERNAME-VOTRE_SPACE_NAME.hf.space  défini lors de l'installation du point 4.
Par défaut l'application affiche les données de la veille. Pour changer la sélection de dates, choisir une nouvelle plage dans le calendrier et cliquer sur "Appliquer les filtres".

![Rapport de fraudes](data/rapport_fraudes.png)

### 6. Création et déploiement de l'application streamlit pour visualisation des données (sur Huggigng Face Spaces)
Le détail de l'installation est documenté dans le [fichier README](API/README.md) du répertoire API.

Les valeurs des variables d'envrionnement à renseigner dans les secrets du hugging face space sont les même que celles définies dans votre fichier .venv


### 7. Utilisation de l'API
Une fois le container fastAPI déployé, l'API est disponible sur https://VOTRE_USERNAME-VOTRE_SPACE_NAME.hf.space  défini lors de l'installation du point 6.

![API fraude](data/API_fraude.png)

---

## 🔄 Data Pipeline

### Etape 1: Extract
- **Real time fraud API Call**: R2cupère une transaction bancaire (fictive)
- Données brutes stockées dans **AWS S3** (format json)

### Etape 2: Transform
- Transformation des données de l'API pour coller aux attendus du modèle
- Appel du modèle de détection de fraude
- Alerting si fraude détectés
- Stockage des données transformées dans **AWS S3** (format CSV)

### Etape 3: Load
- En utilisant **SQLAlchemy**, enregistrement des données dans Neon DB

---

## 🔄 CI / CD

### Etape 1: Mise à jour du code
A chaque mise à jour du code sur github, une action de vérification est lancée.
![Workflow CICD](data/workflow-cicd.png)

### Etape 2: Tests d'intégration
Un ensemble de tests de vérification du code sont exécutés en automatique pour s'assurer de la conformité de celui ci. Si l'ensemble des tests se termine sans échec, on passe à l'étape suivante. Sinon un rapport d'erreur est envoyé.
![Tests 1](data/Pytest1-2.png)
![Tests 2](data/Pytest2-2.png)

### Etape 3: Déploiement automatisé
Si tous les tests de l'étape précedente se sont déroulés sans erreur, la nouvelle application est déployée dans un container docker.
![Déploiement](data/deploiement_application.png)




