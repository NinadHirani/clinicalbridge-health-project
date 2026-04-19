FROM python:3.11-slim

WORKDIR /app

# Copy all files first
COPY pyproject.toml .
COPY src/ src/

# Install dependencies (after source is copied)
RUN pip install --no-cache-dir -e .

# Expose port
EXPOSE 8080

# Set environment variables
ENV PORT=8080
ENV PYTHONUNBUFFERED=1

# Run the server using the entrypoint script
CMD ["clinicalbridge"]
