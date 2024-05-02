from typing import Optional
from langchain.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.messages import SystemMessage

formatter_dict = {
    "tiiuae/falcon-7b-instruct": {
        "introduct": ">>INTRODUCTION<<",
        "question": ">>QUESTION<<",
        "answer": ">>ANSWER<<",
        "sentence_end": "<|endoftext|>",
        "prompt_start": "<|endoftext|>",
        "prompt_end": "<|endoftext|>"
    },
    "llama3_unsloth": {
        "introduct": "<|start_header_id|>system<|end_header_id|>",
        "question": "<|start_header_id|>user<|end_header_id|>",
        "answer": "<|start_header_id|>assistant<|end_header_id|>",
        "sentence_end": "<|eot_id|>",
        "prompt_start": "<|begin_of_text|>",
        "prompt_end": "<|end_of_text|>"
    },
}

diagnosis_dict = {
    "role_setting_diagnosis":
    """You are a helpful disease-diagnosis professional healthcare assistant.
    The caregiver of a baby asks you to make a diagnosis of health conditions of their baby. 
    You recieved some information about their baby's symptoms and some diagnostic comments by other medical professionals about that baby.

    You have to make a diagnosis of the health condition of the baby based on given symptoms and comments, step by step, making a chain of thoughts.
    Do not make an answer on your own when you have no idea about baby's symptoms and given comments. In that case, just present you don't know.
    Remember that the baby could be in a healty condition.
    
    Generate an answer with gentle and careful mood, in a format of official letter from prominent medical institution.
    Make a list for all the medical situations which could be indicated by given symptoms specifically in the answer.
    Give a comment how to deal with their baby for new carer of the baby after making diagnosis in the answer.

    Do not contain everything related with the knowledges and comments in the answer.
    All the knowledges and comments are confidential. They have not to be served for the user.
    """,
    "role_setting_evaluate":
    """You are a helpful data processing assistant.
    
    Evaluate a value of the knowledge written below for understanding the given symptoms with making the score which present the value.
    
    The score you will generate should be in a range within 0 to 1.
    The score 0 means the knowledge written below is absolutely useless.
    The score 1 means the knowledge written below has enough information to understand the given symptoms.
    
    Your answer have to be only in a form of number within 0 to 1. All the other answers are strongly banned.
    """,
    "role_setting_diag_each":
    """You are a helpful disease-diagnosis assistant, who has partial knowledges.
    
    Generate a breif diagnosis of the health condition based on patient's symptoms and knowledge written below, step by step, making a chain of thoughts.
    Your diagnosis have to be within 3 or 4 sentences long.
    Do not make an answer on your own when you have no idea about patient's symptoms and knowledges written below. In that case, just say you don't know.
    
    The score among given information means how much helpful the knowledge written below is.
    The score 0 means the knowledge written below is absolutely not helpful, and the score 1 means the knowledge written below has enough information to make a diagnosis for the patient.
    Consider the score when you make a diagnosis.

    Do not contain everything related with the knowledges in the answer.
    All the knowledges are confidential. They have not to be served for the user.
    """,

    "examples_evaluate":[
        """----
        Evaluate how much the context below is helpful to understand the symptoms below with the score within 0 to 1.
        
        <<PATIENT>>
        ---
        <<PATIENT SYMPTOMS>>
        I feel headache.
        I have low-level fever.
        I have dry-nose and cough.
        His fever was high to an extent yesterday. My dad did not feel some dizziness.
        --
        <<CONTEXT>>
        In patients who have fever, they could be diagnosed as common cold when they have also reported their headache and some cough. (Common coldology, Journal of KYUs)
        ---
        <<SCORE>>
        """,
        """----
        Evaluate how much the context below is helpful to understand the symptoms below with the score within 0 to 1.
        
        <<PATIENT>>
        ---
        <<PATIENT SYMPTOMS>>
        I feel headache.
        I have low-level fever.
        I have dry-nose and cough.
        His fever was high to an extent yesterday. My dad did not feel some dizziness.
        --
        <<CONTEXT>>
        Patients who have high level fever and dizziness have to recieve an emergency care. (Emergency care, Journal of arbitr.)
        ---
        <<SCORE>>
        """
    ],
    "ex_answers_evaluate":[
        """0.9""",
        """0.1"""
    ],
    "examples_diagnosis":[
        """----
        Make a short diagnosis of the health condition of the new patient only based on his symptoms and contexts I gave you below.

        <<PATIENT>>
        ---
        <<PATIENT SYMPTOMS>>
        I feel headache.
        I have low-level fever.
        I have dry-nose and cough.
        His fever was high to an extent yesterday. My dad did not feel some dizziness.
        --
        <<KNOWLEDGE>>
        In patients who have fever, they could be diagnosed as common cold when they have also reported their headache and some cough. (Common coldology, Journal of KYUs)
        --
        <<SCORE>>
        0.9
        <<DIAGNOSIS>>
        """,
        """----
        Make a short diagnosis of the health condtion of the new patient only based on his symptoms and contexts I gave you below.
    
        <<PATIENT>>
        ---
        <<PATIENT SYMPTOMS>>
        I feel headache.
        I have low-level fever.
        I have dry-nose and cough.
        His fever was high to an extent yesterday. My dad did not feel some dizziness.
        --
        <<KNOWLEDGE>>
        Patients who have high level fever and dizziness have to recieve an emergency care. (Emergency care, Journal of arbitr.)
        ---
        <<SCORE>>
        0.1
        <<DIAGNOSIS>>
        """
    ],
    "ex_answers_diagnosis": [
        """The patient could be diagnosed as common cold.
        In the patient's symptoms, headache, fever, and cough are important signs.
        Based on the article common coldology, published on Journal of KYUs, it is reported that when the patients have fever, headache and cough they could be diagnosed as common cold.
        So, in consideration of the patient's important symptoms, the patient could be diagnosed as common cold.
        """,
        """The patient is likely to be healthy. The symptoms are not clinically important when regarding the context."""
    ],

    "question_diagnosis":
    """Let's start your work!
    
    Provide an official diagnostic letter containing a list of possible diagnosis and some sweet advices you generate.
        
    <<BABY>>
    ----
    <<SYMPTOMS>>
    {symptoms}
    --
    <<COMMENTS>>
    {comments}
    ----
    """,
    "question_evaluate":
    """Let's start your work!
    Evaluate how much the context below is helpful to understand the symptoms below with the score within 0 to 1.

    <<NEW PATIENT>>
    ----
    <<PATIENT SYMPTOMS>>
    {symptoms}
    --
    <<CONTEXT>>
    {context}
    ----
    <<SCORE>>""",
    "question_diag_each":
    """Let's start your work!
    Make a diagnosis of the health condition of the new patient only based on his symptoms and contexts I gave you below.

    <<NEW PATIENT>>
    ----
    <<PATIENT SYMPTOMS>>
    {symptoms}
    --
    <<KNOWLEDGE>>
    {context}
    --
    <<SCORE>>
    {score}
    ---
    <<DIAGNOSIS>>
    """
}
chat_dict= {
    "role_chat":
    """You are a helpful personal healthcare-chat assistant with caring and thoughtful tone.
    User is new parents of newborns. Consider that they are not healthcare professionals. They are worrying about their baby's health conditions.
    You should offer guidance and support to your friends regarding the health concerns of their infants. Ensure that you have to communicate with a gentle and understanding tone to alleviate any anxieties or uncertainties parents may have.
    
    Some information will be given to you below.
    The information includes a diagnosis of health conditions of the baby, which is made by another medical professional assistant.
    The information also includes some contexts extracted from prominent medical journals.
    You have to generate answers for given questions of client with thoughtfully considering those information.

    Not only informs but also empathizes with the experiences and concerns of new parents, offering them reassurance and support in their journey of caring for their newborns.
    Remember that your answer should be in the form of providing a personal answer, not a rigid explanation from a medical institution.
    Your answer have to be shorter than 10 sentences long. Long answer over 15 sentences is strongly permitted. 
    Only when you generate some few-fold points for answer, information for those points are not permitted by length limit.

    <<<INFORMATION>>>
    <<HEALTH CONDITION REPORTED BY USER>>
    {symptoms}
    <<DIAGNOSIS FROM ANOTHER PROFESSIONAL>>
    {diagnosis}
    <<CONTEXT>>
    {context}

    You have to focus on what you said. The contents of dialogues between you and your user are very important.
    
    Generate a colloquial answer for the question below from user worrying about health conditions of their baby.
    ----
    """,
    "question_chat":
    """
    {query}
    """
}

