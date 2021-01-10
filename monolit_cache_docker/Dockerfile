FROM python:3

WORKDIR /home/mglps/Documents/DSCC/pro/dscc/monolit_cache_docker

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "gunicorn",  "config.wsgi", " -b 0.0.0.0:8000" ]
# CMD [ "python",  "./manage.py", "runserver" ]
