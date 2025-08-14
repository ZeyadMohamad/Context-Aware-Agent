"""Main Agent Runner - Orchestrates the context-aware conversation logic."""

import os
from typing import Any, List
from langchain.agents import initialize_agent, AgentType
from langchain.agents.agent import AgentExecutor
from langchain.tools import Tool
from langchain_community.llms import Ollama
from tools import (
    build_context_presence_tool, 
    build_web_search_tool,
    build_context_relevance_tool,
    build_context_splitter_tool
)


def initialize_llm() -> Any:
    """Initialize the language model (Ollama or other)."""
    try:
        model_name = os.getenv("OLLAMA_MODEL", "llama3")
        llm = Ollama(model=model_name)
        
        # Test the connection
        test_response = llm.invoke("Hello")  # Updated to use invoke
        print(f"✅ LLM initialized successfully: {model_name}")
        return llm
        
    except Exception as e:
        print(f"❌ Error initializing Ollama: {e}")
        print("💡 Make sure Ollama is running and the model is installed")
        print("   Run: ollama serve")
        print("   Run: ollama pull llama3")
        raise


def build_agent(llm: Any) -> AgentExecutor:
    """
    Build the LangChain React Agent with context-aware tools.
    This creates a TRUE AGENT that makes autonomous decisions about tool usage.
    
    Args:
        llm: The language model to use
        
    Returns:
        AgentExecutor: The initialized agent
    """
    # Build tools
    context_judge_tool = build_context_presence_tool(llm)
    web_search_tool = build_web_search_tool()
    relevance_tool = build_context_relevance_tool(llm)
    splitter_tool = build_context_splitter_tool(llm)

    tools = [context_judge_tool, web_search_tool, relevance_tool, splitter_tool]

    # Initialize the agent with autonomous decision-making capabilities
    agent = initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True,  # Show reasoning to verify true decision making
        handle_parsing_errors=True,
        max_iterations=5,  # Increased slightly to allow for autonomous decisions
        early_stopping_method="generate",  # Generate response even if max iterations reached
        return_intermediate_steps=False,
        agent_kwargs={
            "prefix": """You are an intelligent assistant that can make autonomous decisions about which tools to use to answer user questions.

You have access to these tools:
- ContextPresenceJudge: Determine if the user provided sufficient context
- ContextSplitter: Separate background information from the actual question  
- WebSearchTool: Search for information when you need external knowledge
- ContextRelevanceChecker: Check if context is relevant to the question

You should think step by step and decide which tools will help you provide the best answer. You are autonomous - make your own decisions!""",
            "format_instructions": "Use the following format:\n\nThought: I need to think about what the user is asking and which tools might help.\nAction: [tool name]\nAction Input: [input to the tool]\nObservation: [result from tool]\n... (repeat Thought/Action/Action Input/Observation as needed)\nThought: I now have enough information to answer the question.\nFinal Answer: [your comprehensive answer to the user]",
            "suffix": "Begin!\n\nQuestion: {input}\nThought: {agent_scratchpad}"
        }
    )
    
    print("🤖 Initialized autonomous ReAct agent with 4 tools")
    return agent


