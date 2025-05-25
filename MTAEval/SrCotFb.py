import sys

sys.path.append('/home/zhengy/ScienceDataAnalyze')
import logging
from datetime import datetime

log_filename = datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(levelname)s: %(message)s',
                    handlers=[
                        logging.StreamHandler(),
                        logging.FileHandler(f'sci_classify_logfile_{log_filename}.log',encoding='utf-8')
                    ])


ROLE = 'assistant'
USER_ROLE = 'user'
PROMPT = f'you are {ROLE}.'

def SR_COT_FB_1_1(LLM_Client,story_content, messages):
    prompt = f"""
    “{story_content}”
    To ensure the quality of the text, we have invited two evaluators to conduct a comprehensive assessment of the aforementioned text: Mike and John. You are Mike. Please evaluate the text based on the following eight dimensions:

    1. Repetition: Identical content appearing multiple times in the text.
    2. Logical Inconsistency: Contradictory or logically flawed statements within the text.
    3. Discontinuity: Sudden topic shifts or missing information that disrupts coherence.
    4. Scientific Lexical Choice: The use of scientific terms should be precise and aligned with proper scientific writing conventions.
    5. Scientific Accuracy: Statements that contradict widely accepted scientific knowledge or present misleading information.
    6. Scientific Popularization: The extent to which the article effectively explains scientific concepts through clear explanations, examples, or analogies.
    7. Scientific Coherence: Whether the information follows a logical order, progressing step by step to aid comprehension, avoiding abrupt jumps or missing links in explanation.
    8. Engagement & Readability: The degree to which the article is engaging and accessible, using narrative techniques, questions, or storytelling to maintain reader interest.

    In our evaluation, each error results in a deduction of one point, starting from zero. 
    - "Scientific Lexical Choice" considers whether terminology is used correctly and professionally.
    - "Scientific Accuracy" refers to statements in the article that contradict established scientific facts.
    - "Repetition Issues" (exact duplication of content) are only penalized once, regardless of the number of occurrences.

    Now, let's think step by step.
    What do you believe are the two most discussable issues in the aforementioned text? Please first assess the text focusing on these two issues.
    """
    if len(prompt)>4095:
        prompt = prompt[:4095]
    d = {"role": "user", "content": prompt}
    messages.append(d)
    retries = 20
    while retries > 0:
        try:
            result = LLM_Client.send(messages)
            return result
        except (UnboundLocalError, KeyError) as e:
            print(f"Error occurred: {e}. Retrying...")
            retries -= 1
    raise Exception("Failed after multiple retries.")


# 自我反思
def Self_Reflection_key(LLM_Client,messages):
    prompt = f"""
    Regarding the scientific article previously discussed, I would like you to carefully reconsider and verify whether the issues you identified indeed exist. Are there other places where this type of problem appears? 
    Please note that errors may occur multiple times throughout the text. For example, logical inconsistencies or scientific inaccuracies may be present in different sections. 
    Additionally, consider whether the scientific explanations are clear, logically structured, and engaging for the intended audience. If necessary, refer to and draw inspiration from another assessor's remarks to reflect on your own evaluation.
    If such problems do exist, please amend your assessment of the article accordingly.
    """
    if len(prompt)>4095:
        prompt = prompt[:4095]
    d = {"role": "user", "content": prompt}
    messages.append(d)
    retries = 20
    while retries > 0:
        try:
            result = LLM_Client.send(messages)
            return result
        except (UnboundLocalError, KeyError) as e:
            print(f"Error occurred: {e}. Retrying...")
            retries -= 1
    raise Exception("Failed after multiple retries.")

