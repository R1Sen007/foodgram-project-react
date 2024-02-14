GUNICORNVER=20.1.0
WSGIIP=0.0.0.0:8000
WSGINAME=backend.wsgi

install:
	pip install gunicorn==$(GUNICORNVER)

requirements:
	pip install -r requirements.txt --no-cache-dir

run:
	gunicorn --bind $(WSGIIP) $(WSGINAME)