def run_agent_query(agent: AgentExecutor, user_input: str) -> str:
    """
    Run a query through the agent with true autonomous decision making.
    The agent will decide which tools to use and in what order.
    
    Args:
        agent: The initialized agent
        user_input: User's question/input
        
    Returns:
        str: Agent's response
    """
    try:
        # Create a focused prompt that encourages autonomous tool usage
        agent_prompt = f"""
You are an intelligent assistant. The user asked: "{user_input}"

You have access to these tools and should decide autonomously which ones to use:

🔧 Available Tools:
- ContextPresenceJudge: Check if user provided context/background info
- ContextSplitter: Separate context from question (if input has both)  
- WebSearchTool: Search for information when you need external knowledge
- ContextRelevanceChecker: Verify if context matches the question

🎯 Your Task:
Analyze the user's input and decide which tools will help you provide the best answer. You may use multiple tools or just one - it's your decision based on what the user needs.

Think step by step:
1. Does the user's input need any tool assistance?
2. Which tools would be most helpful?
3. Use them efficiently to gather what you need
4. Provide a comprehensive final answer

Be autonomous - make your own decisions about tool usage!
"""

        # Let the agent make autonomous decisions
        try:
            response = agent.invoke({"input": agent_prompt})
        except Exception as e:
            # Handle specific agent errors gracefully
            error_str = str(e).lower()
            if "none is not a valid tool" in error_str:
                print("⚠️ Agent tried to use invalid tool, providing fallback")
                return "I encountered a tool selection issue. Let me provide a direct answer to your question. Please try asking again if you need more detail."
            elif "maximum iterations" in error_str or "iteration limit" in error_str:
                print("⚠️ Agent reached iteration limit, providing partial response")
                return "I was working on your question but reached my processing limit. Please try rephrasing your question for a complete response."
            else:
                raise e
        
        # Extract the output from the response
        if isinstance(response, dict) and 'output' in response:
            agent_output = response['output']
        else:
            agent_output = str(response)
            
        # Validate response quality
        if not agent_output or len(agent_output.strip()) < 10:
            return "I processed your question but didn't generate a complete response. Please try rephrasing your question."
        
        # Clean up any tool artifacts from the response
        if "Action:" in agent_output or "Observation:" in agent_output:
            # Extract just the final answer if tool traces are present
            lines = agent_output.split('\n')
            final_lines = []
            for line in lines:
                if not line.strip().startswith(('Action:', 'Action Input:', 'Observation:', 'Thought:')):
                    final_lines.append(line)
            cleaned_output = '\n'.join(final_lines).strip()
            if cleaned_output and len(cleaned_output) > 20:
                agent_output = cleaned_output
            
        return agent_output
        
    except Exception as e:
        print(f"Agent error: {e}")
        # Provide helpful error context
        return f"The autonomous agent encountered an issue. Please try rephrasing your question or ask something different."


def run_manual_context_aware_query(user_input: str, llm: Any) -> str:
    """
    A manual implementation of the context-aware workflow that follows your roadmap exactly.
    This demonstrates the ideal workflow without relying on agent decision-making.
    """
    try:
        print(f"🔄 Processing query: {user_input}")
        
        # Build all tools
        context_splitter = build_context_splitter_tool(llm)
        context_judge = build_context_presence_tool(llm)
        web_search = build_web_search_tool()
        relevance_checker = build_context_relevance_tool(llm)
        
        # Step 1: Split the user input into context and question
        print("✂️ Step 1: Splitting context and question...")
        split_result = context_splitter.func(user_input)
        
        # Parse the returned string format "Context: ... Question: ..."
        user_context = ""
        user_question = ""
        if "Context:" in split_result and "Question:" in split_result:
            try:
                parts = split_result.split("Context:", 1)[1]
                context_part, question_part = parts.split("Question:", 1)
                user_context = context_part.strip()
                user_question = question_part.strip()
            except:
                user_question = user_input
        else:
            user_question = user_input
        
        print(f"   Context: '{user_context}'")
        print(f"   Question: '{user_question}'")
        
        # Step 2: Judge if context is sufficient
        print("🕵️ Step 2: Checking if context is sufficient...")
        # If we have extracted context, judge based on the full context + question
        if user_context:
            input_for_judge = f"{user_context} {user_question}"
            context_status = "context_provided"  # We clearly have context
        else:
            # No context extracted, judge the original input
            context_status = context_judge.func(user_input)
        print(f"   Context status: {context_status}")
        
        # Step 3: Search for information if context is missing
        search_results = ""
        final_context = user_context
        
        if context_status == "context_missing" or not user_context:
            print("🌐 Step 3: Searching for missing information...")
            search_query = user_question if user_question else user_input
            search_results = web_search.func(search_query)
            print(f"   Search results length: {len(search_results)} characters")
            
            # Use search results as context if we didn't have any
            if not final_context:
                final_context = search_results
        
        # Step 4: Check relevance of context (if we have any)
        if final_context:
            print("🎯 Step 4: Checking context relevance...")
            # Format the input for relevance checker
            relevance_input = f"Context: {final_context}\nQuestion: {user_question if user_question else user_input}"
            relevance_status = relevance_checker.func(relevance_input)
            print(f"   Relevance status: {relevance_status}")
            
            if relevance_status == "irrelevant":
                final_context = ""  # Discard irrelevant context
        
        # Step 5: Generate final response
        print("🤖 Step 5: Generating final response...")
        if final_context:
            final_prompt = f"""
Based on the following context, please provide a comprehensive answer to the user's question:

Context:
{final_context}

Question: {user_question if user_question else user_input}

Please provide a clear, informative answer that directly addresses the question using the provided context.
"""
        else:
            final_prompt = f"""
Please answer the following question based on your knowledge:

Question: {user_question if user_question else user_input}

Provide a helpful and informative answer. If you need more specific context to give a better answer, please mention what additional information would be helpful.
"""
        
        response = llm.invoke(final_prompt)
        return str(response)
        
    except Exception as e:
        print(f"Error in workflow: {e}")
        return f"I encountered an error while processing your request: {str(e)}"