# 第二位评估
def SR_COT_FB_1_2(LLM_Client,story_content, context, reflection, messages):
    prompt = f"""
    “{story_content}”
    Hi John. The aforementioned article awaits evaluation by both you and another evaluator, Mike. You both are required to deeply assess the text from the following dimensions:

    1. Repetition: Identical content appearing multiple times in the text.
    2. Logical Inconsistency: Contradictory or logically flawed statements within the text.
    3. Discontinuity: Sudden topic shifts or missing information that disrupts coherence.
    4. Scientific Lexical Choice: Inappropriate use of terms, quantifiers, or verbs, especially when the level of terminology is either too complex for the intended audience or oversimplified to the point of inaccuracy.
    5. Scientific Accuracy: Statements that contradict widely accepted scientific knowledge or present misleading information.
    6. Scientific Popularization: The extent to which the article effectively explains scientific concepts through clear explanations, examples, or analogies.
    7. Scientific Coherence: Whether the information follows a logical order, progressing step by step to aid comprehension, avoiding abrupt jumps or missing links in explanation.
    8. Engagement & Readability: The degree to which the article is engaging and accessible, using narrative techniques, questions, or storytelling to maintain reader interest.

    In our evaluation, each error results in a deduction of one point, starting from zero. 
    - "Scientific Lexical Choice" considers whether terminology is used correctly and professionally.
    - "Scientific Accuracy" refers to statements in the article that contradict established scientific facts.
    - "Repetition Issues" (exact duplication of content) are only penalized once, regardless of the number of occurrences.

    Currently, we will only discuss the two most prominent issues. Here are Mike's views on these two issues:
    "{context}"
    "\n"
    "{reflection}"
    Do you have any differing opinions concerning these dimensions? Please provide your analysis, especially regarding scientific clarity, logical flow, and reader engagement.
    """
    if len(prompt)>4095:
        prompt = prompt[:4095]
    d = {"role": "user", "content": prompt}
    messages.append(d)
    retries = 20
    while retries > 0:
        try:
            result = LLM_Client.send(messages)
            return result
        except (UnboundLocalError, KeyError) as e:
            print(f"Error occurred: {e}. Retrying...")
            retries -= 1
    raise Exception("Failed after multiple retries.")

def feed_back(LLM_Client,history, messages):
    prompt = f"""
    "{history}"
    As evaluator July, please conduct a comprehensive assessment of this round of discussion. (The word count must be controlled at 150 tokens)
    1. Were there any omissions or misunderstandings in the evaluation process, especially regarding scientific accuracy, logical coherence, or readability?  
    2. Were there any redundant or irrelevant dialogues that did not contribute to evaluating the scientific and educational quality of the text?  
    3. What areas do you suggest improving for the next round? Should there be more focus on explaining scientific concepts, enhancing logical flow, or improving engagement strategies?  
    If there are disagreements on a certain issue, guide the evaluators to reach a consensus in the next round, aiming to minimize differences while maintaining objective and scientifically valid judgments.  
    Please provide a holistic evaluation and specific recommendations to refine the quality of the discussion and improve the evaluation process in the next round.
    """
    if len(prompt)>4095:
        prompt = prompt[:4095]
    d = {"role": "user", "content": prompt}
    messages.append(d)
    retries = 20
    while retries > 0:
        try:
            result = LLM_Client.send(messages)
            return result
        except (UnboundLocalError, KeyError) as e:
            print(f"Error occurred: {e}. Retrying...")
            retries -= 1
    raise Exception("Failed after multiple retries.")

def SR_COT_FB_2_1(LLM_Client,feedback, messages):
    # prompt = f"""
    #     Hello Mike, During the last round of discussions, an evaluator provided the following suggestions for discussion:
    #     "{feedback}"
    #     Take his advice and address it in this round of discussion.
    #     Next, in addition to the two main issues previously considered, we need to contemplate two additional aspects from the following: 'Repetition', 'Logical Inconsistency', 'Discontinuity', 'Inappropriate Lexical Choice', and 'Factual Error'.
    #     Please proceed with your analysis.
    #     """
    prompt = f"""
    Hello Mike,  
    During the last round of discussions, an evaluator provided the following suggestions for discussion:  
    "{feedback}"  
    Please incorporate this feedback into your analysis in this round.  
    Next, in addition to the two main issues previously considered, we need to examine two additional aspects from the following:  
    - Repetition: Are there instances of unnecessary repetition in the text that do not contribute to clarity?  
    - Logical Inconsistency: Are there any contradictions or logical flaws in the scientific explanations?  
    - Discontinuity: Does the article have abrupt shifts that disrupt the logical flow of scientific concepts?  
    - Scientific Lexical Choice: Are the scientific terms used correctly, and do they align with standard scientific writing conventions?  
    - Scientific Accuracy: Are all claims in the article factually correct and aligned with current scientific consensus?  
    Please proceed with your analysis.
    """
    if len(prompt)>4095:
        prompt = prompt[:4095]
    d = {"role": "user", "content": prompt}
    messages.append(d)
    retries = 20
    while retries > 0:
        try:
            result = LLM_Client.send(messages)
            return result
        except (UnboundLocalError, KeyError) as e:
            print(f"Error occurred: {e}. Retrying...")
            retries -= 1

    raise Exception("Failed after multiple retries.")

