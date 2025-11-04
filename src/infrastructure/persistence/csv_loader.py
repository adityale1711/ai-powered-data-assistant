import os
import pandas as pd
import requests
from io import StringIO
from typing import Any, Optional
from urllib.parse import urlparse
from ...domain.entities import DatasetInfo
from ...domain.repositories import (
    DataLoadError,
    DatasetNotLoadedError,
    IDataRepository
)


class CSVLoader(IDataRepository):
    """CSV implementation of the data repository interface.

    This class handles loading and management of CSV datasets using pandas.
    """

    def __init__(self):
        """Initialize the CSV loader."""
        self._dataset: Optional[pd.DataFrame] = None
        self._dataset_info: Optional[DatasetInfo] = None

    def load_dataset(self, file_source: str) -> DatasetInfo:
        """Load a CSV dataset from file path or URL and return its information.

        Args:
            file_source: Path to the CSV file or URL to the CSV file.

        Returns:
            DatasetInfo object with dataset metadata.

        Raises:
            DataLoadError: If the CSV file cannot be loaded.
        """
        try:
            # Determine if file_source is a URL or local path
            if self._is_url(file_source):
                # Load from URL
                dataset = self._load_from_url(file_source)
                filename = self._extract_filename_from_url(file_source)
            else:
                # Load from local file
                dataset = pd.read_csv(file_source)
                filename = file_source.split(os.sep)[-1]

            self._dataset = dataset

            # Create dataset info
            self._dataset_info = DatasetInfo(
                filename=filename,
                columns=list(self._dataset.columns),
                shape=self._dataset.shape,
                sample_data=self._dataset.head().to_dict("records"),
                column_types={
                    col: str(dtype) for col, dtype in self._dataset.dtypes.items()
                }
            )

            return self._dataset_info
        except FileNotFoundError as e:
            raise DataLoadError(f"Dataset file not found: {file_source}") from e
        except pd.errors.EmptyDataError as e:
            raise DataLoadError("Dataset file is empty") from e
        except pd.errors.ParserError as e:
            raise DataLoadError(f"Error parsing CSV file: {str(e)}") from e
        except Exception as e:
            raise DataLoadError(f"Unexpected error loading dataset: {str(e)}") from e

    def _is_url(self, source: str) -> bool:
        """Check if the source is a URL."""
        try:
            result = urlparse(source)
            return all([result.scheme, result.netloc])
        except Exception:
            return False

    def _load_from_url(self, url: str) -> pd.DataFrame:
        """Load CSV data from a URL."""
        try:
            # Download the file
            response = requests.get(url, timeout=30)
            response.raise_for_status()

            # Check if the response contains CSV data
            content_type = response.headers.get('content-type', '')
            if 'text/csv' not in content_type and not url.endswith('.csv'):
                # For Google Drive links, sometimes the content-type is generic
                # so we proceed with the download
                pass

            # Read CSV from the response content
            csv_data = StringIO(response.text)
            return pd.read_csv(csv_data)

        except requests.exceptions.RequestException as e:
            raise DataLoadError(f"Error downloading file from URL: {str(e)}") from e
        except Exception as e:
            raise DataLoadError(f"Error processing downloaded file: {str(e)}") from e

    def _extract_filename_from_url(self, url: str) -> str:
        """Extract filename from URL."""
        try:
            parsed = urlparse(url)
            path = parsed.path
            filename = path.split('/')[-1]

            # If filename doesn't end with .csv, give it a default name
            if not filename.endswith('.csv'):
                filename = "downloaded_dataset.csv"

            return filename
        except Exception:
            return "downloaded_dataset.csv"
        
    def get_dataset(self) -> Any:
        """Get the loaded dataset.

        Returns:
            The pandas DataFrame containing the dataset.

        Raises:
            DatasetNotLoadedError: If no dataset has been loaded.
        """
        if self._dataset is None:
            raise DatasetNotLoadedError(
                "No dataset has been loaded. Call load_dataset() first."
            )
        
        return self._dataset
