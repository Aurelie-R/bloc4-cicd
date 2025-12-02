FROM python:3.10

# Dossier de travail dans le conteneur
WORKDIR /home/app

# Copier le code de l'app
# COPY ./app/ /home/app

# Copier les requirements de l'app (prod)
COPY requirements.txt /home/app/requirements.txt

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Copier tout le code de l'app
COPY . .

# Pour logs flushés en temps réel
ENV PYTHONUNBUFFERED=1

# Pour que "import app" fonctionne si besoin
ENV PYTHONPATH=/home

# Commande par défaut : exécution une fois du pipeline
CMD ["python", "worker.py"]
