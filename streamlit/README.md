---
title: Dataviz Fraude
emoji: 🏆
colorFrom: purple
colorTo: gray
sdk: docker
pinned: false
short_description: Visualisations sur le jeu de données de fraude
---

# Streamlit application

Ce dépôt permet de lancer une application **Streamlit** dans un conteneur Docker, avec :

- **Neon PostgreSQL** comme _backend store_ (données de transactions)
- Une interface accessible sur : **https://VOTRE_USERNAME-VOTRE_SPACE_NAME.hf.space**

---

## 1. Prérequis

### 1.1. Base de données Neon (BACKEND_STORE_URI)

1. Créez un projet sur : https://neon.tech (utiliser le même pour l'ensemble du projet fraude)
2. Récupérez l’URL PostgreSQL du type : `postgresql://<user>:<password>@<host>/<database>?sslmode=require`

3. Exemple : `postgresql://neondb_owner:MON_MDP@ep-xxxx-pooler.c-2.eu-central-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require`

Cette URL devient votre `BACKEND_STORE_URI`.

---
### 1.2. Hugging Face
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
- `TABLE_NAME` : Nom de la table où sont stockées les transactions 
  - Par défaut dans ce projet : `fraud_transaction_predictions`

### 2.3. Construiction de l'application
Allez sur l'onglet `App` de votre space, il doit se contruire automatiquement.
Une fois la construction démarrée, vous voyez l'application streamlit en arrière plan.

---

## 3. Architecture

- **Backend store** : PostgreSQL (métadonnées des runs, paramètres, métriques)
- **Interface** : Streamlit UI accessible via l'URL du Space

## 4. Utilisation
L'application finalisée sur Hugging Face Spaces est utilisable de suite 🎉 (à condition d'avoir des données en base, of course...)


---