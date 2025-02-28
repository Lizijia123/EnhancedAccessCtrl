import json
from brain_no_LC import Brain  # 确保 `brain_no_LC.py` 在 `test_brain.py` 可导入的路径下


def test_brain():
    """ 测试 Brain 类的基本功能 """
    print("===== 测试 Brain 初始化 =====")

    # 选择不同的 LLM 模型进行测试
    model_names = ["deepseek-v3"] #"gpt-4o-mini", # "qwen-max",  "llama3.3-70b-instruct"
    project_names = ["humhub", "memos", "collegeerp"]  # 你的项目名称

    for project in project_names:
        for model in model_names:
            print(f"\n[+] 正在测试项目: {project}, 模型: {model}")
            try:
                # 初始化 Brain 实例
                brain = Brain(model_name=model, project_name=project)
                print("[✓] Brain 初始化成功")

                # 测试 gen_api_seq 方法
                print("[+] 生成 API 调用序列...")
                api_seq, malicious_sign_seq, role_user_index = brain.gen_api_seq(malicious=False, role="admin",
                                                                                 action_step=3)
                print("[✓] gen_api_seq() 方法返回:", api_seq, malicious_sign_seq, role_user_index)

                # 确保返回值类型正确
                assert isinstance(api_seq, list), "API 调用序列应该是列表"
                assert isinstance(malicious_sign_seq, list), "恶意标记序列应该是列表"
                assert isinstance(role_user_index, int), "角色用户索引应该是整数"
                assert all(isinstance(i, str) for i in api_seq), "API 调用序列应该包含字符串"
                assert all(i in [0, 1] for i in malicious_sign_seq), "恶意标记应该是 0 或 1"

                print(f"[✓] {project} - {model} 通过所有测试")

            except Exception as e:
                print(f"[✗] {project} - {model} 测试失败: {e}")


if __name__ == "__main__":
    test_brain()
