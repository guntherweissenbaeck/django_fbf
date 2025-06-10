from django.core.management.base import BaseCommand
from sendemail.models import Emailadress
from bird.models import Bird, FallenBird


class Command(BaseCommand):
    help = 'Test the email notification system configuration'

    def handle(self, *args, **options):
        self.stdout.write("=" * 60)
        self.stdout.write("DJANGO FBF - E-MAIL BENACHRICHTIGUNGSTEST")
        self.stdout.write("=" * 60)
        self.stdout.write("")
        
        # 1. Check existing email addresses
        self.stdout.write("1. VORHANDENE E-MAIL-ADRESSEN:")
        self.stdout.write("-" * 40)
        email_addresses = Emailadress.objects.all()
        
        if not email_addresses.exists():
            self.stdout.write("❌ KEINE E-Mail-Adressen im System gefunden!")
            self.stdout.write("   Sie müssen zuerst E-Mail-Adressen über das Admin-Interface anlegen.")
            self.stdout.write("")
        else:
            for email in email_addresses:
                self.stdout.write(f"📧 {email.email_address}")
                self.stdout.write(f"   👤 Benutzer: {email.user.username}")
                self.stdout.write(f"   🏛️  Naturschutzbehörde: {'✅' if email.is_naturschutzbehoerde else '❌'}")
                self.stdout.write(f"   🏹 Jagdbehörde: {'✅' if email.is_jagdbehoerde else '❌'}")
                self.stdout.write(f"   🦅 Wildvogelhilfe-Team: {'✅' if email.is_wildvogelhilfe_team else '❌'}")
                self.stdout.write("")
        
        # 2. Check bird species notification settings
        self.stdout.write("2. VOGELARTEN UND BENACHRICHTIGUNGSEINSTELLUNGEN:")
        self.stdout.write("-" * 40)
        birds = Bird.objects.all()
        
        if not birds.exists():
            self.stdout.write("❌ KEINE Vogelarten im System gefunden!")
            self.stdout.write("   Sie müssen zuerst Vogelarten über das Admin-Interface anlegen.")
            self.stdout.write("")
        else:
            for bird in birds:
                self.stdout.write(f"🐦 {bird.name}")
                self.stdout.write(f"   🏛️  Naturschutzbehörde: {'✅' if bird.melden_an_naturschutzbehoerde else '❌'}")
                self.stdout.write(f"   🏹 Jagdbehörde: {'✅' if bird.melden_an_jagdbehoerde else '❌'}")
                self.stdout.write(f"   🦅 Wildvogelhilfe-Team: {'✅' if bird.melden_an_wildvogelhilfe_team else '❌'}")
                self.stdout.write("")
        
        # 3. Simulate email notification for each bird species
        self.stdout.write("3. SIMULATION: WER WÜRDE BENACHRICHTIGT WERDEN?")
        self.stdout.write("-" * 40)
        
        if birds.exists() and email_addresses.exists():
            for bird in birds:
                self.stdout.write(f"🐦 Wenn ein {bird.name} gefunden wird:")
                
                recipients = []
                
                # Check Naturschutzbehörde
                if bird.melden_an_naturschutzbehoerde:
                    naturschutz_emails = Emailadress.objects.filter(is_naturschutzbehoerde=True)
                    if naturschutz_emails.exists():
                        recipients.extend([f"🏛️  {e.email_address}" for e in naturschutz_emails])
                    else:
                        self.stdout.write("   ⚠️  Naturschutzbehörde aktiviert, aber keine passenden E-Mail-Adressen gefunden!")
                
                # Check Jagdbehörde
                if bird.melden_an_jagdbehoerde:
                    jagd_emails = Emailadress.objects.filter(is_jagdbehoerde=True)
                    if jagd_emails.exists():
                        recipients.extend([f"🏹 {e.email_address}" for e in jagd_emails])
                    else:
                        self.stdout.write("   ⚠️  Jagdbehörde aktiviert, aber keine passenden E-Mail-Adressen gefunden!")
                
                # Check Wildvogelhilfe-Team
                if bird.melden_an_wildvogelhilfe_team:
                    team_emails = Emailadress.objects.filter(is_wildvogelhilfe_team=True)
                    if team_emails.exists():
                        recipients.extend([f"🦅 {e.email_address}" for e in team_emails])
                    else:
                        self.stdout.write("   ⚠️  Wildvogelhilfe-Team aktiviert, aber keine passenden E-Mail-Adressen gefunden!")
                
                if recipients:
                    self.stdout.write("   📤 E-Mails würden gesendet an:")
                    for recipient in recipients:
                        self.stdout.write(f"      {recipient}")
                else:
                    self.stdout.write("   ❌ KEINE E-Mails würden gesendet!")
                self.stdout.write("")
        
        # 4. Provide setup instructions
        self.stdout.write("4. SETUP-ANWEISUNGEN:")
        self.stdout.write("-" * 40)
        self.stdout.write("Für die Einrichtung des E-Mail-Systems:")
        self.stdout.write("")
        self.stdout.write("A) E-Mail-Adressen hinzufügen:")
        self.stdout.write("   1. Gehen Sie zum Admin-Interface: http://localhost:8008/admin/")
        self.stdout.write("   2. Melden Sie sich mit admin/abcdef an")
        self.stdout.write("   3. Wählen Sie 'Mail Empfänger' > 'Emailadressen' > 'Hinzufügen'")
        self.stdout.write("   4. Geben Sie die E-Mail-Adresse ein")
        self.stdout.write("   5. Wählen Sie die entsprechenden Kategorien:")
        self.stdout.write("      - Naturschutzbehörde: für offizielle Meldungen")
        self.stdout.write("      - Jagdbehörde: für jagdbare Arten")
        self.stdout.write("      - Wildvogelhilfe-Team: für interne Benachrichtigungen")
        self.stdout.write("")
        self.stdout.write("B) Vogelarten-Benachrichtigungen konfigurieren:")
        self.stdout.write("   1. Gehen Sie zu 'Vögel' > 'Birds' > [Vogelart auswählen]")
        self.stdout.write("   2. Aktivieren Sie die gewünschten Benachrichtigungen:")
        self.stdout.write("      - 'Melden an Naturschutzbehörde'")
        self.stdout.write("      - 'Melden an Jagdbehörde'") 
        self.stdout.write("      - 'Melden an Wildvogelhilfe-Team'")
        self.stdout.write("")
        self.stdout.write("C) Testen:")
        self.stdout.write("   1. Erstellen Sie einen neuen Patienten über 'http://localhost:8008/'")
        self.stdout.write("   2. Wählen Sie eine Vogelart aus")
        self.stdout.write("   3. Das System sendet automatisch E-Mails basierend auf den Einstellungen")
        self.stdout.write("")
        
        # 5. Summary
        self.stdout.write("5. ZUSAMMENFASSUNG:")
        self.stdout.write("-" * 40)
        self.stdout.write(f"📧 E-Mail-Adressen im System: {email_addresses.count()}")
        self.stdout.write(f"🐦 Vogelarten im System: {birds.count()}")
        
        if email_addresses.exists() and birds.exists():
            self.stdout.write("✅ System ist grundsätzlich funktionsfähig")
        else:
            self.stdout.write("❌ System benötigt weitere Konfiguration")
        
        self.stdout.write("")
        self.stdout.write("=" * 60)
        self.stdout.write("Test abgeschlossen! Öffnen Sie http://localhost:8008/admin/ für weitere Konfiguration.")
        self.stdout.write("=" * 60)
