import os
from dotenv import load_dotenv

# Try to import streamlit for secrets, but don't fail if not available
try:
    import streamlit as st
    HAS_STREAMLIT = True
except ImportError:
    HAS_STREAMLIT = False


class Config:
    """Centralized configuration class for the AI Data Assistant.

    This class loads environment variables from .env file and provides
    access to configuration values with validation.
    """

    def __init__(self):
        """Initialize the configuration by loading environment variables."""
        load_dotenv()
        self._validate_required_variables()

    def _get_config_value(self, key: str, default=None):
        """Get configuration value from Streamlit secrets or environment variables.

        Args:
            key: Configuration key
            default: Default value if not found

        Returns:
            Configuration value
        """
        # Try Streamlit secrets first (for deployment)
        if HAS_STREAMLIT:
            try:
                value = st.secrets.get(key)
                if value is not None:
                    return value
            except Exception:
                pass

        # Fall back to environment variables (for local development)
        return os.getenv(key, default)

    def _validate_required_variables(self):
        """Validate that all required environment variables are set."""
        # Check OpenAI API key first
        if not self._get_config_value('OPENAI_API_KEY'):
            raise ValueError(
                "Missing required environment variable: OPENAI_API_KEY. "
                "Please set this variable in your .env file or Streamlit secrets."
            )

        # Check data source configuration
        data_source_type = self._get_config_value('DATA_SOURCE_TYPE', 'local')
        if data_source_type == 'local':
            if not self._get_config_value('DATA_FILE_PATH'):
                raise ValueError(
                    "Missing required environment variable: DATA_FILE_PATH for local data source. "
                    "Please set this variable in your .env file or Streamlit secrets."
                )
        elif data_source_type == 'url':
            if not self._get_config_value('DATA_FILE_URL'):
                raise ValueError(
                    "Missing required environment variable: DATA_FILE_URL for URL data source. "
                    "Please set this variable in your .env file or Streamlit secrets."
                )

        # Check prompt and log paths
        required_variables = [
            'BUILDER_PROMPT_PATH',
            'SYSTEM_PROMPT_PATH',
            'APP_SYSTEM_PROMPT_PATH',
            'ANALYSIS_PROMPT_PATH',
            'LOG_DIR'
        ]

        missing_variables = []
        for var in required_variables:
            if not self._get_config_value(var):
                missing_variables.append(var)

        if missing_variables:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing_variables)}. "
                "Please set these variables in your .env file or Streamlit secrets."
            )

    @property
    def openai_api_key(self) -> str:
        """Get the OpenAI API key."""
        return self._get_config_value('OPENAI_API_KEY')

    @property
    def app_title(self) -> str:
        """Get the application title."""
        return self._get_config_value('APP_TITLE', 'AI Data Assistant')

    @property
    def data_source_type(self) -> str:
        """Get the data source type."""
        return self._get_config_value('DATA_SOURCE_TYPE', 'local')

    @property
    def data_file_path(self) -> str:
        """Get the data file path (for local data source)."""
        if self.data_source_type == 'local':
            return self._get_config_value('DATA_FILE_PATH')
        else:
            raise ValueError("DATA_FILE_PATH is only available for local data source")

    @property
    def data_file_url(self) -> str:
        """Get the data file URL (for URL data source)."""
        if self.data_source_type == 'url':
            return self._get_config_value('DATA_FILE_URL')
        else:
            raise ValueError("DATA_FILE_URL is only available for URL data source")

    @property
    def data_source(self) -> str:
        """Get the appropriate data source (path or URL)."""
        if self.data_source_type == 'local':
            return self.data_file_path
        elif self.data_source_type == 'url':
            return self.data_file_url
        else:
            raise ValueError(f"Unsupported data source type: {self.data_source_type}")

    @property
    def builder_prompt_path(self) -> str:
        """Get the builder prompt file path."""
        return self._get_config_value('BUILDER_PROMPT_PATH')

    @property
    def system_prompt_path(self) -> str:
        """Get the system prompt file path."""
        return self._get_config_value('SYSTEM_PROMPT_PATH')

    @property
    def app_system_prompt_path(self) -> str:
        """Get the application system prompt file path."""
        return self._get_config_value('APP_SYSTEM_PROMPT_PATH')

    @property
    def analysis_prompt_path(self) -> str:
        """Get the analysis prompt file path."""
        return self._get_config_value('ANALYSIS_PROMPT_PATH')

    @property
    def log_dir(self) -> str:
        """Get the log directory path."""
        return self._get_config_value('LOG_DIR')

    @property
    def debug(self) -> bool:
        """Get debug mode setting."""
        return self._get_config_value('DEBUG', 'False').lower() == 'true'


# Global configuration instance
config = Config()