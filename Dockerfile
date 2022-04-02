FROM python:3.9-alpine

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "/bin/sh", "/usr/src/app/run.sh" ]