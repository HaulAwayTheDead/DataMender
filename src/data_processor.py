#!/usr/bin/env python3
"""
DataMender - Cross-Platform CSV/JSON Data Cleaner
Core data processing engine for cleaning and standardizing data files.
"""

import csv
import json
import os
import copy
import re
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path


class DataMenderError(Exception):
    """Base exception for DataMender operations."""
    pass


class UnsupportedFormatError(DataMenderError):
    """Raised when file format is not supported."""
    pass


class DataProcessor:
    """Core data processing engine for DataMender."""
    
    def __init__(self):
        self.data: List[Dict[str, Any]] = []
        self.original_data: List[Dict[str, Any]] = []
        self.issues_report: Dict[str, Any] = {}
        
    def load_data(self, file_path: str) -> List[Dict[str, Any]]:
        """Load data from CSV or JSON file."""
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
            
        extension = path.suffix.lower()
        
        if extension == '.csv':
            return self._load_csv(file_path)
        elif extension == '.json':
            return self._load_json(file_path)
        else:
            raise UnsupportedFormatError(f"Unsupported file format: {extension}")
    
    def _load_csv(self, file_path: str) -> List[Dict[str, Any]]:
        """Load CSV file into list of dictionaries."""
        data = []
        try:
            with open(file_path, 'r', encoding='utf-8', newline='') as file:
                # Detect delimiter
                sample = file.read(1024)
                file.seek(0)
                
                sniffer = csv.Sniffer()
                delimiter = sniffer.sniff(sample).delimiter
                
                reader = csv.DictReader(file, delimiter=delimiter)
                data = [row for row in reader]
                
        except Exception as e:
            raise DataMenderError(f"Error reading CSV file: {e}")
            
        self.data = data
        self.original_data = copy.deepcopy(data)
        return data
    
    def _load_json(self, file_path: str) -> List[Dict[str, Any]]:
        """Load JSON file into list of dictionaries."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                json_data = json.load(file)
                
            # Handle different JSON structures
            if isinstance(json_data, list):
                data = json_data
            elif isinstance(json_data, dict):
                # If it's a single object, wrap in list
                data = [json_data]
            else:
                raise DataMenderError("JSON must contain an array of objects or a single object")
                
        except json.JSONDecodeError as e:
            raise DataMenderError(f"Invalid JSON format: {e}")
        except Exception as e:
            raise DataMenderError(f"Error reading JSON file: {e}")
            
        self.data = data
        self.original_data = copy.deepcopy(data)
        return data
    
    def save_data(self, output_path: str, data: Optional[List[Dict[str, Any]]] = None) -> None:
        """Save data to CSV or JSON file."""
        if data is None:
            data = self.data
            
        path = Path(output_path)
        extension = path.suffix.lower()
        
        # Create directory if it doesn't exist
        path.parent.mkdir(parents=True, exist_ok=True)
        
        if extension == '.csv':
            self._save_csv(output_path, data)
        elif extension == '.json':
            self._save_json(output_path, data)
        else:
            raise UnsupportedFormatError(f"Unsupported output format: {extension}")
    
    def _save_csv(self, file_path: str, data: List[Dict[str, Any]]) -> None:
        """Save data as CSV file."""
        if not data:
            raise DataMenderError("No data to save")
            
        try:
            with open(file_path, 'w', encoding='utf-8', newline='') as file:
                fieldnames = data[0].keys()
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data)
        except Exception as e:
            raise DataMenderError(f"Error saving CSV file: {e}")
    
    def _save_json(self, file_path: str, data: List[Dict[str, Any]]) -> None:
        """Save data as JSON file."""
        try:
            with open(file_path, 'w', encoding='utf-8') as file:
                json.dump(data, file, indent=2, ensure_ascii=False)
        except Exception as e:
            raise DataMenderError(f"Error saving JSON file: {e}")
    
    def detect_issues(self, data: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """Detect common data quality issues."""
        if data is None:
            data = self.data
            
        if not data:
            return {"error": "No data to analyze"}
        
        report = {
            "total_rows": len(data),
            "total_columns": len(data[0].keys()) if data else 0,
            "missing_values": self._find_missing_values(data),
            "duplicates": self._find_duplicate_rows(data),
            "date_issues": self._find_date_issues(data),
            "whitespace_issues": self._find_whitespace_issues(data),
            "case_inconsistencies": self._find_case_inconsistencies(data)
        }
        
        self.issues_report = report
        return report
    
    def _find_missing_values(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Find missing values in the dataset."""
        missing_report = {}
        
        if not data:
            return missing_report
            
        columns = data[0].keys()
        
        for column in columns:
            missing_count = 0
            for row in data:
                value = row.get(column, "")
                if value is None or str(value).strip() in ["", "null", "NULL", "None", "N/A", "n/a"]:
                    missing_count += 1
            
            if missing_count > 0:
                missing_report[column] = {
                    "count": missing_count,
                    "percentage": round((missing_count / len(data)) * 100, 2)
                }
        
        return missing_report
    
    def _find_duplicate_rows(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Find duplicate rows in the dataset."""
        if not data:
            return {"count": 0, "indices": []}
            
        seen = set()
        duplicates = []
        
        for i, row in enumerate(data):
            # Convert row to tuple for hashing
            row_tuple = tuple(sorted(row.items()))
            if row_tuple in seen:
                duplicates.append(i)
            else:
                seen.add(row_tuple)
        
        return {
            "count": len(duplicates),
            "indices": duplicates,
            "percentage": round((len(duplicates) / len(data)) * 100, 2) if data else 0
        }
    
    def _find_date_issues(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Find inconsistent date formats."""
        date_issues = {}
        
        if not data:
            return date_issues
        
        columns = data[0].keys()
        date_patterns = [
            r'\d{4}-\d{2}-\d{2}',  # YYYY-MM-DD
            r'\d{2}/\d{2}/\d{4}',  # MM/DD/YYYY
            r'\d{1,2}/\d{1,2}/\d{4}',  # M/D/YYYY
            r'\d{2}-\d{2}-\d{4}',  # MM-DD-YYYY
        ]
        
        for column in columns:
            formats_found = set()
            for row in data:
                value = str(row.get(column, "")).strip()
                if value:
                    for pattern in date_patterns:
                        if re.match(pattern, value):
                            formats_found.add(pattern)
            
            if len(formats_found) > 1:
                date_issues[column] = {
                    "formats_found": len(formats_found),
                    "patterns": list(formats_found)
                }
        
        return date_issues
    
    def _find_whitespace_issues(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Find whitespace issues in data."""
        whitespace_issues = {}
        
        if not data:
            return whitespace_issues
        
        columns = data[0].keys()
        
        for column in columns:
            issues_count = 0
            for row in data:
                value = row.get(column, "")
                if isinstance(value, str):
                    if value != value.strip():
                        issues_count += 1
            
            if issues_count > 0:
                whitespace_issues[column] = {
                    "count": issues_count,
                    "percentage": round((issues_count / len(data)) * 100, 2)
                }
        
        return whitespace_issues
    
    def _find_case_inconsistencies(self, data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Find case inconsistencies in string data."""
        case_issues = {}
        
        if not data:
            return case_issues
        
        columns = data[0].keys()
        
        for column in columns:
            values = set()
            for row in data:
                value = row.get(column, "")
                if isinstance(value, str) and value.strip():
                    values.add(value.strip())
            
            # Check for case variations of the same word
            lower_values = {}
            for value in values:
                lower_val = value.lower()
                if lower_val not in lower_values:
                    lower_values[lower_val] = []
                lower_values[lower_val].append(value)
            
            inconsistencies = {k: v for k, v in lower_values.items() if len(v) > 1}
            
            if inconsistencies:
                case_issues[column] = {
                    "inconsistent_groups": len(inconsistencies),
                    "examples": dict(list(inconsistencies.items())[:3])  # Show first 3 examples
                }
        
        return case_issues