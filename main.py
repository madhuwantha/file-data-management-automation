#!/usr/bin/env python3
"""
File & Data Management Automation - Main CLI Interface
Comprehensive tool for organizing, renaming, and managing files.
"""

import argparse
import sys
from pathlib import Path
from typing import Optional
import logging

from file_organizer import FileOrganizer
from file_renamer import FileRenamer
from duplicate_finder import DuplicateFinder
from archiver import FileArchiver

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('file_management.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


def organize_files(args):
    """Organize files by type."""
    organizer = FileOrganizer(args.directory)
    
    if args.downloads:
        results = organizer.organize_downloads(args.directory, dry_run=args.dry_run)
    else:
        results = organizer.organize_files(recursive=args.recursive, dry_run=args.dry_run)
    
    print("\n=== Organization Results ===")
    for category, files in results.items():
        if files:
            print(f"{category}: {len(files)} files")
    
    return results


def rename_files(args):
    """Rename files with date prefixes."""
    renamer = FileRenamer(date_format=args.date_format)
    directory = Path(args.directory)
    
    if args.single_file:
        file_path = Path(args.single_file)
        renamer.add_date_prefix(file_path, dry_run=args.dry_run)
    else:
        renamed = renamer.batch_add_date_prefix(directory, recursive=args.recursive, dry_run=args.dry_run)
        print(f"\n=== Renaming Results ===")
        print(f"Renamed {len(renamed)} files")


def bulk_rename_from_excel(args):
    """Bulk rename files from Excel mapping."""
    renamer = FileRenamer()
    excel_path = Path(args.excel_file)
    image_dir = Path(args.directory)
    
    if not excel_path.exists():
        print(f"Error: Excel file not found: {excel_path}")
        return
    
    if not image_dir.exists():
        print(f"Error: Directory not found: {image_dir}")
        return
    
    mapping = renamer.bulk_rename_from_excel(
        excel_path=excel_path,
        image_directory=image_dir,
        filename_column=args.filename_column,
        sku_column=args.sku_column,
        dry_run=args.dry_run
    )
    
    print(f"\n=== Bulk Rename Results ===")
    print(f"Processed {len(mapping)} files")


def find_duplicates(args):
    """Find and optionally delete duplicate files."""
    finder = DuplicateFinder()
    directory = Path(args.directory)
    
    if args.delete:
        results = finder.find_and_delete_duplicates(
            directory=directory,
            recursive=args.recursive,
            keep_strategy=args.keep_strategy,
            dry_run=args.dry_run
        )
        
        print("\n=== Duplicate Removal Results ===")
        print(f"Duplicate sets found: {results['duplicate_sets']}")
        print(f"Total duplicate files: {results['total_duplicate_files']}")
        print(f"Files deleted: {results['deleted_files']}")
    else:
        duplicates = finder.find_duplicates(directory, recursive=args.recursive)
        
        print("\n=== Duplicate Files Found ===")
        print(f"Found {len(duplicates)} sets of duplicates")
        
        for file_hash, file_paths in list(duplicates.items())[:10]:  # Show first 10
            print(f"\nHash: {file_hash[:8]}... ({len(file_paths)} duplicates)")
            for path in file_paths:
                print(f"  - {path}")
        
        if len(duplicates) > 10:
            print(f"\n... and {len(duplicates) - 10} more sets")


def archive_files(args):
    """Archive old files."""
    archiver = FileArchiver()
    directory = Path(args.directory)
    
    if args.by_category:
        archives = archiver.archive_by_category(
            directory=directory,
            days_old=args.days_old,
            delete_after_archive=args.delete,
            dry_run=args.dry_run
        )
        print(f"\n=== Archiving Results ===")
        print(f"Created {len(archives)} archive files")
    else:
        archive_path = archiver.archive_old_files(
            directory=directory,
            days_old=args.days_old,
            delete_after_archive=args.delete,
            dry_run=args.dry_run
        )
        print(f"\n=== Archiving Results ===")
        if not args.dry_run:
            print(f"Created archive: {archive_path}")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='File & Data Management Automation Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Organize files by type
  python main.py organize /path/to/files

  # Organize download folder (invoices to Finance, photos to Media)
  python main.py organize --downloads ~/Downloads

  # Add date prefixes to all files
  python main.py rename /path/to/files --recursive

  # Bulk rename product photos from Excel
  python main.py bulk-rename /path/to/photos --excel mapping.xlsx

  # Find and delete duplicates
  python main.py duplicates /path/to/files --delete

  # Archive files older than 30 days
  python main.py archive /path/to/files --days-old 30 --delete

  # Dry run (see what would happen without making changes)
  python main.py organize /path/to/files --dry-run
        """
    )
    
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be done without making changes')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Organize command
    organize_parser = subparsers.add_parser('organize', help='Organize files by type')
    organize_parser.add_argument('directory', help='Directory to organize')
    organize_parser.add_argument('--recursive', '-r', action='store_true',
                                help='Process subdirectories recursively')
    organize_parser.add_argument('--downloads', action='store_true',
                                help='Use download folder organization (invoices->Finance, photos->Media)')
    organize_parser.set_defaults(func=organize_files)
    
    # Rename command
    rename_parser = subparsers.add_parser('rename', help='Rename files with date prefixes')
    rename_parser.add_argument('directory', nargs='?', help='Directory containing files to rename')
    rename_parser.add_argument('--single-file', help='Rename a single file')
    rename_parser.add_argument('--recursive', '-r', action='store_true',
                              help='Process subdirectories recursively')
    rename_parser.add_argument('--date-format', default='%Y%m%d',
                              help='Date format string (default: %%Y%%m%%d)')
    rename_parser.set_defaults(func=rename_files)
    
    # Bulk rename command
    bulk_rename_parser = subparsers.add_parser('bulk-rename', 
                                               help='Bulk rename files from Excel mapping')
    bulk_rename_parser.add_argument('directory', help='Directory containing files to rename')
    bulk_rename_parser.add_argument('--excel-file', required=True,
                                   help='Excel file with filename and SKU columns')
    bulk_rename_parser.add_argument('--filename-column', default='filename',
                                   help='Column name with current filenames (default: filename)')
    bulk_rename_parser.add_argument('--sku-column', default='sku',
                                   help='Column name with SKU codes (default: sku)')
    bulk_rename_parser.set_defaults(func=bulk_rename_from_excel)
    
    # Duplicates command
    duplicates_parser = subparsers.add_parser('duplicates', 
                                             help='Find and delete duplicate files')
    duplicates_parser.add_argument('directory', help='Directory to search for duplicates')
    duplicates_parser.add_argument('--recursive', '-r', action='store_true',
                                  help='Search subdirectories recursively')
    duplicates_parser.add_argument('--delete', action='store_true',
                                  help='Delete duplicate files (keeps one based on strategy)')
    duplicates_parser.add_argument('--keep-strategy', 
                                  choices=['keep_oldest', 'keep_newest', 'keep_shortest_path', 'keep_first'],
                                  default='keep_oldest',
                                  help='Strategy for which duplicate to keep (default: keep_oldest)')
    duplicates_parser.set_defaults(func=find_duplicates)
    
    # Archive command
    archive_parser = subparsers.add_parser('archive', help='Archive old files')
    archive_parser.add_argument('directory', help='Directory containing files to archive')
    archive_parser.add_argument('--days-old', type=int, default=30,
                               help='Archive files older than this many days (default: 30)')
    archive_parser.add_argument('--delete', action='store_true',
                               help='Delete original files after archiving')
    archive_parser.add_argument('--by-category', action='store_true',
                               help='Create separate archives for each file type')
    archive_parser.set_defaults(func=archive_files)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    try:
        args.func(args)
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
