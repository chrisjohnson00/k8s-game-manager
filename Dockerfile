FROM node:20.0.0-slim as npmbuild
WORKDIR /usr/src/app
RUN npm install vanilla-jsoneditor

FROM python:3.11.2-slim as appbuild

WORKDIR /usr/src/app
EXPOSE 5000

COPY requirements.txt ./
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY --from=npmbuild /usr/src/app/node_modules ./game_manager/static

COPY . .

ARG VERSION=unset
ENV VERSION=$VERSION

CMD gunicorn --log-file=- --workers=2 --threads=4 --worker-class=gthread --worker-tmp-dir /dev/shm --bind 0.0.0.0:5000 "game_manager:create_app()"
