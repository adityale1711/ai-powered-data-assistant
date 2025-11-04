import os
import pandas as pd
from typing import Any, Optional
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

    def load_dataset(self, file_path: str) -> DatasetInfo:
        """Load a CSV dataset and return its information.

        Args:
            file_path: Path to the CSV file.

        Returns:
            DatasetInfo object with dataset metadata.

        Raises:
            DataLoadError: If the CSV file cannot be loaded.
        """
        try:
            # Load the dataset
            self._dataset = pd.read_csv(file_path)

            # Create dataset info
            self._dataset_info = DatasetInfo(
                filename=file_path.split(os.sep)[-1],
                columns=list(self._dataset.columns),
                shape=self._dataset.shape,
                sample_data=self._dataset.head().to_dict("records"),
                column_types={
                    col: str(dtype) for col, dtype in self._dataset.dtypes.items()
                }
            )

            return self._dataset_info
        except FileNotFoundError as e:
            raise DataLoadError(f"Dataset file not found: {file_path}") from e
        except pd.errors.EmptyDataError as e:
            raise DataLoadError("Dataset file is empty") from e
        except pd.errors.ParserError as e:
            raise DataLoadError(f"Error parsing CSV file: {str(e)}") from e
        except Exception as e:
            raise DataLoadError(f"Unexpected error loading dataset: {str(e)}") from e
        
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
