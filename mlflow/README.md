---
title: Mlflow
emoji: 👁
colorFrom: green
colorTo: blue
sdk: docker
pinned: false
short_description: Serveur MLflow pour projets école Jedha
---

# MLflow Server – S3 + Neon + Docker

Ce dépôt permet de lancer un serveur **MLflow** dans un conteneur Docker, avec :

- **Neon PostgreSQL** comme _backend store_ (métadonnées MLflow)
- **Amazon S3** comme _artifact store_ (modèles, métriques, fichiers)
- Une interface accessible sur : **http://localhost:4000**

---

## 1. Prérequis

### 1.1. Un bucket S3 (ARTIFACT_ROOT)

1. Connectez-vous à la console AWS.
2. Allez dans **S3 → Create bucket**.
3. Choisissez un nom (ex. `mlflow-cicd`) et une région (par ex. `eu-central-1`).
4. (Optionnel) créez un dossier dans le bucket, par exemple `mlflow-artifacts/`.

**Valeur à utiliser pour MLflow :**

`s3://mlflow-cicd/mlflow-artifacts/`

---

### 1.2. Un utilisateur IAM avec clés d’accès

Nécessaire pour que MLflow puisse écrire dans S3.

1. Allez dans **IAM → Users → Create user**.
2. Activez **Programmatic access**.
3. Donnez-lui les permissions nécessaires (pour tester : `AmazonS3FullAccess`).
4. Récupérez :
   - `AWS_ACCESS_KEY_ID`
   - `AWS_SECRET_ACCESS_KEY`

---

### 1.3. Base de données Neon (BACKEND_STORE_URI)

1. Créez un projet sur : https://neon.tech
2. Récupérez l’URL PostgreSQL du type :

`postgresql://<user>:<password>@<host>/<database>?sslmode=require`

3. Exemple :
   `postgresql://neondb_owner:MON_MDP@ep-xxxx-pooler.c-2.eu-central-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require`

Cette URL devient votre `BACKEND_STORE_URI`.

---

## 2. Construire l'image Docker

Depuis le répertoire contenant le `Dockerfile` :

```bash
docker build -t mlflow-cicd .
```

---

## 3. Configuration des variables d’environnement
Les variables d'environnement suivantes doivent être définies dans les **Repository secrets** du Space :

### 3.1. Base de données (obligatoire)
- `BACKEND_STORE_URI` : URL de connexion PostgreSQL
  - Format : `postgresql://username:password@host:port/database?sslmode=require`
  - Exemple : `postgresql://mlflow_user:mypassword@db.example.com:5432/mlflow_db?sslmode=require`

### 3.2. Stockage des artifacts S3 (obligatoire)
- `ARTIFACT_ROOT` : Chemin S3 pour stocker les artifacts
  - Format : `s3://nom-du-bucket/chemin/vers/artifacts`
  - Exemple : `s3://my-mlflow-bucket/mlflow-artifacts`

- `AWS_ACCESS_KEY_ID` : Clé d'accès AWS
- `AWS_SECRET_ACCESS_KEY` : Clé secrète AWS
- `AWS_DEFAULT_REGION` : Région AWS du bucket S3
  - Exemple : `eu-west-1`, `us-east-1`, etc.

### 3.3. Authentification MLflow (optionnel)
- `MLFLOW_TRACKING_USERNAME` : Nom d'utilisateur pour l'accès à MLflow
- `MLFLOW_TRACKING_PASSWORD` : Mot de passe pour l'accès à MLflow

## 4. Architecture

- **Backend store** : PostgreSQL (métadonnées des runs, paramètres, métriques)
- **Artifact store** : AWS S3 (modèles, fichiers, plots)
- **Interface** : MLflow UI accessible via l'URL du Space

## 5. Utilisation

Depuis votre code Python :
```python
import mlflow

# Configurer l'URL de tracking
mlflow.set_tracking_uri("https://VOTRE_USERNAME-VOTRE_SPACE_NAME.hf.space")

# Si authentification activée
# import os
# os.environ["MLFLOW_TRACKING_USERNAME"] = "votre_username"
# os.environ["MLFLOW_TRACKING_PASSWORD"] = "votre_password"

# Logger vos expériences
with mlflow.start_run():
    mlflow.log_param("learning_rate", 0.01)
    mlflow.log_metric("accuracy", 0.95)
    mlflow.log_artifact("model.pkl")
```