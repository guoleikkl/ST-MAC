import sys


from MTAEval.SrCotFb import MaPereduMTAEval
sys.path.append('/home/zhengy/ScienceDataAnalyze')
import random
from tempSelect import story,question,layer
from glm.glm4ApiEnglish import GLM4ClientEnglish
from glm.glm4ApiEnglishMulti import GLM4ClientEnglishMulti
import re
class MaPeredu:
    def __init__(self, api_key='.SxJFrFnwsR0EDWYj'):
        self.field = 'Computer Science'
        self.api_key = api_key
        self.score = -1
        self.survey_config=[{
            'name':'beginner',
            'cn_name':'入门者',
            'img':'https://peredu-1322695558.cos.ap-beijing.myqcloud.com/survey/beginner.png',
            'key':'7267771776ca4682a254990d74cbdd26.UTRJPpl84DlWwLh8',
            'info':'A beginner is someone who has just started learning a particular field. They have basic concepts and knowledge but lack in-depth understanding and practical experience. Beginners typically need guidance and foundational learning materials to build a more comprehensive knowledge system.'
        },{
            'name':'proficient',
            'cn_name': '熟练者',
            'img': 'https://peredu-1322695558.cos.ap-beijing.myqcloud.com/survey/proficient.png',
            'key':'.oB8tYDZfgCLRmbjB',
            'info':'A proficient individual has some experience in the field and has mastered the basic concepts and common skills, allowing them to independently complete most tasks. While their understanding is deeper than a beginner’s, they may still lack comprehensive knowledge in more complex or advanced topics.'
        },{
            'name':'advanced',
            'cn_name': '进阶者',
            'key':'.IIQOMdcXg0mUHHGE',
            'img': 'https://peredu-1322695558.cos.ap-beijing.myqcloud.com/survey/advanced.png',
            'info':'An advanced individual possesses specialized knowledge in the field, enabling them to understand and solve relatively complex problems. Their knowledge structure is more systematic than that of a proficient individual, and they are continuously expanding and deepening their understanding of the field, though they have not yet reached expert-level depth or breadth.'
        },{
            'name':'expert',
            'cn_name': '专家型',
            'key':'.LxxV5fibjblZdNZa',
            'img': 'https://peredu-1322695558.cos.ap-beijing.myqcloud.com/survey/expert.png',
            'info':'An expert has extensive knowledge and rich experience in the field, allowing them to solve complex and cutting-edge problems. They have a deep mastery of the core principles and can contribute to research, innovation, or guide others in the field. Experts not only grasp the fundamental theories but also contribute to the advancement of knowledge within the domain.'
        },]
    def transToCn(self,content):
        client = GLM4ClientEnglish(self.api_key)
        prompt=f"""
            你是一位专业的翻译专家，擅长将英文文本精准、流畅地翻译成中文。请严格遵循以下要求进行翻译：
                1.	准确性：确保翻译忠实于原文的意思，不遗漏或篡改信息。
                2.	流畅性：翻译后的文本应符合中文表达习惯，自然易读。
                3.	保留语境：根据上下文选择最合适的词语，避免生硬直译。
                4.	专有名词处理：保持专有名词、专业术语的准确性，如有通用翻译则使用标准翻译，否则保持原文或提供解释。
            
            请将以下英文文本翻译成流畅的中文：{content},直接输入中文结果
        """
        result = client.send(prompt,content)
        return result
    def get_field(self,content):
        self.field = 'Computer Science'
    def get_knowleage(self,content):
        field = self.field
        client = GLM4ClientEnglish(self.api_key)
        prompt = f"""
                        You are an expert in {field}. Based on the given text, enrich the content in the following ways:
                        1. Add some background knowledge and embed it into the article.
                        2. When explaining the knowledge points in the article, add some case information.
                        3. For the knowledge points in the article, add some academic descriptions.
                        The output should maintain logical coherence and scientific accuracy, and the output format should be the same as the original text, which is a short passage without special characters.
                        The result should be in English, and directly output the article content.
                        The article to be revised is:{content}
                    """
        result = client.send(prompt=prompt, content=content)
        result_cn = self.transToCn(result)
        return result_cn
    def get_survey(self):
        questionDoc = []
        for index,user in enumerate(self.survey_config):
            user_name = user['name']
            user_key = user['key']
            cn_name = user['cn_name']
            img = user['img']
            info=user['info']

            LLM = GLM4ClientEnglish(user_key)
            prompt = f"""
            You are a knowledge level assessment expert in the {self.field} field, responsible for generating a questionnaire suitable for the "{user_name}"({info}) level. Based on the user's knowledge level, generate 3-4 questions, ensuring the difficulty of the questions matches the knowledge required at that level. Please adjust the content and depth of the questions according to the following knowledge criteria:
                Basic Concepts and Applications: Design a question that asks the user to explain a basic concept and provide an example of its real-world application. For "Advanced" level users, the difficulty of the question should be adjusted accordingly. For example, basic level questions might involve simple definitions and explanations, while more advanced questions can involve more complex background information and application examples.
                Complex Problems and Analysis: Design a question that asks the user to explain a more complex technology or concept and provide a brief analysis. For "Advanced" level users, the question should consider their ability to understand the scope of knowledge and appropriately challenge their analytical skills.
                Technology Selection and Evaluation: Design a question that asks the user how to select the appropriate technology or tool to solve a practical problem. The difficulty of the question will vary based on the user's level; basic level questions may ask about simple selection criteria, while higher-level users should be asked to consider more complex factors and details.
                Future Development and Challenges: Design a question that asks the user to discuss the future direction or potential challenges of a technology or field. For users at higher knowledge levels, more challenging questions should be asked, requiring them to consider cutting-edge developments and future trends in the field.
                Question 1: 
                Question 2: 
                Question 3: 
                Question 4: 
            Please ensure that the difficulty of the questions matches the knowledge level of the ‘Advanced’ category to accurately assess their ability."""
            content = 'Return the questionnaire that belongs to your knowledge level according to the format.'
            result = LLM.send(prompt=prompt,content=content)
            result_cn = self.transToCn(result)
            # 正则表达式，匹配以“问题X：”开头的每个问题
            # print(result_cn)
            pattern = r"问题[1-4]：([^问题]+)"
            has = random.randint(0, 4)
            # 使用 re.findall() 查找所有匹配的文本
            questions = re.findall(pattern, result_cn)
            survey={
                'name':cn_name,
                'img':img,
                'questions':questions,
                'has':has
            }
            print(result_cn)
            questionDoc.append(survey)

        return questionDoc
    def analyzeDoc(self,content):
        client = GLM4ClientEnglishMulti(self.api_key)
        result = MaPereduMTAEval(client,'1',content)
        result_cn = {
                "ID": '1',
                "document": content,
                "SR_COT_FB_agent1_1": self.transToCn(result['SR_COT_FB_agent1_1']),
                "SR_COT_FB_Reflection1_1": self.transToCn(result['SR_COT_FB_Reflection1_1']),
                "SR_COT_FB_agent1_2": self.transToCn(result['SR_COT_FB_agent1_2']),
                "SR_COT_FB_Reflection1_2": self.transToCn(result['SR_COT_FB_Reflection1_2']),
                "Feedback_1": self.transToCn(result['Feedback_1']),
                "SR_COT_FB_agent2_1": self.transToCn(result['SR_COT_FB_agent2_1']),
                "SR_COT_FB_Reflection2_1": self.transToCn(result['SR_COT_FB_Reflection2_1']),
                "SR_COT_FB_agent2_2": self.transToCn(result['SR_COT_FB_agent2_2']),
                "SR_COT_FB_Reflection2_2": self.transToCn(result['SR_COT_FB_Reflection2_2']),
                "Feedback_2": self.transToCn(result['Feedback_2']),
                "SR_COT_FB_agent3_1": self.transToCn(result['SR_COT_FB_agent3_1']),
                "SR_COT_FB_Reflection3_1":self.transToCn(result['SR_COT_FB_Reflection3_1']),
                "SR_COT_FB_agent3_2": self.transToCn(result['SR_COT_FB_agent3_2']),
                "SR_COT_FB_Reflection3_2": self.transToCn(result['SR_COT_FB_Reflection3_2']),
                "SR_COT_FB_agent_summary": self.transToCn(result['SR_COT_FB_agent_summary']),
                "final_score":self.transToCn(result['final_score']),
                "text_summary": self.transToCn(result['text_summary']),
        }
        return result_cn
    def styleChange(self,content):
        client = GLM4ClientEnglish(self.api_key)
        updateKnowledge = content
        if self.score == -1:
            self.score = self.get_score(content)
        popsciDoc = ''
        if self.score >= 1 and self.score <= 3:
            # 1-3
            popsciDoc = story(updateKnowledge, self.score - 1, client)
        elif self.score >= 4 and self.score <= 7:
            # 1-4
            popsciDoc = question(updateKnowledge, self.score - 3, client)
        elif self.score >= 8 and self.score <= 10:
            # 1-3
            popsciDoc = layer(updateKnowledge, self.score - 7, client)

        result = self.transToCn(popsciDoc)
        return result

    def get_score(self,content):
        updateKnowledge = content
        prompt = f"""
            You are an expert in popular science content analysis, responsible for evaluating the complexity of the following article. Please rate the complexity according to the following dimensions:
            Language simplicity: Does the article use simple and easy - to - understand language? Does it avoid excessive technical terms?
            Sentence structure: Is the sentence structure complex? What is the ratio of long sentences to short sentences? And how complex are the sentences?Use of technical terms: Does the article use a large number of technical terms? Are these terms explained in detail?
            Paragraph structure and content organization: Does the article adopt a narrative structure, a problem - driven approach, or a logical progression? If it clearly uses a narrative approach, the final score should be between 1 - 3; if it clearly uses a problem - driven approach, the final score should be between 4 - 7; if it clearly uses a logical progression, the final score should be between 8 - 10. 1 represents the simplest and 10 represents the most complex.
            Please directly tell me the score from 1 to 10, no need to state the reasons. The content of the article is: {updateKnowledge}
        """
        client = GLM4ClientEnglish(self.api_key)
        result = client.send(prompt=prompt, content=updateKnowledge)
        if '1' in result and '0' not in result:
            score = 1
        elif '2' in result:
            score = 2
        elif '3' in result:
            score = 3
        elif '4' in result:
            score = 4
        elif '5' in result:
            score = 5
        elif '6' in result:
            score = 6
        elif '7' in result:
            score = 7
        elif '8' in result:
            score = 8
        elif '9' in result:
            score = 9
        elif '10' in result:
            score = 10
        self.score = score
        return score


