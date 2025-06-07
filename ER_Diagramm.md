# ER-Diagramm - Django FBF Datenbank

## Übersicht der Datenbankstruktur

```mermaid
erDiagram
    User ||--o{ FallenBird : creates
    User ||--o{ Costs : creates
    User ||--o{ Emailadress : creates
    
    Bird ||--o{ FallenBird : "is type of"
    Bird ||--o{ BirdEmail : "has emails for"
    
    Circumstance ||--o{ FallenBird : "describes finding"
    BirdStatus ||--o{ FallenBird : "has status"
    Aviary ||--o{ FallenBird : "houses"
    
    FallenBird ||--o{ Costs : "has costs"
    
    ContactTag ||--o{ Contact : "categorizes"
    
    Emailadress ||--o{ BirdEmail : "used for birds"
    
    User {
        int id PK
        string username
        string email
        string first_name
        string last_name
        datetime date_joined
        boolean is_active
        boolean is_staff
        boolean is_superuser
    }
    
    FallenBird {
        uuid id PK
        string bird_identifier
        uuid bird_id FK
        string age
        string sex
        date date_found
        string place
        datetime created
        datetime updated
        uuid find_circumstances_id FK
        string diagnostic_finding
        int user_id FK
        int status_id FK
        uuid aviary_id FK
        string sent_to
        text comment
        text finder
    }
    
    Bird {
        bigint id PK
        string name UK
        richtext description
    }
    
    BirdStatus {
        bigint id PK
        string description UK
    }
    
    Circumstance {
        bigint id PK
        string description
    }
    
    Aviary {
        uuid id PK
        string description UK
        string condition
        date last_ward_round
        string comment
    }
    
    Costs {
        uuid id PK
        uuid id_bird_id FK
        decimal costs
        date created
        string comment
        int user_id FK
    }
    
    Contact {
        uuid id PK
        string name
        string phone
        string email
        string address
        string comment
        uuid tag_id_id FK
    }
    
    ContactTag {
        uuid id PK
        string tag
    }
    
    Emailadress {
        int id PK
        string email_address
        datetime created_at
        datetime updated_at
        int user_id FK
    }
    
    BirdEmail {
        int id PK
        int bird_id FK
        int email_id FK
    }
```

## Tabellenbeschreibungen

### Kern-Entitäten

#### `FallenBird` (Patienten)
- **Zweck**: Zentrale Entität für gefundene/verletzte Vögel
- **Primärschlüssel**: UUID
- **Beziehungen**: 
  - Gehört zu einem `Bird` (Vogelart)
  - Hat einen `BirdStatus` (Status)
  - Wird von einem `User` erstellt
  - Kann in einer `Aviary` (Voliere) untergebracht sein
  - Hat `Circumstance` (Fundumstände)
  - Kann `Costs` (Kosten) haben

#### `Bird` (Vogelarten)
- **Zweck**: Katalog der verschiedenen Vogelarten
- **Primärschlüssel**: BigInt
- **Eindeutig**: Name
- **Beziehungen**: Hat viele `FallenBird` Instanzen

#### `Aviary` (Volieren)
- **Zweck**: Unterbringungsplätze für die Vögel
- **Primärschlüssel**: UUID
- **Status**: Offen, Geschlossen, Gesperrt
- **Beziehungen**: Kann mehrere `FallenBird` beherbergen

### Referenz-Tabellen

#### `BirdStatus` (Patientenstatus)
- **Zweck**: Status-Katalog (z.B. "In Behandlung", "Freigelassen", "Verstorben")
- **Primärschlüssel**: BigInt

#### `Circumstance` (Fundumstände)
- **Zweck**: Katalog der Fundumstände (z.B. "Verletzt gefunden", "Aus Nest gefallen")
- **Primärschlüssel**: BigInt

### Kosten-Management

#### `Costs` (Kosten)
- **Zweck**: Kostenerfassung pro Patient
- **Primärschlüssel**: UUID
- **Beziehungen**: Gehört zu einem `FallenBird` und wird von einem `User` erstellt

### Kontakt-Management

#### `Contact` (Kontakte)
- **Zweck**: Kontaktdaten (Finder, Tierärzte, etc.)
- **Primärschlüssel**: UUID
- **Beziehungen**: Kann mit `ContactTag` kategorisiert werden

#### `ContactTag` (Kontakt-Tags)
- **Zweck**: Kategorisierung von Kontakten
- **Primärschlüssel**: UUID

### E-Mail-System

#### `Emailadress` (E-Mail-Adressen)
- **Zweck**: Verwaltung von E-Mail-Adressen
- **Primärschlüssel**: BigInt
- **Beziehungen**: Gehört zu einem `User`

#### `BirdEmail` (Vogel-E-Mail-Verknüpfung)
- **Zweck**: Many-to-Many Beziehung zwischen Vögeln und E-Mail-Adressen
- **Primärschlüssel**: BigInt

## Datenbank-Design-Prinzipien

### Primärschlüssel-Strategien
- **UUID**: Für Geschäftsobjekte (`FallenBird`, `Aviary`, `Contact`, `ContactTag`, `Costs`)
- **BigInt**: Für Referenzdaten (`Bird`, `BirdStatus`, `Circumstance`) und E-Mail-System

### Beziehungstypen
- **1:N**: Die meisten Beziehungen (User zu FallenBird, Bird zu FallenBird, etc.)
- **M:N**: `Bird` ↔ `Emailadress` über `BirdEmail`
- **Optional**: `FallenBird.aviary` (kann NULL sein)

### Besondere Eigenschaften
- **Soft References**: `Costs.id_bird` mit `SET_NULL` für Datenschutz
- **Audit Trail**: `created`/`updated` Felder in wichtigen Tabellen
- **Rich Text**: `Bird.description` für formatierte Beschreibungen
- **JSON/Array Fields**: Potentiell für Kosten-Historie (siehe `costs_default()` Funktion)

## Geschäftslogik-Unterstützung

Das Schema unterstützt folgende Geschäftsprozesse:

1. **Patientenaufnahme**: FallenBird → Bird, Circumstance, User
2. **Unterbringung**: FallenBird → Aviary
3. **Statusverfolgung**: FallenBird → BirdStatus
4. **Kostenverfolgung**: FallenBird → Costs
5. **Kontaktverwaltung**: Contact → ContactTag
6. **E-Mail-Benachrichtigungen**: Bird → BirdEmail → Emailadress
