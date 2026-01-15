"""
File Archiver Module
Handles monthly archiving (zipping) of old files.
"""

import zipfile
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Optional
import logging
import shutil

logger = logging.getLogger(__name__)


class FileArchiver:
    """Handles archiving old files into zip archives."""
    
    def __init__(self, archive_format: str = 'zip'):
        """
        Initialize FileArchiver.
        
        Args:
            archive_format: Format for archives (currently only 'zip' supported)
        """
        self.archive_format = archive_format
    
    def archive_old_files(self, directory: Path, days_old: int = 30,
                         archive_folder: Optional[Path] = None,
                         delete_after_archive: bool = True,
                         dry_run: bool = False) -> Path:
        """
        Archive files older than specified days into a zip file.
        
        Args:
            directory: Directory containing files to archive
            days_old: Age threshold in days (files older than this will be archived)
            archive_folder: Folder to place archive (default: directory/Archives)
            delete_after_archive: Delete original files after archiving
            dry_run: If True, only show what would be archived
            
        Returns:
            Path to created archive file
        """
        cutoff_date = datetime.now() - timedelta(days=days_old)
        
        if archive_folder is None:
            archive_folder = directory / 'Archives'
        
        archive_folder.mkdir(parents=True, exist_ok=True)
        
        # Create archive filename with current month/year
        archive_name = f"archive_{datetime.now().strftime('%Y%m')}.zip"
        archive_path = archive_folder / archive_name
        
        # If archive already exists, append to it or create new with timestamp
        if archive_path.exists():
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            archive_name = f"archive_{datetime.now().strftime('%Y%m')}_{timestamp}.zip"
            archive_path = archive_folder / archive_name
        
        files_to_archive = []
        
        # Find old files
        for file_path in directory.iterdir():
            if file_path.is_file():
                mod_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                if mod_time < cutoff_date:
                    files_to_archive.append(file_path)
        
        if not files_to_archive:
            logger.info("No old files found to archive")
            return archive_path
        
        logger.info(f"Found {len(files_to_archive)} files to archive")
        
        if dry_run:
            logger.info(f"[DRY RUN] Would create archive: {archive_path}")
            for file_path in files_to_archive:
                logger.info(f"[DRY RUN] Would archive: {file_path.name}")
            return archive_path
        
        # Create zip archive
        try:
            with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file_path in files_to_archive:
                    zipf.write(file_path, file_path.name)
                    logger.info(f"Archived: {file_path.name}")
            
            logger.info(f"Created archive: {archive_path}")
            
            # Delete original files if requested
            if delete_after_archive:
                for file_path in files_to_archive:
                    try:
                        file_path.unlink()
                        logger.info(f"Deleted original: {file_path.name}")
                    except Exception as e:
                        logger.error(f"Error deleting {file_path.name}: {e}")
            
            return archive_path
            
        except Exception as e:
            logger.error(f"Error creating archive: {e}")
            raise
    
    def archive_by_category(self, directory: Path, days_old: int = 30,
                           delete_after_archive: bool = True,
                           dry_run: bool = False) -> List[Path]:
        """
        Archive old files, creating separate archives for each file category.
        
        Args:
            directory: Directory containing files
            days_old: Age threshold in days
            delete_after_archive: Delete original files after archiving
            dry_run: If True, only show what would be archived
            
        Returns:
            List of created archive paths
        """
        cutoff_date = datetime.now() - timedelta(days=days_old)
        archive_folder = directory / 'Archives'
        archive_folder.mkdir(parents=True, exist_ok=True)
        
        # Group files by extension
        files_by_type: dict = {}
        
        for file_path in directory.iterdir():
            if file_path.is_file():
                mod_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                if mod_time < cutoff_date:
                    ext = file_path.suffix.lower() or 'no_extension'
                    if ext not in files_by_type:
                        files_by_type[ext] = []
                    files_by_type[ext].append(file_path)
        
        created_archives = []
        
        for ext, files in files_by_type.items():
            if not files:
                continue
            
            # Create archive name based on file type
            ext_name = ext[1:] if ext.startswith('.') else ext
            archive_name = f"archive_{ext_name}_{datetime.now().strftime('%Y%m')}.zip"
            archive_path = archive_folder / archive_name
            
            if archive_path.exists():
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                archive_name = f"archive_{ext_name}_{datetime.now().strftime('%Y%m')}_{timestamp}.zip"
                archive_path = archive_folder / archive_name
            
            if dry_run:
                logger.info(f"[DRY RUN] Would create archive: {archive_path} with {len(files)} {ext} files")
                continue
            
            try:
                with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    for file_path in files:
                        zipf.write(file_path, file_path.name)
                        logger.info(f"Archived: {file_path.name}")
                
                logger.info(f"Created archive: {archive_path}")
                created_archives.append(archive_path)
                
                if delete_after_archive:
                    for file_path in files:
                        try:
                            file_path.unlink()
                        except Exception as e:
                            logger.error(f"Error deleting {file_path.name}: {e}")
                            
            except Exception as e:
                logger.error(f"Error creating archive for {ext}: {e}")
        
        return created_archives
