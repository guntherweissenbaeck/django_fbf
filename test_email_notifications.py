#!/usr/bin/env python3
"""
Test script for Django FBF Email Notification System

This script helps you test which email addresses would receive notifications
when a new patient (fallen bird) is created in the system.
"""

import os
import sys
import django

# Add the Django project path
sys.path.append('/Users/maximilianfischer/git/django_fbf/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

# Setup Django
django.setup()

from sendemail.models import Emailadress
from bird.models import Bird, FallenBird
from django.contrib.auth.models import User

def test_email_notification_system():
    """Test the email notification system configuration."""
    
    print("=" * 60)
    print("DJANGO FBF - E-MAIL BENACHRICHTIGUNGSTEST")
    print("=" * 60)
    print()
    
    # 1. Check existing email addresses
    print("1. VORHANDENE E-MAIL-ADRESSEN:")
    print("-" * 40)
    email_addresses = Emailadress.objects.all()
    
    if not email_addresses.exists():
        print("❌ KEINE E-Mail-Adressen im System gefunden!")
        print("   Sie müssen zuerst E-Mail-Adressen über das Admin-Interface anlegen.")
        print()
    else:
        for email in email_addresses:
            print(f"📧 {email.email_address}")
            print(f"   👤 Benutzer: {email.user.username}")
            print(f"   🏛️  Naturschutzbehörde: {'✅' if email.is_naturschutzbehoerde else '❌'}")
            print(f"   🏹 Jagdbehörde: {'✅' if email.is_jagdbehoerde else '❌'}")
            print(f"   🦅 Wildvogelhilfe-Team: {'✅' if email.is_wildvogelhilfe_team else '❌'}")
            print()
    
    # 2. Check bird species notification settings
    print("2. VOGELARTEN UND BENACHRICHTIGUNGSEINSTELLUNGEN:")
    print("-" * 40)
    birds = Bird.objects.all()
    
    if not birds.exists():
        print("❌ KEINE Vogelarten im System gefunden!")
        print("   Sie müssen zuerst Vogelarten über das Admin-Interface anlegen.")
        print()
    else:
        for bird in birds:
            print(f"🐦 {bird.name}")
            print(f"   🏛️  Naturschutzbehörde: {'✅' if bird.melden_an_naturschutzbehoerde else '❌'}")
            print(f"   🏹 Jagdbehörde: {'✅' if bird.melden_an_jagdbehoerde else '❌'}")
            print(f"   🦅 Wildvogelhilfe-Team: {'✅' if bird.melden_an_wildvogelhilfe_team else '❌'}")
            print()
    
    # 3. Simulate email notification for each bird species
    print("3. SIMULATION: WER WÜRDE BENACHRICHTIGT WERDEN?")
    print("-" * 40)
    
    if birds.exists() and email_addresses.exists():
        for bird in birds:
            print(f"🐦 Wenn ein {bird.name} gefunden wird:")
            
            recipients = []
            
            # Check Naturschutzbehörde
            if bird.melden_an_naturschutzbehoerde:
                naturschutz_emails = Emailadress.objects.filter(is_naturschutzbehoerde=True)
                if naturschutz_emails.exists():
                    recipients.extend([f"🏛️  {e.email_address}" for e in naturschutz_emails])
                else:
                    print("   ⚠️  Naturschutzbehörde aktiviert, aber keine passenden E-Mail-Adressen gefunden!")
            
            # Check Jagdbehörde
            if bird.melden_an_jagdbehoerde:
                jagd_emails = Emailadress.objects.filter(is_jagdbehoerde=True)
                if jagd_emails.exists():
                    recipients.extend([f"🏹 {e.email_address}" for e in jagd_emails])
                else:
                    print("   ⚠️  Jagdbehörde aktiviert, aber keine passenden E-Mail-Adressen gefunden!")
            
            # Check Wildvogelhilfe-Team
            if bird.melden_an_wildvogelhilfe_team:
                team_emails = Emailadress.objects.filter(is_wildvogelhilfe_team=True)
                if team_emails.exists():
                    recipients.extend([f"🦅 {e.email_address}" for e in team_emails])
                else:
                    print("   ⚠️  Wildvogelhilfe-Team aktiviert, aber keine passenden E-Mail-Adressen gefunden!")
            
            if recipients:
                print("   📤 E-Mails würden gesendet an:")
                for recipient in recipients:
                    print(f"      {recipient}")
            else:
                print("   ❌ KEINE E-Mails würden gesendet!")
            print()
    
    # 4. Provide setup instructions
    print("4. SETUP-ANWEISUNGEN:")
    print("-" * 40)
    print("Für die Einrichtung des E-Mail-Systems:")
    print()
    print("A) E-Mail-Adressen hinzufügen:")
    print("   1. Gehen Sie zum Admin-Interface: http://localhost:8008/admin/")
    print("   2. Melden Sie sich mit admin/abcdef an")
    print("   3. Wählen Sie 'Mail Empfänger' > 'Emailadressen' > 'Hinzufügen'")
    print("   4. Geben Sie die E-Mail-Adresse ein")
    print("   5. Wählen Sie die entsprechenden Kategorien:")
    print("      - Naturschutzbehörde: für offizielle Meldungen")
    print("      - Jagdbehörde: für jagdbare Arten")
    print("      - Wildvogelhilfe-Team: für interne Benachrichtigungen")
    print()
    print("B) Vogelarten-Benachrichtigungen konfigurieren:")
    print("   1. Gehen Sie zu 'Vögel' > 'Birds' > [Vogelart auswählen]")
    print("   2. Aktivieren Sie die gewünschten Benachrichtigungen:")
    print("      - 'Melden an Naturschutzbehörde'")
    print("      - 'Melden an Jagdbehörde'") 
    print("      - 'Melden an Wildvogelhilfe-Team'")
    print()
    print("C) Testen:")
    print("   1. Erstellen Sie einen neuen Patienten über 'http://localhost:8008/'")
    print("   2. Wählen Sie eine Vogelart aus")
    print("   3. Das System sendet automatisch E-Mails basierend auf den Einstellungen")
    print()
    
    # 5. Summary
    print("5. ZUSAMMENFASSUNG:")
    print("-" * 40)
    print(f"📧 E-Mail-Adressen im System: {email_addresses.count()}")
    print(f"🐦 Vogelarten im System: {birds.count()}")
    
    if email_addresses.exists() and birds.exists():
        print("✅ System ist grundsätzlich funktionsfähig")
    else:
        print("❌ System benötigt weitere Konfiguration")
    
    print()
    print("=" * 60)
    print("Test abgeschlossen! Öffnen Sie http://localhost:8008/admin/ für weitere Konfiguration.")
    print("=" * 60)

if __name__ == "__main__":
    test_email_notification_system()
