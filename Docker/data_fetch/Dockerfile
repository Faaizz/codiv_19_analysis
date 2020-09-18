# RUN-USING: docker run -v volume-name:/app/data

FROM ubuntu

COPY ./Docker/data_fetch/update_cron /etc/cron.daily/

RUN apt-get update
RUN apt-get upgrade
RUN apt-get install -y python3 cron python3-pip git

COPY ./Docker/data_fetch/requirements.txt /app/
RUN pip3 install -r /app/requirements.txt

COPY ./src/data/get_data.py /app/
COPY ./src/data/process_JH_data.py /app/
COPY ./src/features/build_features.py /app/

COPY ./Docker/data_fetch/update_data.sh /app/
RUN chmod 755 /app/update_data.sh

RUN cron -f &