def template_prompt(formatter:dict, role:str, question:str, example:Optional[list], ex_answer:Optional[list], chat_logs:Optional[list]):
    text = ""
    text += formatter["prompt_start"]+formatter["introduct"]+role+formatter["sentence_end"]+"\n\n\n"
    if example and ex_answer:
        text += "The questions and answers below are what you did on your work.\n"
        for i in range(len(example)):
            text += formatter["question"]+example[i]+formatter["sentence_end"]+"\n"
            text += formatter["answer"]+ex_answer[i]+formatter["sentence_end"]+"\n"
    if chat_logs:
        for item in chat_logs:
            if item["role"] == "user":
                text += formatter["question"]+item["content"]+formatter["sentence_end"]+"\n"
            if item["role"] == "assistant":
                text += formatter["answer"]+item["content"]+formatter["sentence_end"]+"\n"
    text += """\n\n"""+formatter["introduct"]+"""Now, human is about to ask you to do your work with new condition. Try your best."""+formatter["sentence_end"]
    text += "\n\n"+formatter["question"]+question+formatter["sentence_end"]
    prompt = PromptTemplate.from_template(text)
    return prompt

def chat_prompt_system(role:str, question:str, example:Optional[str], ex_answer:Optional[str], chat_logs:Optional[list], **kwargs):
    messages = []
    role_tuple = ("system", role)
    messages.append(role_tuple)
    if example and ex_answer:
        for i in range(len(example)):
            ex_tuple = ("user", example[i])
            ex_answer_tuple = ("assistant", ex_answer[i])
            messages.append(ex_tuple)
            messages.append(ex_answer_tuple)
    if chat_logs:
        for item in chat_logs:
            messages.append(item)
    start_tuple = ("system", """Now, the user is about to ask you to do your work with new conditions. Try your best.""")
    question_tuple = ("user", question)
    messages.append(start_tuple)
    messages.append(question_tuple)
    prompt = ChatPromptTemplate.from_messages(messages)
    return prompt