# Example usage and testing
if __name__ == "__main__":
    print("🚀 Initializing Context-Aware Chatbot...")
    
    try:
        # Initialize LLM
        llm = initialize_llm()
        
        # Test simple approach first
        print("\n" + "="*60)
        print("🧪 TESTING SIMPLE CONTEXT-AWARE APPROACH")
        print("="*60)
        
        test_queries = [
            "What is machine learning?",
            "Tell me how attention mechanisms are used.",
            "Machine learning involves training algorithms on data. What are the main supervised learning algorithms?",
        ]
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n📝 Test Query {i}:")
            print(f"User: {query}")
            print("\n🤖 Response:")
            
            response = run_manual_context_aware_query(query, llm)
            print(response)
            
            print("\n" + "-"*60)
            
        # Test agent approach
        print("\n" + "="*60)
        print("🧪 TESTING AGENT APPROACH")
        print("="*60)
        
        try:
            agent = build_agent(llm)
            
            test_query = "What is LangChain used for?"
            print(f"\n📝 Agent Test Query:")
            print(f"User: {test_query}")
            print("\n🤖 Agent Response:")
            
            response = run_agent_query(agent, test_query)
            print(response)
            
        except Exception as e:
            print(f"❌ Agent approach failed: {e}")
            print("💡 Using simple approach as fallback")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n💡 Troubleshooting Tips:")
        print("1. Make sure Ollama is installed and running")
        print("2. Install the required model: ollama pull llama3")
        print("3. Check that all dependencies are installed")


def run_smart_context_aware_query(user_input: str, llm: Any) -> str:
    """
    A smart implementation that efficiently handles context detection and response generation.
    This version avoids the issues seen in the agent approach.
    """
    try:
        print(f"🔄 Processing query: {user_input}")
        
        # Build tools
        context_splitter = build_context_splitter_tool(llm)
        web_search = build_web_search_tool()
        
        # Step 1: Always split first to understand the input
        print("✂️ Step 1: Analyzing input structure...")
        split_result = context_splitter.func(user_input)
        
        # Parse the result
        user_context = ""
        user_question = ""
        if "Context:" in split_result and "Question:" in split_result:
            try:
                parts = split_result.split("Context:", 1)[1]
                context_part, question_part = parts.split("Question:", 1)
                user_context = context_part.strip()
                user_question = question_part.strip()
            except:
                user_question = user_input
        else:
            user_question = user_input
        
        print(f"   Context found: '{user_context}'")
        print(f"   Question: '{user_question}'")
        
        # Step 2: Smart context decision
        if user_context and len(user_context) > 10:  # Simple but effective check
            print("🎯 Step 2: Context provided - using it directly")
            context_status = "context_provided"
            final_context = user_context
        else:
            print("🌐 Step 2: No context found - searching for information...")
            context_status = "context_missing"
            search_query = user_question if user_question else user_input
            final_context = web_search.func(search_query)
            print(f"   Found information: {len(final_context)} characters")
        
        # Step 3: Generate intelligent response
        print("🤖 Step 3: Generating response...")
        if final_context:
            final_prompt = f"""
Based on the following context, provide a comprehensive and well-structured answer to the user's question.

Context:
{final_context}

Question: {user_question if user_question else user_input}

Instructions:
- Provide a clear, detailed answer that directly addresses the question
- Use the context information to give accurate and relevant details
- Structure your response logically with clear points where appropriate
- Be comprehensive but concise
- If the context doesn't fully address the question, acknowledge that and provide what information you can

Answer:
"""
        else:
            final_prompt = f"""
Please provide a helpful and comprehensive answer to this question based on your knowledge:

Question: {user_question if user_question else user_input}

Instructions:
- Give a detailed, well-structured response
- Include relevant examples or explanations where helpful
- Organize your answer clearly
- Be informative and educational

Answer:
"""
        
        response = llm.invoke(final_prompt)
        return str(response)
        
    except Exception as e:
        print(f"Error in smart workflow: {e}")
        return f"I encountered an error while processing your request: {str(e)}"

