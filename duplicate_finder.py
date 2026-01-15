"""
Duplicate File Finder Module
Detects and handles duplicate files using hash comparison.
"""

import hashlib
from pathlib import Path
from typing import Dict, List, Set, Optional
import logging

logger = logging.getLogger(__name__)


class DuplicateFinder:
    """Finds and manages duplicate files."""
    
    def __init__(self, chunk_size: int = 8192):
        """
        Initialize DuplicateFinder.
        
        Args:
            chunk_size: Size of chunks to read when hashing files
        """
        self.chunk_size = chunk_size
    
    def _calculate_hash(self, file_path: Path) -> str:
        """
        Calculate MD5 hash of a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            MD5 hash as hexadecimal string
        """
        hash_md5 = hashlib.md5()
        
        try:
            with open(file_path, 'rb') as f:
                while chunk := f.read(self.chunk_size):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            logger.error(f"Error calculating hash for {file_path}: {e}")
            return ""
    
    def find_duplicates(self, directory: Path, recursive: bool = True) -> Dict[str, List[Path]]:
        """
        Find duplicate files in a directory.
        
        Args:
            directory: Directory to search for duplicates
            recursive: Search subdirectories recursively
            
        Returns:
            Dictionary mapping file hashes to lists of duplicate file paths
        """
        hash_to_files: Dict[str, List[Path]] = {}
        
        if recursive:
            files = list(directory.rglob('*'))
        else:
            files = list(directory.glob('*'))
        
        files = [f for f in files if f.is_file()]
        
        logger.info(f"Scanning {len(files)} files for duplicates...")
        
        for file_path in files:
            file_hash = self._calculate_hash(file_path)
            
            if not file_hash:
                continue
            
            if file_hash not in hash_to_files:
                hash_to_files[file_hash] = []
            
            hash_to_files[file_hash].append(file_path)
        
        # Filter to only return duplicates (hash with more than one file)
        duplicates = {h: files for h, files in hash_to_files.items() if len(files) > 1}
        
        logger.info(f"Found {len(duplicates)} sets of duplicates")
        
        return duplicates
    
    def delete_duplicates(self, duplicates: Dict[str, List[Path]], 
                         keep_strategy: str = 'keep_oldest',
                         dry_run: bool = False) -> List[Path]:
        """
        Delete duplicate files, keeping one based on strategy.
        
        Args:
            duplicates: Dictionary of hash to file paths (from find_duplicates)
            keep_strategy: Strategy for which file to keep
                - 'keep_oldest': Keep the oldest file (by modification time)
                - 'keep_newest': Keep the newest file
                - 'keep_shortest_path': Keep file with shortest path
                - 'keep_first': Keep the first file in the list
            dry_run: If True, only show what would be deleted
            
        Returns:
            List of deleted file paths
        """
        deleted_files = []
        
        for file_hash, file_paths in duplicates.items():
            if len(file_paths) <= 1:
                continue
            
            # Determine which file to keep
            if keep_strategy == 'keep_oldest':
                keep_file = min(file_paths, key=lambda p: p.stat().st_mtime)
            elif keep_strategy == 'keep_newest':
                keep_file = max(file_paths, key=lambda p: p.stat().st_mtime)
            elif keep_strategy == 'keep_shortest_path':
                keep_file = min(file_paths, key=lambda p: len(str(p)))
            elif keep_strategy == 'keep_first':
                keep_file = file_paths[0]
            else:
                keep_file = file_paths[0]
                logger.warning(f"Unknown strategy '{keep_strategy}', using first file")
            
            # Delete other files
            for file_path in file_paths:
                if file_path == keep_file:
                    logger.debug(f"Keeping: {file_path}")
                    continue
                
                if dry_run:
                    logger.info(f"[DRY RUN] Would delete duplicate: {file_path}")
                else:
                    try:
                        file_path.unlink()
                        logger.info(f"Deleted duplicate: {file_path}")
                        deleted_files.append(file_path)
                    except Exception as e:
                        logger.error(f"Error deleting {file_path}: {e}")
        
        return deleted_files
    
    def find_and_delete_duplicates(self, directory: Path, recursive: bool = True,
                                  keep_strategy: str = 'keep_oldest',
                                  dry_run: bool = False) -> Dict:
        """
        Find and delete duplicates in one operation.
        
        Args:
            directory: Directory to process
            recursive: Search subdirectories recursively
            keep_strategy: Strategy for which file to keep
            dry_run: If True, only show what would be done
            
        Returns:
            Dictionary with results: duplicates found, files deleted, etc.
        """
        duplicates = self.find_duplicates(directory, recursive)
        deleted = self.delete_duplicates(duplicates, keep_strategy, dry_run)
        
        return {
            'duplicate_sets': len(duplicates),
            'total_duplicate_files': sum(len(files) - 1 for files in duplicates.values()),
            'deleted_files': len(deleted),
            'deleted_paths': deleted
        }
