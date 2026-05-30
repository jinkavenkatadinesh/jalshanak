#!/bin/bash
# =========================================================================
# JALRAKSHAK AUTOMATED DATABASE BACKUP ROUTINE
# =========================================================================

# Exit immediately if a command exits with a non-zero status
set -e

# Configuration
BACKUP_DIR="/backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="${BACKUP_DIR}/jalrakshak_db_${TIMESTAMP}.sql"
RETENTION_DAYS=30

echo "[$(date)] Initializing database backup..."

# Ensure backup directory exists
mkdir -p "${BACKUP_DIR}"

# Run pg_dump to export database structures & seed contents
# Database host 'db' matches the service name in docker-compose.prod.yml
PGPASSWORD="${POSTGRES_PASSWORD:-SecureProductionPass123}" pg_dump -h db -U postgres -d jalrakshak_db -F p -f "${BACKUP_FILE}"

echo "[$(date)] Backup successfully compiled: ${BACKUP_FILE}"

# Compress the backup file to conserve storage
gzip "${BACKUP_FILE}"
echo "[$(date)] Backup file compressed successfully: ${BACKUP_FILE}.gz"

# Clean up older backups exceeding the retention threshold
echo "[$(date)] Auditing files older than ${RETENTION_DAYS} days..."
find "${BACKUP_DIR}" -name "jalrakshak_db_*.sql.gz" -mtime +${RETENTION_DAYS} -delete

echo "[$(date)] Database backup routine completed."
