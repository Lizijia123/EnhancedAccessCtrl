import random

from algorithm.brain import Brain
from config.basic import *
from config.role import APIS_OF_USER_ROLES


class Agent:
    """
    项目行为智能体
    """
    brain = None
    apis = []

    @classmethod
    def cinit(cls, api_list, api_knowledge, app_knowledge):
        cls.brain = Brain(api_knowledge, app_knowledge)
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
        self.uname = random.choice([item['username'] for item in LOGIN_CREDENTIALS if item['user_role'] == self.role])

    def exec(self):
        self.api_sequence.clear()
        self._gen_api_seq()

        for index in range(len(self.api_sequence)):
            if self.api_malicious_seq[index] == 0:
                self.action_type_seq.append(NORMAL)
            else:
                if self.api_sequence[index] in APIS_OF_USER_ROLES[self.role]:
                    self.action_type_seq.append(VERTICAL_AUTH_OVERREACH)
                else:
                    self.action_type_seq.append(HORIZONTAL_AUTH_OVERREACH)
