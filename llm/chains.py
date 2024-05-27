import re
from operator import itemgetter
from langchain.vectorstores.faiss import FAISS
from langchain.schema.runnable import RunnableLambda
from utils.util import embedding_openai

def Add_feature_context(_dict: dict):
    vectordb_RAG = FAISS.load_local(folder_path=_dict["faiss_path"], embeddings=embedding_openai, allow_dangerous_deserialization=True)
    retriever = vectordb_RAG.as_retriever(
        search_type = "similarity",
        search_kwargs= {"k": 3}
        )
    _dict["context"] = [item.page_content for item in retriever.invoke(_dict["query"])]
    del _dict["faiss_path"]
    return _dict
def Add_diagnostic_contexts(_dict: dict) -> dict:
    vectordb_RAG = FAISS.load_local(folder_path=_dict["faiss_path"], embeddings=embedding_openai, allow_dangerous_deserialization=True)
    context_list = vectordb_RAG.similarity_search(query=_dict["formatted_sx"], k=_dict["how_many_search"])
    if "article_name" in context_list[0].metadata:
        context_list_modified = [item.page_content.lower()+" ("+item.metadata["article_name"]+","+item.metadata["journal"]+")" for item in context_list]
    else:
        context_list_modified = [item.page_content for item in context_list]
    _dict["context_list"] = context_list_modified
    del _dict["how_many_search"]
    del _dict["faiss_path"]
    del _dict["formatted_sx"]
    return _dict
def Add_chat_context(_dict: dict):
    vectordb_RAG = FAISS.load_local(folder_path=_dict["faiss_path"], embeddings=embedding_openai, allow_dangerous_deserialization=True)
    retriever = vectordb_RAG.as_retriever(
        search_type = "similarity_score_threshold",
        search_kwargs= {"k": 3, "score_threshold": 0.3}
        )
    question = _dict["diagnosis"][:600] +"\n==\n"+ _dict["query"]
    _dict["context"] = [item.page_content for item in retriever.invoke(question)]
    del _dict["faiss_path"]
    return _dict


def Activate_diagnosis_chain(
        chat_model,
        main_prompt,
        evaluate_each_prompt,
        diagnose_each_prompt,
        feature_prompt,
        translate_prompt,
        _dict:dict):
    
    def format_symptoms(_dict: dict) -> dict:
        input_dict = dict()
        input_dict["query"] = _dict["symptoms"]
        input_dict["faiss_path"] = _dict["faiss_path"]
        symptom_chain = RunnableLambda(Add_feature_context) | feature_prompt | chat_model
        _dict["formatted_sx"] = symptom_chain.invoke(input_dict).content
        return _dict
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
    
    output_dict = dict()
    diagnosis_chain = {
        "symptoms": itemgetter("symptoms"),
        "comments": RunnableLambda(format_symptoms) | RunnableLambda(Add_diagnostic_contexts) | RunnableLambda(map_diagnosis),
        } | main_prompt | chat_model
    output_dict["english"] = diagnosis_chain.invoke(_dict).content
    korean_chain = translate_prompt | chat_model
    output_dict["user_language"] = korean_chain.invoke({"input": output_dict["english"]}).content
    return output_dict

def Activate_chat_chain(
        chat_model,
        main_prompt,
        translate_prompt,
        _dict):
    output_dict = dict()
    chat_chain = RunnableLambda(Add_chat_context) | main_prompt | chat_model
    output_dict["english"] = chat_chain.invoke(_dict).content
    korean_chain = translate_prompt | chat_model
    output_dict["user_language"] = korean_chain.invoke({"input": output_dict["english"]}).content
    return output_dict
