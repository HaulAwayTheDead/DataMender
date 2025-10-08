# Changelog

All notable changes to DataMender will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-01-XX

### Added
- Initial release of DataMender
- Command-line interface with comprehensive data cleaning options
- Graphical user interface with tabbed workflow
- Support for CSV and JSON file formats
- Core data cleaning operations:
  - Duplicate row removal
  - Missing value handling and filling
  - Date format standardization (ISO, US, EU)
  - Text case normalization
  - Whitespace trimming
  - Column renaming and validation
- Data quality analysis and issue detection
- Preview functionality for changes before applying
- Cross-platform compatibility (Windows, Linux, macOS)
- Automated setup script with dependency management
- Sample data files for testing and demonstration
- Comprehensive documentation and user guides
- Professional packaging and distribution scripts

### Features
- **CLI Tool**: Full-featured command-line interface with 15+ options
- **Desktop GUI**: Modern Tkinter-based interface with multi-tab workflow
- **Data Processing**: Robust CSV/JSON loading, cleaning, and saving
- **Quality Analysis**: Automatic detection of data quality issues
- **Format Conversion**: Seamless conversion between CSV and JSON
- **Error Handling**: Graceful error management with user-friendly messages
- **Progress Reporting**: Real-time status updates and cleaning statistics

### Technical
- Python 3.8+ compatibility
- Standard library focus for minimal dependencies
- Modular architecture for extensibility
- Comprehensive error handling and validation
- Cross-platform launcher scripts
- Production-ready packaging