import os
from tavily import TavilyClient
from dotenv import load_dotenv

# Load API keys and configuration from the .env file.
load_dotenv()

client = TavilyClient(
    api_key=os.getenv("TAVILY_API_KEY")
)

# =============================================================
# Define a function that searches the web for the given query.
# =============================================================

def tavily_search(query):
    """Search the web and return up to five formatted results."""

    response = client.search(
        query=query,
        max_results=5
    )

    result = []

    for i, r in enumerate(response["results"], 1):
        title = r.get("title", "unknown")
        url = r.get("url", "")
        snippet = r.get("content", "").strip()

        # keep only the first 300 character to avoid wall-of-text
        if len(snippet) > 300:
            snippet = snippet[:300].rsplit(" ", 1)[0] + "..."
        result.append(f"{i}. **{title}**\n {url}\n {snippet}")
    
    return "\n\n".join(result)