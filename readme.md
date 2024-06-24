# AI Assistant with Mixture of Agents and Tree of Thought

This project implements an AI assistant using a combination of the Mixture of Agents (MoA) approach and the Tree of Thought (ToT) algorithm. It uses the Claude API from Anthropic to generate responses and integrates with the Tavily API for internet search capabilities.

## Table of Contents
1. [Features](#features)
2. [How It Works](#how-it-works)
3. [Architecture Diagram](#architecture-diagram)
4. [Prerequisites](#prerequisites)
5. [Installation](#installation)
6. [Usage](#usage)
7. [Project Structure](#project-structure)
8. [Customization](#customization)
9. [Contributing](#contributing)
10. [License](#license)

## Features

- Tree of Thought algorithm for structured problem-solving
- Mixture of Agents approach for diverse perspective generation
- Integration with Tavily API for internet search capabilities
- Rate limiting and error handling for robust API usage
- Streamlit-based user interface for easy interaction
- Modular code structure for easy maintenance and extensibility

## How It Works

The AI Assistant uses a combination of three main concepts: Mixture of Agents (MoA), Tree of Thought (ToT), and Internet Search.

1. **Mixture of Agents (MoA)**:
   - The assistant consists of multiple layers of agents.
   - Each layer contains several individual agents.
   - The input is processed through these layers sequentially.
   - In each layer, multiple agents process the input independently, allowing for diverse perspectives.
   - After all agents in a layer have processed the input, their outputs are synthesized into a single coherent response.
   - This synthesized output becomes the input for the next layer.

2. **Tree of Thought (ToT)**:
   - Each individual agent uses the Tree of Thought algorithm to process its input.
   - ToT generates multiple "thoughts" or potential solution paths.
   - These thoughts are evaluated and the most promising ones are explored further.
   - This process continues up to a maximum depth, creating a tree-like structure of thoughts.
   - The most promising path(s) from this tree are used to generate the agent's output.

3. **Internet Search**:
   - The system integrates with the Tavily API to perform internet searches.
   - This allows the AI assistant to access up-to-date information and provide more accurate responses.
   - Search results are incorporated into the agent's thought process and final output.

4. **Overall Process**:
   - User input is received through the Streamlit interface.
   - The input is passed to the first layer of agents in the MoA.
   - Each agent in the layer processes the input using ToT and may perform internet searches if needed.
   - The outputs from all agents in the layer are synthesized.
   - This synthesized output is passed to the next layer.
   - The process continues through all layers.
   - The final synthesized output from the last layer is presented to the user as the assistant's response.

## Architecture Diagram

Here's a simplified diagram of the system architecture:

```
User Input
    |
    v
+-------------------+
|  Mixture of Agents|
|  +-------------+  |
|  | Layer 1     |  |
|  |  +--------+ |  |
|  |  | Agent 1| |  |
|  |  |  (ToT) | |  |
|  |  +--------+ |  |
|  |  +--------+ |  |
|  |  | Agent 2| |  |
|  |  |  (ToT) | |  |
|  |  +--------+ |  |
|  +-------------+  |
|         |         |
|         v         |
|  +-------------+  |
|  | Layer 2     |  |
|  |  +--------+ |  |
|  |  | Agent 1| |  |
|  |  |  (ToT) | |  |
|  |  +--------+ |  |
|  |  +--------+ |  |
|  |  | Agent 2| |  |
|  |  |  (ToT) | |  |
|  |  +--------+ |  |
|  +-------------+  |
|         |         |
|         v         |
|     (More layers) |
+-------------------+
    |
    v
Final Output
```

In this diagram:
- Each layer contains multiple agents.
- Each agent uses the Tree of Thought (ToT) algorithm.
- Outputs from agents in one layer are synthesized and passed to the next layer.
- The process continues through multiple layers until a final output is produced.

## Prerequisites

- Python 3.7+
- Anthropic API key
- Tavily API key

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/ai-assistant-moa-tot.git
   cd ai-assistant-moa-tot
   ```

2. Install the required packages:
   ```
   pip install anthropic streamlit tenacity ratelimit tavily python-dotenv
   ```

3. Set up your API keys in a `.env` file:
   ```
   ANTHROPIC_API_KEY=your_anthropic_api_key_here
   TAVILY_API_KEY=your_tavily_api_key_here
   ```

## Usage

### Running the Streamlit App

To start the Streamlit user interface:

```
streamlit run main.py
```

This will open a web browser where you can interact with the AI assistant.

### Running Tests

To run the test suite:

```
pytest
```

## Project Structure

- `thought.py`: Defines the Thought class
- `tree_of_thought.py`: Implements the Tree of Thought algorithm
- `agent.py`: Defines the Agent class with internet search capabilities
- `mixture_of_agents.py`: Implements the Mixture of Agents approach
- `ai_assistant.py`: Main AI Assistant class
- `api_utils.py`: Utility functions for API calls and rate limiting
- `main.py`: Streamlit user interface
- `test_internet_search.py`: Test suite for internet search functionality
- `test_tavily_integration.py`: Test suite for Tavily API integration
- `test_assistant.py`: Test suite for the AI assistant

## Customization

- To modify the Thought structure: Edit `thought.py`
- To change the Tree of Thought algorithm: Edit `tree_of_thought.py`
- To adjust individual agent behavior: Edit `agent.py`
- To modify how agents work together: Edit `mixture_of_agents.py`
- To change the main assistant logic: Edit `ai_assistant.py`
- To modify API call handling or rate limiting: Edit `api_utils.py`
- To change the user interface: Edit `main.py`
- To modify or add tests: Edit `test_internet_search.py`, `test_tavily_integration.py`, or `test_assistant.py`

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
