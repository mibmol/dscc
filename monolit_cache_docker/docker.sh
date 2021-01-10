docker build -t app0 .
docker build -t app1 .
docker build -t app2 .
docker run -dp 8000:8000 --network=host app0
docker run -dp 8001:8001 --network=host app1 
docker run -dp 8001:8001 --network=host app3 
