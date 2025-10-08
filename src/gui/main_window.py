"""
DataMender - Main GUI Window
Tkinter-based graphical interface for DataMender.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import os
import sys
from pathlib import Path
from typing import Optional, Dict, Any

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from data_processor import DataProcessor, DataMenderError
from data_cleaner import DataCleaner, CleaningConfig


class DataMenderGUI:
    """Main GUI application for DataMender."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.processor = DataProcessor()
        self.cleaner = DataCleaner()
        
        self.input_file = ""
        self.output_file = ""
        self.current_data = []
        self.issues_report = {}
        
        self.setup_ui()
        
    def setup_ui(self):
        """Initialize the user interface."""
        self.root.title("DataMender - Data Cleaning Tool")
        self.root.geometry("900x700")
        self.root.minsize(800, 600)
        
        # Create main notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create tabs
        self.create_file_tab()
        self.create_analysis_tab()
        self.create_cleaning_tab()
        self.create_output_tab()
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        self.status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def create_file_tab(self):
        """Create file input/output tab."""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Files")
        
        # Input file frame
        input_frame = ttk.LabelFrame(tab, text="Input File", padding=10)
        input_frame.pack(fill=tk.X, padx=10, pady=(10, 5))
        
        self.input_var = tk.StringVar()
        input_entry = ttk.Entry(input_frame, textvariable=self.input_var, width=60)
        input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        ttk.Button(input_frame, text="Browse...", 
                  command=self.browse_input_file).pack(side=tk.RIGHT)
        
        # Output file frame
        output_frame = ttk.LabelFrame(tab, text="Output File", padding=10)
        output_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.output_var = tk.StringVar()
        output_entry = ttk.Entry(output_frame, textvariable=self.output_var, width=60)
        output_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        ttk.Button(output_frame, text="Browse...", 
                  command=self.browse_output_file).pack(side=tk.RIGHT)
        
        # Load button
        load_frame = ttk.Frame(tab)
        load_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.load_button = ttk.Button(load_frame, text="Load & Analyze Data", 
                                     command=self.load_data_async, state=tk.DISABLED)
        self.load_button.pack(side=tk.LEFT)
        
        # File info
        info_frame = ttk.LabelFrame(tab, text="File Information", padding=10)
        info_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(5, 10))
        
        self.file_info_text = scrolledtext.ScrolledText(info_frame, height=10, state=tk.DISABLED)
        self.file_info_text.pack(fill=tk.BOTH, expand=True)
        
        # Bind file path changes
        self.input_var.trace('w', self.on_file_paths_changed)
        self.output_var.trace('w', self.on_file_paths_changed)
    
    def create_analysis_tab(self):
        """Create data analysis tab."""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Analysis")
        
        # Analysis results
        results_frame = ttk.LabelFrame(tab, text="Data Quality Report", padding=10)
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.analysis_text = scrolledtext.ScrolledText(results_frame, state=tk.DISABLED)
        self.analysis_text.pack(fill=tk.BOTH, expand=True)
        
        # Refresh button
        button_frame = ttk.Frame(tab)
        button_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        self.refresh_button = ttk.Button(button_frame, text="Refresh Analysis", 
                                       command=self.refresh_analysis, state=tk.DISABLED)
        self.refresh_button.pack(side=tk.LEFT)
    
    def create_cleaning_tab(self):
        """Create cleaning options tab."""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Cleaning Options")
        
        # Scrollable frame for options
        canvas = tk.Canvas(tab)
        scrollbar = ttk.Scrollbar(tab, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Basic cleaning options
        basic_frame = ttk.LabelFrame(scrollable_frame, text="Basic Cleaning", padding=10)
        basic_frame.pack(fill=tk.X, padx=10, pady=(10, 5))
        
        self.remove_duplicates_var = tk.BooleanVar()
        ttk.Checkbutton(basic_frame, text="Remove duplicate rows", 
                       variable=self.remove_duplicates_var).pack(anchor=tk.W)
        
        self.trim_whitespace_var = tk.BooleanVar()
        ttk.Checkbutton(basic_frame, text="Trim whitespace", 
                       variable=self.trim_whitespace_var).pack(anchor=tk.W)
        
        # Missing values
        missing_frame = ttk.LabelFrame(scrollable_frame, text="Missing Values", padding=10)
        missing_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.fill_missing_var = tk.BooleanVar()
        ttk.Checkbutton(missing_frame, text="Fill missing values", 
                       variable=self.fill_missing_var).pack(anchor=tk.W)
        
        fill_frame = ttk.Frame(missing_frame)
        fill_frame.pack(fill=tk.X, pady=(5, 0))
        ttk.Label(fill_frame, text="Fill with:").pack(side=tk.LEFT)
        self.fill_default_var = tk.StringVar(value="")
        ttk.Entry(fill_frame, textvariable=self.fill_default_var, width=20).pack(side=tk.LEFT, padx=(5, 0))
        
        # Date standardization
        date_frame = ttk.LabelFrame(scrollable_frame, text="Date Standardization", padding=10)
        date_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.standardize_dates_var = tk.BooleanVar()
        ttk.Checkbutton(date_frame, text="Standardize date formats", 
                       variable=self.standardize_dates_var).pack(anchor=tk.W)
        
        format_frame = ttk.Frame(date_frame)
        format_frame.pack(fill=tk.X, pady=(5, 0))
        ttk.Label(format_frame, text="Format:").pack(side=tk.LEFT)
        self.date_format_var = tk.StringVar(value="ISO")
        date_combo = ttk.Combobox(format_frame, textvariable=self.date_format_var, 
                                 values=["ISO", "US", "EU"], state="readonly", width=15)
        date_combo.pack(side=tk.LEFT, padx=(5, 0))
        
        # Case normalization
        case_frame = ttk.LabelFrame(scrollable_frame, text="Case Normalization", padding=10)
        case_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.normalize_case_var = tk.BooleanVar()
        ttk.Checkbutton(case_frame, text="Normalize text case", 
                       variable=self.normalize_case_var).pack(anchor=tk.W)
        
        case_type_frame = ttk.Frame(case_frame)
        case_type_frame.pack(fill=tk.X, pady=(5, 0))
        ttk.Label(case_type_frame, text="Type:").pack(side=tk.LEFT)
        self.case_type_var = tk.StringVar(value="title")
        case_combo = ttk.Combobox(case_type_frame, textvariable=self.case_type_var,
                                 values=["upper", "lower", "title", "capitalize"], 
                                 state="readonly", width=15)
        case_combo.pack(side=tk.LEFT, padx=(5, 0))
        
        # Column options
        column_frame = ttk.LabelFrame(scrollable_frame, text="Column Options", padding=10)
        column_frame.pack(fill=tk.X, padx=10, pady=(5, 10))
        
        self.rename_columns_var = tk.BooleanVar()
        ttk.Checkbutton(column_frame, text="Auto-rename columns (spaces → underscores)", 
                       variable=self.rename_columns_var).pack(anchor=tk.W)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Apply button
        apply_frame = ttk.Frame(tab)
        apply_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        self.apply_button = ttk.Button(apply_frame, text="Apply Cleaning", 
                                     command=self.apply_cleaning_async, state=tk.DISABLED)
        self.apply_button.pack(side=tk.LEFT)
        
        self.preview_button = ttk.Button(apply_frame, text="Preview Changes", 
                                       command=self.preview_changes, state=tk.DISABLED)
        self.preview_button.pack(side=tk.LEFT, padx=(10, 0))
    
    def create_output_tab(self):
        """Create output and results tab."""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Results")
        
        # Results display
        results_frame = ttk.LabelFrame(tab, text="Cleaning Results", padding=10)
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(10, 5))
        
        self.results_text = scrolledtext.ScrolledText(results_frame, state=tk.DISABLED)
        self.results_text.pack(fill=tk.BOTH, expand=True)
        
        # Action buttons
        button_frame = ttk.Frame(tab)
        button_frame.pack(fill=tk.X, padx=10, pady=(5, 10))
        
        self.save_button = ttk.Button(button_frame, text="Save Results", 
                                    command=self.save_results, state=tk.DISABLED)
        self.save_button.pack(side=tk.LEFT)
        
        ttk.Button(button_frame, text="Clear Results", 
                  command=self.clear_results).pack(side=tk.LEFT, padx=(10, 0))
    
    def browse_input_file(self):
        """Browse for input file."""
        filename = filedialog.askopenfilename(
            title="Select Input File",
            filetypes=[
                ("CSV files", "*.csv"),
                ("JSON files", "*.json"),
                ("All files", "*.*")
            ]
        )
        if filename:
            self.input_var.set(filename)
    
    def browse_output_file(self):
        """Browse for output file."""
        filename = filedialog.asksaveasfilename(
            title="Save Output File",
            defaultextension=".csv",
            filetypes=[
                ("CSV files", "*.csv"),
                ("JSON files", "*.json"),
                ("All files", "*.*")
            ]
        )
        if filename:
            self.output_var.set(filename)
    
    def on_file_paths_changed(self, *args):
        """Enable/disable load button based on file paths."""
        input_file = self.input_var.get().strip()
        output_file = self.output_var.get().strip()
        
        if input_file and output_file and Path(input_file).exists():
            self.load_button.config(state=tk.NORMAL)
        else:
            self.load_button.config(state=tk.DISABLED)
    
    def load_data_async(self):
        """Load data in background thread."""
        def load_worker():
            try:
                self.update_status("Loading data...")
                self.load_button.config(state=tk.DISABLED)
                
                # Load data
                self.current_data = self.processor.load_data(self.input_var.get())
                
                # Analyze data
                self.update_status("Analyzing data...")
                self.issues_report = self.processor.detect_issues(self.current_data)
                
                # Update UI on main thread
                self.root.after(0, self.on_data_loaded)
                
            except Exception as e:
                self.root.after(0, lambda: self.show_error(f"Error loading data: {e}"))
                self.root.after(0, lambda: self.load_button.config(state=tk.NORMAL))
        
        threading.Thread(target=load_worker, daemon=True).start()
    
    def on_data_loaded(self):
        """Handle successful data loading."""
        # Update file info
        self.update_file_info()
        
        # Update analysis
        self.update_analysis_display()
        
        # Enable buttons
        self.load_button.config(state=tk.NORMAL)
        self.refresh_button.config(state=tk.NORMAL)
        self.apply_button.config(state=tk.NORMAL)
        self.preview_button.config(state=tk.NORMAL)
        
        # Switch to analysis tab
        self.notebook.select(1)
        
        self.update_status("Data loaded successfully")
    
    def update_file_info(self):
        """Update file information display."""
        self.file_info_text.config(state=tk.NORMAL)
        self.file_info_text.delete(1.0, tk.END)
        
        info = f"File: {self.input_var.get()}\n"
        info += f"Rows: {len(self.current_data):,}\n"
        if self.current_data:
            info += f"Columns: {len(self.current_data[0].keys())}\n\n"
            info += "Column Names:\n"
            for i, col in enumerate(self.current_data[0].keys(), 1):
                info += f"{i:2d}. {col}\n"
        
        self.file_info_text.insert(1.0, info)
        self.file_info_text.config(state=tk.DISABLED)
    
    def update_analysis_display(self):
        """Update analysis results display."""
        self.analysis_text.config(state=tk.NORMAL)
        self.analysis_text.delete(1.0, tk.END)
        
        report = self.format_issues_report(self.issues_report)
        self.analysis_text.insert(1.0, report)
        self.analysis_text.config(state=tk.DISABLED)
    
    def format_issues_report(self, report: Dict[str, Any]) -> str:
        """Format issues report for display."""
        output = "DATA QUALITY REPORT\n"
        output += "=" * 50 + "\n\n"
        
        output += f"Total rows: {report.get('total_rows', 0):,}\n"
        output += f"Total columns: {report.get('total_columns', 0)}\n\n"
        
        # Missing values
        missing = report.get('missing_values', {})
        if missing:
            output += f"Missing values found in {len(missing)} columns:\n"
            for column, info in missing.items():
                output += f"  • {column}: {info['count']} missing ({info['percentage']:.1f}%)\n"
        else:
            output += "✓ No missing values found\n"
        output += "\n"
        
        # Duplicates
        duplicates = report.get('duplicates', {})
        if duplicates.get('count', 0) > 0:
            output += f"⚠ Found {duplicates['count']} duplicate rows ({duplicates['percentage']:.1f}%)\n"
        else:
            output += "✓ No duplicate rows found\n"
        output += "\n"
        
        # Date issues
        date_issues = report.get('date_issues', {})
        if date_issues:
            output += f"Date format inconsistencies in {len(date_issues)} columns:\n"
            for column, info in date_issues.items():
                output += f"  • {column}: {len(info['formats_found'])} different formats\n"
        else:
            output += "✓ No date format issues found\n"
        output += "\n"
        
        # Whitespace issues
        whitespace = report.get('whitespace_issues', {})
        if whitespace:
            output += f"Whitespace issues in {len(whitespace)} columns:\n"
            for column, info in whitespace.items():
                output += f"  • {column}: {info['count']} values ({info['percentage']:.1f}%)\n"
        else:
            output += "✓ No whitespace issues found\n"
        output += "\n"
        
        # Case inconsistencies
        case_issues = report.get('case_inconsistencies', {})
        if case_issues:
            output += f"Case inconsistencies in {len(case_issues)} columns:\n"
            for column, info in case_issues.items():
                output += f"  • {column}: {info['inconsistent_groups']} groups with variations\n"
        else:
            output += "✓ No case inconsistencies found\n"
        
        return output
    
    def refresh_analysis(self):
        """Refresh data analysis."""
        if not self.current_data:
            return
        
        def refresh_worker():
            try:
                self.update_status("Refreshing analysis...")
                self.issues_report = self.processor.detect_issues(self.current_data)
                self.root.after(0, self.update_analysis_display)
                self.root.after(0, lambda: self.update_status("Analysis refreshed"))
            except Exception as e:
                self.root.after(0, lambda: self.show_error(f"Error refreshing analysis: {e}"))
        
        threading.Thread(target=refresh_worker, daemon=True).start()
    
    def create_cleaning_config(self) -> CleaningConfig:
        """Create cleaning configuration from GUI settings."""
        fill_defaults = {}
        if self.fill_missing_var.get():
            fill_defaults["_default"] = self.fill_default_var.get()
        
        return CleaningConfig(
            remove_duplicates=self.remove_duplicates_var.get(),
            trim_whitespace=self.trim_whitespace_var.get(),
            fill_missing=self.fill_missing_var.get(),
            fill_defaults=fill_defaults,
            standardize_dates=self.standardize_dates_var.get(),
            date_format=self.date_format_var.get(),
            normalize_case=self.normalize_case_var.get(),
            case_type=self.case_type_var.get(),
            rename_columns=self.rename_columns_var.get()
        )
    
    def preview_changes(self):
        """Preview cleaning changes."""
        if not self.current_data:
            return
        
        config = self.create_cleaning_config()
        
        # Apply to sample
        sample_size = min(5, len(self.current_data))
        sample_data = self.current_data[:sample_size]
        cleaned_sample = self.cleaner.clean_data(sample_data, config)
        
        # Show preview window
        self.show_preview_window(sample_data, cleaned_sample)
    
    def show_preview_window(self, original: list, cleaned: list):
        """Show preview window with before/after comparison."""
        preview_window = tk.Toplevel(self.root)
        preview_window.title("Preview Changes")
        preview_window.geometry("800x600")
        
        # Create notebook for before/after
        notebook = ttk.Notebook(preview_window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Before tab
        before_frame = ttk.Frame(notebook)
        notebook.add(before_frame, text="Before")
        before_text = scrolledtext.ScrolledText(before_frame)
        before_text.pack(fill=tk.BOTH, expand=True)
        before_text.insert(1.0, self.format_data_sample(original))
        before_text.config(state=tk.DISABLED)
        
        # After tab
        after_frame = ttk.Frame(notebook)
        notebook.add(after_frame, text="After")
        after_text = scrolledtext.ScrolledText(after_frame)
        after_text.pack(fill=tk.BOTH, expand=True)
        after_text.insert(1.0, self.format_data_sample(cleaned))
        after_text.config(state=tk.DISABLED)
        
        # Close button
        ttk.Button(preview_window, text="Close", 
                  command=preview_window.destroy).pack(pady=10)
    
    def format_data_sample(self, data: list) -> str:
        """Format data sample for display."""
        if not data:
            return "(No data)"
        
        # Get column names
        columns = list(data[0].keys())
        
        # Create formatted table
        output = "Sample Data (first 5 rows):\n"
        output += "=" * 50 + "\n\n"
        
        # Header
        header = " | ".join(f"{col[:15]:15}" for col in columns)
        output += header + "\n"
        output += "-" * len(header) + "\n"
        
        # Rows
        for row in data:
            row_str = " | ".join(
                f"{str(row.get(col, ''))[:15]:15}" for col in columns
            )
            output += row_str + "\n"
        
        return output
    
    def apply_cleaning_async(self):
        """Apply cleaning operations in background thread."""
        def clean_worker():
            try:
                self.update_status("Applying cleaning operations...")
                self.apply_button.config(state=tk.DISABLED)
                
                config = self.create_cleaning_config()
                cleaned_data = self.cleaner.clean_data(self.current_data, config)
                stats = self.cleaner.get_cleaning_stats()
                
                # Save results
                self.processor.save_data(self.output_var.get(), cleaned_data)
                
                # Update UI on main thread
                self.root.after(0, lambda: self.on_cleaning_complete(stats))
                
            except Exception as e:
                self.root.after(0, lambda: self.show_error(f"Error applying cleaning: {e}"))
                self.root.after(0, lambda: self.apply_button.config(state=tk.NORMAL))
        
        threading.Thread(target=clean_worker, daemon=True).start()
    
    def on_cleaning_complete(self, stats: Dict[str, Any]):
        """Handle successful cleaning completion."""
        # Update results display
        self.update_results_display(stats)
        
        # Enable buttons
        self.apply_button.config(state=tk.NORMAL)
        self.save_button.config(state=tk.NORMAL)
        
        # Switch to results tab
        self.notebook.select(3)
        
        self.update_status("Cleaning completed successfully")
    
    def update_results_display(self, stats: Dict[str, Any]):
        """Update cleaning results display."""
        self.results_text.config(state=tk.NORMAL)
        self.results_text.delete(1.0, tk.END)
        
        results = "CLEANING RESULTS\n"
        results += "=" * 50 + "\n\n"
        
        results += f"Original rows: {stats.get('original_rows', 0):,}\n"
        results += f"Final rows: {stats.get('final_rows', 0):,}\n"
        
        if stats.get('rows_removed', 0) > 0:
            results += f"Rows removed: {stats['rows_removed']:,}\n"
        
        if stats.get('duplicates_removed', 0) > 0:
            results += f"Duplicates removed: {stats['duplicates_removed']:,}\n"
        
        if stats.get('whitespace_trimmed', 0) > 0:
            results += f"Values trimmed: {stats['whitespace_trimmed']:,}\n"
        
        if stats.get('missing_values_filled', 0) > 0:
            results += f"Missing values filled: {stats['missing_values_filled']:,}\n"
        
        if stats.get('dates_standardized', 0) > 0:
            results += f"Dates standardized: {stats['dates_standardized']:,}\n"
        
        if stats.get('cases_normalized', 0) > 0:
            results += f"Cases normalized: {stats['cases_normalized']:,}\n"
        
        if stats.get('columns_renamed', 0) > 0:
            results += f"Columns renamed: {stats['columns_renamed']:,}\n"
        
        results += f"\nOutput saved to: {self.output_var.get()}\n"
        
        self.results_text.insert(1.0, results)
        self.results_text.config(state=tk.DISABLED)
    
    def save_results(self):
        """Save results to file (already done, just show confirmation)."""
        messagebox.showinfo("Save Complete", 
                          f"Results have been saved to:\n{self.output_var.get()}")
    
    def clear_results(self):
        """Clear results display."""
        self.results_text.config(state=tk.NORMAL)
        self.results_text.delete(1.0, tk.END)
        self.results_text.config(state=tk.DISABLED)
        self.save_button.config(state=tk.DISABLED)
    
    def update_status(self, message: str):
        """Update status bar message."""
        self.status_var.set(message)
        self.root.update_idletasks()
    
    def show_error(self, message: str):
        """Show error message dialog."""
        messagebox.showerror("Error", message)
        self.update_status("Error occurred")
    
    def run(self):
        """Run the GUI application."""
        # Center window on screen
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        
        self.root.mainloop()


def main():
    """Main entry point for GUI."""
    app = DataMenderGUI()
    app.run()


if __name__ == "__main__":
    main()