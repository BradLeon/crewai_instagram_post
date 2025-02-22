#!/usr/bin/env python
from random import randint
import asyncio
import typer
import warnings
import logging
from typing import Optional

from pydantic import BaseModel

from crewai.flow.flow import Flow, listen, start

from .crews.analysis_crew import AnalysisCrew
from .crews.instagram_ad_copy_writer import InstagramAdCopyWriter
from .crews.image_prompt_generator import ImagePromptGenerator
from instagram_post_flow.tools.stable_diffusion_tool import StableDiffusionTools


warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# This main file is intended to be a way for you to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information
import textwrap

app = typer.Typer()

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class InstagramPostState(BaseModel):
    '''自定义关键state变量'''
    sentence_count: int = 1
    poem: str = ""
    product_website: str = ""
    product_details: str = ""
    # analysis_result: Optional[dict] = None  # 存储分析结果

class InstagramPostFlow(Flow[InstagramPostState]):
   
    inputs =  {
        "product_website": "https://www.kickstarter.com/projects/yoshiakiito/new-morphits-transforming-wooden-toy-snake-and-turtle-combo?ref=discovery_category&total_hits=1504&category_id=396",
        "product_details": "Morphits® emerged from a vision to blend the classic charm of wooden toys with contemporary innovation. Crafted by the acclaimed artist and designer Yoshiaki Ito, Morphits® has captured hearts worldwide with its marriage of traditional craftsmanship and modern aesthetics. Each Morphits® piece is meticulously handcrafted from sustainable wood, ensuring both durability and timeless beauty."
        }

    @start()
    def generate_sentence_count(self):
        self.state.product_website = self.inputs["product_website"]
        self.state.product_details = self.inputs["product_details"]
        print("## Welcome to the marketing Crew")
    
    @listen(generate_sentence_count)
    def generate_analysis_report(self):
        logger.debug("Starting generate_analysis_report")
        try:
            result = AnalysisCrew().crew().kickoff(inputs=self.inputs)
            print('--------analysis report generated---------')
            print("type of result:", type(result))
            print(result)
            return result
        except Exception as e:
            logger.error(f"Error during crew execution: {str(e)}", exc_info=True)
            raise
    
    
    #@listen(generate_analysis_report)
    def generate_instagram_ad_copy(self):
        logger.debug("Starting generate_instagram_ad_copy")
        try:
            result = InstagramAdCopyWriter().crew().kickoff(inputs=self.inputs)
            print('--------instagram_ad_copy generated---------')
            print("type of result:", type(result))
            print(result)
            
            # 将 ad_copy 结果添加到 inputs 字典
            if result:
                self.inputs["ad_copy"] = result.raw # 确保是字符串格式
            return result
        except Exception as e:
            logger.error(f"Error during crew execution: {str(e)}", exc_info=True)
            raise

    @listen(generate_instagram_ad_copy)
    def generate_instagram_post_image_prompt(self):
        logger.debug("Starting generate_instagram_post_image_prompt")
        try:
            # 传递包含 ad_copy 的 inputs
            result = ImagePromptGenerator().crew().kickoff(inputs=self.inputs)
            print('--------instagram_post_image_prompt generated---------')
            print(result)
            return result
        except Exception as e:
            logger.error(f"Error during crew execution: {str(e)}", exc_info=True)
            raise

    
    @listen(generate_instagram_post_image_prompt)
    def generate_instagram_post_image(self):
        logger.debug("Starting generate_instagram_post_image")
        try:   
            sd_tool = StableDiffusionTools()
            image_review_results = self.inputs.get("image_review_results", [])
            for image_review_result in image_review_results:
                txt2img_prompt = image_review_result.get('txt2img_prompt')
                if txt2img_prompt:
                    generated_img_path = sd_tool._run(text_prompt=txt2img_prompt)
                    print('--------instagram_post_image generated---------')
                    print(generated_img_path)
            return True
        except Exception as e:
            logger.error(f"Error during image generation: {str(e)}", exc_info=True)
            raise


def kickoff():
    """
    Kickoff the Instagram post flow
    """
    try:
        flow = InstagramPostFlow()
        analysis_report = flow.generate_analysis_report()  
        ad_copy=flow.generate_instagram_ad_copy()
        ins_image=flow.generate_instagram_post_image_prompt()
        flow.plot("salesPipeline_flow")
        return ad_copy
    except Exception as e:
        print(f"An error occurred while running the flow: {str(e)}")
        raise typer.Exit(code=1)



if __name__ == "__main__":
    kickoff()
