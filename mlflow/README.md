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

### 3.1. macOS / Linux – via un fichier secrets.sh

Créer un fichier :

```bash
export AWS_ACCESS_KEY_ID="VOTRE_ACCESS_KEY_ID"
export AWS_SECRET_ACCESS_KEY="VOTRE_SECRET_ACCESS_KEY"

export BACKEND_STORE_URI="postgresql://neondb_owner:VOTRE_MDP@ep-xxxx-pooler.c-2.eu-central-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

export ARTIFACT_ROOT="s3://mlflow-cicd/mlflow-artifacts/"
```

Charger les variables :

```bash
source secrets.sh
```

---

### 3.2. Windows (PowerShell)

```powershell
$env:AWS_ACCESS_KEY_ID     = "VOTRE_ACCESS_KEY_ID"
$env:AWS_SECRET_ACCESS_KEY = "VOTRE_SECRET_ACCESS_KEY"
$env:BACKEND_STORE_URI     = "postgresql://neondb_owner:VOTRE_MDP@ep-xxxx-pooler.c-2.eu-central-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
$env:ARTIFACT_ROOT         = "s3://mlflow-cicd/mlflow-artifacts/"
```

---

## 4. Lancer le serveur MLflow

### 4.1. macOS / Linux

```bash
docker run -it -p 4000:4000 -v "$(pwd):/home/app" -e PORT=4000 -e AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY -e BACKEND_STORE_URI=$BACKEND_STORE_URI -e ARTIFACT_ROOT=$ARTIFACT_ROOT mlflow-cicd
```

### 4.2. Windows (PowerShell)

```bash
docker run -it -p 4000:4000 -v "$(pwd):/home/app" -e PORT=4000 -e AWS_ACCESS_KEY_ID=$env:AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY=$env:AWS_SECRET_ACCESS_KEY -e BACKEND_STORE_URI=$env:BACKEND_STORE_URI -e ARTIFACT_ROOT=$env:ARTIFACT_ROOT mlflow-cicd
```

---

## 5. Accès à l’interface MLflow

Ouvrez votre navigateur :

```arduino
http://localhost:4000
```

Vous êtes prêt à lancer vos expériences MLflow 🎉

---
