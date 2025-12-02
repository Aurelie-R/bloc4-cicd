# avant de lancer la ligne ci dessous, il faut remettre les valeurs dans les variables d'environnement.

# lancement du serveur ML Flow
docker run -it -p 4000:4000 -v "$(pwd):/home/app" -e PORT=4000 -e AWS_ACCESS_KEY_ID=$env:AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY=$env:AWS_SECRET_ACCESS_KEY -e BACKEND_STORE_URI=$env:BACKEND_STORE_URI -e ARTIFACT_ROOT=$env:ARTIFACT_ROOT img_bloc03


# BLOC 03 #
# pour lancer l'application streamlit qui permet de visualiser le tableau de bord des transactions de la veille 
docker run -it -p 8501:8501 -e BACKEND_STORE_URI=$env:BACKEND_STORE_URI streamlit_app_03


# docker run -it -p 6000:6000 -v "$(pwd):/home/app" -e PORT=6000 -e AWS_ACCESS_KEY_ID=$env:AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY=$env:AWS_SECRET_ACCESS_KEY -e BACKEND_STORE_URI=$env:BACKEND_STORE_URI -e ARTIFACT_ROOT=$env:ARTIFACT_ROOT api_prediction