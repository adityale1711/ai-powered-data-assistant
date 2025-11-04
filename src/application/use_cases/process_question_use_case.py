import time
from ...domain.entities import (
    AnalysisResult,
    Question,
    VisualizationType,
    Answer,
    DataSummary
)
from ...domain.repositories import (
    ChartGenerationError,
    IChartGenerator,
    ICodeExecutor,
    IDataRepository,
    ILLMProvider,
    IPromptService
)
from ...config import config


class ProcessQuestionUseCase:
    """Use case for processing user questions about the dataset.

    This class orchestrates the flow of data between different components
    to analyze user questions and generate comprehensive results.
    """

    def __init__(
        self,
        llm_provider: ILLMProvider,
        data_repository: IDataRepository,
        code_executor: ICodeExecutor,
        chart_generator: IChartGenerator,
        prompt_service: IPromptService
    ):
        """Initialize the use case with required dependencies.

        Args:
            llm_provider: Service for LLM interactions.
            data_repository: Service for data access.
            code_executor: Service for code execution.
            chart_generator: Service for visualization generation.
            prompt_service: Service for prompt building.
        """
        self.llm_provider = llm_provider
        self.data_repository = data_repository
        self.code_executor = code_executor
        self.chart_generator = chart_generator
        self.prompt_service = prompt_service

    def _suggest_chart_type(self, question_text: str) -> VisualizationType:
        """Suggest the best chart type based on the question.

        Args:
            question_text: The user's question.

        Returns:
            Suggested visualization type.
        """
        question_text_lower = question_text.lower()

        if any(keyword in question_text_lower for keyword in ["trend", "over time", "timeline", "series"]):
            return VisualizationType.LINE
        elif any(keyword in question_text_lower for keyword in ["compare", "vs", "versus", "difference"]):
            return VisualizationType.BAR
        elif any(keyword in question_text_lower for keyword in ["proportion", "percentage", "share", "distribution"]):
            return VisualizationType.PIE
        else:
            return VisualizationType.BAR  # Default choice

    async def execute(self, question_text: str) -> AnalysisResult:
        """Execute the question processing use case.

        Args:
            question_text: The user's natural language question.

        Returns:
            AnalysisResult containing the complete analysis.

        Raises:
            Various exceptions from the underlying services.
        """
        start_time = time.time()

        # Create Question entity
        question = Question(
            text=question_text,
            language="en"
        ) # Auto-detect language can be implemented later

        try:
            # Get dataset information
            dataset_info = self.data_repository.load_dataset(config.data_file_path)
            dataset = self.data_repository.get_dataset()

            # Build the comprehensive prompt using the prompt service
            prompt = self.prompt_service.build_analysis_prompt(question, dataset_info)

            # Generate answer and analysis code using LLM with the prepared prompt
            answer, analysis_code = await self.llm_provider.generate_answer_with_prompt(
                question, dataset_info, prompt
            )

            # Execute the generated code
            data_summary = self.code_executor.execute_code(analysis_code, dataset)

            # Generate visualizations if code execution was successful
            visualizations = None
            if data_summary.execution_successful and data_summary.data is not None:
                try:
                    # Auto-detect best visualization type
                    chart_type = self._suggest_chart_type(question_text)
                    visualizations = self.chart_generator.generate_chart(
                        chart_type=chart_type,
                        data=data_summary.data,
                        title=f"Analysis for: {question_text[:50]}...",
                        config={"description": answer.text}
                    )
                except ChartGenerationError:
                    pass

            execution_time = time.time() - start_time

            return AnalysisResult(
                question=question,
                answer=answer,
                data_summary=data_summary,
                visualization=visualizations,
                execution_time=execution_time
            )
        except Exception as e:
            # Return a result with error information
            execution_time = time.time() - start_time

            error_answer = Answer(
                text=f"An error occurred while processing your question: {str(e)}",
                confidence_score=0.0,
                explanation="Processing failed due to an error."
            )

            error_summary = DataSummary(
                data=None,
                summary_text="Processing failed",
                execution_successful=False,
                error_message=str(e)
            )

            return AnalysisResult(
                question=question,
                answer=error_answer,
                data_summary=error_summary,
                visualization=None,
                execution_time=execution_time
            )