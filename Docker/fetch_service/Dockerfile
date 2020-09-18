# BUILD-USING docker build -f ./Dockerfile ../../ -t covid_fetch_service
# RUN-USING: docker run -d -v --rm volume-name:/app/data

# DEVELOPMENT
# FROM python:3.8.5-buster
PRODUCTION
# FROM python:3.8.5-slim-buster

RUN apt-get update
RUN apt-get install -y cron git

COPY ./Docker/fetch_service/requirements.txt /app/
RUN pip3 install -r /app/requirements.txt

COPY ./src/data/get_data.py /app/
COPY ./src/data/process_JH_data.py /app/
COPY ./src/features/build_features.py /app/

COPY ./Docker/fetch_service/update_pipeline.sh /app/
RUN chmod 755 /app/update_pipeline.sh

# DEVELOPMENT
COPY ./Docker/fetch_service/update_cron /app/

ENTRYPOINT [ "/bin/bash", "-c", "cat /app/update_cron >> /etc/crontab && cron -f -L 1"]