def SR_COT_FB_2_2(LLM_Client,feedback, context, reflection, messages):
    prompt = f"""
    Hi John,  
    During the last round of discussions, an evaluator provided the following suggestions for discussion:  
    "{feedback}"  
    Please incorporate this feedback into your analysis in this round.  
    Next, in addition to the two main issues previously considered, we need to examine two additional aspects from the following:  
    - Repetition: Are there instances of unnecessary repetition in the text that do not contribute to clarity?  
    - Logical Inconsistency: Are there any contradictions or logical flaws in the scientific explanations?  
    - Discontinuity: Does the article have abrupt shifts that disrupt the logical flow of scientific concepts?  
    - Scientific Lexical Choice: Are the scientific terms used correctly, and do they align with standard scientific writing conventions?  
    - Scientific Accuracy: Are all claims in the article factually correct and aligned with current scientific consensus?  
    Mike has the following opinion:  
    "{context}"  
    "{reflection}"  
    What are your thoughts on this? Please provide an objective evaluation considering the scientific clarity, logical coherence, and readability of the article.
    """
    # prompt = f"""
    #     Hi John,
    #     During the last round of discussions, an evaluator provided the following suggestions for discussion:
    #     "{feedback}"
    #     Take his advice and address it in this round of discussion.
    #     Next, in addition to the two main issues previously considered, we need to contemplate two additional aspects from the following: 'Repetition', 'Logical Inconsistency', 'Discontinuity', 'Inappropriate Lexical Choice', and 'Factual Error'.
    #     Mike has the following opinion:
    #     "{context}"
    #     "\n"
    #     "{reflection}"
    #     What are your thoughts on this?
    #     """
    d = {"role": "user", "content": prompt}
    messages.append(d)
    retries = 20
    while retries > 0:
        try:
            result = LLM_Client.send(messages)
            return result
        except (UnboundLocalError, KeyError) as e:
            print(f"Error occurred: {e}. Retrying...")
            retries -= 1

    raise Exception("Failed after multiple retries.")


def SR_COT_FB_3_1(LLM_Client,feedback, messages):
    prompt = f"""
    Hello Mike,  
    During the last round of discussions, an evaluator provided the following suggestions for discussion:  
    "{feedback}"  
    Please incorporate this feedback into your analysis in this round.  
    Next, we need to continue discussing the remaining last issue among the following aspects:  
    - Repetition: Does the text contain unnecessary repetition that affects clarity and engagement?  
    - Logical Inconsistency: Are there contradictions or logical flaws in the scientific explanations?  
    - Discontinuity: Are there abrupt content shifts that disrupt the logical progression of scientific concepts?  
    - Scientific Lexical Choice: Are the scientific terms used correctly, and do they align with standard scientific writing conventions?  
    - Scientific Accuracy: Are all claims in the article factually correct and aligned with current scientific consensus?  
    Please continue your analysis, focusing on ensuring the scientific clarity, logical coherence, and readability of the article.
    """
    if len(prompt)>4095:
        prompt = prompt[:4095]
    d = {"role": "user", "content": prompt}
    messages.append(d)
    retries = 20
    while retries > 0:
        try:
            result = LLM_Client.send(messages)

            return result
        except (UnboundLocalError, KeyError) as e:
            print(f"Error occurred: {e}. Retrying...")
            retries -= 1

    raise Exception("Failed after multiple retries.")

