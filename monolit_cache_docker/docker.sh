docker build -t app0 .
docker run -dp 8000:8000 --network=host app0
