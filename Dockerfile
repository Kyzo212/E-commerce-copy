# Use Ubuntu 24.04 as base (matches Lab 1)
FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

# Install system packages
RUN apt-get update && apt-get install -y \
    python3 python3-pip python3-venv \
    nginx git openssh-server \
    curl vim && rm -rf /var/lib/apt/lists/*

# Install Python packages needed by the e-commerce app
RUN pip3 install --break-system-packages \
    werkzeug jinja2 sqlalchemy gunicorn

# SSH access (root password: root123) — matches Lab 1
RUN mkdir /var/run/sshd && echo 'root:root123' | chpasswd

# Working directory — will be mounted from host app/ folder
WORKDIR /var/www/html

# Copy Nginx config
COPY nginx.conf /etc/nginx/sites-available/default

# Expose HTTP and SSH ports
EXPOSE 80 22

# Start SSH, Nginx, init DB, then Gunicorn
CMD service ssh start && \
    service nginx start && \
    python3 /var/www/html/init_db.py && \
    gunicorn --bind 0.0.0.0:5000 --chdir /var/www/html app:app