def SR_COT_FB_3_2(LLM_Client,feedback, context, reflection, messages):
    prompt = f"""
    Hello John,  
    During the last round of discussions, an evaluator provided the following suggestions for discussion:  
    "{feedback}"  
    Please incorporate this feedback into your analysis in this round.  
    Next, we need to continue discussing the remaining last issue among the following aspects:  
    - Repetition: Does the text contain unnecessary repetition that affects clarity and engagement?  
    - Logical Inconsistency: Are there contradictions or logical flaws in the scientific explanations?  
    - Discontinuity: Are there abrupt content shifts that disrupt the logical progression of scientific concepts?  
    - Scientific Lexical Choice: Are the scientific terms used correctly, and do they align with standard scientific writing conventions?  
    - Scientific Accuracy: Are all claims in the article factually correct and aligned with current scientific consensus?  
    Mike has the following opinion:  
    "{context}"  
    "{reflection}"  
    What are your thoughts on this, John? Please provide an evaluation focusing on scientific clarity, logical coherence, and readability, and suggest improvements where necessary.
    """
    if len(prompt)>4095:
        prompt = prompt[:4095]
    d = {"role": "user", "content": prompt}
    messages.append(d)
    retries = 20
    while retries > 0:
        try:
            result = LLM_Client.send(messages)

            return result
        except (UnboundLocalError, KeyError) as e:
            print(f"Error occurred: {e}. Retrying...")
            retries -= 1

    raise Exception("Failed after multiple retries.")

def SR_COT_FB_summary(LLM_Client,story_content, history, messages):
    prompt = f"""
        "{history}"
        Based on the provided scientific article and the evaluations from the two previous reviewers across three rounds, please provide a comprehensive assessment.
        "{story_content}"
        Note:  
        - Each error type may occur multiple times in the text. Each instance should be identified and scored accordingly.  
        - We will start with a base score of 0 for the article. For each detected error, 1 point will be deducted.  
        You only need to answer the following Boolean-type questions (Yes/No) and strictly follow this format:  
        - If the answer is "Yes", list the specific original sentences, explain the issue, and detail the deductions based on the type and severity of the error. If the issue occurs in multiple places, list them all.  
        - If the answer is "No", no further explanation is required.  
        Evaluation Questions:
    
        Question: Does the above article contain 'Repetition'?  
        Answer:  
        Score for individual questions:  
    
        Question: Does the above article contain 'Logical Inconsistency' (including flawed scientific reasoning)?  
        Answer:  
        Score for individual questions:  
    
        Question: Does the above article contain 'Discontinuity' (lack of smooth transitions in scientific explanations)?  
        Answer:  
        Score for individual questions:  
    
        Question: Does the above article contain 'Scientific Lexical Choice Issues' (misuse of scientific terms or unclear explanations)?  
        Answer:  
        Score for individual questions:  
    
        Question: Does the above article contain 'Scientific Accuracy Issues' (factually incorrect or misleading claims)?  
        Answer:  
        Score for individual questions:  
    
        Question: Does the article maintain 'Engagement & Readability' (clear explanations, engaging style)?  
        Answer:  
        Score for individual questions:  
        Final Score: _ points.
        Calculation process:
    """
    if len(prompt)>4095:
        prompt = prompt[:4095]
    d = {"role": "user", "content": prompt}
    messages.append(d)
    retries = 20
    while retries > 0:
        try:
            result = LLM_Client.send(messages)

            return result
        except (UnboundLocalError, KeyError) as e:
            print(f"Error occurred: {e}. Retrying...")
            retries -= 1

    raise Exception("Failed after multiple retries.")


def SR_COT_FB_summary_score(LLM_Client, story_content, history, messages):
    prompt = f"""
        "{history}"
        Based on the provided scientific article and the evaluations from the two previous reviewers across three rounds, please provide a comprehensive assessment.
        "{story_content}"
        Note:  
        - Each error type may occur multiple times in the text. Each instance should be identified and scored accordingly.  
        - We will start with a base score of 0 for the article. For each detected error, 1 point will be deducted.  
        You only need to answer the following Boolean-type questions (Yes/No) and strictly follow this format:  
        - If the answer is "Yes", list the specific original sentences, explain the issue, and detail the deductions based on the type and severity of the error. If the issue occurs in multiple places, list them all.  
        - If the answer is "No", no further explanation is required.  
        Evaluation Questions:

        Question: Does the above article contain 'Repetition'?  
        Answer:  
        Score for individual questions:  

        Question: Does the above article contain 'Logical Inconsistency' (including flawed scientific reasoning)?  
        Answer:  
        Score for individual questions:  

        Question: Does the above article contain 'Discontinuity' (lack of smooth transitions in scientific explanations)?  
        Answer:  
        Score for individual questions:  

        Question: Does the above article contain 'Scientific Lexical Choice Issues' (misuse of scientific terms or unclear explanations)?  
        Answer:  
        Score for individual questions:  

        Question: Does the above article contain 'Scientific Accuracy Issues' (factually incorrect or misleading claims)?  
        Answer:  
        Score for individual questions:  

        Question: Does the article maintain 'Engagement & Readability' (clear explanations, engaging style)?  
        Answer:  
        Score for individual questions:  
        Final Score: _ points.
        Please directly tell me what the final score is. The result should be in numeric form.
    """
    if len(prompt)>4095:
        prompt = prompt[:4095]
    d = {"role": "user", "content": prompt}
    messages.append(d)
    retries = 20
    while retries > 0:
        try:
            result = LLM_Client.send(messages)

            return result
        except (UnboundLocalError, KeyError) as e:
            print(f"Error occurred: {e}. Retrying...")
            retries -= 1

    raise Exception("Failed after multiple retries.")

