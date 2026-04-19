FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY pyproject.toml .
RUN pip install --no-cache-dir -e .

# Copy application code
COPY src/ src/
COPY data/ data/

# Expose port
EXPOSE 8080

# Set environment variables
ENV PORT=8080
ENV PYTHONUNBUFFERED=1

# Run the server
CMD ["python", "-m", "clinicalbridge.server"]
