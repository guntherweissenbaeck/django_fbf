#!/bin/bash

# start_test.sh - Test Runner for Fallen Birdy Form
# Führt alle Tests aus und zeigt eine Zusammenfassung an

echo "🧪 ===== FALLEN BIRDY FORM - TEST SUITE ====="
echo "📅 Start: $(date '+%d.%m.%Y %H:%M:%S')"
echo ""

# Farben für die Ausgabe
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Test Counters
TOTAL_TESTS=0
TOTAL_FAILED=0
ALL_PASSED=true

echo -e "${BLUE}🔍 Überprüfung der Voraussetzungen...${NC}"

# Prüfen ob Docker Container läuft
if ! docker ps | grep -q "django_fbf_web_1"; then
    echo -e "${RED}❌ Django Container läuft nicht!${NC}"
    echo "   Bitte starten Sie das Projekt zuerst mit: ./start_project.sh"
    exit 1
fi

echo -e "${GREEN}✅ Container läuft${NC}"
echo ""

# 1. Django Tests
echo -e "${BLUE}1️⃣  Django Tests (im Docker Container)...${NC}"
echo "----------------------------------------"

DJANGO_RESULT=$(docker exec django_fbf_web_1 python manage.py test 2>&1)
DJANGO_EXIT=$?

if [ $DJANGO_EXIT -eq 0 ]; then
    DJANGO_COUNT=$(echo "$DJANGO_RESULT" | grep -o "Ran [0-9]\+ tests" | grep -o "[0-9]\+" || echo "0")
    echo -e "${GREEN}✅ Django Tests: $DJANGO_COUNT Tests bestanden${NC}"
    TOTAL_TESTS=$((TOTAL_TESTS + DJANGO_COUNT))
else
    echo -e "${RED}❌ Django Tests: Fehler aufgetreten${NC}"
    echo "$DJANGO_RESULT" | tail -5
    ALL_PASSED=false
    TOTAL_FAILED=$((TOTAL_FAILED + 1))
fi
echo ""

# 2. Pytest Tests (alle zusammen)
echo -e "${BLUE}2️⃣  Pytest Tests (Unit, Integration, Functional)...${NC}"
echo "------------------------------------------------"

if command -v python3 >/dev/null 2>&1 && python3 -c "import pytest" 2>/dev/null; then
    PYTEST_RESULT=$(python3 -m pytest test/ -v --tb=short 2>&1)
    PYTEST_EXIT=$?
    
    if [ $PYTEST_EXIT -eq 0 ]; then
        PYTEST_COUNT=$(echo "$PYTEST_RESULT" | grep -E "=+ [0-9]+ passed" | grep -o "[0-9]\+ passed" | grep -o "[0-9]\+" || echo "0")
        echo -e "${GREEN}✅ Pytest Tests: $PYTEST_COUNT Tests bestanden${NC}"
        TOTAL_TESTS=$((TOTAL_TESTS + PYTEST_COUNT))
    else
        PYTEST_FAILED=$(echo "$PYTEST_RESULT" | grep -E "=+ [0-9]+ failed" | grep -o "[0-9]\+ failed" | grep -o "[0-9]\+" || echo "0")
        echo -e "${RED}❌ Pytest Tests: $PYTEST_FAILED Tests fehlgeschlagen${NC}"
        echo "$PYTEST_RESULT" | tail -10
        ALL_PASSED=false
        TOTAL_FAILED=$((TOTAL_FAILED + PYTEST_FAILED))
    fi
else
    echo -e "${YELLOW}⚠️  Pytest nicht verfügbar - überspringe externe Tests${NC}"
fi
echo ""

# Zusammenfassung
echo "🎯 ===== TEST ZUSAMMENFASSUNG ====="
echo "📊 Gesamt Tests ausgeführt: $TOTAL_TESTS"

if [ "$ALL_PASSED" = true ] && [ $TOTAL_FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 ALLE TESTS BESTANDEN! 🎉${NC}"
    EXIT_CODE=0
else
    echo -e "${RED}❌ Es gab Fehler bei den Tests${NC}"
    echo "   Fehlgeschlagene Tests: $TOTAL_FAILED"
    EXIT_CODE=1
fi

echo ""
echo "⏱️  Beendet: $(date '+%d.%m.%Y %H:%M:%S')"
echo "=================================="

# Coverage Report (optional)
if [ "$ALL_PASSED" = true ] && command -v python3 >/dev/null 2>&1; then
    echo ""
    echo -e "${BLUE}📈 Generiere Test Coverage Report...${NC}"
    if python3 -m pytest test/ --cov=app --cov-report=html -q >/dev/null 2>&1; then
        echo -e "${GREEN}✅ Coverage Report: htmlcov/index.html${NC}"
    else
        echo -e "${YELLOW}⚠️  Coverage Report nicht verfügbar${NC}"
    fi
fi

exit $EXIT_CODE
