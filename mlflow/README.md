---
title: Mlflow
emoji: 📊
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
- Une interface accessible sur : **https://VOTRE_USERNAME-VOTRE_SPACE_NAME.hf.space**

---

## 1. Prérequis

### 1.1. Un bucket S3 (ARTIFACT_ROOT)

1. Connectez-vous à la console AWS.
2. Allez dans **S3 → Create bucket**.
3. Choisissez un nom (ex. `mlflow-cicd`) et une région (par ex. `eu-central-1`). (utiliser le même pour l'ensemble du projet fraude)
4. (Optionnel) créez un dossier dans le bucket, par exemple `mlflow-artifacts/`.

**Valeur à utiliser pour MLflow avec cet exemple :**
`ARTIFACT_ROOT=s3://mlflow-cicd/mlflow-artifacts/`

---

### 1.2. Un utilisateur IAM avec clés d’accès

Nécessaire pour que MLflow puisse écrire dans S3. (utiliser le même pour l'ensemble du projet fraude)

1. Allez dans **IAM → Users → Create user**.
2. Activez **Programmatic access**.
3. Donnez-lui les permissions nécessaires (pour tester : `AmazonS3FullAccess`).
4. Récupérez :
   - `AWS_ACCESS_KEY_ID`
   - `AWS_SECRET_ACCESS_KEY`

---

### 1.3. Base de données Neon (BACKEND_STORE_URI)

1. Créez un projet sur : https://neon.tech (utiliser le même pour l'ensemble du projet fraude)
2. Récupérez l’URL PostgreSQL du type : `postgresql://<user>:<password>@<host>/<database>?sslmode=require`

3. Exemple : `postgresql://neondb_owner:MON_MDP@ep-xxxx-pooler.c-2.eu-central-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require`

Cette URL devient votre `BACKEND_STORE_URI`.

---
### 1.4. Hugging Face
Créez un compte sous hugging face : https://huggingface.co/ si vous n'en avez pas déjà un.


## 2. Construire l'app depuis Hugging Face Spaces

### 2.1. Création du nouveau Space

1. Depuis Hugging Face Spaces : https://huggingface.co/spaces, créez un **+ New Space** avec les informations suivantes : 
    - Space name : choisissez un nom
    - Select the Space SDK : `Docker`
    - Choose a Docker template : `Blank`
    - Space hardware : `CPU Basic`
    - `Public`
  Cliquez sur `Create Space`.

2. Dans l'onglet `Files` de votre space nouvellement créé, importez les fichiers suivants (remplacez si déjà existants) :
    - mlflow/Dockerfile
    - mlflow/app.py
    - mlflow/requirements.txt

### 2.2. Configuration des variables d'environnement
Les variables d'environnement suivantes doivent être définies dans les **Repository secrets** du Space (menu `Settings`):

#### 2.2.1. Base de données (obligatoire)
- `BACKEND_STORE_URI` : URL de connexion PostgreSQL
  - Format : `postgresql://username:password@host:port/database?sslmode=require`
  - Exemple : `postgresql://mlflow_user:mypassword@db.example.com:5432/mlflow_db?sslmode=require`

#### 2.2.2. Stockage des artifacts S3 (obligatoire)
- `ARTIFACT_ROOT` : Chemin S3 pour stocker les artifacts
  - Format : `s3://nom-du-bucket/chemin/vers/artifacts`
  - Exemple : `s3://my-mlflow-bucket/mlflow-artifacts`

- `AWS_ACCESS_KEY_ID` : Clé d'accès AWS
- `AWS_SECRET_ACCESS_KEY` : Clé secrète AWS
- `AWS_DEFAULT_REGION` : Région AWS du bucket S3
  - Exemple : `eu-west-1`, `us-east-1`, etc.

#### 2.2.3. Authentification MLflow (optionnel)
- `MLFLOW_TRACKING_USERNAME` : Nom d'utilisateur pour l'accès à MLflow
- `MLFLOW_TRACKING_PASSWORD` : Mot de passe pour l'accès à MLflow

### 2.3. Construiction de l'application
Allez sur l'onglet `App` de votre space, il doit se contruire automatiquement.
Une fois la construction démarrée, vous voyez le serveur mlflow en arrière plan. 
Fermez la fenêtre des logs, et en haut de l'écran entre le menu "Settings" et l'image de votre user, cliquez sur les trois petits points verticaux, puis sur `Embed this space` pour récupérer la valeur du `src` qui sera à renseigner dans la variable d'environnement MLFLOW_TRACKING_URI (cf point 4. ci-dessous)

---

## 3. Architecture

- **Backend store** : PostgreSQL (métadonnées des runs, paramètres, métriques)
- **Artifact store** : AWS S3 (modèles, fichiers, plots)
- **Interface** : MLflow UI accessible via l'URL du Space

## 4. Utilisation
Ajouter les variables d'environnement suivantes dans votre .env : 

```
MLFLOW_TRACKING_URI=https://VOTRE_USERNAME-VOTRE_SPACE_NAME.hf.space

# Si authentification activée :
# MLFLOW_TRACKING_USERNAME = votre_username
# MLFLOW_TRACKING_PASSWORD = votre_password
```

Vous êtes prêt à lancer vos expériences MLflow 🎉

---