FROM alpine:latest
RUN apk add --no-cache wget
RUN apk add --no-cache npm
RUN apk add --no-cache python3 py3-pip

WORKDIR /
ADD . /
RUN pip install --no-cache-dir -r /server/requirements.txt

WORKDIR /client
RUN npm install

WORKDIR /
EXPOSE 5173
EXPOSE 5000
CMD flask --app ./server/app.py:create_app run --host 0.0.0.0 | npm --prefix ./client/ run serve 