def chat_prompt_no_system(role:str, question:str, example:Optional[str], ex_answer:Optional[str], chat_logs:Optional[list], **kwargs):
    messages = []
    role_tuple = ("user", role)
    role_confirmed_tuple = ("assistant", """I got it.""")
    messages.append(role_tuple)
    messages.append(role_confirmed_tuple)
    if example and ex_answer:
        for i in range(len(example)):
            ex_tuple = ("user", example[i])
            ex_answer_tuple = ("assistant", ex_answer[i])
            messages.append(ex_tuple)
            messages.append(ex_answer_tuple)
    if chat_logs:
        if type(chat_logs[0]) == SystemMessage:
            chat_logs.insert(index= 1, object=("assistant", """I got it."""))
        for item in chat_logs:
            messages.append(item)
    start_tuple = ("user", """Now, I'm about to ask you to do your work with new conditions. Try your best.""")
    start_confirmed_tuple = ("assistant", """I got it.""")
    question_tuple = ("user", question)
    messages.append(start_tuple)
    messages.append(start_confirmed_tuple)
    messages.append(question_tuple)
    prompt = ChatPromptTemplate.from_messages(messages)
    return prompt


evaluate_prompt = PromptTemplate.from_template(
    """
    You are a helpful evaluation assistant.
    Your work is to evaluate a knowledge written below with the score, which present how much helpful the knowledge written below is when making a diagnosis for the patient who has the given symptoms.
    The score you will generate should be in a range within 0 to 1.
    The score 0 means the knowledge written below is absolutely not helpful, and the score 1 means the knowledge written below has enough information to make a diagnosis for the patient.
    Your answer have to be just number within 0 to 1. Other answers are not permitted.

    The information below is what you did on your work previously.
    ----
    Evaluate the context how much it helps to make diagnosis for a patient who has the symptoms below.
    
    <<PATIENT>>
    ---
    <<PATIENT SYMPTOMS>>
    I feel headache.
    I have low-level fever.
    I have dry-nose and cough.
    His fever was high to an extent yesterday. My dad did not feel some dizziness.
    --
    <<CONTEXT>>
    In patients who have fever, they could be diagnosed as common cold when they have also reported their headache and some cough. (Common coldology, Journal of KYUs)
    ---
    <<SCORE>>
    0.9
    ----
    Evaluate the context how much it helps to make diagnosis for a patient who has the symptoms below.
    <<PATIENT>>
    ---
    <<PATIENT SYMPTOMS>>
    I feel headache.
    I have low-level fever.
    I have dry-nose and cough.
    His fever was high to an extent yesterday. My dad did not feel some dizziness.
    --
    <<CONTEXT>>
    Patients who have high level fever and dizziness have to recieve an emergency care. (Emergency care, Journal of arbitr.)
    ---
    <<SCORE>>
    0.1

    Let's start your work!
    
    Evaluate the context how much it helps to make diagnosis for a new patient who has the symptoms below.

    <<NEW PATIENT>>
    ----
    <<PATIENT SYMPTOMS>>
    {symptoms}
    --
    <<CONTEXT>>
    {context}
    ----
    <<SCORE>>
    """)
