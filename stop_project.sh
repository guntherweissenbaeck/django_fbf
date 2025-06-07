#!/bin/bash

# Django FBF Projekt Stopp Script

echo "🛑 Stoppe Django FBF Projekt..."

# Docker Container stoppen
docker compose down

echo "✅ Projekt gestoppt"
echo ""
echo "📝 Zum erneuten Starten verwenden Sie:"
echo "   ./start_project.sh"
