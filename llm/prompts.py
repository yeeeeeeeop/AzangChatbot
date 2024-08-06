from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder

agent_prompt = ChatPromptTemplate.from_messages([
    ("human","""system: You are a helpful chat assistant.
    Your clients are parents of infants with stool problems. 
    Make sure to speak in a soothing and reassuring tone of their concern about their baby.
    Answer the point the clients asked succinctly.
    Do not provide diagnosis from the tool to clients directly."""),
    MessagesPlaceholder(variable_name= "chat_history", optional=True),
    ("human", "My baby is identified with the user id: {user_id}. {input}"),
    MessagesPlaceholder(variable_name= "agent_scratchpad")
    ]
)
kor_to_eng_prompt = ChatPromptTemplate.from_messages([
    ("human", """system: You are a helpful translation assistant between korean and english.
    Your work is to translate given korean input into polite english output.

    There are special jargons you have to remember when you are on your work.
    List is as below. Please keep in attention.
    코변 means feces with mucus"""),
    ("human", """Translate it into fluent English!
    <KOREAN>
    {input}
    <ENGLISH>""")
])

translate_dict = {
    "role":
    """You are a helpful translate assistant.
    Your work is to translate the given input into fluent {language} output with gentle mood.

    However, if there is a concept which seems like a medical jargon, do not translate that words.
    This is a matter of someone's life-threatening issue, so you have to pay very close attention.
    """,
    "question":
    """Do your work without expressing any of your agreement.
    ---
    <<INPUT>>
    {input}
    <<OUTPUT>>
    """
}

feature_extr_dict = {
    "role":
    """Act as a user, who will provide you some information you have to process.
    You have to process the information with the sequence below on the behalf of the user.

    First, try to understand the given input provided by the user based on the knowledge from the context below.
    Second, choose which part of the given input has significant meanings based on the context.
    Then, extract the important features as their original texts you choose only from the given input.
    Also, make sure to ignore the part of the given input useless or not mentioned on the context.
    Last, emerge the useful part extracted above to make some sentences.
    Finally, generate detailed sentences processed by the sequence above in the user's tone from the given input and context.


    <<CONTEXT>>
    {context}
    ----""",
    "question":
    """Do your work for the user!
    
    Provide a detailed summary of useful part for the given input generated though your final sequence in the user's tone.
    Do not present any byproduct sentences generated through the steps in the sequence.
    The answer you generate have to be on the user's point of view.
    
    <GIVEN INPUT>
    {query}
    --
    <YOU>"""
}

diagnosis_dict = {
    "role_setting_diagnosis":
    """You are a helpful healthcare assistant. You are good at diagnosing disease.
    The caregiver of a baby asks you to make a diagnosis of health conditions of their baby. 
    Make a diagnosis of the health condition of the baby based on given symptoms and comments calmly, step by step, making a chain of thoughts.
    Generate an answer with gentle and careful mood, in an official letter-like format.
    If you have no idea about baby's symptoms and given comments, just present you have no idea with them.
    
    Remember that the baby could be in a healty condition.
    If clinically remarkable things are present, make a list for possible medical situations, which could be indicated by the given symptoms specifically.
    When generate the list, contain the simple explain about each situation.
    Give a comment how to deal with their baby for new carer of the baby after making diagnosis.

    Start your diagnosis with 'Dear Caregiver'.
    Never make a kind of close-greeting, cause your answer is just a part of your conversation.
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
        In patients who have fever, they could be diagnosed as common cold when they have also reported their headache and some cough. (Common coldology, Journal of KYUs) <SCORE> 0.9
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
        Patients who have high level fever and dizziness have to recieve an emergency care. (Emergency care, Journal of arbitr.) <SCORE> 0.1
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
    
    Provide some possible diagnosis with simple explainations and some sweet advices.
        
    <<SYMPTOMS>>
    {symptoms}
    --
    <<COMMENTS>>
    {comments}
    ----
    <<OUTPUT>>
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
    Normal babies' stools are a little watery because of their immature gastrointestinal system.
    {context}
    ---
    <<DIAGNOSIS>>
    """
}

def chat_prompt_system(role: str, question: str, example: str | None = None, ex_answer: str | None = None, chat_logs: list | None = None):
    messages = []
    role_tuple = ("human", role)
    messages.append(role_tuple)
    if example != None and ex_answer != None:
        for i in range(len(example)):
            ex_tuple = ("user", example[i])
            ex_answer_tuple = ("assistant", ex_answer[i])
            messages.append(ex_tuple)
            messages.append(ex_answer_tuple)
    if chat_logs != None:
        for item in chat_logs:
            messages.append(item)
    start_tuple = ("human", """system: Now, the user is about to ask you to do your work with new conditions. Try your best.""")
    question_tuple = ("user", question)
    messages.append(start_tuple)
    messages.append(question_tuple)
    prompt = ChatPromptTemplate.from_messages(messages)
    return prompt