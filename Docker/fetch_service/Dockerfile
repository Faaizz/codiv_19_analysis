# BUILD-USING docker build -f ./Dockerfile ../../ -t covid_fetch_service
# RUN-USING: docker run -d --rm -v volume-name:/app/data

# DEVELOPMENT
# FROM python:3.8.5-buster

FROM python:3.8.5-slim-buster

# Install OS dependencies
RUN apt-get update
RUN apt-get install -y cron git

# Install Python dependencies
COPY ./Docker/fetch_service/requirements.txt /app/
RUN pip3 install --no-cache-dir -r /app/requirements.txt

# Copy app files
COPY ./src/data/get_data.py /app/
COPY ./src/data/process_JH_data.py /app/
COPY ./src/features/build_features.py /app/

COPY ./Docker/fetch_service/update_pipeline.sh /app/
RUN chmod 755 /app/update_pipeline.sh

COPY ./Docker/fetch_service/update_cron /app/

# Data fetching and processing
RUN mkdir /app/data
RUN ["/bin/bash", "/app/update_pipeline.sh"]

# Launch command
ENTRYPOINT [ "/bin/bash", "-c", "cat /app/update_cron >> /etc/crontab && cron -f -L 1"]