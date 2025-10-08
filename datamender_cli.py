#!/usr/bin/env python3
"""
DataMender - Command Line Interface
CLI for the DataMender data cleaning tool.
"""

import argparse
import sys
import os
from pathlib import Path
from typing import Optional

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.data_processor import DataProcessor, DataMenderError
from src.data_cleaner import DataCleaner, CleaningConfig


class DataMenderCLI:
    """Command-line interface for DataMender."""
    
    def __init__(self):
        self.processor = DataProcessor()
        self.cleaner = DataCleaner()
    
    def create_parser(self) -> argparse.ArgumentParser:
        """Create command-line argument parser."""
        parser = argparse.ArgumentParser(
            description="DataMender - Clean and standardize CSV/JSON data files",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  datamender input.csv -o clean_output.csv --remove-duplicates --trim-whitespace
  datamender data.json -o output.csv --standardize-dates --normalize-case
  datamender messy.csv --preview --remove-duplicates --fill-missing
            """
        )
        
        # Input/Output
        parser.add_argument('input_file', nargs='?', help='Input CSV or JSON file')
        parser.add_argument('-o', '--output', help='Output file path')
        
        # Preview and analysis
        parser.add_argument('--preview', action='store_true', 
                          help='Preview changes before applying')
        parser.add_argument('--analyze-only', action='store_true',
                          help='Only analyze data and show issues report')
        
        # Cleaning operations
        parser.add_argument('--remove-duplicates', action='store_true',
                          help='Remove duplicate rows')
        parser.add_argument('--trim-whitespace', action='store_true',
                          help='Remove leading/trailing whitespace')
        parser.add_argument('--fill-missing', action='store_true',
                          help='Fill missing values with defaults')
        parser.add_argument('--fill-default', type=str, default="",
                          help='Default value for missing data')
        parser.add_argument('--standardize-dates', action='store_true',
                          help='Standardize date formats')
        parser.add_argument('--date-format', choices=['ISO', 'US', 'EU'], 
                          default='ISO', help='Target date format')
        parser.add_argument('--normalize-case', action='store_true',
                          help='Normalize text case')
        parser.add_argument('--case-type', choices=['upper', 'lower', 'title', 'capitalize'],
                          default='title', help='Type of case normalization')
        parser.add_argument('--auto-rename-columns', action='store_true',
                          help='Automatically rename columns (spaces to underscores, etc.)')
        
        # Options
        parser.add_argument('--gui', action='store_true',
                          help='Launch GUI interface')
        parser.add_argument('--verbose', '-v', action='store_true',
                          help='Verbose output')
        parser.add_argument('--quiet', '-q', action='store_true',
                          help='Quiet mode (minimal output)')
        
        return parser
    
    def run(self, args: Optional[list] = None) -> int:
        """Run the CLI application."""
        parser = self.create_parser()
        parsed_args = parser.parse_args(args)
        
        try:
            if parsed_args.gui:
                return self.launch_gui()
            else:
                return self.run_cli(parsed_args)
        except KeyboardInterrupt:
            if not parsed_args.quiet:
                print("\nOperation cancelled by user.")
            return 1
        except Exception as e:
            if not parsed_args.quiet:
                print(f"Error: {e}")
            return 1
    
    def launch_gui(self) -> int:
        """Launch the GUI interface."""
        try:
            from src.gui.main_window import DataMenderGUI
            app = DataMenderGUI()
            app.run()
            return 0
        except ImportError:
            print("GUI components not available. Please install required dependencies.")
            return 1
        except Exception as e:
            print(f"Error launching GUI: {e}")
            return 1
    
    def run_cli(self, args) -> int:
        """Run command-line workflow."""
        # Check if required arguments are provided for CLI mode
        if not args.input_file:
            print("Error: Input file is required for CLI mode.")
            return 1
        
        if not args.output:
            print("Error: Output file is required for CLI mode.")
            return 1
        
        # Validate input file
        if not Path(args.input_file).exists():
            print(f"Error: Input file '{args.input_file}' not found.")
            return 1
        
        # Load data
        if not args.quiet:
            print(f"Loading data from {args.input_file}...")
        
        try:
            data = self.processor.load_data(args.input_file)
            if not args.quiet:
                print(f"Loaded {len(data)} rows with {len(data[0].keys()) if data else 0} columns.")
        except DataMenderError as e:
            print(f"Error loading data: {e}")
            return 1
        
        # Analyze data
        if not args.quiet:
            print("\nAnalyzing data for issues...")
        
        issues_report = self.processor.detect_issues(data)
        self.display_issues_report(issues_report, args.quiet)
        
        if args.analyze_only:
            return 0
        
        # Create cleaning configuration
        config = self.create_cleaning_config(args)
        
        # Preview changes if requested
        if args.preview:
            if not self.preview_changes(data, config, args.quiet):
                print("Operation cancelled.")
                return 0
        
        # Clean data
        if not args.quiet:
            print("\nCleaning data...")
        
        cleaned_data = self.cleaner.clean_data(data, config)
        
        # Show cleaning statistics
        if not args.quiet:
            stats = self.cleaner.get_cleaning_stats()
            self.display_cleaning_stats(stats)
        
        # Save cleaned data
        try:
            self.processor.save_data(args.output, cleaned_data)
            if not args.quiet:
                print(f"\nCleaned data saved to {args.output}")
                print(f"Processed {len(cleaned_data)} rows successfully.")
        except DataMenderError as e:
            print(f"Error saving data: {e}")
            return 1
        
        return 0
    
    def create_cleaning_config(self, args) -> CleaningConfig:
        """Create cleaning configuration from CLI arguments."""
        fill_defaults = {"_default": args.fill_default} if args.fill_missing else {}
        
        config = CleaningConfig(
            remove_duplicates=args.remove_duplicates,
            trim_whitespace=args.trim_whitespace,
            fill_missing=args.fill_missing,
            fill_defaults=fill_defaults,
            standardize_dates=args.standardize_dates,
            date_format=args.date_format,
            normalize_case=args.normalize_case,
            case_type=args.case_type,
            rename_columns=args.auto_rename_columns
        )
        
        if args.auto_rename_columns:
            # Get automatic column rename suggestions
            suggestions = self.cleaner.auto_suggest_column_renames(self.processor.data)
            config.column_mapping = suggestions
        
        return config
    
    def display_issues_report(self, report: dict, quiet: bool = False) -> None:
        """Display data issues report."""
        if quiet:
            return
        
        print("\n" + "="*50)
        print("DATA QUALITY REPORT")
        print("="*50)
        
        print(f"Total rows: {report.get('total_rows', 0)}")
        print(f"Total columns: {report.get('total_columns', 0)}")
        
        # Missing values
        missing = report.get('missing_values', {})
        if missing:
            print(f"\nMissing values found in {len(missing)} columns:")
            for column, info in missing.items():
                print(f"  - {column}: {info['count']} missing ({info['percentage']}%)")
        else:
            print("\n✓ No missing values found")
        
        # Duplicates
        duplicates = report.get('duplicates', {})
        if duplicates.get('count', 0) > 0:
            print(f"\n⚠ Found {duplicates['count']} duplicate rows ({duplicates['percentage']}%)")
        else:
            print("\n✓ No duplicate rows found")
        
        # Date issues
        date_issues = report.get('date_issues', {})
        if date_issues:
            print(f"\nDate format inconsistencies in {len(date_issues)} columns:")
            for column, info in date_issues.items():
                print(f"  - {column}: {info['formats_found']} different formats")
        else:
            print("\n✓ No date format issues found")
        
        # Whitespace issues
        whitespace = report.get('whitespace_issues', {})
        if whitespace:
            print(f"\nWhitespace issues in {len(whitespace)} columns:")
            for column, info in whitespace.items():
                print(f"  - {column}: {info['count']} values ({info['percentage']}%)")
        else:
            print("\n✓ No whitespace issues found")
        
        # Case inconsistencies
        case_issues = report.get('case_inconsistencies', {})
        if case_issues:
            print(f"\nCase inconsistencies in {len(case_issues)} columns:")
            for column, info in case_issues.items():
                print(f"  - {column}: {info['inconsistent_groups']} groups with variations")
        else:
            print("\n✓ No case inconsistencies found")
    
    def display_cleaning_stats(self, stats: dict) -> None:
        """Display cleaning operation statistics."""
        print("\n" + "="*50)
        print("CLEANING STATISTICS")
        print("="*50)
        
        print(f"Original rows: {stats.get('original_rows', 0)}")
        print(f"Final rows: {stats.get('final_rows', 0)}")
        
        if stats.get('rows_removed', 0) > 0:
            print(f"Rows removed: {stats['rows_removed']}")
        
        if stats.get('duplicates_removed', 0) > 0:
            print(f"Duplicates removed: {stats['duplicates_removed']}")
        
        if stats.get('whitespace_trimmed', 0) > 0:
            print(f"Values trimmed: {stats['whitespace_trimmed']}")
        
        if stats.get('missing_values_filled', 0) > 0:
            print(f"Missing values filled: {stats['missing_values_filled']}")
        
        if stats.get('dates_standardized', 0) > 0:
            print(f"Dates standardized: {stats['dates_standardized']}")
        
        if stats.get('cases_normalized', 0) > 0:
            print(f"Cases normalized: {stats['cases_normalized']}")
        
        if stats.get('columns_renamed', 0) > 0:
            print(f"Columns renamed: {stats['columns_renamed']}")
        
        if stats.get('columns_removed', 0) > 0:
            print(f"Columns removed: {stats['columns_removed']}")
    
    def preview_changes(self, original_data: list, config: CleaningConfig, quiet: bool = False) -> bool:
        """Preview cleaning changes and get user confirmation."""
        if not original_data:
            return True
        
        # Apply cleaning to a sample
        sample_size = min(5, len(original_data))
        sample_data = original_data[:sample_size]
        cleaned_sample = self.cleaner.clean_data(sample_data, config)
        
        if not quiet:
            print("\n" + "="*50)
            print("PREVIEW - First 5 rows")
            print("="*50)
            
            print("\nBEFORE:")
            self.display_data_sample(sample_data)
            
            print("\nAFTER:")
            self.display_data_sample(cleaned_sample)
        
        # Get user confirmation
        while True:
            try:
                response = input("\nApply these changes? (y/n): ").strip().lower()
                if response in ['y', 'yes']:
                    return True
                elif response in ['n', 'no']:
                    return False
                else:
                    print("Please enter 'y' for yes or 'n' for no.")
            except EOFError:
                return False
    
    def display_data_sample(self, data: list) -> None:
        """Display a sample of data in a formatted way."""
        if not data:
            print("(No data)")
            return
        
        # Get column names
        columns = list(data[0].keys())
        
        # Calculate column widths
        col_widths = {}
        for col in columns:
            col_widths[col] = max(
                len(col),
                max(len(str(row.get(col, ""))) for row in data[:3])  # Check first 3 rows
            )
            col_widths[col] = min(col_widths[col], 20)  # Limit width
        
        # Print header
        header = " | ".join(col.ljust(col_widths[col]) for col in columns)
        print(header)
        print("-" * len(header))
        
        # Print rows
        for row in data:
            row_str = " | ".join(
                str(row.get(col, "")).ljust(col_widths[col])[:col_widths[col]] 
                for col in columns
            )
            print(row_str)


def main():
    """Main entry point for CLI."""
    cli = DataMenderCLI()
    return cli.run()


if __name__ == "__main__":
    sys.exit(main())