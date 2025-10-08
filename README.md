# DataMender

**Cross‑Platform CSV/JSON Cleaner**

---

## 🚩 Problem Statement

Many people who work with CSV/JSON data—developers, analysts, small‑business owners—waste hours manually detecting and fixing errors in spreadsheets and data files. Data cleaning is time‑consuming, labor‑intensive, and error‑prone. Common issues include:
- Missing values
- Duplicate records
- Inconsistent formatting
- Invalid dates

These problems can skew analyses and force people to write ad‑hoc scripts repeatedly. "Bad data" refers to missing, corrupt, or inaccurate values, and must be dealt with before any analysis. DataMender automates routine cleaning tasks so users can obtain clean data quickly without writing custom scripts.

---

## ✨ Features & Scope

**Platforms:**
- Standalone desktop application (Windows exe, Linux AppImage)
- Command‑line tool (CLI)
- No Internet or server hosting required

**Supported File Types:**
- CSV
- JSON
- Optional: Convert JSON ↔ CSV

**Core Cleaning Capabilities:**
- Detect and remove duplicate rows
- Identify missing values and optionally replace with user‑defined defaults
- Standardize date/time formats (e.g., convert “3/5/2025” and “2025‑03‑05” to ISO)
- Trim whitespace and normalize string case (e.g., capitalize names consistently)
- Validate and rename column headers (replace spaces with underscores)
- Optionally filter or reorder columns

---

## 🛠️ User Workflow

1. **Select a file** (CLI argument or via GUI)
2. **Load data** into an internal table
3. **Detect issues** (missing values, duplicates, invalid dates, etc.)
4. **Choose cleaning actions** (CLI flags or GUI checkboxes)
5. **Preview changes** on a sample of rows
6. **Confirm and export** cleaned data to a new file (CSV or JSON)
7. **Optionally save configuration** for future runs

---

## 🧩 High-Level Pseudocode

```python
# Main entry point
function main():
    args = parse_command_line_args()
    if args.gui:
        launch_gui()
    else:
        run_cli(args)

# Command-line workflow
function run_cli(args):
    data = load_data(args.input_path)
    issues_report = detect_issues(data)
    display_issues_report(issues_report)

    cleaning_config = get_cleaning_config_from_args(args)
    cleaned_data = clean_data(data, cleaning_config)

    if args.preview:
        preview_changes(data, cleaned_data)
        if not user_confirms():
            exit_program()

    save_data(cleaned_data, args.output_path)
    print("Cleaning complete.")

# Data loading
function load_data(path):
    ext = file_extension(path)
    if ext == ".csv":
        return read_csv_as_list_of_dicts(path)
    else if ext == ".json":
        return read_json_as_list_of_dicts(path)
    else:
        throw UnsupportedFormatError

# Issue detection
function detect_issues(data):
    report = {}
    report["missing_values"] = find_missing_values(data)
    report["duplicates"]     = find_duplicate_rows(data)
    report["date_formats"]   = find_inconsistent_dates(data)
    # add more checks as needed
    return report

# Cleaning pipeline
function clean_data(data, config):
    cleaned = deepcopy(data)
    if config.remove_duplicates:
        cleaned = remove_duplicates(cleaned)
    if config.standardise_dates:
        cleaned = standardise_date_columns(cleaned, config.date_format)
    if config.fill_missing:
        cleaned = fill_missing_values(cleaned, config.fill_defaults)
    if config.normalise_case:
        cleaned = normalise_string_case(cleaned, config.case_type)
    if config.rename_columns:
        cleaned = rename_columns(cleaned, config.column_mapping)
    return cleaned

# Preview before writing
function preview_changes(original, cleaned):
    sample_original = original[0:5]
    sample_cleaned  = cleaned[0:5]
    display_side_by_side(sample_original, sample_cleaned)

# Data saving
function save_data(data, path):
    ext = file_extension(path)
    if ext == ".csv":
        write_list_of_dicts_to_csv(data, path)
    else if ext == ".json":
        write_list_of_dicts_to_json(data, path)
    else:
        throw UnsupportedFormatError

# GUI workflow (simplified)
function launch_gui():
    create_main_window()
    # UI elements: file chooser, checkboxes for cleaning actions, preview area
    when user_selects_file:
        data = load_data(file_path)
        display_issue_report(detect_issues(data))
    when user_clicks_preview:
        cleaned = clean_data(data, get_config_from_form())
        update_preview_area(cleaned)
    when user_clicks_save:
        save_data(cleaned, get_output_path())
        show_message("File saved successfully")
```

---

## � Installation & Usage

DataMender is ready to use! Follow these simple steps:

### **Quick Start**
```bash
# Clone or download the project
git clone <repository-url>
cd DataMender

# Install dependencies
python setup.py

# Use the CLI tool
python datamender_cli.py samples/sample_messy.csv -o clean.csv --remove-duplicates --trim-whitespace

# Launch the GUI
python datamender_cli.py --gui
```

### **Command Line Examples**
```bash
# Basic cleaning
python datamender_cli.py input.csv -o output.csv --remove-duplicates --trim-whitespace

# Full cleaning pipeline
python datamender_cli.py messy.csv -o clean.csv \
  --remove-duplicates \
  --trim-whitespace \
  --fill-missing \
  --standardize-dates \
  --normalize-case

# Analysis only (no changes)
python datamender_cli.py data.csv -o output.csv --analyze-only

# Preview changes before applying
python datamender_cli.py data.csv -o output.csv --preview --remove-duplicates
```

### **Features Implemented**
- ✅ **CLI Interface**: Complete command-line tool with 15+ options
- ✅ **GUI Interface**: Desktop application with tabbed workflow
- ✅ **Data Formats**: CSV and JSON input/output support
- ✅ **Issue Detection**: Missing values, duplicates, date inconsistencies, whitespace, case problems
- ✅ **Data Cleaning**: All core operations implemented and tested
- ✅ **Cross-Platform**: Windows, Linux, and macOS compatibility
- ✅ **Sample Data**: Included for testing and demonstration

---

## 📄 License & Contributing

DataMender is released under the MIT License - see the LICENSE file for details.

**Contributing:**
- Issues and feature requests are welcome!
- Fork the repository and submit pull requests
- Follow the existing code style and add tests for new features

**Project Status:** ✅ **Production Ready** - v1.0.0 Released

---

## 📚 References
- [numerous.ai](https://numerous.ai)
- [datascienceinpractice.github.io](https://datascienceinpractice.github.io)

---

*Last updated: January 2025*