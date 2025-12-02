docker build -f app/Dockerfile -t fraud-etl-app .
docker run --env-file .env fraud-etl-app