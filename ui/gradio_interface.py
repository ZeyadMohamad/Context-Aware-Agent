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
            
            # Use smart workflow as primary (most reliable), with agent as fallback for testing
            try:
                print("🎯 Using smart context-aware workflow...")
                response = run_smart_context_aware_query(message, llm)
                print("✅ Smart workflow completed successfully")
                
            except Exception as e:
                print(f"🔄 Smart workflow failed ({str(e)[:50]}...), trying agent")
                # Try agent as fallback
                try:
                    agent = build_agent(llm)
                    response = run_agent_query(agent, message)
                    
                    # Check if agent response is meaningful
                    if response and len(response.strip()) > 20 and "error" not in response.lower():
                        print("✅ Used autonomous agent as fallback")
                    else:
                        raise Exception("Agent response insufficient")
                        
                except Exception as e2:
                    print(f"🔄 Agent also failed, using manual workflow")
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
        # 🤖 Context-Aware Chatbot
        
        This chatbot is context-aware! It will:
        
        1. 🕵️ Check if you provided enough context in your question
        2. 🌐 Search the web if more information is needed  
        3. 🎯 Provide comprehensive answers using all available information
        
        Try asking questions with and without context to see the difference!
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