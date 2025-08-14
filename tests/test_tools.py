"""Unit tests for the chatbot tools."""

import unittest
from unittest.mock import Mock, patch
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from tools.context_presence_judge import build_context_presence_tool
from tools.web_search_tool import build_web_search_tool, wikipedia_search
from tools.context_relevance_checker import build_context_relevance_tool
from tools.context_splitter import build_context_splitter_tool


class TestContextPresenceJudge(unittest.TestCase):
    """Test cases for the Context Presence Judge tool."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_llm = Mock()
        self.context_tool = build_context_presence_tool(self.mock_llm)
    
    def test_context_provided_response(self):
        """Test when LLM returns context_provided."""
        self.mock_llm.return_value = "context_provided"
        
        # Mock the chain's run method
        with patch('tools.context_presence_judge.LLMChain') as mock_chain_class:
            mock_chain = Mock()
            mock_chain.run.return_value = "Analysis: This contains context. Decision: context_provided"
            mock_chain_class.return_value = mock_chain
            
            tool = build_context_presence_tool(self.mock_llm)
            result = tool.func("Machine learning is AI. What are the types?")
            
            self.assertEqual(result, "context_provided")
    
    def test_context_missing_response(self):
        """Test when LLM returns context_missing."""
        with patch('tools.context_presence_judge.LLMChain') as mock_chain_class:
            mock_chain = Mock()
            mock_chain.run.return_value = "Analysis: No context provided. Decision: context_missing"
            mock_chain_class.return_value = mock_chain
            
            tool = build_context_presence_tool(self.mock_llm)
            result = tool.func("What is machine learning?")
            
            self.assertEqual(result, "context_missing")


class TestWebSearchTool(unittest.TestCase):
    """Test cases for the Web Search tool."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.web_search_tool = build_web_search_tool()
    
    @patch('tools.web_search_tool.wikipedia_search')
    def test_wikipedia_search_success(self, mock_wiki_search):
        """Test successful Wikipedia search."""
        mock_wiki_search.return_value = "Machine learning is a method of data analysis..."
        
        with patch.dict(os.environ, {"USE_SIMULATED_SEARCH": "true"}):
            result = self.web_search_tool.func("machine learning")
            
        mock_wiki_search.assert_called_once_with("machine learning")
        self.assertIn("Machine learning", result)
    
    def test_wikipedia_search_real(self):
        """Test real Wikipedia search (integration test)."""
        result = wikipedia_search("machine learning")
        
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 50)  # Should return substantial content
        self.assertIn("machine learning", result.lower())

class TestContextRelevanceChecker(unittest.TestCase):
    def setUp(self):
        self.llm = Mock()
        self.tool = build_context_relevance_tool(self.llm)

    def test_relevant(self):
        self.llm.invoke.return_value = "Decision: relevant"
        res = self.tool.func({"context":"Transformers use attention...", "question":"How does attention work?"})
        self.assertEqual(res, "relevant")

    def test_irrelevant(self):
        self.llm.invoke.return_value = "irrelevant"
        res = self.tool.func({"context":"CSS selectors...", "question":"What is LangChain?"})
        self.assertEqual(res, "irrelevant")

class TestContextSplitter(unittest.TestCase):
    def setUp(self):
        self.llm = Mock()
        self.tool = build_context_splitter_tool(self.llm)

    def test_split_with_context(self):
        self.llm.invoke.return_value = (
            "CONTEXT:\nI read a paper on attention...\n\nQUESTION:\nHow does attention work?"
        )
        res = self.tool.func("dummy")
        self.assertEqual(res["context"].startswith("I read a paper"), True)
        self.assertIn("How does attention work", res["question"])

    def test_split_question_only(self):
        self.llm.invoke.return_value = "CONTEXT:\n\nQUESTION:\nWhat is LangChain?"
        res = self.tool.func("dummy")
        self.assertEqual(res["context"], "")
        self.assertEqual(res["question"], "What is LangChain?")


if __name__ == "__main__":
    # Run the tests
    unittest.main(verbosity=2)