if __name__ == '__main__':
    demo = MaPeredu()
    content = """ <h2>人工智能、机器学习与深度学习的关系</h2>
  
      <p>人工智能（Artificial Intelligence，AI）、机器学习（Machine Learning，ML）和深度学习（Deep Learning，DL）是现代智能技术领域的重要概念，它们既相互关联，又各具特点，形成了一种层级递进的关系。</p>
    
      <h3>1. 人工智能（AI）：智能系统的总体概念</h3>
      <p>人工智能是计算机科学的一个分支，旨在研究如何让机器模拟和实现人类智能，包括理解自然语言、视觉识别、决策制定、问题求解等能力。AI 的目标是让计算机能够执行通常需要人类智能才能完成的任务，如自动驾驶、语音识别、医疗诊断等。</p>
    
      <h4>AI 可分为两类：</h4>
      <ul>
        <li><strong>弱人工智能（Narrow AI）</strong>：专注于特定任务，如智能语音助手（如 Siri、Alexa）、推荐系统、智能客服等。</li>
        <li><strong>强人工智能（General AI）</strong>：具备类似人类的通用智能，能够自主学习、推理和适应不同环境，但目前仍处于研究阶段。</li>
      </ul>
    
      <h3>2. 机器学习（ML）：实现人工智能的重要途径</h3>
      <p>机器学习是人工智能的一个子集，它指的是通过数据训练，使计算机能够自动学习和改进，而无需显式编程。机器学习的核心在于算法能够基于数据进行模式识别，并进行预测或决策。</p>
    
      <h4>常见的机器学习方法包括：</h4>
      <ul>
        <li><strong>监督学习</strong>：使用带有标签的数据进行训练，如图像分类、语音识别等。</li>
        <li><strong>无监督学习</strong>：对无标签数据进行模式发现，如聚类分析、降维等。</li>
        <li><strong>强化学习</strong>：通过奖励机制学习最佳策略，如 AlphaGo 通过强化学习掌握围棋。</li>
      </ul>
    
      <h3>3. 深度学习（DL）：机器学习的进阶形式</h3>
      <p>深度学习是机器学习的一个子集，主要基于<strong>人工神经网络</strong>（Artificial Neural Networks, ANN）模拟人脑的神经结构，从大量数据中学习特征，并进行复杂的任务处理。</p>
    
      <h4>深度学习的关键技术：</h4>"""
    updateKnowledge = """
    人工智能（AI）、机器学习（ML）和深度学习（DL）的融合彻底改变了智能系统领域，它们各自在技术进步的进程中扮演着独特的角色。<h2>人工智能、机器学习和深度学习：理解它们之间的关系</h2><p>人工智能（AI）、机器学习（ML）和深度学习（DL）是现代智能技术领域的关键概念。它们相互关联，各具特色，形成了一种层次递进的关系。</p><h3>1. 人工智能（AI）：智能系统的总体概念</h3><p>人工智能是计算机科学的一个分支，致力于使机器能够模拟并实现人类智能，包括自然语言理解、视觉识别、决策和问题解决等能力。人工智能的目标是使计算机能够执行通常需要人类智能的任务，如自动驾驶、语音识别和医疗诊断。</p><h4>人工智能可以分为两种类型：</h4><ul>  <li><strong>窄人工智能（弱人工智能）</strong>：专注于特定任务，如智能语音助手（例如，Siri、Alexa）、推荐系统和智能客户服务。</li>  <li><strong>通用人工智能（强人工智能）</strong>：具有类似于人类的通用智能，能够学习、推理和适应不同的环境。然而，通用人工智能仍处于研究阶段。</li></ul><h3>2. 机器学习（ML）：实现人工智能的关键方法</h3><p>机器学习是人工智能的一个子集，指的是训练计算机自动学习和改进的过程，而不需要明确的编程。机器学习的核心在于能够从数据中识别模式并做出预测或决策的算法。</p><h4>常见的机器学习方法包括：</h4><ul>  <li><strong>监督学习</strong>：使用标记数据进行训练，如图像分类和语音识别。</li>  <li><strong>无监督学习</strong>：在未标记数据中发现模式，如聚类分析和降维。</li>  <li><strong>强化学习</strong>：通过奖励机制学习最佳策略，如AlphaGo通过强化学习掌握围棋。</li></ul><h3>3. 深度学习（DL）：机器学习的高级形式</h3><p>深度学习是机器学习的一个子集，主要依赖于模拟人脑神经结构的<strong>人工神经网络（ANNs）</strong>。它从大量数据集中学习特征，并执行复杂任务处理。</p><h4>深度学习的关键技术包括：</h4><ul>  <li><strong>神经网络</strong>：一系列试图通过模拟人脑运作方式来识别数据集中潜在关系的算法。</li>  <li><strong>反向传播</strong>：用于训练神经网络的算法，通过调整网络的权重和偏差来最小化预测输出与实际输出之间的误差。</li>  <li><strong>卷积神经网络（CNNs）</strong>：一类深度神经网络，特别适合分析视觉图像。</li>  <li><strong>循环神经网络（RNNs）</strong>：一类能够识别数据序列中模式（如时间序列或自然语言）的神经网络。</li></ul>从人工智能到机器学习再到深度学习的演变，代表了智能系统能力的重大飞跃，深度学习在处理复杂和大规模数据分析任务方面尤其强大。这为医疗保健、金融和自动驾驶等领域的发展铺平了道路，在这些领域中，处理和解释大量数据的能力至关重要。
    """
    style_change_content = """
    您是否曾想过，机器如何模仿人类智能并执行通常需要人类认知能力的任务？人工智能（AI）、机器学习（ML）和深度学习（DL）这三个领域已经彻底改变了智能系统的领域，每个领域都在技术进步中扮演着独特的角色。但这三个概念之间究竟有何关系呢？让我们深入探讨AI、ML和DL的复杂性。什么是人工智能（AI），它与人类智能有何不同？人工智能是计算机科学的一个分支，旨在使机器能够模拟并实现人类智能，包括自然语言理解、视觉识别、决策和解决问题的能力。AI的目标是使计算机能够执行通常需要人类智能的任务，如自动驾驶、语音识别和医疗诊断。AI可以分为两种类型：窄AI（弱AI）和通用AI（强AI）。窄AI专注于特定任务，例如智能语音助手（如Siri、Alexa）、推荐系统和智能客户服务。另一方面，通用AI拥有类似于人类的通用智能，能够学习、推理和适应各种环境。然而，通用AI目前仍处于研究阶段。机器学习（ML）是如何有助于实现AI的？机器学习是AI的一个子集，指的是训练计算机自动学习和改进的过程，而不需要明确的编程。ML的核心在于算法能够识别数据中的模式并做出预测或决策。常见的ML方法包括：- 监督学习：使用标记数据进行训练，如图像分类和语音识别。- 无监督学习：在未标记数据中发现模式，如聚类分析和降维。- 强化学习：通过奖励机制学习最佳策略，如AlphaGo通过强化学习掌握围棋。什么是深度学习（DL），它是如何推进机器学习的？深度学习是ML的一个子集，主要依赖于模拟人脑结构的神经网络。DL从大量数据集中学习特征，并执行复杂的任务处理。DL的关键技术包括：- 神经网络：通过模拟人脑功能尝试识别数据中潜在关系的算法。- 反向传播：一种通过调整权重和偏差来最小化预测输出与实际输出之间误差的算法。- 卷积神经网络（CNN）：一种特别适合分析视觉图像的深度神经网络。- 循环神经网络（RNN）：一种能够识别数据序列（如时间序列或自然语言）中模式的神经网络。从AI到ML再到DL的演变代表了智能系统能力的一次重大飞跃。DL在处理复杂和大规模数据分析任务方面特别强大，为医疗保健、金融和自动驾驶等领域的发展铺平了道路，在这些领域，处理和解释大量数据的能力至关重要。总之，AI、ML和DL是相互关联的概念，它们相互构建，形成一个层次结构。理解它们之间的关系和功能对于欣赏智能系统领域的进步和它们对未来所持有的潜力至关重要。
    """
    print(demo.analyzeDoc(style_change_content))
