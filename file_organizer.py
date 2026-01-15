"""
File Organizer Module
Handles automatic sorting of files by type into designated folders.
"""

import os
import shutil
from pathlib import Path
from typing import Dict, List, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class FileOrganizer:
    """Organizes files by type into designated folders."""
    
    # File type mappings
    FILE_TYPES = {
        'PDFs': ['.pdf'],
        'Images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.svg', '.webp', '.ico'],
        'CSVs': ['.csv'],
        'Reports': ['.csv', '.xlsx', '.xls', '.xlsm'],
        'Documents': ['.doc', '.docx', '.txt', '.rtf', '.odt'],
        'Spreadsheets': ['.xlsx', '.xls', '.xlsm', '.ods'],
        'Presentations': ['.ppt', '.pptx', '.odp'],
        'Archives': ['.zip', '.rar', '.7z', '.tar', '.gz'],
        'Videos': ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.mkv', '.webm'],
        'Audio': ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a'],
        'Code': ['.py', '.js', '.html', '.css', '.java', '.cpp', '.c', '.php', '.rb'],
        'Other': []  # Catch-all for unclassified files
    }
    
    def __init__(self, base_path: str, organize_config: Optional[Dict[str, str]] = None):
        """
        Initialize FileOrganizer.
        
        Args:
            base_path: Base directory where files are located
            organize_config: Custom mapping of file types to folder names
        """
        self.base_path = Path(base_path)
        self.organize_config = organize_config or {}
        self._setup_directories()
    
    def _setup_directories(self):
        """Create organization folders if they don't exist."""
        folders = list(self.FILE_TYPES.keys())
        if self.organize_config:
            folders.extend(self.organize_config.values())
        
        for folder in set(folders):
            folder_path = self.base_path / folder
            folder_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"Ensured directory exists: {folder_path}")
    
    def _get_file_category(self, file_path: Path) -> str:
        """
        Determine which category a file belongs to.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Category name for the file
        """
        extension = file_path.suffix.lower()
        
        # Check custom config first
        for category, extensions in self.organize_config.items():
            if extension in extensions:
                return category
        
        # Check default mappings
        for category, extensions in self.FILE_TYPES.items():
            if extension in extensions:
                return category
        
        return 'Other'
    
    def organize_files(self, recursive: bool = False, dry_run: bool = False) -> Dict[str, List[str]]:
        """
        Organize files in the base directory by type.
        
        Args:
            recursive: If True, process subdirectories recursively
            dry_run: If True, only show what would be done without moving files
            
        Returns:
            Dictionary mapping categories to lists of moved files
        """
        results = {category: [] for category in self.FILE_TYPES.keys()}
        results['Other'] = []
        
        if recursive:
            files = list[Path](self.base_path.rglob('*'))
        else:
            files = list(self.base_path.glob('*'))
        
        # Filter to only files (not directories)
        files = [f for f in files if f.is_file()]
        
        for file_path in files:
            # Skip if file is already in an organization folder
            if file_path.parent.name in self.FILE_TYPES.keys():
                continue
            
            category = self._get_file_category(file_path)
            target_folder = self.base_path / category
            target_path = target_folder / file_path.name
            
            # Handle name conflicts
            if target_path.exists() and target_path != file_path:
                counter = 1
                stem = file_path.stem
                while target_path.exists():
                    target_path = target_folder / f"{stem}_{counter}{file_path.suffix}"
                    counter += 1
            
            if dry_run:
                logger.info(f"[DRY RUN] Would move: {file_path.name} -> {category}/{target_path.name}")
            else:
                try:
                    shutil.move(str(file_path), str(target_path))
                    logger.info(f"Moved: {file_path.name} -> {category}/{target_path.name}")
                    results[category].append(str(target_path))
                except Exception as e:
                    logger.error(f"Error moving {file_path.name}: {e}")
        
        return results
    
    def organize_downloads(self, download_path: str, dry_run: bool = False) -> Dict[str, List[str]]:
        """
        Organize download folder with specific rules:
        - Invoices -> Finance
        - Photos -> Media
        - Other files by type
        
        Args:
            download_path: Path to download folder
            dry_run: If True, only show what would be done
            
        Returns:
            Dictionary of organized files
        """
        download_dir = Path(download_path)
        results = {
            'Finance': [],
            'Media': [],
            'Other': []
        }
        
        # Create Finance and Media folders
        finance_folder = download_dir / 'Finance'
        media_folder = download_dir / 'Media'
        
        if not dry_run:
            finance_folder.mkdir(exist_ok=True)
            media_folder.mkdir(exist_ok=True)
        
        # Keywords for invoice detection
        invoice_keywords = ['invoice', 'bill', 'receipt', 'payment', 'statement', 'invoice_', 'inv_']
        
        for file_path in download_dir.iterdir():
            if file_path.is_file():
                file_name_lower = file_path.name.lower()
                
                # Check if it's an invoice
                is_invoice = any(keyword in file_name_lower for keyword in invoice_keywords)
                is_image = file_path.suffix.lower() in self.FILE_TYPES['Images']
                
                if is_invoice:
                    target = finance_folder / file_path.name
                    category = 'Finance'
                elif is_image:
                    target = media_folder / file_path.name
                    category = 'Media'
                else:
                    # Use standard organization
                    category = self._get_file_category(file_path)
                    target_folder = download_dir / category
                    if not dry_run:
                        target_folder.mkdir(exist_ok=True)
                    target = target_folder / file_path.name
                    if category not in results:
                        results[category] = []
                
                # Handle name conflicts
                if target.exists() and target != file_path:
                    counter = 1
                    stem = file_path.stem
                    while target.exists():
                        target = target.parent / f"{stem}_{counter}{file_path.suffix}"
                        counter += 1
                
                if dry_run:
                    logger.info(f"[DRY RUN] Would move: {file_path.name} -> {category}/")
                else:
                    try:
                        shutil.move(str(file_path), str(target))
                        logger.info(f"Moved: {file_path.name} -> {category}/")
                        results[category].append(str(target))
                    except Exception as e:
                        logger.error(f"Error moving {file_path.name}: {e}")
        
        return results
