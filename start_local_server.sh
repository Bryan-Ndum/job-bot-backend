#!/bin/bash

echo "Starting Job Application Bot Server..."
echo ""
echo "The dashboard will be available at:"
echo "  http://localhost:8000/dashboard"
echo ""
echo "Press CTRL+C to stop the server"
echo ""

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000






