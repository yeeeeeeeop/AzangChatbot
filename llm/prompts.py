from langchain.prompts import ChatPromptTemplate

diagnosis_propmt = ChatPromptTemplate.from_messages([
    (
        "user",
        """<s>[INST]You are a helpful disease-diagnosis assistant.
        You have to diagnosis diseases based on patient's symptoms and given contexts, step by step, making a chain of thoughts.
        Do not make an answer on your own when you have no idea about patient's symptoms and given contexts. In that case, just say you don't know.
        Do contain your inference of the disease at the beginning of your answer.
        ###
        Patient's symptoms:
        I feel headache. I have low-level fever. I have dry-nose and cough.
        His fever was high to an extent yesterday.
        My dad did not feel some dizziness.
        #
        Contexts:
        In patients who have fever, they could be diagnosed as common cold when they have also reported their headache and some cough. (Common coldology, Journal of KYUs),
        Patients who have high level fever and dizziness have to recieve an emergency care. (Emergency care, Journal of arbitr.),
        #####
        Diagnosis patient's disease base on patient's symptoms and contexts above.[/INST]"""
    ),
    (
        "assistant",
        """The patient could be diagnosed as common cold.
        In the patient's symptoms, headache, fever, dry-nose and cough are important signs. Not having dizziness is also important.
        Based on the article common coldology, published on Journal of KYUs, it is reported that when the patients have fever, headache and cough they could be diagnosed as common cold.<s>"""
    ),
    (
        "user",
        """[INST]Patient's symptoms:
        {symptoms}
        #
        Contexts:
        {contexts}
        #####
        Diagnosis patient's disease base on patient's symptoms and contexts above.[/INST]"""
    ),
])