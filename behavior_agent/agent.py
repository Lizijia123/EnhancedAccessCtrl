from behavior_agent.brain.brain import Brain
from config.basic import CURR_APP_NAME, NORMAL, VERTICAL_AUTH_OVERREACH, HORIZONTAL_AUTH_OVERREACH
from config.role import APIS_OF_USER_ROLES
from entity.api import API


class Agent:
    """
    项目行为智能体
    """
    _brain = Brain()
    _apis = []

    @classmethod
    def cinit(cls):
        cls._brain = None # TODO
        cls._apis = API.from_api_doc()

    def __init__(self, role, action_step, malicious=False):
        self.role = role
        self.action_step = action_step
        self.malicious = malicious

        self.api_sequence = []
        self.malicious_api_indexes = []
        self.action_type_seq = [] # 0为正常，1为水平越权，2为垂直越权


    def _gen_api_seq(self):
        self.api_sequence, self.malicious_api_indexes = Agent._brain.gen_api_seq(
            malicious=self.malicious,
            role=self.role,
            action_step=self.action_step,
        )

    def exec(self):
        self.api_sequence.clear()
        self._gen_api_seq()

        for index in range(len(self.api_sequence)):
            if index not in self.malicious_api_indexes:
                self.action_type_seq.append(NORMAL)
            else:
                if self.api_sequence[index] in APIS_OF_USER_ROLES[CURR_APP_NAME][self.role]:
                    self.action_type_seq.append(VERTICAL_AUTH_OVERREACH)
                else:
                    self.action_type_seq.append(HORIZONTAL_AUTH_OVERREACH)
