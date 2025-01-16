import json
import random
import logging
from langchain.document_loaders import JSONLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.chains import ConversationalRetrievalChain
from langchain.chat_models import ChatOpenAI
import os

from config.basic import *


class Brain:

    def __init__(self):
        os.environ["OPENAI_API_KEY"] = "YOUR_API_KEY"
        self.chat_history = []

        # 初始化日志记录器
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler = logging.FileHandler(f'./log/{CURR_APP_NAME}_brain_log.log')
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

        # 构建API知识库
        loader = JSONLoader(file_path=f'./knowledge_base/{CURR_APP_NAME}_apis.json', jq_schema='.[]')
        documents = loader.load()
        text_splitter = CharacterTextSplitter(chunk_size=300, chunk_overlap=0)
        texts = text_splitter.split_documents(documents)
        embeddings = OpenAIEmbeddings()
        vectorstore = Chroma.from_documents(texts, embeddings)

        # 初始化大模型
        llm = ChatOpenAI(model_name='gpt-3.5-turbo', temperature=0)
        self.qa_chain = ConversationalRetrievalChain.from_llm(
            llm,
            retriever=vectorstore.as_retriever(search_kwargs={"k": 2})
        )

        # 构建context
        with open(f'./knowledge_base/{CURR_APP_NAME}_knowledge.json', 'r') as f:
            knowledge = json.load(f)
        func_description = knowledge['func_description']
        normal_seqs = knowledge['normal_seqs']
        malicious_seqs = knowledge['malicious_seqs']
        self.auth_info_set = knowledge['auth_info']
        self.context_prompt = (f"假设有一款Web应用，它的功能描述为：\n{str(func_description)}\n"
                               f"应用包含基本的权限检测机制。下面给出一些正常用户和一些恶意越权用户的操作行为示例：\n"
                               f"正常用户的操作行为示例：[\n    {'\n    '.join(normal_seqs)}\n]\n"
                               f"恶意越权用户的操作行为示例：[\n    {'\n    '.join(malicious_seqs)}\n]\n"
                               f"恶意越权用户的操作序列，通常会混杂正常操作与恶意越权操作，也就是试图伪装成善意用户。正常用户的操作序列中，所有操作均为正常操作。"
                               f"你需要利用下面的知识库内容来回答问题。"
                               f"最终输出格式为恰好包含两个列表的列表："
                               f"第一个列表是API调用序列（注意，问题中可能指明了序列的长度），格式为知识库中的API编号列表，例如['API2', 'API1', 'API3']；"
                               f"第二个列表用来标识调用序列中哪些是正常操作，哪些是恶意越权操作，正常用0表示，恶意用1表示，例如[0, 1, 0]。"
                               f"不要输出任何多余的文字描述、解释、换行符等空白字符。最终输出示例：[['API2', 'API1', 'API3'], [0, 1, 0]]")

    def _retry_query(self, answer):
        retry_request = f"你刚刚的回复{answer}: 无法解析成两个列表的列表，请严格按照要求输出"
        new_query = {
            "question": retry_request,
            "chat_history": self.chat_history,
            "context": self.context_prompt
        }
        try:
            new_answer = self.qa_chain.query(new_query)['answer']
            self.chat_history.append((retry_request, new_answer))
            self.logger.info(f"重试查询: Question - {retry_request}, Answer - {new_answer}")
            return new_answer
        except Exception as e:
            self.logger.error(f"重试查询期间出错: {e}", exc_info=True)
            raise

    def query(self, question):
        query = {
            "question": question,
            "chat_history": self.chat_history,
            "context": self.context_prompt
        }
        try:
            answer = self.qa_chain.query(query)['answer']
            self.chat_history.append((question, answer))
            self.logger.info(f"初次查询: Question - {question}, Answer - {answer}")

            retries = 0
            while True:
                try:
                    result_lists = json.loads(answer)
                    api_call_sequence = result_lists[0]
                    malicious_indicator = result_lists[1]
                    if not isinstance(api_call_sequence, list) or not isinstance(malicious_indicator, list):
                        raise TypeError()
                    return api_call_sequence, malicious_indicator
                except Exception:
                    retries += 1
                    if retries > BRAIN_MAX_FORMAT_RETRY:
                        self.logger.error("超过最大重试次数，仍无法获取正确格式的回复")
                        raise ValueError("超过最大重试次数，仍无法获取正确格式的回复")
                    self.logger.error(f"LLM的本次回答无法解析为正确格式: {answer}")
                    answer = self._retry_query(answer)
        except Exception as e:
            self.logger.error(f"初次查询期间出错: {e}", exc_info=True)
            raise

    def gen_api_seq(self, malicious, role, action_step):
        role_user_index = random.choice(range(len(self.auth_info_set[role])))
        auth_info = self.auth_info_set[role][role_user_index]
        if malicious:
            question = (
                f"假设你是{auth_info}，你打破了权限检测机制，可以实现任意你想做的越权行为；作为恶意越权用户，你倾向于伪装成善意的用户。"
                f"请再给我一个可能的API调用序列，长度为{action_step}，实现某个或某些越权行为。")
        else:
            question = (f"假设你是{auth_info}，你可以调用你有权调用的API，来进行某些你想去完成的业务操作。"
                        f"请再给我一个可能的API调用序列，长度为{action_step}，代表正常用户的操作序列。")
        question += "如果可能，尽量保证你的输出与历史输出之间的多样性。以我指定的格式输出。"
        try:
            seq, indexes = self.query(question)
            self.logger.info(f"生成API序列: Question - {question}, Result - {(seq, indexes)}")
            return seq, indexes, role_user_index
        except Exception as e:
            self.logger.error(f"生成API序列期间出错: {e}", exc_info=True)
