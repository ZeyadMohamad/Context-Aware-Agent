from langchain.tools import Tool
from langchain.prompts import PromptTemplate
import os
from typing import Any

def _load_prompt() -> str:
    """Load the context splitter prompt from file."""
    prompt_path = os.path.join(os.path.dirname(__file__), '..', 'prompts', 'context_splitter_prompt.txt')
    try:
        with open(prompt_path, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except FileNotFoundError:
        # Fallback prompt if file doesn't exist
        return """
You extract two fields from a user message: CONTEXT and QUESTION.

Rules:
- CONTEXT: only background details, definitions, examples, snippets the user provided.
- QUESTION: the actual question the user wants answered.
- If the message is just a question, CONTEXT should be empty.
- Output exactly in this format (no extra text):
CONTEXT:
<context here>

QUESTION:
<question here>

User Message:
{input}
""".strip()

def build_context_splitter_tool(llm: Any) -> Tool:
    prompt_template = _load_prompt()
    prompt = PromptTemplate.from_template(prompt_template)

    def _split(user_input: str) -> str:
        """
        Returns a formatted string with context and question for easy parsing.
        Agent-friendly output format with strict context validation.
        """
        if not user_input or not user_input.strip():
            return "Context: \nQuestion: "
            
        try:
            # First, do a simple check - if input is just a question (starts with what/how/why/when/where/is/are/do/does)
            # and contains no background info, likely no context
            simple_question_patterns = ["what is", "what are", "how do", "how does", "why", "when", "where", "is", "are", "do", "does"]
            input_lower = user_input.lower().strip()
            
            # Check if it's likely just a simple question
            is_simple_question = any(input_lower.startswith(pattern) for pattern in simple_question_patterns)
            has_background_markers = any(marker in input_lower for marker in [
                "given that", "since", "because", "as we know", "considering that", 
                "is a", "are a", "defined as", "refers to", "means that"
            ])
            
            # If it's a simple question without background markers, skip LLM and return empty context
            if is_simple_question and not has_background_markers and len(user_input.split('.')) <= 1:
                return f"Context: \nQuestion: {user_input.strip()}"
            
            formatted_prompt = prompt.format(input=user_input)
            out = str(llm.invoke(formatted_prompt)).strip()
            
            # Parse the LLM response to extract context and question
            ctx = ""
            q = ""
            if "CONTEXT:" in out and "QUESTION:" in out:
                try:
                    after_ctx = out.split("CONTEXT:", 1)[1]
                    ctx, after_q = after_ctx.split("QUESTION:", 1)
                    q = after_q.strip()
                    ctx = ctx.strip()
                    
                    # Additional validation: if context is just repeating the question or is very short, ignore it
                    if ctx and (len(ctx) < 15 or ctx.lower() in user_input.lower() or user_input.lower() in ctx.lower()):
                        if len(ctx) < len(user_input) * 0.3:  # Context should be substantial
                            ctx = ""
                            
                except Exception:
                    # If parsing fails, treat entire input as question
                    q = user_input
                    ctx = ""
            else:
                # If format not found, treat entire input as question
                q = user_input
                ctx = ""
                
            # Return in a format that's easy for other tools and the agent to use
            return f"Context: {ctx}\nQuestion: {q}"
            
        except Exception as e:
            print(f"Error in context splitting: {e}")
            return f"Context: \nQuestion: {user_input}"

    return Tool.from_function(
        func=_split,
        name="ContextSplitter",
        description="Splits a user message into context and question parts. Returns 'Context: <context>\\nQuestion: <question>' format that other tools can easily parse."
    )
