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
        # Fallback prompt if file doesn't exist
        return """
You are a relevance judge. Decide if the provided CONTEXT helps answer the QUESTION.

Rules:
- Output ONLY "relevant" or "irrelevant".
- "relevant" if the context directly supports, defines, describes, or contains facts needed to answer the question.
- Be strict: tangential or generic info ⇒ "irrelevant".

CONTEXT:
{context}

QUESTION:
{question}

Decision:
""".strip()

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
            print(f"Error in relevance checking: {e}")
            return "relevant"  # Default to relevant on error

    return Tool.from_function(
        func=_judge,
        name="ContextRelevanceChecker",
        description="Checks if provided context is relevant to a question. Input can be: 'Context: <context> Question: <question>' or just a question (will assume relevant). Returns 'relevant' or 'irrelevant'."
    )