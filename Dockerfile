FROM python:3.11-slim

# Install cron and other dependencies
RUN apt-get update && \
    apt-get install -y cron && \
    rm -rf /var/lib/apt/lists/*

# Create working directories
WORKDIR /app
RUN mkdir /app/logs

# Copy source code
COPY . /app

# Create virtual environment and install dependencies
RUN python -m venv TREC-logsheets-venv && \
    . TREC-logsheets-venv/bin/activate && \
    pip install --upgrade pip && \
    if [ -f requirements.txt ]; then pip install -r requirements.txt; fi

# Add cron job to run script every minute and log output
RUN echo "* * * * * cd /app/ && . /app/TREC-logsheets-venv/bin/activate && python /app/process_new_submissions.py > /app/logs/stdout.log 2>&1" > /etc/cron.d/mycron && \
    chmod 0644 /etc/cron.d/mycron && \
    crontab /etc/cron.d/mycron

# Make log folder available outside container
VOLUME ["/app/logs"]

# Start cron in foreground
CMD ["cron", "-f"]
