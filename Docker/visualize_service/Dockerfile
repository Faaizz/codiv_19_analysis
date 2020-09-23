# BUILD-USING docker build -f ./Docker/visualize_service/Dockerfile -t covid_visualize_service
# RUN-USING: docker run -d --restart unless-stopped -p 127.0.0.1:3456:8080 -v volume-name:/app/data covid_visualize_service

FROM python:3.8.5-slim-buster

# Install Python dependencies
COPY ./Docker/visualize_service/requirements.txt /app/
RUN pip3 install --no-cache-dir -r /app/requirements.txt

# Copy files
COPY ./src/visualization/visualize.py /app/
RUN chmod 755 /app/visualize.py

EXPOSE 8080

# Launch command
ENTRYPOINT ["python", "/app/visualize.py",  "--data_path",  "/app/data/"]