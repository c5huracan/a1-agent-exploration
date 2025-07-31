# A1 Agent - DSPy Optimized Security Analyzer

This project is a Python-based implementation of the AI agent methodology described in the paper "AI Agent Smart Contract Exploit Generation" (arXiv:2507.05558v2). This specific implementation is optimized using the **DSPy framework** to create a more robust and modular system for smart contract security analysis.

The primary focus is on **defensive security research and education**, adapting the paper's offensive techniques to proactively identify and understand vulnerabilities.

## Key Features

- **DSPy-Optimized:** Leverages DSPy for building and optimizing the AI agent, using signatures and modules for clear, composable, and optimizable components.
- **Iterative Analysis:** The agent performs a multi-step analysis, selecting the most appropriate tools at each stage to build a comprehensive picture of a contract's security posture.
- **Multi-LLM Support:** Easily configurable to use different Large Language Models (LLMs) like Anthropic's Claude or Google's Gemini.
- **Modular Tooling:** Integrates multiple analysis tools that can be individually selected and executed by the agent based on the analysis context.
- **Educational Focus:** Designed to be a learning resource for understanding how AI agents can be applied to automated security analysis.

## Project Structure

- `a1_dspy_agent.py`: The core implementation of the DSPy-based A1 agent, including all DSPy signatures, modules, and the main agent logic.
- `test_a1_dspy.py`: The primary test runner for the agent. It can be used to test the system's architecture or run a full integration test against sample contracts.
- `A1_SPEC.md`: A detailed technical specification comparing this implementation to the one described in the original research paper.
- `RESEARCH_PLAN.md`: Outlines the broader research goals and the multi-worktree strategy used for parallel development.

## Setup and Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd a1-agent-exploration/worktrees/miprov2-optimized
    ```

2.  **Install dependencies:**
    It is recommended to use a virtual environment.
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```

## How to Run

The primary way to interact with this project is by running the test script, which analyzes several example smart contracts.

### 1. Configure Environment Variables

You must configure the environment variables to specify which LLM to use and to provide the necessary API keys.

-   **Set the Model:** Choose between `claude` and `gemini`.
    ```bash
    export DSPY_MODEL="gemini" # or "claude"
    ```

-   **Set the API Key:** Provide the key for the chosen model.
    -   For Gemini:
        ```bash
        export GEMINI_API_KEY="YOUR_GEMINI_API_KEY"
        ```
    -   For Claude:
        ```bash
        export ANTHROPIC_API_KEY="YOUR_ANTHROPIC_API_KEY"
        ```

### 2. Run the Tests

Execute the test runner script from the `miprov2-optimized` directory:

```bash
python3 test_a1_dspy.py
```

The script will automatically detect the environment variables and run a full integration test. If no API key is found, it will fall back to a simple architecture test that validates the code structure without making live API calls.

### Example Output (Success)

```
🔑 API key found - running full integration test
🔬 Testing A1 DSPy Agent
========================================
🔧 Configuring DSPy LM...
✅ Configuring DSPy with Google Gemini (gemini-1.5-flash-latest)...
🤖 Initializing A1 DSPy Agent...

📋 Testing with VulnerableDeFiPool (0x123)
------------------------------
✅ Analysis completed:
   - Tools used: ['contract_analysis', 'deployment_context']
   - Vulnerabilities found: 3
   - Risk score: 8.5/10.0
   - Confidence: 0.85
✅ Critical reentrancy vulnerability detected!

...

🎯 DSPy Agent Test: SUCCESS
```
