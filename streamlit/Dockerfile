FROM python:3.10-slim

WORKDIR /home/app

# Installation des dépendances système
RUN apt-get update \
    && apt-get install -y --no-install-recommends nano unzip curl \
    && rm -rf /var/lib/apt/lists/*

# Copie des fichiers de l'application
COPY requirements.txt /dependencies/requirements.txt
RUN pip install --no-cache-dir -r /dependencies/requirements.txt

# Copie du reste des fichiers
COPY . .

# Configuration de Streamlit pour Hugging Face Spaces
RUN mkdir -p ~/.streamlit \
    && echo "[server]\nheadless = true\nport = 7860\nenableCORS = false\nenableXsrfProtection = false\n" > ~/.streamlit/config.toml

# Exposition du port
EXPOSE 7860

# Variables d'environnement
ENV BACKEND_STORE_URI=${BACKEND_STORE_URI}

# Commande de démarrage
CMD streamlit run app.py --server.port=7860 --server.address=0.0.0.0