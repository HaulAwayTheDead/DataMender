#!/usr/bin/env python3
"""
DataMender - Data Cleaning Operations
Implementation of various data cleaning and standardization operations.
"""

import re
import copy
from datetime import datetime
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass


@dataclass
class CleaningConfig:
    """Configuration for data cleaning operations."""
    remove_duplicates: bool = False
    standardize_dates: bool = False
    date_format: str = "ISO"  # ISO, US, EU
    fill_missing: bool = False
    fill_defaults: Optional[Dict[str, str]] = None
    normalize_case: bool = False
    case_type: str = "title"  # title, upper, lower
    rename_columns: bool = False
    column_mapping: Optional[Dict[str, str]] = None
    trim_whitespace: bool = False
    filter_columns: Optional[List[str]] = None
    
    def __post_init__(self):
        if self.fill_defaults is None:
            self.fill_defaults = {}
        if self.column_mapping is None:
            self.column_mapping = {}
        if self.filter_columns is None:
            self.filter_columns = []


class DataCleaner:
    """Data cleaning operations for DataMender."""
    
    def __init__(self):
        self.cleaning_stats = {}
    
    def clean_data(self, data: List[Dict[str, Any]], config: CleaningConfig) -> List[Dict[str, Any]]:
        """Apply cleaning operations based on configuration."""
        if not data:
            return data
        
        cleaned = copy.deepcopy(data)
        self.cleaning_stats = {"original_rows": len(data)}
        
        # Apply cleaning operations in order
        if config.trim_whitespace:
            cleaned = self._trim_whitespace(cleaned)
        
        if config.remove_duplicates:
            cleaned = self._remove_duplicates(cleaned)
        
        if config.fill_missing:
            cleaned = self._fill_missing_values(cleaned, config.fill_defaults or {})
        
        if config.standardize_dates:
            cleaned = self._standardize_dates(cleaned, config.date_format)
        
        if config.normalize_case:
            cleaned = self._normalize_case(cleaned, config.case_type)
        
        if config.rename_columns:
            cleaned = self._rename_columns(cleaned, config.column_mapping or {})
        
        if config.filter_columns:
            cleaned = self._filter_columns(cleaned, config.filter_columns or [])
        
        self.cleaning_stats["final_rows"] = len(cleaned)
        self.cleaning_stats["rows_removed"] = self.cleaning_stats["original_rows"] - len(cleaned)
        
        return cleaned
    
    def _trim_whitespace(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove leading and trailing whitespace from string values."""
        trimmed_count = 0
        
        for row in data:
            for key, value in row.items():
                if isinstance(value, str):
                    trimmed_value = value.strip()
                    if trimmed_value != value:
                        trimmed_count += 1
                        row[key] = trimmed_value
        
        self.cleaning_stats["whitespace_trimmed"] = trimmed_count
        return data
    
    def _remove_duplicates(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate rows from the dataset."""
        seen = set()
        unique_data = []
        duplicates_removed = 0
        
        for row in data:
            # Convert row to tuple for hashing
            row_tuple = tuple(sorted(row.items()))
            if row_tuple not in seen:
                seen.add(row_tuple)
                unique_data.append(row)
            else:
                duplicates_removed += 1
        
        self.cleaning_stats["duplicates_removed"] = duplicates_removed
        return unique_data
    
    def _fill_missing_values(self, data: List[Dict[str, Any]], fill_defaults: Dict[str, str]) -> List[Dict[str, Any]]:
        """Fill missing values with specified defaults."""
        filled_count = 0
        
        for row in data:
            for key, value in row.items():
                if self._is_missing_value(value):
                    # Use column-specific default or global default
                    default_value = fill_defaults.get(key, fill_defaults.get("_default", ""))
                    row[key] = default_value
                    filled_count += 1
        
        self.cleaning_stats["missing_values_filled"] = filled_count
        return data
    
    def _is_missing_value(self, value: Any) -> bool:
        """Check if a value is considered missing."""
        if value is None:
            return True
        
        if isinstance(value, str):
            cleaned_value = value.strip().lower()
            return cleaned_value in ["", "null", "none", "n/a", "na", "#n/a", "nan"]
        
        return False
    
    def _standardize_dates(self, data: List[Dict[str, Any]], target_format: str) -> List[Dict[str, Any]]:
        """Standardize date formats across the dataset."""
        dates_converted = 0
        
        # Common date patterns
        date_patterns = [
            (r'^(\d{4})-(\d{1,2})-(\d{1,2})$', '%Y-%m-%d'),  # YYYY-MM-DD
            (r'^(\d{1,2})/(\d{1,2})/(\d{4})$', '%m/%d/%Y'),  # MM/DD/YYYY
            (r'^(\d{4})/(\d{1,2})/(\d{1,2})$', '%Y/%m/%d'),  # YYYY/MM/DD
            (r'^(\d{1,2})-(\d{1,2})-(\d{4})$', '%d-%m-%Y'),  # DD-MM-YYYY
            (r'^(\d{1,2})\.(\d{1,2})\.(\d{4})$', '%d.%m.%Y'),  # DD.MM.YYYY
            (r'^(\d{1,2})/(\d{1,2})/(\d{2})$', '%m/%d/%y'),  # MM/DD/YY
        ]
        
        for row in data:
            for key, value in row.items():
                if isinstance(value, str) and value.strip():
                    standardized_date = self._convert_date(value.strip(), date_patterns, target_format)
                    if standardized_date != value:
                        row[key] = standardized_date
                        dates_converted += 1
        
        self.cleaning_stats["dates_standardized"] = dates_converted
        return data
    
    def _convert_date(self, date_str: str, patterns: List[tuple], target_format: str) -> str:
        """Convert date string to target format."""
        for pattern, format_str in patterns:
            try:
                if re.match(pattern, date_str):
                    # Parse the date
                    date_obj = datetime.strptime(date_str, format_str)
                    
                    # Convert to target format
                    if target_format.upper() == "ISO":
                        return date_obj.strftime('%Y-%m-%d')
                    elif target_format.upper() == "US":
                        return date_obj.strftime('%m/%d/%Y')
                    elif target_format.upper() == "EU":
                        return date_obj.strftime('%d/%m/%Y')
                    else:
                        return date_obj.strftime('%Y-%m-%d')  # Default to ISO
            except ValueError:
                continue
        
        # If no pattern matches, return original
        return date_str
    
    def _normalize_case(self, data: List[Dict[str, Any]], case_type: str) -> List[Dict[str, Any]]:
        """Normalize string case across the dataset."""
        cases_normalized = 0
        
        for row in data:
            for key, value in row.items():
                if isinstance(value, str) and value.strip():
                    original_value = value
                    
                    if case_type.lower() == "upper":
                        row[key] = value.upper()
                    elif case_type.lower() == "lower":
                        row[key] = value.lower()
                    elif case_type.lower() == "title":
                        row[key] = value.title()
                    elif case_type.lower() == "capitalize":
                        row[key] = value.capitalize()
                    
                    if row[key] != original_value:
                        cases_normalized += 1
        
        self.cleaning_stats["cases_normalized"] = cases_normalized
        return data
    
    def _rename_columns(self, data: List[Dict[str, Any]], column_mapping: Dict[str, str]) -> List[Dict[str, Any]]:
        """Rename columns based on mapping."""
        if not column_mapping or not data:
            return data
        
        renamed_data = []
        columns_renamed = 0
        
        for row in data:
            new_row = {}
            for old_key, value in row.items():
                new_key = column_mapping.get(old_key, old_key)
                new_row[new_key] = value
                if new_key != old_key:
                    columns_renamed += 1
            renamed_data.append(new_row)
        
        self.cleaning_stats["columns_renamed"] = len(column_mapping)
        return renamed_data
    
    def _filter_columns(self, data: List[Dict[str, Any]], columns_to_keep: List[str]) -> List[Dict[str, Any]]:
        """Filter dataset to keep only specified columns."""
        if not columns_to_keep or not data:
            return data
        
        filtered_data = []
        original_columns = len(data[0].keys()) if data else 0
        
        for row in data:
            filtered_row = {key: row.get(key, "") for key in columns_to_keep if key in row}
            filtered_data.append(filtered_row)
        
        final_columns = len(filtered_data[0].keys()) if filtered_data else 0
        self.cleaning_stats["columns_removed"] = original_columns - final_columns
        
        return filtered_data
    
    def get_cleaning_stats(self) -> Dict[str, Any]:
        """Get statistics about the cleaning operations performed."""
        return self.cleaning_stats.copy()
    
    def auto_suggest_column_renames(self, data: List[Dict[str, Any]]) -> Dict[str, str]:
        """Suggest column renames for better formatting."""
        if not data:
            return {}
        
        suggestions = {}
        columns = data[0].keys()
        
        for column in columns:
            # Convert spaces to underscores and make lowercase
            suggested_name = re.sub(r'\s+', '_', column.strip().lower())
            # Remove special characters except underscores
            suggested_name = re.sub(r'[^a-zA-Z0-9_]', '', suggested_name)
            # Remove multiple underscores
            suggested_name = re.sub(r'_+', '_', suggested_name)
            # Remove leading/trailing underscores
            suggested_name = suggested_name.strip('_')
            
            if suggested_name != column and suggested_name:
                suggestions[column] = suggested_name
        
        return suggestions