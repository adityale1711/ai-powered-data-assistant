import os
import asyncio
import streamlit as st
from dotenv import load_dotenv
from .ui_components import UIComponents
from ..application.services.prompt_service import PromptService
from ..infrastructure.persistence.csv_loader import CSVLoader
from ..infrastructure.external.openai_client import OpenAIClient
from ..infrastructure.execution.code_executor import SandboxedCodeExecutor
from ..infrastructure.visualization.plotly_chart import PlotlyChartGenerator
from ..application.use_cases.process_question_use_case import ProcessQuestionUseCase

# Load environment variables from .env file
load_dotenv()


class StreamlitApp:
    """Main Streamlit application for the AI-powered data assistant."""

    def __init__(self):
        """Initialize the Streamlit application."""
        # Initialize services and use case
        self.llm_client = OpenAIClient(
            api_key=os.getenv("OPENAI_API_KEY", ""),
            model="gpt-4o-mini"
        )
        self.data_loader = CSVLoader()
        self.code_executor = SandboxedCodeExecutor()
        self.chart_generator = PlotlyChartGenerator()
        self.prompt_service = PromptService()

        self.process_question_use_case = ProcessQuestionUseCase(
            llm_provider=self.llm_client,
            data_repository=self.data_loader,
            code_executor=self.code_executor,
            chart_generator=self.chart_generator,
            prompt_service=self.prompt_service
        )

    def run(self) -> None:
        """Run the Streamlit application."""

        # Render header
        UIComponents.render_header(
            title="AI-Powered Data Assistant",
            subtitle="Ask questions about the superstore dataset using natural language and get instant insights!"
        )

        # Check the API key
        if not os.getenv("OPENAI_API_KEY"):
            st.error("OpenAI API key is not set. Please set the OPENAI_API_KEY environment variable.")
            st.info("To set up the API key:")
            st.code(
                "1. Copy .env.example to .env\n2. Add your OpenAI API key to the .env file"
            )
            return
        
        # Initialize session state for results
        if "analysis_result" not in st.session_state:
            st.session_state.analysis_result = None

        # Initialize submit trigger
        if "submit_trigger" not in st.session_state:
            st.session_state.submit_trigger = False

        # Render question input
        question = UIComponents.render_question_input()

        # Check if submit was triggered by Enter key or button click
        submit_triggered = st.button("Submit Question", type="primary") or st.session_state.submit_trigger

        # Reset submit trigger after checking
        if st.session_state.submit_trigger:
            st.session_state.submit_trigger = False

        if submit_triggered:
            if question.strip():
                # Clear previous result
                st.session_state.analysis_result = None

                # Show loading indicator
                loading_placeholder = st.empty()
                loading_placeholder.info("⏳ Processing your question, please wait...")

                try:
                    # Process the question asynchronously
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    result = loop.run_until_complete(
                        self.process_question_use_case.execute(question)
                    )
                    loop.close()

                    # Store the result in session state
                    st.session_state.analysis_result = result
                except Exception as e:
                    st.error(f"An error occurred while processing your question: {str(e)}")
                finally:
                    loading_placeholder.empty()
            else:
                st.warning("⚠️ Please enter a question before analyzing.")
        
        # Display results if available
        if st.session_state.analysis_result:
            UIComponents.render_analysis_result(st.session_state.analysis_result)


def main() -> None:
    """Entry point for the Streamlit application."""
    app = StreamlitApp()
    app.run()


if __name__ == "__main__":
    main()