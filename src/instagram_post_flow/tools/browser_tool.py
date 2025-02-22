import json
import os

import requests
from crewai import Agent, Task
from crewai.tools import tool, BaseTool
from unstructured.partition.html import partition_html
from playwright.sync_api import sync_playwright
from pydantic import Field, PrivateAttr
from pydantic import BaseModel
from typing import Any, Optional, Type
from crewai import LLM

class FixedPlaywrightBrowserSchema(BaseModel):
    """Input for PlaywrightBrowser"""

class PlaywrightBrowserSchema(FixedPlaywrightBrowserSchema):
    """Input for PlaywrightBrowser"""
    website: str = Field(..., description="Mandatory website url to read the file")


class PlaywrightBrowser(BaseTool):
    name: str = "Playwright Browser"
    description: str = "A tool to browse websites and extract their content using Playwright"
    args_schema: Type[BaseModel] = PlaywrightBrowserSchema
    # 使用 PrivateAttr 来存储不需要序列化的实例属性
    _playwright = PrivateAttr(default=None)
    _browser = PrivateAttr(default=None)
    website: Optional[str] = None

    def __init__(self, 
                 website: Optional[str] = None,
                 **kwargs):
        super().__init__()
        if website is not None:
            self._playwright = sync_playwright().start()
            self._browser = self._playwright.chromium.launch(
            headless=True,
            executable_path='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
            )
            self.website = website
            self.description = (
                    f"A tool that can be used to read {website}'s content."
                )
            self.args_schema = FixedPlaywrightBrowserSchema
            self._generate_description()
    '''
    def _run(self, url: str) -> str:
        """Execute the tool's main functionality"""
        try:
            page = self._browser.new_page()
            page.goto(url)
            content = page.content()
            page.close()
            return content
        except Exception as e:
            return f"Error browsing: {str(e)}"
    '''

    def _run(
        self,
        **kwargs: Any,
    ) -> Any:
        """Execute the tool's main functionality"""
        website = kwargs.get("website", self.website)
        try:
            page = self._browser.new_page()
            page.goto(website)
            content = page.content()
            page.close()
            return content
        except Exception as e:
            return f"Error browsing: {str(e)}"


    def __del__(self):
        """Clean up resources"""
        if hasattr(self, '_browser'):
            self._browser.close()
        if hasattr(self, '_playwright'):
            self._playwright.stop()


class BrowserTools():
    def __init__(self):
        pass
        
    @tool("Scrape website content")
    def scrape_and_summarize_website(self, website):
        """Useful to scrape and summarize a website content, just pass a string with
        only the full url, no need for a final slash `/`, eg: https://google.com or https://clearbit.com/about-us"""

        llm = LLM(
                model="openrouter/deepseek/deepseek-r1:free",
			      base_url="https://openrouter.ai/api/v1",
			      api_key=os.environ['OPENROUTER_API_KEY'],
                temperature=0.1
        )
         
        url = f"https://chrome.browserless.io/content?token={os.environ['BROWSERLESS_API_KEY']}"
        payload = json.dumps({"url": website})
        #
        print("broserless scrape url:", website)
        headers = {'cache-control': 'no-cache', 'content-type': 'application/json'}
        response = requests.request("POST", url, headers=headers, data=payload)
        elements = partition_html(text=response.text)
        content = "\n\n".join([str(el) for el in elements])
        content = [content[i:i + 8000] for i in range(0, len(content), 8000)]
        summaries = []
        for chunk in content:
          agent = Agent(
              role='Principal Researcher',
              goal=
              'Do amazing researches and summaries based on the content you are working with',
              backstory=
              "You're a Principal Researcher at a big company and you need to do a research about a given topic.",
              llm=llm,
              verbose=True,
              allow_delegation=False)
          task = Task(
              agent=agent,
              description=
              f'Analyze and make a LONG summary the content bellow, make sure to include the ALL relevant information in the summary, return only the summary nothing else.\n\nCONTENT\n----------\n{chunk}'
          )
          summary = task.execute()
          summaries.append(summary)
          content = "\n\n".join(summaries)
        return f'\nScrapped Content: {content}\n'
