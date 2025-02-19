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
        """调用 LLM 生成 API 调用序列"""
        try:
            messages = [
                {"role": "system", "content": self.context_prompt},
                {"role": "user", "content": prompt}
            ]

            answer = self.client.Think(messages)
            self.logger.info(f"Query: {prompt}, Answer: {answer}")

            return self._parse_llm_response(answer, "api_seq", "malicious_sign_seq")

        except Exception as e:
            self.logger.error(f"Failed to process LLM response: {e}", exc_info=True)
            return [], []

    def query_for_api_explanation(self, prompt):
        """调用 LLM 生成 API 解释"""
        try:
            messages = [
                {"role": "system", "content": self.context_prompt},
                {"role": "user", "content": prompt}
            ]

            answer = self.client.Think(messages)
            self.logger.info(f"Query for API explanation: {prompt}, Answer: {answer}")

            return self._parse_llm_response(answer, "api_seq_exp")

        except Exception as e:
            self.logger.error(f"Failed to process LLM response for API explanation: {e}", exc_info=True)
            return []

    def _parse_llm_response(self, response, *keys):
        """解析 LLM 返回的 JSON"""
        try:
            match = re.search(r"```json\s*(\{.*?\})\s*```", response, re.DOTALL)
            json_str = match.group(1) if match else response

            parsed_data = json.loads(json_str)

            return [parsed_data.get(key, []) for key in keys]

        except json.JSONDecodeError as e:
            self.logger.error(f"JSON decoding error: {e}\nRaw response: {response}", exc_info=True)
            return [[] for _ in keys]

    def gen_api_seq(self, malicious, role):
        """生成 API 调用序列，并返回 API 解释"""
        if role not in self.auth_info_set:
            raise ValueError(f"Invalid role: {role}")

        role_user_index = random.choice(range(len(self.auth_info_set[role])))
        auth_info = self.auth_info_set[role][role_user_index]

        prompt = (
            f"Assume you are a user with the following identity: {auth_info}.\n"
            f"Generate an API call sequence that helps you achieve your goal efficiently.\n"
        )

        if malicious:
            prompt += "However, you will attempt privilege escalation by making unauthorized API calls.\n"

        prompt += (
            "Your response MUST be in JSON format, and you MUST NOT include any explanations.\n"
            "The number of API calls should be sufficient to achieve the goal but not fixed.\n"
            "Example format:\n"
            "```json\n"
            "{\n"
            '  "api_seq": ["API_1", "API_2", "API_3", "API_4"],\n'
            '  "malicious_sign_seq": [0, 0, 1, 0]\n'
            "}\n"
            "```\n"
        )

        seq, malicious_sign_seq = self.query_for_api_seq(prompt)

        exp_prompt = (
            "For the following API sequence, provide a step-by-step explanation of what each API does.\n"
            "Also, indicate whether each API call is legal or illegal based on the user's role.\n"
            "Your response MUST be in JSON format, and you MUST NOT include any explanations outside JSON.\n"
            "Example format:\n"
            "```json\n"
            "{\n"
            '  "api_seq_exp": [\n'
            '    "API_1 - Access system homepage (normal user)",\n'
            '    "API_2 - View user details (normal user)",\n'
            '    "API_3 - Modify system settings (illegal, requires admin)",\n'
            '    "API_4 - Create a new memo (normal user)"\n'
            "  ]\n"
            "}\n"
            "```\n"
            f"API Sequence: {seq}"
        )

        api_seq_exp = self.query_for_api_explanation(exp_prompt)

        return seq, malicious_sign_seq, api_seq_exp[0], role_user_index
