from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from instagram_post_flow.tools.browser_tool import BrowserTools, PlaywrightBrowser
from instagram_post_flow.tools.instagram_search_tool import InstagramSearchTool
from langchain_community.agent_toolkits import PlayWrightBrowserToolkit
from playwright.sync_api import sync_playwright
from crewai_tools import SerperDevTool, ScrapeWebsiteTool
from .analysis_crew import AnalysisCrew
from crewai import LLM
import os 
import logging

# 设置日志
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@CrewBase
class InstagramAdCopyWriter():
	"""product & competitors analysis Crew"""

	agents_config = 'config/agents.yaml'
	tasks_config = 'config/tasks.yaml'

	request_config = {
		'verify': False,
		'proxies': {
			'http': 'http://127.0.0.1:10080',
			'https': 'http://127.0.0.1:10080'
		},
		'timeout': 30,
		'headers': {
			'Content-Type': 'application/json'
		}
	}

	# custom tools
	scrape_tool = ScrapeWebsiteTool()
	instagram_search_tool = InstagramSearchTool()
	google_search_tool = SerperDevTool()

	# custom llm
	llm = LLM(
            model="openrouter/deepseek/deepseek-chat:free",
			base_url="https://openrouter.ai/api/v1",
			api_key=os.environ['OPENROUTER_API_KEY'],
          temperature=0.1
    )

	@agent
	def strategy_planner_agent(self) -> Agent:
		agent = Agent(
			config=self.agents_config['marketing_strategist_agent'],
			tools=[self.scrape_tool, self.google_search_tool, self.instagram_search_tool],
			llm=self.llm,
			verbose=True
		)
		logger.debug("Agent created successfully")
		return agent
	

	@agent
	def creative_content_creator_agent(self) -> Agent:
		agent = Agent(
			config=self.agents_config['creative_content_creator_agent'],
			tools=[self.google_search_tool, self.instagram_search_tool],
			llm=self.llm,
			verbose=True
		)
		logger.debug("Agent created successfully")
		return agent
	
	@task
	def campaign_development_task(self) -> Task:
		return Task(
			config=self.tasks_config['campaign_development'],
			agent=self.strategy_planner_agent(),
			verbose=True
		)

	@task
	def instagram_ad_copy_task(self) -> Task:
		return Task(
			config=self.tasks_config['instagram_ad_copy'],
			agent=self.creative_content_creator_agent(),
			verbose=True
		)
	
	@crew
	def crew(self) -> Crew:
		"""Creates Crew"""
		return Crew(
			agents=self.agents,
			tasks=self.tasks,
			process=Process.sequential,
			verbose=True,
		)
