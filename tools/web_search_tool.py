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
        return f"Search error: {str(e)}"


def wikipedia_search(query: str) -> str:
    """Fallback search using Wikipedia."""
    try:
        wikipedia.set_lang("en")
        search_results = wikipedia.search(query, results=3)
        
        if not search_results:
            return "No relevant Wikipedia articles found."
        
        page_title = search_results[0]
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
            
        tavily_api_key = os.getenv("TAVILY_API_KEY")
        use_simulated = os.getenv("USE_SIMULATED_SEARCH", "true").lower() == "true"
        
        if tavily_api_key and not use_simulated:
            result = tavily_search(query, tavily_api_key)
            
            if "error" in result.lower():
                return wikipedia_search(query)
            return result
        else:
            return wikipedia_search(query)
    
    return Tool.from_function(
        func=web_search,
        name="WebSearchTool",
        description="""
Use this tool to gather fresh and relevant context from the internet when:
observation shows "context_missing" or "irrelevant_context" from the previous tools.
This tool performs a web search based on the user's input.
Pass the entire input to this tool, and it will return the most relevant web search result.
""",
        return_direct = True
    )