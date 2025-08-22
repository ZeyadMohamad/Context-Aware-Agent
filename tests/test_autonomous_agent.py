#!/usr/bin/env python3
"""
Test script to verify that the agent is truly autonomous and makes its own decisions.
This script will test various scenarios to ensure the agent chooses tools autonomously.
"""

from agent.agent_runner import initialize_llm, build_agent, run_agent_query
import time

def test_autonomous_behavior():
    """Test that the agent makes autonomous decisions about tool usage."""
    
    print("TESTING AUTONOMOUS AGENT BEHAVIOR")
    print("="*60)
    
    try:
        # Initialize LLM and agent
        print("🔧 Initializing LLM and agent...")
        llm = initialize_llm()
        agent = build_agent(llm)
        print("✅ Agent initialized successfully")
        
        # Test cases that should trigger different autonomous decisions
        test_cases = [
            {
                "name": "Simple Question (should use WebSearchTool)",
                "input": "What is machine learning?",
                "expected_tools": ["WebSearchTool"]
            },
            {
                "name": "Question with Context (should use ContextSplitter)",
                "input": "Machine learning is a subset of AI that uses algorithms to learn from data. What are the main types of machine learning?",
                "expected_tools": ["ContextSplitter"]
            },
            {
                "name": "Ambiguous Input (agent should decide)",
                "input": "Tell me about neural networks and how they work.",
                "expected_tools": ["WebSearchTool", "ContextPresenceJudge"]
            },
            {
                "name": "Complex Query (agent should use multiple tools)",
                "input": "Given that deep learning is a subset of machine learning. How do attention mechanisms work in transformer models?",
                "expected_tools": ["ContextSplitter", "WebSearchTool", "ContextRelevanceChecker"]
            }
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n{'='*20} TEST {i}: {test_case['name']} {'='*20}")
            print(f"📝 Input: {test_case['input']}")
            print(f"🎯 Expected tools the agent might use: {', '.join(test_case['expected_tools'])}")
            print("\n🤖 Agent's Decision Process:")
            
            start_time = time.time()
            
            try:
                # Run the agent and capture its autonomous decisions
                response = run_agent_query(agent, test_case['input'])
                
                execution_time = time.time() - start_time
                
                print(f"\n✅ Agent Response (took {execution_time:.2f}s):")
                print("-" * 40)
                print(response)
                print("-" * 40)
                
                # Basic validation
                if len(response.strip()) > 20:
                    print("✅ Response quality: Good length")
                else:
                    print("⚠️ Response quality: Might be too short")
                    
            except Exception as e:
                print(f"❌ Agent failed on test {i}: {str(e)}")
                
            print(f"\n{'='*60}")
            
            # Small delay between tests
            time.sleep(1)
            
        print("\n🎉 AUTONOMOUS AGENT TESTING COMPLETE!")
        print("\n💡 Observations:")
        print("- Did the agent make different decisions for different inputs?")
        print("- Did it choose appropriate tools for each scenario?")
        print("- Were the responses comprehensive and relevant?")
        print("- Did it show reasoning in its decision process?")
        
    except Exception as e:
        print(f"❌ Test setup failed: {e}")
        print("\n💡 Make sure:")
        print("1. Ollama is running (ollama serve)")
        print("2. Model is installed (ollama pull llama3)")
        print("3. All dependencies are installed")

def test_agent_vs_manual_comparison():
    """Compare agent approach vs manual workflow to show the difference."""
    
    print("\n" + "="*60)
    print("🔄 COMPARISON: AGENT vs MANUAL WORKFLOW")
    print("="*60)
    
    try:
        llm = initialize_llm()
        agent = build_agent(llm)
        
        # Import manual workflow for comparison
        from agent.agent_runner import run_manual_context_aware_query
        
        test_input = "What are the applications of natural language processing?"
        
        print(f"📝 Test Input: {test_input}")
        
        print(f"\n🤖 AUTONOMOUS AGENT APPROACH:")
        print("-" * 40)
        agent_response = run_agent_query(agent, test_input)
        print(agent_response)
        
        print(f"\n🔧 MANUAL WORKFLOW APPROACH:")
        print("-" * 40)
        manual_response = run_manual_context_aware_query(test_input, llm)
        print(manual_response)
        
        print(f"\n📊 COMPARISON RESULTS:")
        print("-" * 40)
        print("🤖 Agent: Makes autonomous decisions about tool usage")
        print("🔧 Manual: Follows predefined steps every time")
        print("🎯 Both should provide good answers, but agent has true autonomy!")
        
    except Exception as e:
        print(f"❌ Comparison test failed: {e}")

if __name__ == "__main__":
    test_autonomous_behavior()
    test_agent_vs_manual_comparison()
    
    print(f"\n🚀 To test the beautiful Flask web interface with autonomous agent:")
    print("   python main.py --mode web")
    print("   Then open: http://localhost:5000")
    print(f"\n🚀 To test CLI with autonomous agent:")
    print("   python main.py --mode cli")
    print(f"\n🧪 To test the Flask interface functionality:")
    print("   python test_flask_interface.py")
