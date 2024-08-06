import re
from operator import itemgetter
from langchain.vectorstores.faiss import FAISS
from langchain.schema.runnable import RunnableLambda
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_google_genai import GoogleGenerativeAIEmbeddings

from utils.util import openai_api, gemini_api

embedding_openai = OpenAIEmbeddings(api_key = openai_api)
embedding_gemini = GoogleGenerativeAIEmbeddings(model="models/embedding-001", api_key=gemini_api)


def Retriever_from_faiss(faiss_path: str):
    database = FAISS.load_local(folder_path=faiss_path, embeddings=embedding_openai, allow_dangerous_deserialization=True)
    retriever = database.as_retriever()
    return retriever
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
    context_list = vectordb_RAG.similarity_search(query=_dict["formatted_sx"], k=21)
    _dict["context_list"] = [item.page_content for item in context_list]
    del _dict["faiss_path"]
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
        _dict:dict):
    
    def format_symptoms(_dict: dict) -> dict:
        symptom_chain = RunnableLambda(Add_feature_context) | feature_prompt | chat_model
        _dict["formatted_sx"] = symptom_chain.invoke({
            "query": _dict["symptoms"],
            "faiss_path": _dict["faiss_path"]
            }).content
        return _dict
    def map_diagnosis(_dict: dict) -> str:
        text = ""
        cnt = 0
        above_thr_list = []
        def add_score(_dict:dict, cnt) -> dict:
            evaluate_each_chain = evaluate_each_prompt | chat_model
            res = evaluate_each_chain.invoke(_dict)
            try:
                score = re.match(r"^\d([.]\d+)?", res.content).group(0)
            except:
                score = "0"
            if float(score) > 0.3:
                above_thr_list.append(_dict["context"]+" <SCORE> "+score+"\n")
            else:
                cnt += 1
            return cnt
        def make_comment(_dict: dict):
            comment_chain = diagnose_each_prompt | chat_model
            comment = comment_chain.invoke(_dict).content
            return comment
        for item in _dict["context_list"]:
            cnt = add_score({
                "symptoms": _dict["formatted_sx"],
                "context": item
            }, cnt)
        text += f"{cnt} of 21 professionals said that the baby could be in a healthy condition. Other professionals said as below."
        for i in range(0, len(above_thr_list), 3):
            joined_context = "\n".join(above_thr_list[i:i+3])
            comment = make_comment({
                "symptoms": _dict["formatted_sx"], 
                "context": joined_context
                })
            text += "\n==\n"+comment
        return text
    
    diagnosis_chain = {
        "symptoms": itemgetter("symptoms"),
        "comments": RunnableLambda(format_symptoms) | RunnableLambda(Add_diagnostic_contexts) | RunnableLambda(map_diagnosis),
        } | main_prompt | chat_model
    return diagnosis_chain.invoke(_dict).content

def Activate_chat_chain(
        chat_model,
        agent_prompt,
        path,
        tools,
        _dict):
    from llm.agent import Chatting_agent
    chatbot = Chatting_agent(
        llm= chat_model,
        main_path= path,
        chat_tools= tools,
        agent_prompt= agent_prompt,
    )
    res = chatbot.invoke(
        input= _dict["input"],
        config= {
            "configurable": {
                "user_id": _dict["user_id"],
                "conversation_id":_dict["conversation_id"]
            }
        }
    )
    return res["output"]

def Activate_translate_chain(
        chat_model,
        main_prompt,
        _dict):
    translate_chain = main_prompt | chat_model
    return translate_chain.invoke(_dict).content