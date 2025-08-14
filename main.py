"""
Main entry point for the Context-Aware Chatbot.

This script initializes the chatbot and provides options to run it via:
1. Command line interface
2. Gradio web interface
"""

import os
import argparse
from dotenv import load_dotenv

from agent.agent_runner import initialize_llm, build_agent, run_agent_query
from ui.gradio_interface import create_gradio_interface


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
        default=7860,
        help="Port for web interface (default: 7860)"
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
    """Run the chatbot in web mode using Gradio."""
    print(f"\n🌐 Starting Web Interface on port {port}...")
    
    try:
        # Create Gradio interface
        interface = create_gradio_interface(llm)
        
        # Launch the interface
        interface.launch(
            server_port=port,
            share=False,  # Set to True if you want a public link
            show_error=True # Show error messages in the interface
        )
        
    except Exception as e:
        print(f"❌ Error launching web interface: {e}")
        print("💡 Falling back to CLI mode...")
        run_cli_mode(llm)


if __name__ == "__main__":
    main()