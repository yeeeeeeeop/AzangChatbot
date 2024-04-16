from operator import itemgetter
from langchain.schema.runnable import RunnableLambda

from utils.util import Generate_context, Generate_symptom
from llm.prompts import diagnosis_propmt

def Activate_diagnosis_chain(chat_model, _dict:dict):
    diagnosis_chain = {
        "symptoms": itemgetter("user_data") | RunnableLambda(Generate_symptom),
        "contexts": {
            "query": itemgetter("user_data") | RunnableLambda(Generate_symptom),
            "how_many_search": itemgetter("how_many_search"),
            "faiss_path": itemgetter("faiss_path")
            } | RunnableLambda(Generate_context),
        } | diagnosis_propmt | chat_model
    res = diagnosis_chain.invoke(_dict).content
    return res