from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from instagram_post_flow.tools.browser_tool import BrowserTools, PlaywrightBrowser
from instagram_post_flow.tools.instagram_search_tool import InstagramSearchTool
from playwright.sync_api import sync_playwright
from crewai_tools import SerperDevTool, ScrapeWebsiteTool
from crewai import LLM
from crewai.memory import LongTermMemory, ShortTermMemory, EntityMemory, UserMemory
from crewai.memory.storage.rag_storage import RAGStorage
from crewai.memory.storage.ltm_sqlite_storage import LTMSQLiteStorage
from pydantic import BaseModel, Field
from typing import Dict, Optional, List, Set, Tuple
import os 
import logging

# 设置日志
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


'''
#自定义model产出格式
class ProductAnalysisResult(BaseModel):
	key_selling_points: str = Field(..., description="key selling point of the product")
	market_appeal: str = Field(..., description="market appeal of the product")
	suggestions: str = Field(..., description="suggestions for making the product enhance positioning.")

class CompetitorAnalysisResult(BaseModel):
	product: str = Field(..., description="the product name of competitor")
	market_positioning: str = Field(..., description="the Market Positioning of competitor")
	product_strategy: str = Field(..., description="the strategy of competitor")
	customer_perception: str = Field(..., description="Customer Perception of competitor's product")

class ProductAndCompetitorsAnalysisResult(BaseModel):
	competitor_analysis_result: List[CompetitorAnalysisResult] = Field(..., description="the list of top 3 competitors' analysis result ")
	strategic_recommendations: str=Field(..., description="Customer Perception of competitor's product")
	product_analysis_result: ProductAnalysisResult=Field(..., description="product analysis report of competitor_analysis task")
'''

@CrewBase
class AnalysisCrew():
	"""product & competitors analysis Crew"""

	agents_config = 'config/agents.yaml'
	tasks_config = 'config/tasks.yaml'

	# custom tools
	# playWright_browser_tools = PlaywrightBrowser()
	# custom tools
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
	
	# 减少重复浏览网页，缓存crew执行结果。
	# rag_storage = LTMSQLiteStorage(db_path="./memory/")
	# long_term_memory = LongTermMemory(storage=rag_storage)

	@agent
	def product_competitor_agent(self) -> Agent:
		logger.debug("Creating product_competitor_agent")
		agent = Agent(
			config=self.agents_config['product_competitor_agent'],
			tools=[self.scrape_tool],
			llm=self.llm,
			verbose=True
		)
		logger.debug("Agent created successfully")
		return agent
	
	@task
	def product_analysis(self) -> Task:
		return Task(
			config=self.tasks_config['product_analysis'],
			agent=self.product_competitor_agent(),
			# output_pydantic=ProductAnalysisResult,
			verbose=True
		)

	@task
	def competitor_analysis(self) -> Task:
		return Task(
			config=self.tasks_config['competitor_analysis'],
			agent=self.product_competitor_agent(),
			# output_pydantic=ProductAndCompetitorsAnalysisResult,
			verbose=True
		)
	
	@crew
	def crew(self) -> Crew:
		"""Creates  Crew"""
		return Crew(
			agents=self.agents, # Automatically created by the @agent decorator
			tasks=self.tasks, # Automatically created by the @task decorator
			process=Process.sequential,
			verbose=True,
		)
