"""Web Search Tool - Retrieves information when context is missing."""

import os
import requests
import wikipedia
from langchain.tools import Tool

def tavily_search(query: str, api_key: str) -> str:
    """Search using Tavily API."""
    try:
        response = requests.post(
            "https://api.tavily.com/search",
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "query": query,
                "max_results": 3,
                "search_depth": "basic"
            },
            timeout=10  # Add timeout
        )
        
        if response.status_code == 200:
            results = response.json()
            if "results" in results and results["results"]:
                # Combine top results
                content_pieces = []
                for result in results["results"][:2]:  # Take top 2 results
                    if "content" in result and result["content"]:
                        content_pieces.append(result["content"][:500])  # Limit length
                
                return "\n\n".join(content_pieces) if content_pieces else "No relevant content found."
            else:
                return "No relevant results found."
        else:
            return f"Search API error: {response.status_code}"
            
    except Exception as e:
        print(f"Tavily search error: {e}")
        return f"Search error: {str(e)}"


def wikipedia_search(query: str) -> str:
    """Fallback search using Wikipedia."""
    try:
        # Set Wikipedia language to English
        wikipedia.set_lang("en")
        
        # Search for relevant pages
        search_results = wikipedia.search(query, results=3)
        
        if not search_results:
            return "No relevant Wikipedia articles found."
        
        # Get the first relevant page
        page_title = search_results[0]
        
        # Return summary (first few sentences)
        summary = wikipedia.summary(page_title, sentences=4, auto_suggest=False)
        return f"From Wikipedia ({page_title}):\n{summary}"
        
    except wikipedia.exceptions.DisambiguationError as e:
        # Handle disambiguation by picking the first option
        try:
            page_title = e.options[0]
            summary = wikipedia.summary(page_title, sentences=4, auto_suggest=False)
            return f"From Wikipedia ({page_title}):\n{summary}"
        except Exception:
            return "Could not retrieve information from Wikipedia due to disambiguation."
            
    except wikipedia.exceptions.PageError:
        return "No relevant Wikipedia page found for this topic."
        
    except Exception as e:
        print(f"Wikipedia search error: {e}")
        return f"Wikipedia search error: {str(e)}"


def build_web_search_tool() -> Tool:
    """
    Build a web search tool that can use either Tavily API or Wikipedia fallback.
    
    Returns:
        Tool: A LangChain Tool object for web searching
    """
    
    def web_search(query: str) -> str:
        """Search the web for information about the given query."""
        if not query or not query.strip():
            return "Empty search query provided."
            
        # Check for Tavily API key
        tavily_api_key = os.getenv("TAVILY_API_KEY")
        use_simulated = os.getenv("USE_SIMULATED_SEARCH", "true").lower() == "true"
        
        if tavily_api_key and not use_simulated:
            print(f"🌐 Searching with Tavily API: {query}")
            result = tavily_search(query, tavily_api_key)
            # Fallback to Wikipedia if Tavily fails
            if "error" in result.lower():
                print("🔄 Tavily failed, falling back to Wikipedia...")
                return wikipedia_search(query)
            return result
        else:
            print(f"🔍 Searching with Wikipedia: {query}")
            return wikipedia_search(query)
    
    return Tool.from_function(
        func=web_search,
        name="WebSearchTool",
        description="Searches the web (using Tavily API or Wikipedia) to retrieve information about a given topic. Use this when the user's question lacks sufficient context."
    )

# Example usage and testing
if __name__ == "__main__":
    # Build the tool
    search_tool = build_web_search_tool()
    
    # Test cases
    test_queries = [
        "machine learning algorithms",
        "attention mechanisms in transformers",
        "LangChain framework"
    ]
    
    print("Testing Web Search Tool:")
    for i, query in enumerate(test_queries, 1):
        result = search_tool.func(query)
        print(f"\nTest {i}:")
        print(f"Query: {query}")
        print(f"Result: {result[:200]}...")  # Show first 200 chars