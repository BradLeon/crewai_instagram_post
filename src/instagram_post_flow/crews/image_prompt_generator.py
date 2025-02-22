from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from instagram_post_flow.tools.browser_tool import BrowserTools, PlaywrightBrowser
from instagram_post_flow.tools.instagram_search_tool import InstagramSearchTool
from langchain_community.agent_toolkits import PlayWrightBrowserToolkit
from playwright.sync_api import sync_playwright
from crewai_tools import SerperDevTool, ScrapeWebsiteTool
from instagram_post_flow.tools.stable_diffusion_tool import StableDiffusionTools
from .analysis_crew import AnalysisCrew
from crewai import LLM
from pydantic import BaseModel, Field
from typing import List 
import os 
import logging
import base64
from pathlib import Path

# 设置日志
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class ImageReviewResult(BaseModel):
	txt2img_prompt: str = Field(..., description="the photo from the senior photographer")
	review_score: int = Field(..., description="a final suitable score from (0-100) to value how suitable the photo for the ad copy. ")
	validation_note: str = Field(..., description="a summary validation notes explains the score reason.")

class ImageReviewResults(BaseModel):
	image_review_results: List[ImageReviewResult] = Field(..., description="A list of image review result")

@CrewBase
class ImagePromptGenerator():
	"""product & competitors analysis Crew"""

	agents_config = 'config/agents.yaml'
	tasks_config = 'config/tasks.yaml'

	# custom tools
	scrape_tool = ScrapeWebsiteTool()
	instagram_search_tool = InstagramSearchTool()
	google_search_tool = SerperDevTool()
	stable_diffusion_tools = StableDiffusionTools()

	# custom llm
	llm = LLM(
            model="openrouter/deepseek/deepseek-chat:free",
			base_url="https://openrouter.ai/api/v1",
			api_key=os.environ['OPENROUTER_API_KEY'],
          temperature=0.1
    )
	
    	# custom llm
	multi_modal_llm = LLM(
        model="openrouter/google/gemini-2.0-flash-lite-preview-02-05:free",  # 使用 Gemini 模型
        api_key=os.environ['OPENROUTER_API_KEY'],
        temperature=0.7
    )
    

	@agent
	def senior_photographer_agent(self) -> Agent:
		agent = Agent(
			config=self.agents_config['senior_photographer_agent'],
			tools=[self.scrape_tool, self.google_search_tool, self.instagram_search_tool, self.stable_diffusion_tools],
			llm=self.llm,
			allow_delegation=False,
			verbose=True
		)
		logger.debug("Agent created successfully")
		return agent
	

	@agent
	def chief_creative_diretor_agent(self) -> Agent:
		agent = Agent(
			config=self.agents_config['chief_creative_diretor_agent'],
			llm=self.multi_modal_llm,  # 使用支持多模态的 LLM
			allow_delegation=True,
			verbose=True
		)
		logger.debug("Agent created successfully")
		return agent
	
	@task
	def take_photograph_task(self) -> Task:
		return Task(
			config=self.tasks_config['take_photograph_task'],
			agent=self.senior_photographer_agent(),
			verbose=True
		)

	@task
	def review_photo_task(self) -> Task:
		"""
		    review the generated image and provide a detailed analysis.
		"""
		def process_image(image_path: str) -> dict:
			"""处理图片并构建多模态消息"""
			encoded_image = self.encode_image(image_path)
			return {
				"type": "image_url",
				"image_url": {
					"url": f"data:image/jpeg;base64,{encoded_image}"
				}
			}

		def get_all_images(directory: str) -> list:
			"""获取目录下所有图片文件"""
			image_files = []
			for ext in ['.png', '.jpg', '.jpeg']:
				image_files.extend(Path(directory).glob(f'*{ext}'))
			return sorted(image_files)  # 按文件名排序

		# 构建图片内容列表

		# test
		print("out_dir_t2i:",self.stable_diffusion_tools.out_dir_t2i)
		image_files =get_all_images(self.stable_diffusion_tools.out_dir_t2i)
		print("image_files:",image_files)

		content = []
		for image_path in get_all_images(self.stable_diffusion_tools.out_dir_t2i):
			content.append(process_image(str(image_path)))


		# 构建正确的 context 格式
		context = [
			{
				"description": "Review these generated images for the Instagram ad",
				"expected_output": "A detailed review with scores and recommendations",
				"role": "user",
				"content": [
					{"type": "text", "text": "Please review these images and provide a detailed analysis."},
					*content  # 展开所有图片内容
				]
			}
		]

		return Task(
			config=self.tasks_config['review_photo_task'],
			agent=self.chief_creative_diretor_agent(),
			context=context,
			verbose=True
		)

	def encode_image(self, image_path: str) -> str:
		"""将本地图片转换为 base64 格式"""
		with open(image_path, "rb") as image_file:
			return base64.b64encode(image_file.read()).decode("utf-8")


	@crew
	def crew(self) -> Crew:
		"""Creates Crew"""
		return Crew(
			agents=self.agents,
			tasks=[self.take_photograph_task(),self.review_photo_task()], #限定前后执行顺序
			process=Process.sequential,
			verbose=True,
		)
