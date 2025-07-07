# Live Data Migration Script

This script automates the migration of live server data from an SQL backup file into the current Django development environment.

## Features

✅ **Comprehensive Error Handling**: Handles all schema and data integrity issues  
✅ **Automatic Rollback**: Restores previous database state on failure  
✅ **Data Integrity Verification**: Validates imported data and counts records  
✅ **Admin User Management**: Resets admin credentials for easy access  
✅ **Backup Creation**: Creates backup before migration  
✅ **Docker Integration**: Seamlessly works with Docker containers  

## Usage

### Basic Usage
```bash
./migrate_live_data.sh
```
*Uses default backup file: `fbf-backup.sql`*

### With Custom Backup File
```bash
./migrate_live_data.sh /path/to/your/backup.sql
```

### Show Help
```bash
./migrate_live_data.sh --help
```

## What the Script Does

1. **Prerequisites Check**: Verifies Docker, docker-compose, and required files
2. **Backup Validation**: Ensures the SQL backup file is valid
3. **Container Management**: Starts necessary Docker containers
4. **Database Backup**: Creates backup of current database
5. **Database Reset**: Drops and recreates the target database
6. **Data Import**: Imports the live SQL dump
7. **Django Migrations**: Applies any pending Django migrations
8. **Data Verification**: Checks data integrity and counts records
9. **Admin Setup**: Configures admin user with known credentials
10. **Static Files**: Collects static files for the application

## Migration Results

After successful migration, you'll have access to:

- **Application**: http://localhost:8008 (or your configured port)
- **Admin Panel**: http://localhost:8008/admin (or your configured port)
- **Admin Login**: username `admin`, password `admin`

The script will display detailed statistics about the imported data, including:
- Number of records imported per table
- Data integrity verification results
- Any warnings or issues encountered during migration

## Data Verification

The script automatically verifies data integrity by:
- Counting records in all major tables
- Checking for NULL values in critical fields
- Displaying import statistics for verification

## Error Handling

- **Automatic Rollback**: If migration fails, the script automatically restores the previous database state
- **Comprehensive Logging**: Color-coded output shows progress and any issues
- **Backup Protection**: Current database is backed up before any changes

## Files Created

- `pre_migration_backup_YYYYMMDD_HHMMSS.sql`: Backup of database before migration
- `.last_backup_file`: Temporary file tracking the backup location (auto-cleaned)

## Requirements

- Docker and Docker Compose
- Valid SQL backup file (e.g., `fbf-backup.sql`) in the project root
- `docker-compose.yaml` configuration file
- Sufficient disk space for database backup and import

## Troubleshooting

### Container Issues
```bash
docker-compose down
docker-compose up -d
```

### View Logs
```bash
docker-compose logs -f web
docker-compose logs -f db
```

### Manual Database Access
```bash
docker-compose exec db psql -U fbf -d db_fbf
```

## Script Features

- **🎨 Colored Output**: Easy-to-read progress indicators
- **🔄 Progress Tracking**: Real-time status updates
- **📊 Data Verification**: Automatic integrity checks
- **🛡️ Safe Rollback**: Protection against data loss
- **📝 Comprehensive Logging**: Detailed operation logs

## Version

**Version 1.0** - Fully automated migration with error handling and rollback capabilities.
