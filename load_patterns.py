"""
Pattern Data Loader

Loads pattern data from CSV export into a pandas DataFrame for analysis and manipulation.
Provides validation, statistics, and data access utilities.
"""

import pandas as pd
from pathlib import Path
from typing import Optional
import sys


class PatternDataLoader:
    """
    Loads and manages pattern data from CSV exports.
    
    This class handles loading the export_updated.csv file, validates its structure,
    and provides access to the pattern data through a pandas DataFrame.
    """
    
    EXPECTED_COLUMNS = [
        'pattern_id', 'pattern_name', 'pattern_type', 'category', 'status',
        'complexity', 'version', 'domains', 'last_updated', 'tuple_notation',
        'tuple_notation_format', 'definition_description', 'components',
        'type_definitions', 'properties', 'operations', 'requires_dependencies',
        'uses_dependencies', 'specializes_dependencies', 'specialized_by_dependencies',
        'manifestations'
    ]
    
    def __init__(self, csv_path: str = "output/export_updated.csv"):
        """
        Initialize the loader with the path to the CSV file.
        
        Args:
            csv_path: Path to the CSV file (relative to project root or absolute)
        
        Raises:
            FileNotFoundError: If the CSV file doesn't exist
            ValueError: If the CSV structure is invalid
        """
        self.csv_path = Path(csv_path)
        if not self.csv_path.is_absolute():
            # Make path relative to this script's location
            script_dir = Path(__file__).parent
            self.csv_path = script_dir / csv_path
        
        if not self.csv_path.exists():
            raise FileNotFoundError(
                f"CSV file not found: {self.csv_path}\n"
                f"Expected location: {self.csv_path.absolute()}"
            )
        
        self.df: Optional[pd.DataFrame] = None
        self._loaded = False
    
    def load(self) -> pd.DataFrame:
        """
        Load the CSV file into a pandas DataFrame.
        
        Returns:
            DataFrame containing the pattern data
        
        Raises:
            ValueError: If CSV structure is invalid or missing required columns
            pd.errors.EmptyDataError: If CSV file is empty
        """
        try:
            self.df = pd.read_csv(self.csv_path, encoding='utf-8')
        except pd.errors.EmptyDataError:
            raise ValueError(f"CSV file is empty: {self.csv_path}")
        except Exception as e:
            raise ValueError(f"Error reading CSV file: {e}")
        
        self._validate_structure()
        self._loaded = True
        
        return self.df
    
    def _validate_structure(self) -> None:
        """
        Validate that the DataFrame has the expected structure.
        
        Raises:
            ValueError: If required columns are missing
        """
        if self.df is None:
            raise ValueError("DataFrame not loaded. Call load() first.")
        
        missing_columns = set(self.EXPECTED_COLUMNS) - set(self.df.columns)
        if missing_columns:
            raise ValueError(
                f"CSV missing required columns: {sorted(missing_columns)}\n"
                f"Found columns: {sorted(self.df.columns.tolist())}"
            )
        
        if len(self.df) == 0:
            raise ValueError("CSV file contains no data rows")
    
    def get_dataframe(self) -> pd.DataFrame:
        """
        Get the loaded DataFrame.
        
        Returns:
            DataFrame containing the pattern data
        
        Raises:
            RuntimeError: If data hasn't been loaded yet
        """
        if not self._loaded or self.df is None:
            raise RuntimeError("Data not loaded. Call load() first.")
        
        return self.df
    
    def summary(self) -> dict:
        """
        Get summary statistics about the loaded data.
        
        Returns:
            Dictionary containing summary information
        """
        if not self._loaded or self.df is None:
            raise RuntimeError("Data not loaded. Call load() first.")
        
        return {
            'total_patterns': len(self.df),
            'pattern_types': self.df['pattern_type'].value_counts().to_dict(),
            'categories': self.df['category'].value_counts().to_dict(),
            'status_distribution': self.df['status'].value_counts().to_dict(),
            'complexity_levels': self.df['complexity'].value_counts().to_dict(),
            'columns': self.df.columns.tolist(),
            'memory_usage_mb': self.df.memory_usage(deep=True).sum() / (1024 * 1024)
        }
    
    def get_pattern_by_id(self, pattern_id: str) -> Optional[pd.Series]:
        """
        Retrieve a specific pattern by its ID.
        
        Args:
            pattern_id: The pattern ID to look up (e.g., 'C1', 'F1.1')
        
        Returns:
            Series containing the pattern data, or None if not found
        """
        if not self._loaded or self.df is None:
            raise RuntimeError("Data not loaded. Call load() first.")
        
        matches = self.df[self.df['pattern_id'] == pattern_id]
        if len(matches) == 0:
            return None
        
        return matches.iloc[0]
    
    def filter_by_type(self, pattern_type: str) -> pd.DataFrame:
        """
        Filter patterns by type.
        
        Args:
            pattern_type: Type to filter by (e.g., 'concept', 'flow', 'pattern')
        
        Returns:
            DataFrame containing only patterns of the specified type
        """
        if not self._loaded or self.df is None:
            raise RuntimeError("Data not loaded. Call load() first.")
        
        return self.df[self.df['pattern_type'] == pattern_type].copy()
    
    def filter_by_category(self, category: str) -> pd.DataFrame:
        """
        Filter patterns by category.
        
        Args:
            category: Category to filter by
        
        Returns:
            DataFrame containing only patterns of the specified category
        """
        if not self._loaded or self.df is None:
            raise RuntimeError("Data not loaded. Call load() first.")
        
        return self.df[self.df['category'] == category].copy()


def main():
    """
    Main entry point demonstrating usage of PatternDataLoader.
    """
    try:
        # Initialize and load the data
        loader = PatternDataLoader()
        print(f"Loading patterns from: {loader.csv_path.absolute()}")
        
        df = loader.load()
        print(f"✓ Successfully loaded {len(df)} patterns")
        
        # Display summary statistics
        print("\n=== Summary Statistics ===")
        summary = loader.summary()
        print(f"Total patterns: {summary['total_patterns']}")
        print(f"Memory usage: {summary['memory_usage_mb']:.2f} MB")
        
        print("\nPattern types:")
        for ptype, count in summary['pattern_types'].items():
            print(f"  {ptype}: {count}")
        
        print("\nCategories:")
        for category, count in summary['categories'].items():
            print(f"  {category}: {count}")
        
        print("\nStatus distribution:")
        for status, count in summary['status_distribution'].items():
            print(f"  {status}: {count}")
        
        print("\nComplexity levels:")
        for complexity, count in summary['complexity_levels'].items():
            print(f"  {complexity}: {count}")
        
        # Example: Show first few patterns
        print("\n=== First 5 Patterns ===")
        print(df[['pattern_id', 'pattern_name', 'pattern_type', 'category']].head())
        
        # Example: Look up specific pattern
        print("\n=== Example: Pattern C1 ===")
        pattern = loader.get_pattern_by_id('C1')
        if pattern is not None:
            print(f"ID: {pattern['pattern_id']}")
            print(f"Name: {pattern['pattern_name']}")
            print(f"Type: {pattern['pattern_type']}")
            print(f"Category: {pattern['category']}")
        
        # Example: Filter by type
        flow_patterns = loader.filter_by_type('flow')
        print(f"\n=== Flow Patterns ({len(flow_patterns)} total) ===")
        print(flow_patterns[['pattern_id', 'pattern_name']].head(10))
        
        return 0
        
    except FileNotFoundError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1
    except ValueError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2
    except Exception as e:
        print(f"UNEXPECTED ERROR: {e}", file=sys.stderr)
        return 3


if __name__ == "__main__":
    sys.exit(main())


