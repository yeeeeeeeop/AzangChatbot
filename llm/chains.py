from operator import itemgetter
from langchain.schema.runnable import RunnableLambda
from utils.util import Add_diagnostic_contexts, Add_chat_context

def Activate_diagnosis_chain(chat_model, main_prompt, evaluate_each_prompt, diagnose_each_prompt, _dict:dict):
    """
    _dict should be {"user_data": something, "how_many_search": int, "faiss_path": faiss_path}
    """
    def map_diagnosis(_dict: dict) -> str:
        text = ""
        evaluate_each_chain = evaluate_each_prompt | chat_model
        diagnose_each_chain = diagnose_each_prompt | chat_model
        for item in _dict["context_list"]:
            diagnosis_map_chain = {
                "symptoms": itemgetter("symptoms"),
                "context": itemgetter("context"),
                "score": evaluate_each_chain
                } | diagnose_each_chain
            res = diagnosis_map_chain.invoke({
                "symptoms": _dict["symptoms"],
                "context": item
            })
            text += res.content+"\n"
        return text

    diagnosis_chain = {
        "symptoms": itemgetter("symptoms"),
        "comments": RunnableLambda(Add_diagnostic_contexts) | RunnableLambda(map_diagnosis)
        } | main_prompt | chat_model
    
    res = diagnosis_chain.invoke(_dict).content
    return res


def Activate_chat_chain(chat_model, main_prompt, _dict):
    chat_chain =  RunnableLambda(Add_chat_context) | main_prompt | chat_model
    res = chat_chain.invoke(_dict).content
    return res