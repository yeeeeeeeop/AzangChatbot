import os
import streamlit as st
from utils.util import Read_json, Split_and_format_documents, Generate_local_faiss
from llm.base import llm_list, choose_llm_for_chatmodel
from llm.chains import Activate_diagnosis_chain

def Setting_path():
    global main_path, faiss_path
    main_path = os.getcwd()
    faiss_path = main_path+"\\ForFAISS"
    if not os.path.isdir(faiss_path):
        os.mkdir(faiss_path)

@st.cache_data(show_spinner="Model setting proceeds...")
def Load_chat_model(chosen_llm: str, api_token: str):
    chat_model = choose_llm_for_chatmodel(chosen_llm, api_token)
    return chat_model

@st.cache_data(show_spinner="RAG preparation proceeds...")
def Prepare_for_RAG():
    papers_json = Read_json(main_path + "\\resource\\Entrez_selected_for_RAG.json")
    abs_list_raw = list(items["abstract"] for items in papers_json["paper_list"])
    metadata_list_raw = list(dict(filter(lambda items: items[0] != "abstract", article_dict.items())) for article_dict in papers_json["paper_list"])
    abs_list, metadata_list = Split_and_format_documents(abs_list_raw, metadata_list_raw)
    Generate_local_faiss(abs_list, metadata_list, faiss_path)

@st.cache_data(show_spinner="Making diagnosis...")
def Making_diagnosis(chat_model, _dict: dict):
    diagnosis_str = Activate_diagnosis_chain(chat_model, _dict)
    return diagnosis_str

def Setting_session_state():
    if "RAG_prepare" not in st.session_state:
        st.session_state.RAG_prepare = "no"
    if "model_prepare" not in st.session_state:
        st.session_state.model_prepare = "no"
    if "progress" not in st.session_state:
        st.session_state.progress = "Start_state"
    if "user_data" not in st.session_state:
        st.session_state["user_data"] = {}
    if "user_input_instance" not in st.session_state:
        st.session_state.user_input_instance = ""

def Sidebar():
    global chat_model
    with st.sidebar:
        chosen_llm = st.selectbox(
            label="Choose your llm!",
            options=llm_list,
            placeholder="choose an option!"
        )
        api_token = st.text_input(label="Write your huggingface api token!", placeholder="HUGGINGFACEHUB_API_KEY", type="password")
        chat_model = None
        load_model = st.button(
            label="Load Chat model!",
            use_container_width=True,
            )
        if chosen_llm == "None":
            st.session_state.model_prepare = "no"
        if load_model and chosen_llm != "None":
            st.session_state.model_prepare = "yes"
        if st.session_state.model_prepare == "yes" and chosen_llm != "None" and api_token:
            chat_model = Load_chat_model(chosen_llm, api_token)
            if chat_model:
                st.write("Model has been activated!")
        if st.session_state.RAG_prepare == "no":
            rag_prepare = st.button(
                label="Start preparation for RAG!",
                use_container_width= True
            )
            if rag_prepare:
                if not os.path.isdir(faiss_path):
                    Prepare_for_RAG()
                st.session_state.RAG_prepare = "yes"
                st.rerun()
        if st.session_state.RAG_prepare == "yes":
            st.write("RAG has been activated!")

def User_input_below():
    def Submit():
        st.session_state.user_input_instance = st.session_state.widget
        st.session_state.widget = ""
    below_input_bar = st.text_input(label="Send a message to your ai!", key="widget", on_change=Submit)
    if st.session_state.user_input_instance and st.session_state.progress == "Start_state":
        st.error("Oh... you might forget to fill the form above! Can you double-check? I need some information about your baby's poop to help you!")
        st.session_state.user_input_instance = ""
    if st.session_state.user_input_instance and st.session_state.progress == "information":
        st.session_state["user_data"]["additional_context"] =  st.session_state.user_input_instance
        st.session_state.user_input_instance = ""
        st.rerun()

def Clear():
    col1, col2, col3 = st.columns(3)
    with col3:
        clear_button = st.button(label="CLEAR", use_container_width=True)
    if clear_button:
        st.session_state.progress = "Start_state"
        st.session_state["user_data"] = {}
        st.session_state.user_input_instance = ""
        st.rerun()

def main():
    st.title("Chatbot for you!")
    with st.chat_message("ai"):
        st.write("""Hi! I'm baby poop expert... And I'm here for YOU! 
                \nBut wait... I need some information about your baby's poop.
                \nCan you fill the form below for me to help you?
                \nOh, I recommend you to do something on your left sidebar first!""")

    with st.expander(label="Tell me some informations about your baby's poop!", expanded=True):
        with st.form(key="form_first"):
            poop_color = st.text_input(
                label="Write your baby's poop color",
                placeholder="Red or Green or Black... or else"
            )
            poop_form = st.select_slider(
                label="Choose the baby poop's form",
                options=["severe diarrhea", "diarrhea", "normal", "constipation", "severe constipation"],
                help="this is your help tooltip",
                value="normal"
            )
            blood_form = st.select_slider(
                label="Which form you baby's bloody poop?",
                options=["not-bloody", "bloody",]
            )
            baby_poop_information = st.form_submit_button()
    if baby_poop_information:
        if not poop_color:
            st.error("You must tell me about poop color!")
        else:
            st.session_state["user_data"]["basic_info"] = {"color": poop_color, "form": poop_form, "blood": blood_form}
            st.session_state.progress = "information"
    
    if st.session_state.progress != "Start_state":
        with st.chat_message("ai"):
            st.write("The form submitted! You can fold the form above.")
            st.write(f"Okay. Now I know that your baby's poop was {poop_form}, {poop_color}, and {blood_form}")
            st.write("Is there something more to tell me about your baby? Tell me about it in one message!")
    
    if "additional_context" in st.session_state["user_data"]:
        with st.chat_message("human"):
            st.write(st.session_state["user_data"]["additional_context"])
        with st.chat_message("ai"):
            st.write("""Do you think the explanation you sent is enough?
                        \nPlease correct and send the explanation until you are satisfied, and press the button below if you are satisfied""")
        if st.session_state.progress != "user_qa_end":
            context_end = st.button("I am satisfied with my explanation.", use_container_width=True)
            if context_end:
                st.session_state.progress = "user_qa_end"
                st.rerun()
    
    if st.session_state.progress == "user_qa_end":
        with st.chat_message("human"):
            st.write("I am satisfied with my explanation.")
        with st.chat_message("ai"):
            st.write("""Okay. Just give me a few minutes, or just seconds. I'll help you.""")
            if st.session_state.RAG_prepare == "yes" and chat_model:
                diagnosis_input_dict= {
                    "user_data" : st.session_state["user_data"],
                    "how_many_search" : 20,
                    "faiss_path": faiss_path,
                }
                st.write(Activate_diagnosis_chain(chat_model, diagnosis_input_dict))
            elif st.session_state.RAG_prepare == "no":
                st.error("You have to prepare RAG thorough left sidebar for me to diagnosis.")
            else:
                st.error("You have to set a chat model thorough left sidebar for me to diagnosis.")
                st.session_state.model_prepare = "no"

    User_input_below()
    Clear()

if __name__ == "__main__":
    st.set_page_config(
        page_title="Azang Health"
    )
    Setting_path()
    Setting_session_state()
    Sidebar()
    main()