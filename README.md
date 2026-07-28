# DECODE AI

**Intelligent Code Review, Explanation and Optimization System**

> Understand. Debug. Optimize.

## About the Project

DECODE AI is an AI-powered developer tool that reviews source code, detects bugs, explains the code in beginner-friendly language and generates an improved version.

DECODE represents:

- **D** – Detect bugs
- **E** – Explain code
- **C** – Correct errors
- **O** – Optimize performance
- **D** – Debug issues
- **E** – Enhance code quality

## Features

- Upload source-code files
- Paste code directly
- Supports Python, Java and JavaScript
- Detects programming language
- Displays line and character counts
- Finds bugs and risky behaviour
- Explains code in simple language
- Generates corrected and optimized code
- Downloads the AI review as a Markdown file
- Never executes the submitted code

## Technologies Used

- Python
- Streamlit
- Gemini API
- OpenAI-compatible Python SDK
- python-dotenv

## Project Structure

```text
DECODE-AI/
├── .venv/
├── app.py
├── code_reviewer.py
├── requirements.txt
├── .env
├── .env.example
├── .gitignore
├── README.md
└── sample_buggy_code.py
```

## Installation

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows:

```bash
.venv\Scripts\activate
```

Install the required libraries:

```bash
pip install -r requirements.txt
```

## Environment Configuration

Create a `.env` file containing:

```env
GEMINI_API_KEY=your_real_api_key
GEMINI_MODEL=gemini-3.6-flash
```

Never upload the `.env` file to GitHub.

## Run the Application

```bash
python -m streamlit run app.py
```

Open the application at:

```text
http://localhost:8501
```

## Security

DECODE AI treats uploaded code as untrusted text and never executes it. API keys are stored locally using environment variables.