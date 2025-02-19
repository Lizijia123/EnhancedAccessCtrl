import sys
import os
import json
import random
import logging
import re

# 自动添加 LLM.py 所在的路径，防止 ModuleNotFoundError
current_dir = os.path.dirname(os.path.abspath(__file__))
thoughts_dir = os.path.join(current_dir, "Thoughts")
sys.path.append(thoughts_dir)

from LLM import GPTClient, QwenClient, DeepSeekClient, LlamaClient

class Brain:
    def __init__(self, model_name, project_name):
        """初始化 Brain 实例"""
        self.project_name = project_name
        self.client = self._select_client(model_name)
        self.chat_history = []

        # 初始化日志
        self.logger = self.setup_logger()

        # 加载知识库
        self.load_knowledge()

    def _select_client(self, model_name):
        """选择对应的 LLM Client"""
        model_mapping = {
            "gpt-4o-mini": GPTClient,
            "qwen-max": QwenClient,
            "deepseek-r1": DeepSeekClient,
            "llama3.3-70b-instruct": LlamaClient,
        }

        if model_name not in model_mapping:
            raise ValueError(f"Unsupported model name: {model_name}")

        return model_mapping[model_name](model_name=model_name)

    def setup_logger(self):
        """配置日志"""
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)

        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

        file_handler = logging.FileHandler(f'./log/brain_log.log')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        return logger

    def load_knowledge(self):
        """加载知识库"""
        try:
            api_file = f'./knowledge_base/{self.project_name}_apis.json'
            knowledge_file = f'./knowledge_base/{self.project_name}_knowledge.json'

            if not os.path.exists(api_file):
                raise FileNotFoundError(f"API config file {api_file} not found")
            if not os.path.exists(knowledge_file):
                raise FileNotFoundError(f"Knowledge base file {knowledge_file} not found")

            with open(api_file, 'r') as f:
                self.documents = json.load(f)

            with open(knowledge_file, 'r') as f:
                knowledge = json.load(f)

            self.func_description = knowledge['func_description']
            self.normal_seqs = knowledge['normal_seqs']
            self.malicious_seqs = knowledge['malicious_seqs']
            self.auth_info_set = knowledge['auth_info']
            self.context_prompt = self.build_context_prompt()
        except Exception as e:
            self.logger.error(f"Failed to load knowledge base: {e}", exc_info=True)
            raise

    def build_context_prompt(self):
        """构造上下文提示"""
        return (
            f"Imagine a web application with the following functionality:\n{self.func_description}\n"
            f"The application has basic permission control mechanisms. Below are some examples of user behaviors:\n"
            f"Normal user behavior examples: {self.normal_seqs}\n"
            f"Malicious privilege escalation behavior examples: {self.malicious_seqs}\n"
            f"Malicious users often mix normal operations with unauthorized actions.\n"
            f"Your task is to generate an API call sequence based on user roles and behavior patterns.\n"
            f"The response must only be in JSON format: {{'api_seq': ['API_1', 'API_3'], 'malicious_sign_seq': [0,1]}}"
        )

    def query_for_api_seq(self, prompt):
        """调用 LLM 生成 API 调用序列，确保返回符合 gen_api_seq 需要的格式"""
        try:
            messages = [
                {"role": "system", "content": self.context_prompt},
                {"role": "user", "content": prompt}
            ]

            answer = self.client.Think(messages)
            self.logger.info(f"Query: {prompt}, Answer: {answer}")

            # 调用专门的解析方法
            return self._parse_llm_response_for_api_seq(answer)

        except Exception as e:
            self.logger.error(f"Failed to process LLM response: {e}", exc_info=True)
            return [], []  # 确保返回空列表，防止 unpack 失败

    def _parse_llm_response_for_api_seq(self, response):
        """解析 LLM 返回的 JSON，确保符合 gen_api_seq 需要的格式"""
        try:
            # 1. 使用正则找到 ```json ... ``` 之间的内容
            match = re.search(r"```json\s*(\{.*?\})\s*```", response, re.DOTALL)
            if match:
                json_str = match.group(1)  # 提取 JSON 字符串
            else:
                json_str = response  # 如果没有 ```json 包裹，直接尝试解析整个返回内容

            # 2. 解析 JSON
            parsed_data = json.loads(json_str)

            # 3. 确保返回数据格式正确
            if isinstance(parsed_data, dict) and "api_seq" in parsed_data and "malicious_sign_seq" in parsed_data:
                return parsed_data["api_seq"], parsed_data["malicious_sign_seq"]

            raise ValueError("Unexpected response format from LLM")

        except json.JSONDecodeError as e:
            self.logger.error(f"JSON decoding error: {e}\nRaw response: {response}", exc_info=True)
            return [], []  # 返回空列表，防止 unpack 失败

    def gen_api_seq(self, malicious, role, action_step):
        """生成 API 调用序列，确保返回 3 个值"""
        if role not in self.auth_info_set:
            raise ValueError(f"Invalid role: {role}")

        role_user_index = random.choice(range(len(self.auth_info_set[role])))
        auth_info = self.auth_info_set[role][role_user_index]

        # **构造 LLM 提示**
        prompt = (
            f"Assume you are a user with the following identity: {auth_info}.\n"
            f"You need to generate an API call sequence with approximately {action_step} steps.\n"
        )

        if malicious:
            prompt += "However, you will attempt privilege escalation by making unauthorized API calls.\n"

        prompt += (
            "Your response MUST be in the following JSON format, and you MUST NOT include any explanations:\n"
            "```json\n"
            "{\n"
            '  "api_seq": ["API_1", "API_3", "API_5"],\n'
            '  "malicious_sign_seq": [0, 1, 0]\n'
            "}\n"
            "```\n"
        )

        # **调用 query_for_api_seq**
        seq, malicious_sign_seq = self.query_for_api_seq(prompt)

        # **确保返回格式正确**
        if not isinstance(seq, list) or not isinstance(malicious_sign_seq, list):
            self.logger.error(f"Invalid LLM response format: seq={seq}, malicious_sign_seq={malicious_sign_seq}")
            seq, malicious_sign_seq = [], []  # **防止 `NoneType` 错误**

        return seq, malicious_sign_seq, role_user_index
