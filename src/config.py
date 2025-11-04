import os
from dotenv import load_dotenv


class Config:
    """Centralized configuration class for the AI Data Assistant.

    This class loads environment variables from .env file and provides
    access to configuration values with validation.
    """

    def __init__(self):
        """Initialize the configuration by loading environment variables."""
        load_dotenv()
        self._validate_required_variables()

    def _validate_required_variables(self):
        """Validate that all required environment variables are set."""
        required_variables = [
            'OPENAI_API_KEY',
            'DATA_FILE_PATH',
            'BUILDER_PROMPT_PATH',
            'SYSTEM_PROMPT_PATH',
            'APP_SYSTEM_PROMPT_PATH',
            'ANALYSIS_PROMPT_PATH',
            'LOG_DIR'
        ]

        missing_variables = []
        for var in required_variables:
            if not os.getenv(var):
                missing_variables.append(var)

        if missing_variables:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing_variables)}. "
                "Please set these variables in your .env file or environment."
            )

    @property
    def openai_api_key(self) -> str:
        """Get the OpenAI API key."""
        return os.environ['OPENAI_API_KEY']

    @property
    def app_title(self) -> str:
        """Get the application title."""
        return os.getenv('APP_TITLE', 'AI Data Assistant')

    @property
    def data_file_path(self) -> str:
        """Get the data file path."""
        return os.environ['DATA_FILE_PATH']

    @property
    def builder_prompt_path(self) -> str:
        """Get the builder prompt file path."""
        return os.environ['BUILDER_PROMPT_PATH']

    @property
    def system_prompt_path(self) -> str:
        """Get the system prompt file path."""
        return os.environ['SYSTEM_PROMPT_PATH']

    @property
    def app_system_prompt_path(self) -> str:
        """Get the application system prompt file path."""
        return os.environ['APP_SYSTEM_PROMPT_PATH']

    @property
    def analysis_prompt_path(self) -> str:
        """Get the analysis prompt file path."""
        return os.environ['ANALYSIS_PROMPT_PATH']

    @property
    def log_dir(self) -> str:
        """Get the log directory path."""
        return os.environ['LOG_DIR']

    @property
    def debug(self) -> bool:
        """Get debug mode setting."""
        return os.getenv('DEBUG', 'False').lower() == 'true'


# Global configuration instance
config = Config()