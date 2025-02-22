from datetime import datetime
import urllib.request
import base64
import json
import time
import os
from crewai.tools import BaseTool, tool
from pydantic import BaseModel, Field, PrivateAttr
from typing import List, Type
import logging

logger = logging.getLogger(__name__)

class Text2ImgInput(BaseModel):
    """Input for text2img tool"""
    text_prompt: str = Field(..., description="Text prompt to generate image")

class StableDiffusionTools(BaseTool):
    """A tool to generate images using Stable Diffusion""" 
    
    '''
    remember the example code: https://gist.github.com/w-e-w/0f37c04c18e14e4ee1482df5c4eb9f53
    '''
    name: str = "Stable Diffusion Tool"
    description: str = "A tool to generate images using Stable Diffusion"
    args_schema: Type[BaseModel] = Text2ImgInput
    
    # 使用 PrivateAttr 来存储实例属性
    _webui_server_url: str = PrivateAttr(default='http://127.0.0.1:7860')
    _out_dir: str = PrivateAttr(default='api_out')
    _out_dir_t2i: str = PrivateAttr()
    _out_dir_i2i: str = PrivateAttr()

    def __init__(self):
        super().__init__()
        # 初始化输出目录
        self._out_dir_t2i = os.path.join(self._out_dir, 'txt2img')
        self._out_dir_i2i = os.path.join(self._out_dir, 'img2img')
        os.makedirs(self._out_dir_t2i, exist_ok=True)
        os.makedirs(self._out_dir_i2i, exist_ok=True)

    @property
    def out_dir_t2i(self) -> str:
        return self._out_dir_t2i

    @property
    def out_dir_i2i(self) -> str:
        return self._out_dir_i2i

    def timestamp(self):
        return datetime.fromtimestamp(time.time()).strftime("%Y%m%d-%H%M%S")

    def encode_file_to_base64(self, path):
        with open(path, 'rb') as file:
            return base64.b64encode(file.read()).decode('utf-8')

    def decode_and_save_base64(self, base64_str, save_path):
        with open(save_path, "wb") as file:
            file.write(base64.b64decode(base64_str))

    def call_api(self, api_endpoint, **payload):
        data = json.dumps(payload).encode('utf-8')
        request_url = f'{self._webui_server_url}/{api_endpoint}'
        logger.debug(f"Calling API: {request_url} with payload: {data}")
        request = urllib.request.Request(
            request_url,
            headers={'Content-Type': 'application/json'},
            data=data,
        )
        try:
            response = urllib.request.urlopen(request)
            return json.loads(response.read().decode('utf-8'))
        except urllib.error.HTTPError as e:
            logger.error(f"HTTP error occurred: {e.code} - {e.reason}")
            raise
        except Exception as e:
            logger.error(f"An error occurred: {str(e)}")
            raise

    def _run(self, text_prompt: str) -> str:
        """Execute the tool's main functionality"""
        # test
        print("run stable diffusion text_prompt:",text_prompt)
        payload = {
            "prompt": text_prompt,
            "negative_prompt": "",
            "seed": 1,
            "steps": 20,
            "width": 512,
            "height": 512,
            "cfg_scale": 7,
            "sampler_name": "DPM++ 2M",
            "n_iter": 1,
            "batch_size": 1,
        }
            
        response = self.call_api('sdapi/v1/txt2img', **payload)
        save_path = None
        for index, image in enumerate(response.get('images', [])):
            save_path = os.path.join(self.out_dir_t2i, f'txt2img-{self.timestamp()}-{index}.png')
            print("image save_path:",save_path)
            self.decode_and_save_base64(image, save_path)
        return save_path or "No image was generated"

