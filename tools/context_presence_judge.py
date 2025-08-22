"""Context Presence Judge Tool - Determines if user input contains sufficient context."""

from langchain.tools import Tool
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
import os
from typing import Any


def load_context_judge_prompt() -> str:
    """Load the context judge prompt from file."""
    prompt_path = os.path.join(os.path.dirname(__file__), '..', 'prompts', 'context_judge_prompt.txt')
    
    try:
        with open(prompt_path, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except FileNotFoundError:
        # Fallback prompt if file doesn't exist
        return """
You are a context analyzer. Determine if the user's message includes background context or is just a direct question.

Rules:
- If the message includes background information, output "context_provided"
- If the message is just a direct question without context, output "context_missing"

User Message: {input}

Analysis: Let me check if this message contains sufficient context...

Decision:
""".strip()


def build_context_presence_tool(llm: Any) -> Tool:
    """
    Build a LangChain Tool that judges whether user input contains sufficient context.
    
    Args:
        llm: The language model to use for context judgment
        
    Returns:
        Tool: A LangChain Tool object for context presence detection
    """
    prompt_template = load_context_judge_prompt()
    prompt = PromptTemplate.from_template(prompt_template)
    
    # Use the modern approach with invoke
    def judge_context(user_input: str) -> str:
        """Judge if the user input contains sufficient context."""
        try:
            if not user_input or not user_input.strip():
                return "context_missing"
            
            # Create the prompt
            formatted_prompt = prompt.format(input=user_input)
            
            # Use invoke instead of run
            result = llm.invoke(formatted_prompt)
            
            # Clean up the response and extract the decision
            result = str(result).strip().lower()
            
            if "context_provided" in result:
                return "context_provided"
            elif "context_missing" in result:
                return "context_missing"
            else:
                # Default to missing if unclear
                return "context_missing"
                
        except Exception as e:
            return "context_missing"
    
    return Tool.from_function(
        func=judge_context,
        name="ContextPresenceJudge",
        description="Analyzes user input to determine if sufficient context is provided for answering the question. Returns 'context_provided' or 'context_missing'."
    )


# Example usage and testing
if __name__ == "__main__":
    from langchain_ollama import OllamaLLM
    
    # Initialize LLM (adjust model name as needed)
    llm = OllamaLLM(model="llama3")
    
    # Build the tool
    context_tool = build_context_presence_tool(llm)
    
    # Test cases - silent testing
    test_inputs = [
        "What is machine learning?",
        "Machine learning is a subset of AI that uses algorithms to learn from data. What are the main types of machine learning?",
        "How does attention work in transformers?",
    ]
    
    for test_input in test_inputs:
        context_tool.func(test_input)  # Run silently