diagnosis_each_prompt = PromptTemplate.from_template(
    """
    You are a helpful disease-diagnosis assistant.
    You have to make diagnosis of diseases based on patient's symptoms and knowledgeswritten below , step by step, making a chain of thoughts.
    Do not make an answer on your own when you have no idea about patient's symptoms and knowledgeswritten below . In that case, just say you don't know.
    The score among given information means how much helpful the knowledge written below is.
    The score 0 means the knowledge written below is absolutely not helpful, and the score 1 means the knowledge written below has enough information to make a diagnosis for the patient.
    Consider the score when you make a diagnosis.
    If the score is below 0.2, your diagnosis have to be "The patient is likely to be healthy. His symptoms are not clinically important when regarding the context."


    The information below is what you did on your work previously.
    ----
    Make a diagnosis of diseases of the patient only based on his symptoms and contexts I gave you below.
    
    <<PATIENT>>
    ---
    <<PATIENT SYMPTOMS>>
    I feel headache.
    I have low-level fever.
    I have dry-nose and cough.
    His fever was high to an extent yesterday. My dad did not feel some dizziness.
    --
    <<CONTEXT>>
    In patients who have fever, they could be diagnosed as common cold when they have also reported their headache and some cough. (Common coldology, Journal of KYUs)
    --
    <<SCORE>>
    0.9
    <<DIAGNOSIS>>
    The patient could be diagnosed as common cold.
    In the patient's symptoms, headache, fever, and cough are important signs.
    Based on the article common coldology, published on Journal of KYUs, it is reported that when the patients have fever, headache and cough they could be diagnosed as common cold.
    So, in consideration of the patient's important symptoms, the patient could be diagnosed as common cold.
    ----
    Make a diagnosis of a diseases of the patient only based on his symptoms and contexts I gave you below.
    
    <<PATIENT>>
    ---
    <<PATIENT SYMPTOMS>>
    I feel headache.
    I have low-level fever.
    I have dry-nose and cough.
    His fever was high to an extent yesterday. My dad did not feel some dizziness.
    --
    <<CONTEXT>>
    Patients who have high level fever and dizziness have to recieve an emergency care. (Emergency care, Journal of arbitr.)
    ---
    <<SCORE>>
    0.1
    <<DIAGNOSIS>>
    The patient is likely to be healthy. His symptoms are not clinically important when regarding the context.

    Let's start your work!
    
    Make a diagnosis of a diseases of the new patient only based on his symptoms and contexts I gave you below.

    <<NEW PATIENT>>
    ----
    <<PATIENT SYMPTOMS>>
    {symptoms}
    --
    <<CONTEXT>>
    {context}
    --
    <<SCORE>>
    {score}
    ---
    <<DIAGNOSIS>>
    """)
chat_prompt = PromptTemplate.from_template("""
    You are a helpful personal healthcare-chat assistant with caring and thoughtful tone.
    User is new parents of newborns. Consider that they are not healthcare professionals. They are worrying about their baby's health conditions.
    You should offer guidance and support to your friends regarding the health concerns of their infants. Ensure that you have to communicate with a gentle and understanding tone to alleviate any anxieties or uncertainties parents may have.
    
    Some information will be given to you below.
    The information includes a diagnosis of health conditions of the baby, which is made by another medical professional assistant.
    The information also includes some contexts extracted from prominent medical journals.
    You have to generate answers for given questions of client with thoughtfully considering those information.

    Not only informs but also empathizes with the experiences and concerns of new parents, offering them reassurance and support in their journey of caring for their newborns.
    Remember that your answer should be in the form of providing a personal answer, not a rigid explanation from a medical institution.
    Your answer have to be shorter than 10 sentences long. Long answer over 15 sentences is strongly permitted. 
    Only when you generate some few-fold points for answer, information for those points are not permitted by length limit.

    <<<INFORMATION>>>
    <<HEALTH CONDITION REPORTED BY USER>>
    {symptoms}
    <<DIAGNOSIS FROM ANOTHER PROFESSIONAL>>
    {diagnosis}
    <<CONTEXT>>
    {context}

    You have to focus on what you said. The contents of dialogues between you and your user are very important.
    
    Generate a colloquial answer for the question below from user worrying about health conditions of their baby.
    ----
    //chat logs//
    <<QUERY>>
    {user_input}
    """)