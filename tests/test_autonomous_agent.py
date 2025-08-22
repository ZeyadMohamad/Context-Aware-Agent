#!/usr/bin/env python3
"""
Test script to verify that the agent is truly autonomous and makes its own decisions.
This script will test various scenarios to ensure the agent chooses tools autonomously.
"""

from agent.agent_runner import initialize_llm, build_agent, run_agent_query
import time

def test_autonomous_behavior():
    """Test that the agent makes autonomous decisions about tool usage."""
    
    try:
        # Initialize LLM and agent
        llm = initialize_llm()
        agent = build_agent(llm)
        
        # Test cases that should trigger different autonomous decisions
        test_cases = [
            {
                "name": "Simple Question",
                "input": "What is machine learning?",
                "expected_tools": ["WebSearchTool"]
            },
            {
                "name": "Question with Context",
                "input": "Machine learning is a subset of AI that uses algorithms to learn from data. What are the main types of machine learning?",
                "expected_tools": ["ContextSplitter"]
            },
            {
                "name": "Ambiguous Input",
                "input": "Tell me about neural networks and how they work.",
                "expected_tools": ["WebSearchTool", "ContextPresenceJudge"]
            },
            {
                "name": "Complex Query",
                "input": "Given that deep learning is a subset of machine learning. How do attention mechanisms work in transformer models?",
                "expected_tools": ["ContextSplitter", "WebSearchTool", "ContextRelevanceChecker"]
            }
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            start_time = time.time()
            
            try:
                # Run the agent and capture its autonomous decisions
                response = run_agent_query(agent, test_case['input'])
                execution_time = time.time() - start_time
                
            except Exception as e:
                print(f"Agent failed on test {i}: {str(e)}")
            
            # Small delay between tests
            time.sleep(1)
        
    except Exception as e:
        print(f"Test setup failed: {e}")
        print("Make sure:")
        print("1. Ollama is running (ollama serve)")
        print("2. Model is installed (ollama pull llama3)")
        print("3. All dependencies are installed")

def test_agent_vs_manual_comparison():
    """Compare agent approach vs manual workflow to show the difference."""
    
    try:
        llm = initialize_llm()
        agent = build_agent(llm)
        
        # Import manual workflow for comparison
        from agent.agent_runner import run_manual_context_aware_query
        
        test_input = "What are the applications of natural language processing?"
        
        agent_response = run_agent_query(agent, test_input)
        manual_response = run_manual_context_aware_query(test_input, llm)
        
    except Exception as e:
        print(f"Comparison test failed: {e}")

if __name__ == "__main__":
    test_autonomous_behavior()
    test_agent_vs_manual_comparison()
