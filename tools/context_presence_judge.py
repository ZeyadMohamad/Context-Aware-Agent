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
        return "prompt file not found"


def judge_context(user_input: str, llm: Any, prompt: PromptTemplate) -> str:
    """Judge if the user input contains sufficient context."""
    try:
        if not user_input or not user_input.strip():
            return "context_missing"
        
        # Create the prompt
        formatted_prompt = prompt.format(input=user_input)
        result = llm.invoke(formatted_prompt)
        result = str(result).strip().lower()
        
        if "context_provided" in result:
            return "context_provided"
        elif "context_missing" in result:
            return "context_missing"
        else:
            return "context_missing"
            
    except Exception as e:
        return "context_missing"


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
    
    # Create a wrapper function that captures llm and prompt
    def judge_wrapper(user_input: str) -> str:
        return judge_context(user_input, llm, prompt)
    
    return Tool.from_function(
        func=judge_wrapper,
        name="ContextPresenceJudge",
        description="""
Use this tool first to determine if the user's input contains any explicit context (background information, previous conversation details, or supporting text) in addition to the main question.
This tool does not judge whether the context is correct or useful — only whether it exists.
"""
    )