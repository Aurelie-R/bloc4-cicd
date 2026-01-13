# monitoring/Dockerfile

# ============================================================================
# Stage 1: Builder - Installation des dépendances
# ============================================================================
FROM python:3.10-slim as builder

# Définir le répertoire de travail
WORKDIR /build

# Installer les dépendances système nécessaires pour compiler certains packages Python
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copier uniquement requirements.txt d'abord (pour optimiser le cache Docker)
COPY requirements.txt .

# Installer les dépendances Python dans un environnement virtuel
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Installer les packages Python
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt


# ============================================================================
# Stage 2: Runtime - Image finale légère
# ============================================================================
FROM python:3.10-slim

# Métadonnées
LABEL maintainer="monmail@example.com"
LABEL description="Service de monitoring Evidently pour détection de fraude"
LABEL version="1.0"

# Créer un utilisateur non-root pour la sécurité
RUN groupadd -r monitoring && useradd -r -g monitoring monitoring

# Définir le répertoire de travail
WORKDIR /app

# Installer uniquement les dépendances système runtime minimales
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    tzdata \
    && rm -rf /var/lib/apt/lists/*

# Copier l'environnement virtuel depuis le builder
COPY --from=builder /opt/venv /opt/venv

# Activer l'environnement virtuel
ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Créer la structure de dossiers nécessaire
RUN mkdir -p /app/reports \
    /app/reference_data \
    /app/logs \
    /data \
    && chown -R monitoring:monitoring /app /data

# Copier le code de l'application
COPY --chown=monitoring:monitoring . .

# Définir les variables d'environnement par défaut
ENV MONITORING_INTERVAL=daily \
    ALERT_THRESHOLD_DRIFT=0.3 \
    ALERT_THRESHOLD_F1=0.7 \
    ALERT_THRESHOLD_RECALL=0.75 \
    TZ=Europe/Paris \
    LOG_LEVEL=INFO

# Créer un script d'initialisation
RUN echo '#!/bin/bash\n\
set -e\n\
\n\
echo "🚀 Initialisation du service de monitoring Evidently..."\n\
\n\
# Vérifier que les dossiers existent\n\
if [ ! -d "/app/reports" ]; then\n\
    echo "❌ Erreur: /app/reports n'\''existe pas"\n\
    exit 1\n\
fi\n\
\n\
if [ ! -d "/app/reference_data" ]; then\n\
    echo "❌ Erreur: /app/reference_data n'\''existe pas"\n\
    exit 1\n\
fi\n\
\n\
# Vérifier que les données de référence existent\n\
if [ ! -f "/app/reference_data/baseline.parquet" ]; then\n\
    echo "⚠️  Attention: Données de référence manquantes (/app/reference_data/baseline.parquet)"\n\
    echo "   Vous devez d'\''abord entraîner un modèle et générer les données de référence"\n\
    echo "   Le service va démarrer mais les rapports ne pourront pas être générés"\n\
fi\n\
\n\
# Afficher la configuration\n\
echo ""\n\
echo "📊 Configuration:"\n\
echo "   - Intervalle: $MONITORING_INTERVAL"\n\
echo "   - Seuil Drift: $ALERT_THRESHOLD_DRIFT"\n\
echo "   - Seuil F1: $ALERT_THRESHOLD_F1"\n\
echo "   - Seuil Recall: $ALERT_THRESHOLD_RECALL"\n\
echo "   - Timezone: $TZ"\n\
echo ""\n\
\n\
# Démarrer l'\''application\n\
echo "✅ Démarrage du service de monitoring..."\n\
exec python generate_reports.py\n\
' > /app/entrypoint.sh && chmod +x /app/entrypoint.sh

# Healthcheck - vérifie que le service fonctionne correctement
HEALTHCHECK --interval=1h \
    --timeout=30s \
    --start-period=10s \
    --retries=3 \
    CMD python -c "import os, sys; \
from pathlib import Path; \
from datetime import datetime, timedelta; \
reports_dir = Path('/app/reports'); \
if not reports_dir.exists(): sys.exit(1); \
reports = list(reports_dir.glob('report_*.html')); \
if not reports: print('⚠️  Aucun rapport généré'); sys.exit(0); \
latest = max(reports, key=lambda p: p.stat().st_mtime); \
age_hours = (datetime.now().timestamp() - latest.stat().st_mtime) / 3600; \
print(f'✅ Dernier rapport: {latest.name} ({age_hours:.1f}h)'); \
sys.exit(0 if age_hours < 25 else 1)"

# Changer vers l'utilisateur non-root
USER monitoring

# Exposer un port pour un éventuel serveur web de visualisation des rapports
# EXPOSE 8080

# Point d'entrée
ENTRYPOINT ["/app/entrypoint.sh"]

# Commande par défaut (peut être overridée)
# CMD ["python", "generate_reports.py"]