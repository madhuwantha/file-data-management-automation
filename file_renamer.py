"""
File Renamer Module
Handles renaming files with date prefixes and bulk renaming from Excel.
"""

import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
import logging
import pandas as pd

logger = logging.getLogger(__name__)


class FileRenamer:
    """Handles file renaming operations."""
    
    def __init__(self, date_format: str = "%Y%m%d"):
        """
        Initialize FileRenamer.
        
        Args:
            date_format: Format string for date prefix (default: YYYYMMDD)
        """
        self.date_format = date_format
    
    def add_date_prefix(self, file_path: Path, use_modification_date: bool = True, 
                       custom_date: Optional[datetime] = None, dry_run: bool = False) -> Optional[Path]:
        """
        Add date prefix to a file name.
        
        Args:
            file_path: Path to the file
            use_modification_date: Use file's modification date if True
            custom_date: Custom date to use instead of modification date
            dry_run: If True, only return what the new name would be
            
        Returns:
            New file path if renamed, None if dry_run
        """
        if not file_path.exists():
            logger.warning(f"File does not exist: {file_path}")
            return None
        
        # Determine date to use
        if custom_date:
            date_str = custom_date.strftime(self.date_format)
        elif use_modification_date:
            mod_time = datetime.fromtimestamp(file_path.stat().st_mtime)
            date_str = mod_time.strftime(self.date_format)
        else:
            date_str = datetime.now().strftime(self.date_format)
        
        # Create new name with date prefix
        new_name = f"{date_str}_{file_path.name}"
        new_path = file_path.parent / new_name
        
        # Handle name conflicts
        if new_path.exists() and new_path != file_path:
            counter = 1
            stem = f"{date_str}_{file_path.stem}"
            while new_path.exists():
                new_path = file_path.parent / f"{stem}_{counter}{file_path.suffix}"
                counter += 1
        
        if dry_run:
            logger.info(f"[DRY RUN] Would rename: {file_path.name} -> {new_path.name}")
            return new_path
        
        try:
            file_path.rename(new_path)
            logger.info(f"Renamed: {file_path.name} -> {new_path.name}")
            return new_path
        except Exception as e:
            logger.error(f"Error renaming {file_path.name}: {e}")
            return None
    
    def batch_add_date_prefix(self, directory: Path, recursive: bool = False, 
                             dry_run: bool = False) -> List[Path]:
        """
        Add date prefix to all files in a directory.
        
        Args:
            directory: Directory containing files to rename
            recursive: Process subdirectories recursively
            dry_run: If True, only show what would be done
            
        Returns:
            List of renamed file paths
        """
        renamed_files = []
        
        if recursive:
            files = list(directory.rglob('*'))
        else:
            files = list(directory.glob('*'))
        
        files = [f for f in files if f.is_file()]
        
        for file_path in files:
            # Skip if already has date prefix (simple check)
            if file_path.name[0:8].isdigit() and len(file_path.name) > 8 and file_path.name[8] == '_':
                logger.debug(f"Skipping {file_path.name} - already has date prefix")
                continue
            
            new_path = self.add_date_prefix(file_path, dry_run=dry_run)
            if new_path:
                renamed_files.append(new_path)
        
        return renamed_files
    
    def bulk_rename_from_excel(self, excel_path: Path, image_directory: Path, 
                               filename_column: str = 'filename', 
                               sku_column: str = 'sku',
                               dry_run: bool = False) -> Dict[str, str]:
        """
        Bulk rename files based on Excel mapping.
        
        Args:
            excel_path: Path to Excel file with mapping
            image_directory: Directory containing files to rename
            filename_column: Column name in Excel with current filenames
            sku_column: Column name in Excel with SKU codes
            dry_run: If True, only show what would be done
            
        Returns:
            Dictionary mapping old names to new names
        """
        try:
            # Read Excel file
            df = pd.read_excel(excel_path)
            
            if filename_column not in df.columns:
                raise ValueError(f"Column '{filename_column}' not found in Excel file")
            if sku_column not in df.columns:
                raise ValueError(f"Column '{sku_column}' not found in Excel file")
            
            rename_mapping = {}
            
            for _, row in df.iterrows():
                old_filename = str(row[filename_column]).strip()
                sku = str(row[sku_column]).strip()
                
                # Find the file
                old_path = image_directory / old_filename
                
                if not old_path.exists():
                    logger.warning(f"File not found: {old_filename}")
                    continue
                
                # Create new filename with SKU
                file_extension = old_path.suffix
                new_filename = f"{sku}{file_extension}"
                new_path = image_directory / new_filename
                
                # Handle name conflicts
                if new_path.exists() and new_path != old_path:
                    counter = 1
                    while new_path.exists():
                        new_filename = f"{sku}_{counter}{file_extension}"
                        new_path = image_directory / new_filename
                        counter += 1
                
                if dry_run:
                    logger.info(f"[DRY RUN] Would rename: {old_filename} -> {new_filename}")
                else:
                    try:
                        old_path.rename(new_path)
                        logger.info(f"Renamed: {old_filename} -> {new_filename}")
                    except Exception as e:
                        logger.error(f"Error renaming {old_filename}: {e}")
                        continue
                
                rename_mapping[old_filename] = new_filename
            
            return rename_mapping
            
        except Exception as e:
            logger.error(f"Error processing Excel file: {e}")
            raise