def text_summary(LLM_Client,mes):
    prompt = f"""
    Please summarize the following assessment Q&A pairs into a coherent and concise evaluative paragraph:
    "\n"
    {mes}
    """
    if len(prompt)>4095:
        prompt = prompt[:4095]
    ROLE = 'assistant'
    messages = [{"role": "system", "content": ROLE}]
    d = {"role": "user", "content": prompt}
    messages.append(d)
    retries = 20
    while retries > 0:
        try:
            result = LLM_Client.send(messages)

            return result
        except (UnboundLocalError, KeyError) as e:
            print(f"Error occurred: {e}. Retrying...")
            retries -= 1

    raise Exception("Failed after multiple retries.")


def MaPereduMTAEval(LLM_Client,original_id,document):
    messages_agent1 = [{"role": "system", "content": ROLE}]
    messages_agent2 = [{"role": "system", "content": ROLE}]
    messages_agent3 = [{"role": "system", "content": ROLE}]
    messages_agent4 = [{"role": "system", "content": ROLE}]
    while True:
        try:
            # 第一轮
            SR_COT_FB_agent1_1 = SR_COT_FB_1_1(LLM_Client,document, messages_agent1)
            messages_agent1.append({"role": "user", "content": SR_COT_FB_agent1_1})
            Self_Reflection_agent1_1 = Self_Reflection_key(LLM_Client,messages_agent1)
            messages_agent1.append(
                {"role": "user", "content": Self_Reflection_agent1_1})

            # 第二个人
            SR_COT_FB_agent1_2 = SR_COT_FB_1_2(LLM_Client,document, SR_COT_FB_agent1_1, Self_Reflection_agent1_1,
                                               messages_agent2)
            messages_agent2.append({"role": "user",
                                    "content": SR_COT_FB_agent1_1 + "\n" + " " + Self_Reflection_agent1_1 + "\n" + " " + SR_COT_FB_agent1_2})
            Self_Reflection_agent1_2 = Self_Reflection_key(LLM_Client,messages_agent2)
            messages_agent2.append(
                {"role": "user", "content": Self_Reflection_agent1_2})
            messages_agent1.append(
                {"role": "user", "content": SR_COT_FB_agent1_2 + "\n" + " " + Self_Reflection_agent1_2})
            # 反馈
            history1 = SR_COT_FB_agent1_1 + "\n" + " " + Self_Reflection_agent1_1 + "\n" + " " + SR_COT_FB_agent1_2 + "\n" + " " + Self_Reflection_agent1_2
            feedback_1 = feed_back(LLM_Client,history1, messages_agent4)
            messages_agent4.append({"role": "user", "content": feedback_1})
            # ---------------------------------------------------------------------------------------------------------------------------------------------------
            # 第二轮
            # 第一人
            SR_COT_FB_agent2_1 = SR_COT_FB_2_1(LLM_Client,feedback_1, messages_agent1)
            messages_agent1.append(
                {"role": "user", "content": SR_COT_FB_agent2_1})

            # 反思
            Self_Reflection_agent2_1 = Self_Reflection_key(LLM_Client,messages_agent1)
            messages_agent1.append(
                {"role": "user", "content": Self_Reflection_agent2_1})

            # 第二个人
            SR_COT_FB_agent2_2 = SR_COT_FB_2_2(LLM_Client,feedback_1, SR_COT_FB_agent2_1, Self_Reflection_agent2_1,
                                               messages_agent2)
            messages_agent2.append({"role": "user",
                                    "content": SR_COT_FB_agent2_1 + "\n" + " " + Self_Reflection_agent2_1 + "\n" + " " + SR_COT_FB_agent2_2})

            # 反思
            Self_Reflection_agent2_2 = Self_Reflection_key(LLM_Client,messages_agent2)
            messages_agent2.append(
                {"role": "user", "content": Self_Reflection_agent2_2})
            messages_agent1.append(
                {"role": "user", "content": SR_COT_FB_agent2_2 + "\n" + " " + Self_Reflection_agent2_2})
            # 反馈
            history2 = SR_COT_FB_agent2_1 + "\n" + " " + Self_Reflection_agent2_1 + "\n" + " " + SR_COT_FB_agent2_2 + "\n" + " " + Self_Reflection_agent2_2
            feedback_2 = feed_back(LLM_Client,history2, messages_agent4)
            messages_agent4.append({"role": "user", "content": feedback_2})
            # ---------------------------------------------------------------------------------------------------------------------------------------------------
            # 第三轮
            # 第一人
            SR_COT_FB_agent3_1 = SR_COT_FB_3_1(LLM_Client,feedback_2, messages_agent1)
            messages_agent1.append(
                {"role": "user", "content": SR_COT_FB_agent3_1})

            Self_Reflection_agent3_1 = Self_Reflection_key(LLM_Client,messages_agent1)
            messages_agent1.append(
                {"role": "user", "content": Self_Reflection_agent3_1})

            # 第二个人
            SR_COT_FB_agent3_2 = SR_COT_FB_3_2(LLM_Client,feedback_2, SR_COT_FB_agent3_1, Self_Reflection_agent3_1,
                                               messages_agent2)

            messages_agent2.append(
                {"role": "user",
                 "content": SR_COT_FB_agent3_1 + "\n" + " " + Self_Reflection_agent3_1 + "\n" + " " + SR_COT_FB_agent3_2})

            Self_Reflection_agent3_2 = Self_Reflection_key(LLM_Client,messages_agent2)

            messages_agent2.append(
                {"role": "user", "content": Self_Reflection_agent3_2})

            # ---------------------------------------------------------------------------------------------------------------------------------------------------
            his = "Mike：" + Self_Reflection_agent1_1 + "\n " + "John：" + Self_Reflection_agent1_2 + "\n " + "Mike：" + Self_Reflection_agent2_1 + "\n " + "John：" + Self_Reflection_agent2_2 + "\n " + "Mike：" + Self_Reflection_agent3_1 + "\n " + "John：" + Self_Reflection_agent3_2 + "\n "
            SR_COT_FB_agent_summary = SR_COT_FB_summary(LLM_Client,document, his, messages_agent3)
            final_score = SR_COT_FB_summary_score(LLM_Client, document, his, messages_agent3)
            summary = text_summary(LLM_Client,SR_COT_FB_agent_summary)

            SR_COT_FB_data = {
                "ID": original_id,
                "document": document,
                "SR_COT_FB_agent1_1": SR_COT_FB_agent1_1,
                "SR_COT_FB_Reflection1_1": Self_Reflection_agent1_1,
                "SR_COT_FB_agent1_2": SR_COT_FB_agent1_2,
                "SR_COT_FB_Reflection1_2": Self_Reflection_agent1_2,
                "Feedback_1": feedback_1,
                "SR_COT_FB_agent2_1": SR_COT_FB_agent2_1,
                "SR_COT_FB_Reflection2_1": Self_Reflection_agent2_1,
                "SR_COT_FB_agent2_2": SR_COT_FB_agent2_2,
                "SR_COT_FB_Reflection2_2": Self_Reflection_agent2_2,
                "Feedback_2": feedback_2,
                "SR_COT_FB_agent3_1": SR_COT_FB_agent3_1,
                "SR_COT_FB_Reflection3_1": Self_Reflection_agent3_1,
                "SR_COT_FB_agent3_2": SR_COT_FB_agent3_2,
                "SR_COT_FB_Reflection3_2": Self_Reflection_agent3_2,
                "SR_COT_FB_agent_summary": SR_COT_FB_agent_summary,
                "final_score":final_score,
                "text_summary": summary
            }
            # print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Processed {idx + 1}/{len(stories)} prompts")
            # print(SR_COT_FB_data[-1])
            return SR_COT_FB_data

        except Exception as e:
            logging.error(e)


if __name__ == '__main__':
    MaPereduMTAEval()