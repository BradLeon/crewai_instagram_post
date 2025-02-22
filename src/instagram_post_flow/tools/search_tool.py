from typing import Type
from crewai.tools import tool

from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from crewai_tools import SerperDevTool
import os 
import requests
import json 


class SearchToolInput(BaseModel):
    """Input schema for MyCustomTool."""

    search_query: str = Field(
        ..., description="Mandatory search query you want to use to search the internet"
    )


class SearchTool(BaseTool):
    name: str = "Search the internet about given query"
    description: str = (
         "A tool that can be used to search the internet with a search_query. "
        "Supports different search types: 'search' (default), 'news'"
    )
    args_schema: Type[BaseModel] = SearchToolInput

    @tool("Search the internet")
    def _search_internet(self, query: str) -> str:
        # Implementation goes here
        """Useful to search the internet about a given topic and return relevant
        results."""
        return self.search(query)
    

    @tool("Search Instagram")
    def search_instagram(self, query: str) -> str:
        """Useful to search for instagram post about a given topic and return relevant
        results."""
        query = f"site:instagram.com {query}"
        return self.search(query)
    
    def search(self, query, n_results=5):
        url = "https://google.serper.dev/search"
        payload = json.dumps({"q": query})
        headers = {
            'X-API-KEY': os.environ['SERPER_API_KEY'],
            'content-type': 'application/json'
        }
        response = requests.request("POST", url, headers=headers, data=payload)
        results = response.json()['organic']
        stirng = []
        for result in results[:n_results]:
            try:
                stirng.append('\n'.join([
                    f"Title: {result['title']}", f"Link: {result['link']}",
                    f"Snippet: {result['snippet']}", "\n-----------------"
                ]))
            except KeyError:
                next

        content = '\n'.join(stirng)
        return f"\nSearch result: {content}\n"
