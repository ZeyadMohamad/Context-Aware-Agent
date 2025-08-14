"""Gradio Interface for the Context-Aware Chatbot."""

import gradio as gr
from typing import Any, List, Tuple
from agent.agent_runner import build_agent, run_agent_query, run_manual_context_aware_query, run_smart_context_aware_query


def create_gradio_interface(llm: Any) -> gr.Interface:
    """
    Create a Gradio interface for the chatbot.
    
    Args:
        llm: The initialized language model
        
    Returns:
        gr.Interface: The Gradio interface
    """
    
    def chat_function(message: str, history: List[List[str]]) -> Tuple[str, List[List[str]]]:
        """Process chat message through the agent."""
        try:
            if not message.strip():
                return "", history
                
            print(f"🔄 Processing: {message}")
            
            # Use AGENT as primary approach (true autonomous decision making)
            try:
                print("🤖 Using autonomous ReAct agent (primary approach)...")
                agent = build_agent(llm)
                response = run_agent_query(agent, message)
                
                # Validate agent response quality
                if response and len(response.strip()) > 20 and "error" not in response.lower() and "maximum iterations" not in response.lower():
                    print("✅ Autonomous agent completed successfully")
                else:
                    raise Exception("Agent response insufficient or hit iteration limit")
                    
            except Exception as e:
                print(f"🔄 Agent failed ({str(e)[:50]}...), trying smart workflow")
                # Fallback to smart workflow
                try:
                    response = run_smart_context_aware_query(message, llm)
                    print("✅ Used smart workflow as fallback")
                    
                except Exception as e2:
                    print(f"🔄 Smart workflow also failed, using manual workflow")
                    # Final fallback to manual workflow
                    try:
                        response = run_manual_context_aware_query(message, llm)
                        print("✅ Used manual workflow as final fallback")
                    except Exception as e3:
                        print(f"❌ All approaches failed: {e3}")
                        response = f"I apologize, but I encountered an error processing your request. Please try rephrasing your question."
            
            # Update history
            history.append([message, response])
            return "", history
            
        except Exception as e:
            error_response = f"❌ Error: {str(e)}"
            history.append([message, error_response])
            return "", history
    
    # Create the chat interface
    with gr.Blocks(
        title="🤖 Context-Aware Chatbot",
        theme=gr.themes.Soft()
    ) as interface:
        
        gr.Markdown("""
        # 🤖 Context-Aware Chatbot with Autonomous Agent
        
        This chatbot uses a **true autonomous ReAct agent** that makes its own decisions about which tools to use!
        
        🧠 **How it works:**
        - The agent **autonomously decides** which tools are needed for your question
        - It can **reason through complex problems** using multiple tools in sequence
        - **No predefined steps** - the agent chooses its own path to answer your question
        
        🔧 **Available Tools for the Agent:**
        1. 🕵️ **ContextPresenceJudge** - Determines if you provided context
        2. ✂️ **ContextSplitter** - Separates background info from questions  
        3. 🌐 **WebSearchTool** - Searches for missing information
        4. 🎯 **ContextRelevanceChecker** - Validates context relevance
        
        Try different types of questions to see the agent's autonomous decision-making in action!
        """)
        
        chatbot = gr.Chatbot(
            label="Chat History",
            height=400,
            show_label=True
        )
        
        with gr.Row():
            msg = gr.Textbox(
                label="Your Message",
                placeholder="Ask me anything...",
                lines=2,
                scale=4
            )
            submit_btn = gr.Button("Send", variant="primary", scale=1)
        
        with gr.Row():
            clear_btn = gr.Button("🗑️ Clear Chat", variant="secondary")
        
        # Example questions
        gr.Examples(
            examples=[
                ["What is machine learning?"],
                ["Machine learning is a subset of AI. What are the main types of machine learning algorithms?"],
                ["How do attention mechanisms work in neural networks?"],
                ["Tell me about LangChain and its uses in building AI applications."]
            ],
            inputs=msg,
            label="Try these examples:"
        )
        
        # Event handlers
        submit_btn.click(
            fn=chat_function,
            inputs=[msg, chatbot],
            outputs=[msg, chatbot]
        )
        
        msg.submit(
            fn=chat_function,
            inputs=[msg, chatbot],
            outputs=[msg, chatbot]
        )
        
        clear_btn.click(
            fn=lambda: ([], ""),
            inputs=[],
            outputs=[chatbot, msg]
        )
    
    return interface