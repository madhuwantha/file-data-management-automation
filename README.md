# File & Data Management Automation

A comprehensive Python tool for automating file organization, renaming, duplicate detection, and archiving tasks. Perfect for small businesses and administrators who need to manage large numbers of files efficiently.

## Features

### 📁 File Organization
- **Automatic sorting by type**: Organizes files into folders by extension (PDFs, Images, CSVs, Documents, etc.)
- **Download folder automation**: Special handling for download folders - moves invoices to 'Finance', photos to 'Media'
- **Recursive processing**: Process entire directory trees
- **Smart conflict resolution**: Automatically handles filename conflicts

### 📝 File Renaming
- **Date prefix renaming**: Add date prefixes to files based on modification date or custom date
- **Batch processing**: Rename all files in a directory at once
- **Bulk rename from Excel**: Rename hundreds of product photos using SKU codes from an Excel spreadsheet

### 🔍 Duplicate Detection
- **Hash-based detection**: Uses MD5 hashing to find exact duplicate files
- **Multiple keep strategies**: Choose to keep oldest, newest, shortest path, or first file
- **Safe deletion**: Preview duplicates before deletion

### 📦 File Archiving
- **Monthly archiving**: Automatically zip old files monthly
- **Age-based filtering**: Archive files older than specified days
- **Category-based archiving**: Create separate archives for each file type
- **Optional deletion**: Delete originals after archiving to save space

## Installation

1. **Clone or download this repository**

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

## Usage

### Organize Files by Type

Organize files in a directory into folders by type:

```bash
python main.py organize /path/to/files
```

Organize download folder (special handling for invoices and photos):

```bash
python main.py organize ~/Downloads --downloads
```

Process subdirectories recursively:

```bash
python main.py organize /path/to/files --recursive
```

### Rename Files with Date Prefixes

Add date prefixes to all files in a directory:

```bash
python main.py rename /path/to/files
```

Rename a single file:

```bash
python main.py rename --single-file /path/to/file.pdf
```

Custom date format:

```bash
python main.py rename /path/to/files --date-format "%Y-%m-%d"
```

### Bulk Rename from Excel

Rename product photos using SKU codes from an Excel file:

```bash
python main.py bulk-rename /path/to/photos --excel-file mapping.xlsx
```

Custom column names:

```bash
python main.py bulk-rename /path/to/photos --excel-file mapping.xlsx \
  --filename-column "current_name" --sku-column "product_sku"
```

**Excel file format:**
| filename | sku |
|----------|-----|
| IMG_001.jpg | SKU-12345 |
| IMG_002.jpg | SKU-12346 |
| photo1.png | SKU-12347 |

### Find and Delete Duplicates

Find duplicates (preview only):

```bash
python main.py duplicates /path/to/files
```

Find and delete duplicates (keeps oldest file):

```bash
python main.py duplicates /path/to/files --delete
```

Keep newest file instead:

```bash
python main.py duplicates /path/to/files --delete --keep-strategy keep_newest
```

### Archive Old Files

Archive files older than 30 days:

```bash
python main.py archive /path/to/files --days-old 30
```

Archive and delete originals:

```bash
python main.py archive /path/to/files --days-old 30 --delete
```

Create separate archives by file type:

```bash
python main.py archive /path/to/files --days-old 30 --by-category
```

### Dry Run Mode

Test any command without making changes:

```bash
python main.py organize /path/to/files --dry-run
python main.py rename /path/to/files --dry-run
python main.py duplicates /path/to/files --delete --dry-run
```

## Examples

### Example 1: Organize Download Folder Daily

```bash
# Run this daily to keep downloads organized
python main.py organize ~/Downloads --downloads
```

### Example 2: Organize and Rename Files

```bash
# First organize by type
python main.py organize /path/to/files

# Then add date prefixes
python main.py rename /path/to/files --recursive
```

### Example 3: Bulk Rename Product Photos

1. Create Excel file `product_mapping.xlsx`:
   - Column A: `filename` (current photo names)
   - Column B: `sku` (product SKU codes)

2. Run:
```bash
python main.py bulk-rename /path/to/product/photos --excel-file product_mapping.xlsx
```

### Example 4: Monthly Cleanup Workflow

```bash
# 1. Remove duplicates
python main.py duplicates /path/to/files --delete

# 2. Archive files older than 90 days
python main.py archive /path/to/files --days-old 90 --delete

# 3. Organize remaining files
python main.py organize /path/to/files
```

## Module Structure

- **`file_organizer.py`**: File sorting and organization
- **`file_renamer.py`**: Date prefix and bulk renaming
- **`duplicate_finder.py`**: Duplicate detection and removal
- **`archiver.py`**: File archiving and compression
- **`main.py`**: CLI interface

## Configuration

### Custom File Type Mappings

You can customize file type mappings by modifying the `FILE_TYPES` dictionary in `file_organizer.py`:

```python
FILE_TYPES = {
    'PDFs': ['.pdf'],
    'Images': ['.jpg', '.jpeg', '.png', ...],
    # Add your custom categories
}
```

### Date Format

Default date format is `YYYYMMDD`. You can change it using the `--date-format` argument or by modifying the `FileRenamer` class.

## Safety Features

- **Dry run mode**: Test commands without making changes
- **Conflict resolution**: Automatically handles filename conflicts
- **Logging**: All operations are logged to `file_management.log`
- **Error handling**: Graceful error handling with informative messages

## Logging

All operations are logged to `file_management.log` in the current directory. Check this file for detailed operation history.

## Requirements

- Python 3.7+
- pandas >= 2.0.0
- openpyxl >= 3.1.0

## License

This project is provided as-is for personal and commercial use.

## Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

## Troubleshooting

### "Module not found" errors
Make sure all dependencies are installed:
```bash

python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
```

### Excel file not found
Use absolute paths or ensure you're in the correct directory when running commands.

### Permission errors
Make sure you have read/write permissions for the directories you're working with.

### Large file operations
For very large directories (10,000+ files), operations may take time. Use `--dry-run` first to estimate processing time.
