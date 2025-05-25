# pip install zhipuai 请先在终端进行安装

from zhipuai import ZhipuAI
class GLM4Client:
    def __init__(self, api_key):
        self.client = ZhipuAI(api_key=api_key)
    def send(self, prompt,content):
        try:
            # 如果内容超过4095个字符，进行截断
            if len(content) > 4095:
                content = content[:4095]
            response = self.client.chat.completions.create(
                model="glm-4-flash",
                messages=[
                    {
                        "role": "system",
                        "content": f"{prompt}"
                    },
                    {
                        "role": "user",
                        "content": f"{content}"
                    }
                ],
                top_p=0.7,
                temperature=0.95,
                max_tokens=1024,
                tools=[{"type": "web_search", "web_search": {"search_result": True}}],
                stream=True
            )

            result = ""
            for trunk in response:
                for choice in trunk.choices:
                    content = choice.delta.content.replace('\n', '').strip()
                    result += content
            return result

        except Exception as e:
            print(f"Error processing prompt: {e}")
            return None



if __name__ == '__main__':
    # 使用示例
    prompt = "你是一个信息提取专家，你的任务是帮我对科普文章进行内容摘要，先确保科普文章的知识含量，然后对超过500字的文章进行摘要，我将告诉你文本。"
    content = "接口测试"
    glm4_client = GLM4Client()
    result = glm4_client.send(prompt,content)
    print(result)