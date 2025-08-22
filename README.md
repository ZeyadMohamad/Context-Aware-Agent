# Autonomous Context-Aware Agent
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
[![LangChain](https://img.shields.io/badge/LangChain-1C3C3C?logo=langchain&logoColor=white)](https://www.langchain.com/)&nbsp;&nbsp;&nbsp;
[![Ollama](https://img.shields.io/badge/Ollama-000000?logo=llama&logoColor=white)](https://ollama.ai/)
[![Flask](https://img.shields.io/badge/Flask-000000?logo=flask&logoColor=white)](https://flask.palletsprojects.com/)&nbsp;&nbsp;&nbsp;
[![HTML5](https://img.shields.io/badge/HTML5-E34F26?logo=html5&logoColor=white)](https://developer.mozilla.org/en-US/docs/Web/HTML)&nbsp;&nbsp;&nbsp;
[![CSS3](https://img.shields.io/badge/CSS3-1572B6?logo=css3&logoColor=white)](https://developer.mozilla.org/docs/Web/CSS)&nbsp;&nbsp;&nbsp;
[![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white)](https://www.python.org/)&nbsp;&nbsp;&nbsp;
[![Requests](https://img.shields.io/badge/Requests-FF6F00?logo=python&logoColor=white)](https://requests.readthedocs.io/)&nbsp;&nbsp;&nbsp;
[![Wikipedia](https://img.shields.io/badge/Wikipedia-000000?logo=wikipedia&logoColor=white)](https://github.com/goldsmith/Wikipedia)&nbsp;&nbsp;&nbsp;
[![pytest](https://img.shields.io/badge/pytest-0A9EDC?logo=pytest&logoColor=white)](https://pytest.org/)

A sophisticated conversational AI system that uses an autonomous ReAct Agent to intelligently decide which tools to use for answering user questions. The system provides context-aware responses through intelligent tool selection and multi-layered fallback mechanisms.

## 🚀 Features

- **Autonomous Agent Decision Making**: Uses LangChain ReAct agent that independently chooses which tools to use
- **Context-Aware Processing**: Intelligent context detection, splitting, and relevance checking
- **Web Search Integration**: Automatic web search when external knowledge is needed
- **Multi-layered Fallbacks**: Robust system with manual and smart workflow backups
- **Web Interface**: Clean, responsive chat interface with session management
- **CLI Support**: Command-line interface for direct interaction

## 🤖 How It Works

### 1. Autonomous Agent Architecture
The system uses a **LangChain ReAct Agent** that makes independent decisions about tool usage:

```python
# The agent autonomously decides which tools to use
agent = initialize_agent(
    tools = [context_judge, web_search, relevance_checker, context_splitter],
    llm = llm,
    agent = AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose = True  # Shows the agent's reasoning process
)
```

### 2. Available Tools
| Tool | Role |
| --- | --- |
| 🕵️ Context Presence Judge | Determines whether the user gave enough background/context |
| 🌐 Web Search Tool | Searches online if context is missing |
| 🎯 Context Relevance Checker | Checks if the context matches the question |
| ✂️ Context Splitter | Separates background info from the user's actual question |

### 3. Multi-layered Fallback System
1. **Primary**: Autonomous Agent (ReAct-based decision making)
2. **Fallback 1**: Smart Context-Aware Workflow
3. **Fallback 2**: Manual Context Processing
4. **Final**: Direct LLM response

### 4. Example Agent Workflow
```
User: "Machine learning is a subset of AI. What are the main types?"

Agent Reasoning:
Thought: I need to check if context is provided
Action: ContextPresenceJudge
Observation: context_provided

Thought: Let me separate the context from the question
Action: ContextSplitter  
Observation: Context: ML is subset of AI, Question: What are main types?

Thought: I should verify the context is relevant
Action: ContextRelevanceChecker
Observation: relevant

Final Answer: Based on the context, the main types of machine learning 
algorithms are supervised learning, unsupervised learning, and 
reinforcement learning.
```
<br>

## 🏗️ Project Structure

```
project_directory/
├── agent/
│   └── agent_runner.py         # Main agent orchestration and workflows
├── tools/
│   ├── __init__.py             # Tool imports and exports
│   ├── context_presence.py     # Context detection tool
│   ├── context_splitter.py     # Context/question separation tool
│   ├── context_relevance.py    # Context relevance checker
│   └── web_search.py           # Web search functionality
├── web/
│   ├── app.py                  # Flask web application
│   ├── templates/
│   │   └── chat.html           # Chat interface template
│   └── static/
│       └── css/
│           └── style.css       # Styling for web interface
├── tests/
│   ├── test_integration.py     # Integration tests
│   ├── test_flask_interface.py # Web interface tests
│   └── test_autonomous_agent.py # Agent functionality tests
├── main.py                     # Main entry point
├── README.md                   # This file
└── requirements.txt            # Text file containing the used packages and dependencies
```

## 🛠️ Installation

### Prerequisites
- Python 3.8+
- Ollama (for local LLM)
- Required Python packages (see installation steps)

### Setup Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/ZeyadMohamad/Context-Aware-Agent/
   cd "project_directory"
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install and configure Ollama**
   ```bash
   # Install Ollama (visit https://ollama.ai for platform-specific instructions)
   # Pull a model (e.g., llama3)
   ollama pull llama3
   ```

4. **Set environment variables** (optional)
   ```bash
   # Create .env file
   echo "OLLAMA_MODEL=llama3" > .env
   ```

## 🚀 Usage

### Web Interface (Recommended)
```bash
python main.py --web
```
Then open your browser to `http://localhost:5000`

### Command Line Interface
```bash
python main.py --cli
```

### Default Mode (Web Interface)
```bash
python main.py
```



## 🧪 Testing

Run the comprehensive test suite:

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test files
python tests/test_integration.py
python tests/test_autonomous_agent.py
python tests/test_flask_interface.py
```

## 🌐 Web Interface Features

- **Session-based Chat History**: Conversations persist during browser session
- **Responsive Design**: Works on desktop and mobile devices
- **Real-time Processing**: Live indication of agent activity
- **Clear Chat Function**: Reset conversation history
- **Health Check Endpoint**: `/health` for system monitoring

## 📊 System Monitoring

The system provides verbose output showing:
- Agent reasoning process ("Thought", "Action", "Observation")
- Tool selection decisions
- Response processing steps
- Fallback system activation

## 🔧 Configuration Options

### Environment Variables
```bash
OLLAMA_MODEL = llama3        # Ollama model name
FLASK_DEBUG = True           # Enable Flask debug mode
FLASK_PORT = 5000           # Web server port
```

### Agent Parameters
- `max_iterations=5`: Maximum reasoning steps
- `verbose=True`: Show agent reasoning
- `handle_parsing_errors=True`: Robust error handling

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Commit changes (`git commit -am 'Add new feature'`)
4. Push to branch (`git push origin feature/new-feature`)
5. Create a Pull Request

## 🐛 Troubleshooting

### Common Issues

**Agent not making autonomous decisions:**
- Check that `verbose=True` is set to see reasoning
- Ensure Ollama is running (`ollama serve`)
- Verify model is available (`ollama list`)

**Web interface not loading:**
- Check that Flask is running on correct port
- Verify browser is accessing `http://localhost:5000`
- Check console for JavaScript errors

**Empty or incomplete responses:**
- Check terminal output for agent reasoning
- Verify all tools are properly initialized
- Test with simpler questions first

### Debug Mode
Run with debug output to see detailed processing:
```bash
python main.py --web --debug
```

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built with [LangChain](https://langchain.com) for agent orchestration
- Uses [Ollama](https://ollama.ai) for local LLM inference  
- Web interface powered by [Flask](https://flask.palletsprojects.com/)
- Styling with modern CSS and responsive design