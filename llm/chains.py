import re
from operator import itemgetter
from langchain.schema.runnable import RunnableLambda
from utils.util import Add_diagnostic_contexts, Add_chat_context

def Activate_diagnosis_chain(chat_model, main_prompt, evaluate_each_prompt, diagnose_each_prompt, _dict:dict):
    """
    _dict should be {"user_data": something, "how_many_search": int, "faiss_path": faiss_path}
    """
    def add_score(_dict:dict) -> dict:
        evaluate_each_chain = evaluate_each_prompt | chat_model
        res = evaluate_each_chain.invoke(_dict)
        try:
            score = re.match(r"^\d([.]\d+)?", res.content).group(0)
        except:
            score = "0"
        _dict["score"] = score
        return _dict
    def make_comment(_dict: dict):
        if float(_dict["score"]) < 0.3:
            comment = "The patient is likely to be healthy. The symptoms are not clinically important when regarding the context."
        else:
            comment_chain = diagnose_each_prompt | chat_model
            comment = comment_chain.invoke(_dict).content
        return comment
    def map_diagnosis(_dict: dict) -> str:
        text = ""
        for item in _dict["context_list"]:
            diagnosis_map_chain = RunnableLambda(add_score) | RunnableLambda(make_comment)
            res = diagnosis_map_chain.invoke({
                "symptoms": _dict["symptoms"],
                "context": item
            })
            text += res+"\n===\n"
        return text

    diagnosis_chain = {
        "symptoms": itemgetter("symptoms"),
        "comments": RunnableLambda(Add_diagnostic_contexts) | RunnableLambda(map_diagnosis),
        "language": itemgetter("language")
        } | main_prompt | chat_model
    
    res = diagnosis_chain.invoke(_dict).content
    return res


def Activate_chat_chain(chat_model, main_prompt, _dict):
    chat_chain =  RunnableLambda(Add_chat_context) | main_prompt | chat_model
    res = chat_chain.invoke(_dict).content
    return res