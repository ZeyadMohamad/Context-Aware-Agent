# Context-Aware Chatbot

A smart chatbot implementation that understands and responds to user questions based on provided or retrieved context. Unlike simple chatbots, this agent is aware of whether the user gave it enough information and can take autonomous steps to improve its answers.

## 🎨 **Beautiful Web Interface**

The chatbot features a modern, responsive Flask web interface with:
- 🎨 **Modern Design**: Clean, professional UI with smooth animations
- 📱 **Responsive Layout**: Works perfectly on desktop, tablet, and mobile
- 🤖 **Real-time Chat**: Interactive messaging with typing indicators
- 🧠 **Agent Status**: Visual indicators showing autonomous tool selection
- 💡 **Example Questions**: Quick-start buttons for testing different scenarios

## 🧠 How It Works

At the core of this system is a **LangChain React Agent** that doesn't follow hardcoded rules, but instead decides which tools to use based on what the user says.

The chatbot:
1. **Judges if the user provided context**
2. **Finds missing context using web search**, if needed
3. **Checks if the provided context is relevant**
4. **Separates the context from the actual question**
5. **Finally, answers the question using everything above**

## 🧰 Core Tools

| Tool | Role |
| --- | --- |
| 🕵️ Context Presence Judge | Determines whether the user gave enough background/context |
| 🌐 Web Search Tool | Searches online if context is missing |
| 🎯 Context Relevance Checker | Checks if the context matches the question |
| ✂️ Context Splitter | Separates background info from the user's actual question |

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Ollama (for local LLM)

### Installation

1. **Clone the repository**:
   ```bash
   git clone <your-repo-url>
   cd context-aware-chatbot
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Install and start Ollama**:
   ```bash
   # Install Ollama from https://ollama.ai/
   ollama serve
   ollama pull llama3
   ```

4. **Run the chatbot**:
   ```bash
   # Beautiful Flask web interface (recommended)
   python main.py --mode web
   
   # Command line interface
   python main.py --mode cli
   
   # Custom port for web interface
   python main.py --mode web --port 8080
   ```

## 🧪 Example Usage

**Input**: `"What is machine learning?"`
- 🕵️ Context Judge: Context missing
- 🌐 Web Search: Triggered
- 🤖 Response: Comprehensive answer with searched information

**Input**: `"Machine learning is a subset of AI. What are the main types?"`
- 🕵️ Context Judge: Context provided
- 🎯 Direct processing using provided context
- 🤖 Response: Answer based on given context

## 📁 Project Structure

```
context-aware-chatbot/
├── agent/                  # Core agent logic
│   └── agent_runner.py    # LangChain agent implementation
├── tools/                 # Context-aware tools
│   ├── context_presence_judge.py
│   ├── web_search_tool.py
│   ├── context_relevance_checker.py
│   └── context_splitter.py
├── prompts/               # LLM prompts
├── web/                   # Flask web interface
│   ├── app.py            # Main Flask application
│   ├── templates/        # HTML templates
│   │   └── chat.html     # Beautiful chat interface
│   └── static/           # CSS, JS, and assets
│       ├── css/style.css # Modern styling
│       └── js/chat.js    # Interactive chat functionality
├── tests/                 # Unit and integration tests
├── main.py               # Application entry point
└── requirements.txt      # Dependencies
```

## 🔧 Configuration

### Environment Variables (Optional)
Create a `.env` file:
```bash
OLLAMA_MODEL=llama3
TAVILY_API_KEY=your_tavily_key  # Optional: for enhanced web search
USE_SIMULATED_SEARCH=true      # Use Wikipedia fallback
```

## 🧪 Testing

```bash
# Run unit tests
python tests/test_tools.py

# Run integration tests  
python tests/test_integration.py

# Test fixes and improvements
python test_agent_fixes.py
```

## 💡 Why It's Different

- **Learning-based**, not rule-based
- **Smart decisions dynamically** (not scripted)
- **Open-source tools** (LangChain, Flask, Ollama)
- **Human-like reasoning**:
  - "Did you give me what I need to answer?"
  - "If not, let me look it up."
  - "Wait… does that even relate?"
  - "Okay, now let me answer properly."

## 🎯 Architecture

The system implements a **ReAct (Reasoning + Acting) pattern** where the agent:
1. **Reasons** about the user's input
2. **Acts** by choosing appropriate tools
3. **Observes** the results
4. **Repeats** until it can provide a comprehensive answer

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built with [LangChain](https://langchain.com/) for agent orchestration
- Beautiful web UI powered by [Flask](https://flask.palletsprojects.com/) with modern HTML/CSS/JS
- Local LLM support via [Ollama](https://ollama.ai/)
- Web search capabilities through Wikipedia and Tavily APIs
