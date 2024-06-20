import os
#import json
import streamlit as st
from langchain_core.tools import create_retriever_tool, tool
from llm.chains import Retriever_from_faiss

def Tools_for_chat(main_path) -> list:
    ds_retriever = Retriever_from_faiss(faiss_path=os.path.join(main_path, "faiss", "textbook"))
    care_retriever = Retriever_from_faiss(faiss_path=os.path.join(main_path, "faiss", "care"))

    ds_search = create_retriever_tool(
        retriever= ds_retriever,
        name="PediatricGastroenterology",
        description= "Use this tool when you need to look for a disease concept or pathology",
    )
    care_search = create_retriever_tool(
        retriever= care_retriever,
        name="InfantCare",
        description= "Use this tool when you need to look for how to treat a baby or what care is needed for the baby",
    )

    @tool
    def ClinicalIdentity(user_id: str):
        """
        This tool was created to access patient's personal information.
        By giving user id to this tool, you can see the symptoms the patient complained of and the diagnosis made by another healthcare expert.
        """
        #with open(file=os.path.join(main_path, "user", user_id+".json"), mode="r") as f:
        #    personal_data = json.load(f)
        personal_data = st.session_state.user_data[user_id]
        return personal_data["personal"]+"\n===\n"+personal_data["symptoms"]+"\n===\n"+personal_data["diagnosis"]

    chat_tools = [ds_search, care_search, ClinicalIdentity]
    return chat_tools