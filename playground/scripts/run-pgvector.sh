#!/bin/bash

# Stop and remove existing container if it exists
docker stop pgvector 2>/dev/null
docker rm pgvector 2>/dev/null

# Run pgvector container
docker run -d \
  -e POSTGRES_DB=ai \
  -e POSTGRES_USER=ai \
  -e POSTGRES_PASSWORD=ai \
  -e PGDATA=/var/lib/postgresql/data/pgdata \
  -v pgvolume:/var/lib/postgresql/data \
  -p 5532:5432 \
  --name pgvector \
  agnohq/pgvector:16

# Wait a few seconds for the container to start
sleep 5

# Check if container is running
if docker ps | grep -q pgvector; then
    echo "✅ pgvector container is running successfully"
    echo "Connection details:"
    echo "  Host: localhost"
    echo "  Port: 5532"
    echo "  Database: ai"
    echo "  Username: ai"
    echo "  Password: ai"
else
    echo "❌ Failed to start pgvector container"
    docker logs pgvector
fi
