import json
import random
import config.basic

from algorithm.brain import Brain
from config.log import LOGGER
from config.role import APIS_OF_USER_ROLES


class Agent:
    """
    项目行为智能体
    """
    brain = None
    apis = []

    @classmethod
    def cinit(cls, api_list, api_knowledge, app_knowledge):
        cls.brain = Brain(config.basic.LLM_MODEL_NAME, api_knowledge, app_knowledge)
        cls.apis = api_list

    def __init__(self, role, action_step, malicious=False, unlogged=False):
        self.role = role
        self.action_step = action_step
        self.malicious = malicious
        self.unlogged = unlogged

        self.api_sequence = []
        self.api_malicious_seq = []
        self.action_type_seq = []  # 0为正常，1为水平越权，2为垂直越权

    def _gen_api_seq(self):
        # role_user_index表示brain生成的API seq对应的用户是哪个身份下的哪种类型
        self.api_sequence, self.api_malicious_seq = Agent.brain.gen_api_seq(
            malicious=self.malicious,
            role=self.role,
            action_step=self.action_step,
        )
        # 选取当前用户的用户名，后续基于此用户名的cookie进行参数填充并生成具体流量
        LOGGER.info(config.basic.LOGIN_CREDENTIALS)
        self.uname = random.choice([item['username'] for item in config.basic.LOGIN_CREDENTIALS if item['user_role'] == self.role])

    def exec(self):
        self.api_sequence.clear()
        self._gen_api_seq()

        for index in range(len(self.api_sequence)):
            if self.api_malicious_seq[index] == 0:
                self.action_type_seq.append(config.basic.NORMAL)
            else:
                if self.api_sequence[index] in APIS_OF_USER_ROLES[self.role]:
                    self.action_type_seq.append(config.basic.VERTICAL_AUTH_OVERREACH)
                else:
                    self.action_type_seq.append(config.basic.HORIZONTAL_AUTH_OVERREACH)

    @classmethod
    def deserialize(cls, data):
        # 从字典中恢复 Agent 实例
        agent = cls(
            role=data["role"],
            action_step=data["action_step"],
            malicious=data["malicious"],
            unlogged=data["unlogged"]
        )
        agent.api_sequence = data["api_sequence"]
        agent.api_malicious_seq = data["api_malicious_seq"]
        agent.action_type_seq = data["action_type_seq"]
        if "uname" in data:
            agent.uname = data["uname"]
        return agent

    def serialize(self):
        # 将 Agent 实例转换为可序列化的字典
        serialized = {
            "role": self.role,
            "action_step": self.action_step,
            "malicious": self.malicious,
            "unlogged": self.unlogged,
            "api_sequence": self.api_sequence,
            "api_malicious_seq": self.api_malicious_seq,
            "action_type_seq": self.action_type_seq,
            "uname": getattr(self, "uname", None)
        }
        return serialized


def save_agents_to_file(agents, file_path):
    """
    将多个 Agent 对象存储到文件中
    :param agents: Agent 对象列表
    :param file_path: 存储文件的路径
    """
    serialized_agents = [agent.serialize() for agent in agents]
    with open(file_path, 'w') as f:
        json.dump(serialized_agents, f)


def load_agents_from_file(file_path):
    """
    从文件中读取多个 Agent 对象
    :param file_path: 存储文件的路径
    :return: Agent 对象列表
    """
    try:
        with open(file_path, 'r') as f:
            serialized_agents = json.load(f)
        return [Agent.deserialize(agent_data) for agent_data in serialized_agents]
    except FileNotFoundError:
        LOGGER.error(f"文件 {file_path} 未找到。")
        return []

