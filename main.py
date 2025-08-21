"""
Main entry point for the Context-Aware Chatbot.

This script initializes the chatbot and provides options to run it via:
1. Command line interface
2. Flask web interface
"""

import os
import argparse
from dotenv import load_dotenv

from agent.agent_runner import initialize_llm, build_agent, run_agent_query
from web.app import create_flask_app


def main():
    """Main function to run the chatbot."""
    # Load environment variables
    load_dotenv()
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Context-Aware Chatbot")
    parser.add_argument(
        "--mode", 
        choices=["cli", "web"], 
        default="web",  # Changed default to web
        help="Run mode: CLI or Web interface (default: web)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=5000,
        help="Port for Flask web interface (default: 5000)"
    )
    
    args = parser.parse_args()
    
    try:
        print("🚀 Initializing Context-Aware Chatbot...")
        
        # Initialize LLM
        llm = initialize_llm()
        
        if args.mode == "cli":
            run_cli_mode(llm)
        else:
            run_web_mode(llm, args.port)
            
    except Exception as e:
        print(f"❌ Error starting chatbot: {e}")
        print("\n💡 Make sure Ollama is installed and running:")
        print("   1. Install: https://ollama.ai/")
        print("   2. Run: ollama serve")
        print("   3. Install model: ollama pull llama3")


def run_cli_mode(llm):
    """Run the chatbot in CLI mode."""
    print("\n🤖 Starting CLI Mode...")
    print("Type 'quit' or 'exit' to stop the chatbot")
    print("="*60)
    
    # Build agent
    agent = build_agent(llm)
    
    while True:
        try:
            user_input = input("\n👤 You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Goodbye!")
                break
                
            if not user_input:
                continue
                
            print("\n🤖 Assistant:")
            response = run_agent_query(agent, user_input)
            print(response)
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")


def run_web_mode(llm, port):
    """Run the chatbot in web mode using Flask."""
    print(f"\n🌐 Starting Flask Web Interface on port {port}...")
    
    try:
        # Create Flask app
        flask_app = create_flask_app(llm)
        
        # Launch the Flask server
        print(f"🚀 Server starting at http://localhost:{port}")
        print("📱 Open your browser and navigate to the URL above")
        print("🔄 Press Ctrl+C to stop the server")
        
        flask_app.run(host='127.0.0.1', port=port, debug=False)
        
    except Exception as e:
        print(f"❌ Error launching Flask interface: {e}")
        print("💡 Falling back to CLI mode...")
        run_cli_mode(llm)


if __name__ == "__main__":
    main()