from langchain.tools import Tool
from langchain.prompts import PromptTemplate
import os
from typing import Any

def _load_prompt() -> str:
    """Load the context relevance prompt from file."""

    prompt_path = os.path.join(os.path.dirname(__file__), '..', 'prompts', 'context_relevance_prompt.txt')
    
    try:
        with open(prompt_path, 'r', encoding='utf-8') as f:
            return f.read().strip()
        
    except FileNotFoundError:
        return "prompt file not found"

def build_context_relevance_tool(llm: Any) -> Tool:
    prompt_template = _load_prompt()
    tmpl = PromptTemplate.from_template(prompt_template)

    def _judge(payload: str) -> str:
        """
        Expects a string that contains both context and question.
        Can handle various input formats from the agent.
        Returns: "relevant" | "irrelevant"
        """
        try:
            context = ""
            question = ""
            
            # Try to parse different input formats
            if isinstance(payload, dict):
                context = payload.get("context", "").strip()
                question = payload.get("question", "").strip()
            elif isinstance(payload, str):
                payload_str = str(payload).strip()
                
                # Try to parse "Context: ... Question: ..." format
                if "Context:" in payload_str and "Question:" in payload_str:
                    try:
                        parts = payload_str.split("Context:", 1)[1]
                        context_part, question_part = parts.split("Question:", 1)
                        context = context_part.strip()
                        question = question_part.strip()
                    except:
                        # If parsing fails, treat entire input as question
                        question = payload_str
                        context = ""
                else:
                    # If no clear structure, treat as question
                    question = payload_str
                    context = ""
            
            # If no question extracted, return irrelevant
            if not question:
                return "irrelevant"
            
            # If no context, return relevant (assume question is fine as-is)
            if not context:
                return "relevant"
            
            # Use the template with both context and question
            formatted = tmpl.format(context=context, question=question)
            out = str(llm.invoke(formatted)).strip().lower()
            
            if "relevant" in out and "irrelevant" not in out:
                return "relevant"
            elif "irrelevant" in out:
                return "irrelevant"
            else:
                return "relevant"  # Default to relevant if unclear
        
        except Exception as e:
            return "relevant"  # Default to relevant on error

    return Tool.from_function(
        func=_judge,
        name="ContextRelevanceChecker",
        description="""
Use this tool when observation shows "context_provided" from the Context Presence Judge.
؛ass the entire user input to this tool, including both the context and the question.
The output should clearly indicate whether the context is relevant or irrelevant to the question."
 """    
    )