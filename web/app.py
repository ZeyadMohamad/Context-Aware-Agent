"""
Flask Web Interface for Context-Aware Chatbot
Server-side rendered interface with session-based chat history
"""

from flask import Flask, render_template, request, redirect, url_for, session
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.agent_runner import build_agent, run_agent_query, run_smart_context_aware_query, run_manual_context_aware_query

class ChatbotApp:
    def __init__(self, llm):
        self.app = Flask(__name__)
        # Secret key for sessions (change in production)
        self.app.secret_key = 'context-aware-chatbot-secret-key-change-in-production'
        
        # Store the LLM and build agent once
        self.llm = llm
        self.agent = None
        self._setup_routes()
    
    def _setup_routes(self):
        """Configure all Flask routes"""
        
        @self.app.route('/', methods=['GET', 'POST'])
        def home():
            """Main chat interface page with form handling"""
            
            # Initialize session chat history if not exists
            if 'messages' not in session:
                session['messages'] = []
            
            # Handle form submission (POST request)
            if request.method == 'POST':
                message = request.form.get('message', '').strip()
                
                if message:
                    # Add user message to history
                    session['messages'].append({
                        'user': message,
                        'bot': None  # Will be filled after processing
                    })
                    session.modified = True
                    
                    # Show processing page first
                    return render_template('processing.html', messages=session['messages'], user_message=message)
            
            # For GET request, check if we have a pending message to process
            if request.args.get('process') == 'true' and session['messages'] and not session['messages'][-1]['bot']:
                # Process the pending message
                pending_message = session['messages'][-1]['user']
                response = self._process_message(pending_message)
                
                # Update the message with response
                session['messages'][-1]['bot'] = response
                session.modified = True
                
                # Redirect to clean URL
                return redirect(url_for('home'))
            
            # Render template with chat history
            return render_template('chat.html', messages=session['messages'])
        
        @self.app.route('/clear')
        def clear_chat():
            """Clear chat history"""
            session['messages'] = []
            return redirect(url_for('home'))
        
        @self.app.route('/health')
        def health_check():
            """Health check endpoint"""
            return {'status': 'healthy', 'agent': 'ready'}
    
    def _process_message(self, message):
        """
        Process user message through the autonomous agent
        Uses cascading fallback system for reliability
        """
        
        # Primary: Autonomous Agent Approach
        try:
            if not self.agent:
                self.agent = build_agent(self.llm)
            
            response = run_agent_query(self.agent, message)
            
            # Validate agent response quality
            if response and len(response.strip()) > 20 and "error" not in response.lower():
                return self._format_response(response)
            else:
                raise Exception("Agent response insufficient")
                
        except Exception:
            # Fallback 1: Smart Workflow
            try:
                response = run_smart_context_aware_query(message, self.llm)
                return self._format_response(response)
            except Exception:
                # Fallback 2: Manual Workflow (last resort)
                try:
                    response = run_manual_context_aware_query(message, self.llm)
                    return self._format_response(response)
                except Exception:
                    return "I apologize, but I'm having trouble processing your request. Please try rephrasing your question."
    
    def _format_response(self, response):
        """Format response for HTML display"""
        if not response:
            return "I couldn't generate a response. Please try again."
        
        # Basic formatting for better display
        formatted = response.replace('\n\n', '<br><br>')
        formatted = formatted.replace('\n', '<br>')
        
        # Handle basic markdown-style formatting
        formatted = formatted.replace('**', '<strong>').replace('**', '</strong>')
        
        return formatted
    
    def run(self, host='127.0.0.1', port=5000, debug=False):
        """Start the Flask development server"""
        self.app.run(host=host, port=port, debug=debug)


def create_flask_app(llm):
    """Factory function to create Flask app instance"""
    chatbot_app = ChatbotApp(llm)
    return chatbot_app


if __name__ == "__main__":
    """Main execution - start the Flask development server"""
    from agent.agent_runner import initialize_llm
    
    # Initialize the language model
    llm = initialize_llm()
    if llm is None:
        print("Failed to initialize LLM. Exiting.")
        exit(1)
    
    # Create and run the Flask app
    chatbot_app = ChatbotApp(llm)
    
    try:
        chatbot_app.run(host='127.0.0.1', port=5000, debug=True)
    except KeyboardInterrupt:
        print("Server stopped by user")
    except Exception as e:
        print(f"Server error: {e}")
