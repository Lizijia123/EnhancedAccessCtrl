
from http import HTTPStatus
import dashscope

def qwen_bot_invoke(prompt):
    response = dashscope.Generation.call(model='qwen-turbo', prompt=prompt)
    if response.status_code == HTTPStatus.OK:
        # TODO: 记录日志
        return response.output["text"]


class Brain:

    # TODO：初始化
    def __init__(self):
        dashscope.api_key = "sk-3c4ef494f412425eb8b75588d354f8fa"


    # TODO：生成某个角色为role的用户的行为序列，长度为action_step；其中包含的恶意行为的个数为malicious_step
    #  返回调用的API编号序列，以及序列中的恶意行为索引
    def gen_api_sequence(self,role,action_step,malicious_step=0):
        if malicious_step == 0:
            return ['API_1', 'API_3'], []
        else:
            return ['API_1', 'API_2', 'API_3'], [1]

