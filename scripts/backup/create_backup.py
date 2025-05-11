import subprocess
import os
import datetime
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_backup():
    """Create a backup of the database before running migrations"""
    try:
        # Get database connection details from environment
        db_url = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/test_db")
        db_name = db_url.split("/")[-1]
        
        # Create backup directory if it doesn't exist
        backup_dir = Path("backups")
        backup_dir.mkdir(exist_ok=True)
        
        # Generate backup filename with timestamp
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = backup_dir / f"{db_name}_{timestamp}.sql"
        
        # Run pg_dump to create backup
        cmd = [
            "pg_dump",
            "-h", "localhost",
            "-U", "postgres",
            "-F", "c",  # Custom format
            "-b",  # Include large objects
            "-v",  # Verbose
            "-f", str(backup_file),
            db_name
        ]
        
        logger.info(f"Creating backup: {backup_file}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info("Backup created successfully")
            
            # Verify backup integrity
            verify_cmd = ["pg_restore", "--list", str(backup_file)]
            verify_result = subprocess.run(verify_cmd, capture_output=True, text=True)
            
            if verify_result.returncode == 0:
                logger.info("Backup verified successfully")
                return str(backup_file)
            else:
                logger.error("Backup verification failed")
                raise Exception(f"Backup verification failed: {verify_result.stderr}")
        else:
            logger.error("Backup creation failed")
            raise Exception(f"Backup creation failed: {result.stderr}")
            
    except Exception as e:
        logger.error(f"Error during backup: {str(e)}")
        raise

if __name__ == "__main__":
    try:
        backup_path = create_backup()
        print(f"Backup created successfully at: {backup_path}")
    except Exception as e:
        print(f"Backup failed: {str(e)}")
        exit(1) 