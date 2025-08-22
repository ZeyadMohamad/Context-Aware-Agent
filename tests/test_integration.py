"""Integration tests that demonstrate the complete context-aware workflow."""

import unittest
from unittest.mock import Mock
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from agent.agent_runner import run_simple_context_aware_query
from tools import (
    build_context_presence_tool,
    build_web_search_tool, 
    build_context_relevance_tool,
    build_context_splitter_tool
)


class TestIntegratedWorkflow(unittest.TestCase):
    """Test the complete context-aware workflow as described in the roadmap."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_llm = Mock()
        
    def test_workflow_with_missing_context(self):
        """Test the workflow when user provides no context (should trigger web search)."""
        # Mock LLM responses for each step
        self.mock_llm.invoke.side_effect = [
            # Context splitter response
            "CONTEXT:\n\nQUESTION:\nWhat is machine learning?",
            # Context judge response  
            "context_missing",
            # Final answer generation
            "Machine learning is a subset of artificial intelligence..."
        ]
        
        # Mock the web search to return something
        with unittest.mock.patch('tools.web_search_tool.wikipedia_search') as mock_search:
            mock_search.return_value = "Machine learning is a method of data analysis that uses algorithms..."
            
            result = run_simple_context_aware_query(
                "What is machine learning?", 
                self.mock_llm
            )
            
            self.assertIsInstance(result, str)
            self.assertGreater(len(result), 10)
            
    def test_workflow_with_provided_context(self):
        """Test the workflow when user provides context (should not trigger web search)."""
        # Mock LLM responses
        self.mock_llm.invoke.side_effect = [
            # Context splitter response
            "CONTEXT:\nMachine learning is AI that learns from data.\n\nQUESTION:\nWhat are the main types?",
            # Context judge response
            "context_provided", 
            # Relevance checker response
            "relevant",
            # Final answer
            "The main types of machine learning are supervised, unsupervised, and reinforcement learning..."
        ]
        
        result = run_simple_context_aware_query(
            "Machine learning is AI that learns from data. What are the main types?",
            self.mock_llm
        )
        
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 10)

    def test_all_tools_can_be_built(self):
        """Test that all four core tools can be successfully built."""
        mock_llm = Mock()
        
        # Test that all tools can be instantiated
        context_judge = build_context_presence_tool(mock_llm)
        web_search = build_web_search_tool()
        relevance_checker = build_context_relevance_tool(mock_llm) 
        context_splitter = build_context_splitter_tool(mock_llm)
        
        # Verify they are proper LangChain tools
        self.assertEqual(context_judge.name, "ContextPresenceJudge")
        self.assertEqual(web_search.name, "WebSearchTool")
        self.assertEqual(relevance_checker.name, "ContextRelevanceChecker")
        self.assertEqual(context_splitter.name, "ContextSplitter")
        
        # Verify they have descriptions
        self.assertIsNotNone(context_judge.description)
        self.assertIsNotNone(web_search.description)
        self.assertIsNotNone(relevance_checker.description)
        self.assertIsNotNone(context_splitter.description)

    def test_context_splitter_functionality(self):
        """Test that context splitter properly separates context from questions."""
        mock_llm = Mock()
        mock_llm.invoke.return_value = """CONTEXT:
Machine learning is a subset of AI that uses algorithms to learn from data.

QUESTION:
What are the main supervised learning algorithms?"""
        
        splitter = build_context_splitter_tool(mock_llm)
        result = splitter.func("Machine learning is a subset of AI. What are supervised learning algorithms?")
        
        self.assertIsInstance(result, dict)
        self.assertIn("context", result)
        self.assertIn("question", result)

    def test_context_presence_judge_functionality(self):
        """Test that context presence judge makes correct decisions."""
        mock_llm = Mock()
        
        # Test with context missing
        mock_llm.invoke.return_value = "Analysis: No context provided. Decision: context_missing"
        judge = build_context_presence_tool(mock_llm)
        result = judge.func("What is machine learning?")
        self.assertEqual(result, "context_missing")
        
        # Test with context provided  
        mock_llm.invoke.return_value = "Analysis: Context is provided. Decision: context_provided"
        result = judge.func("Machine learning is AI. What are the types?")
        self.assertEqual(result, "context_provided")


if __name__ == "__main__":
    print("Running Integration Tests for Context-Aware Chatbot")
    print("=" * 60)
    unittest.main(verbosity=2)
