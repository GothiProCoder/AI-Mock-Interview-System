# Interview Analysis Pipeline

This project provides a production-ready pipeline for analyzing interview transcripts using large language models (LLMs). It leverages a two-stage analysis process (Analyst → Synthesis) to extract objective insights and generate a comprehensive, actionable report for hiring managers and mentors.

## Features

- **Two-Stage Analysis**:
    - **Analyst Agent**: Meticulously extracts factual, objective performance snippets from the transcript without judgment.
    - **Synthesis Agent**: Acts as a world-class Senior Engineering Manager, taking the analyst's report to generate a holistic, empathetic, and actionable final report.
- **Robust and Resilient**: Includes automatic error handling with retries to ensure reliability when interacting with external APIs.
- **Cost-Effective**: Features an in-memory caching system to avoid re-processing the same transcript, saving API costs.
- **Data Validation**: Utilizes Pydantic for rigorous input and output validation, ensuring data integrity and quality.
- **Comprehensive Logging**: Detailed logging provides visibility into the pipeline's execution, making it easy to monitor and debug.
- **High-Quality, Actionable Output**: The final report includes a candidate summary, key strengths and weaknesses with evidence, a prioritized 2-week development roadmap, and recommended learning resources.

## Requirements

- Python 3.8+
- An API key for Google Gemini

The specific Python dependencies are listed in `requirements.txt`:
- `python-dotenv`
- `langchain`
- `langchain-google-genai`
- `google-generativeai`
- `pydantic`
- `pytest` (for development)

## Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/GothiProCoder/AI-Mock-Interview-System.git
    cd AI-Mock-Interview-System
    ```

2.  **Create and activate a virtual environment** (recommended):
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install the required dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Configuration

The pipeline requires a Google Gemini API key to function.

1.  **Copy the example environment file:**
    ```bash
    cp .env.example .env
    ```

2.  **Edit the `.env` file** and add your API key:
    ```
    GEMINI_API_KEY=YOUR_API_KEY
    ```
    The application will automatically load this key from the `.env` file.

## Usage

Using the pipeline is straightforward. Instantiate the `InterviewAnalysisPipeline` class and call the `analyze` method with your transcript data.

```python
import os
from dotenv import load_dotenv
from pipeline.pipeline import InterviewAnalysisPipeline

# Load environment variables (for API key)
load_dotenv()

# Example transcript data
mock_transcript = {
  "metadata": {
    "candidate_id": "C-EDGE-01",
    "position": "Backend Engineer Intern"
  },
  "transcript": {
    "interviewer": "Can you explain the difference between SQL and NoSQL databases?",
    "candidate": "Yeah, SQL is for structured data, tables and rows. NoSQL is for everything else.",
    "interviewer_1": "Okay, could you give an example of when you might prefer a NoSQL database?",
    "candidate_1": "You'd use Mongo for something like a social media feed, where it's schema-less.",
    # ... more transcript exchanges
  }
}

# Initialize the pipeline
# The API key is loaded automatically from the .env file
api_key = os.getenv("GEMINI_API_KEY")
pipeline = InterviewAnalysisPipeline(api_key=api_key)

# Run the analysis
try:
    final_report = pipeline.analyze(mock_transcript)

    # Print the generated report
    print("--- Candidate Summary ---")
    print(final_report.candidate_summary.headline)
    print(final_report.candidate_summary.overall_impression)
    print("\n--- Insights ---")
    # ... and so on
except ValueError as e:
    print(f"Error: {e}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
```

The `analyze` method returns a `FinalReport` Pydantic object, which gives you structured, validated access to the results.

## API Usage

This project includes a FastAPI server to expose the analysis pipeline as a microservice.

### Running the API Server

1.  **Ensure your `.env` file is configured** with your `GEMINI_API_key` as described in the "Configuration" section.

2.  **Start the server** using `uvicorn`:
    ```bash
    uvicorn main:app --reload
    ```
    The server will be available at `http://127.0.0.1:8000`.

### Sending an Analysis Request

You can send a POST request to the `/analyze` endpoint with your transcript data.

Here is an example using `curl`:

```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/analyze' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "metadata": {
    "candidate_id": "C-API-01",
    "position": "Software Engineer"
  },
  "transcript": {
    "interviewer": "What is the difference between a list and a tuple in Python?",
    "candidate": "A list is mutable, meaning you can change its contents, while a tuple is immutable.",
    "interviewer_1": "Good. Can you give me an example of when you would use a tuple?",
    "candidate_1": "You might use a tuple for something like dictionary keys or for a collection of constants that should not change."
  }
}'
```

On success, the API will return a JSON object containing the detailed `FinalReport`.

## Project Structure

```
.
├── .env.example        # Example environment file for API keys
├── LICENSE             # Project License
├── requirements.txt    # Python dependencies
├── pipeline/           # Main source code directory
│   ├── __init__.py
│   ├── models.py       # Pydantic models for data structures
│   ├── pipeline.py     # Core InterviewAnalysisPipeline class
│   └── utils.py        # Helper functions for validation and formatting
└── tests/              # Tests for the pipeline
    ├── __init__.py
    ├── test_pipeline.py  # Tests for the main pipeline logic
    └── test_validation.py # Tests for transcript validation utilities
```

-   **`pipeline/pipeline.py`**: This is the heart of the project. The `InterviewAnalysisPipeline` class orchestrates the entire process, including initializing LLMs, setting up LangChain chains, handling caching, and managing the two-stage analysis.
-   **`pipeline/models.py`**: Defines all the Pydantic data structures used in the project, such as `AnalysisReport` and `FinalReport`. This ensures that all data flowing through the pipeline is well-defined and validated.
-   **`pipeline/utils.py`**: Contains standalone utility functions for formatting the raw transcript into a clean string and for validating both the input transcript and the quality of the final generated report.
-   **`tests/`**: Contains unit tests to ensure the reliability and correctness of the pipeline's components.

## Testing

The project uses `pytest` for testing. To run the tests, execute the following command from the root directory:

```bash
pytest
```

The tests cover:
-   Correct initialization of the pipeline.
-   Validation logic for transcripts (e.g., handling empty or incomplete data).
-   Basic checks to ensure the `analyze` method runs and produces a structured report.
-   Correct functioning of the caching mechanism.
-   Automated tests for the FastAPI endpoint, including success and error cases.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
