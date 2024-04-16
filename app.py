import os
import streamlit as st
import json
from operator import itemgetter
from langchain_community.llms.huggingface_endpoint import HuggingFaceEndpoint
from langchain_community.chat_models.huggingface import ChatHuggingFace
from langchain.embeddings.huggingface import HuggingFaceInferenceAPIEmbeddings
from langchain.vectorstores.faiss import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.prompts import ChatPromptTemplate
from langchain.schema.runnable import RunnableLambda
#from langchain.callbacks.base import BaseCallbackHandler

# 함수 구현
base_embedding = HuggingFaceInferenceAPIEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
)
#if "diagnosis" not in st.session_state:
#    st.session_state.diagnosis = ""
#class ChatbotCallbackHandler(BaseCallbackHandler):
#    message = ""
#    def on_llm_start(self, *args, **kwars):
#        self.message_box = st.empty()
#    def on_llm_new_token(self, token: str, *args, **kwargs):
#        self.message += token
#        self.message_box.markdown(self.message)
#    
#class DiagnosisCallbackHandler(ChatbotCallbackHandler):
#    def on_llm_end(self, *args, **kwargs):
#        st.session_state.diagnosis = self.message


@st.cache_data(show_spinner="Model setting proceeds...")
def Choose_llm(chosen_llm: str, type: str):
    if chosen_llm == "Mistral-7B-Instruct-v0.2: Latest but not fine-tuned":
        llm_diagnosis =  HuggingFaceEndpoint(
            repo_id="mistralai/Mistral-7B-Instruct-v0.2",
            temperature= 0.1,
            #callbacks=DiagnosisCallbackHandler,
        )
        llm_chating = HuggingFaceEndpoint(
            repo_id="mistralai/Mistral-7B-Instruct-v0.2",
            temperature= 0.1,
            #callbacks=ChatbotCallbackHandler,
        )
    if chosen_llm == "BioGPT: fine-tuned but not latest":
        llm_diagnosis =  HuggingFaceEndpoint(
            repo_id="microsoft/BioGPT-Large",
            temperature= 0.1,
            #callbacks=DiagnosisCallbackHandler,
        )
        llm_chating =  HuggingFaceEndpoint(
            repo_id="microsoft/BioGPT-Large",
            temperature= 0.1,
            #callbacks=ChatbotCallbackHandler,
        )
    chat_model_diagnosis = ChatHuggingFace(llm=llm_diagnosis)
    chat_model_chating = ChatHuggingFace(llm=llm_chating)
    if type == "d":
        return chat_model_diagnosis
    if type == "c":
        return chat_model_chating

@st.cache_data(show_spinner= "RAG preparation proceeds...")
def Prepare_for_RAG():
    on_file_path = os.getcwd()
    on_dir_path = os.path.dirname(on_file_path)
    faiss_path = on_dir_path+"\\ForFAISS"
    os.mkdir(faiss_path)
    file_path = on_dir_path+"Entrez_selected_for_RAG.json"
    with open(file_path, "r") as f:
        try:
            papers_json = json.load(f)
        except:
            raise KeyError("JSON file has not been found. Please check your file path.")
    if papers_json:
        st.write("JSON File detected.")
    abs_list_raw = list(items["abstract"] for items in papers_json["paper_list"])
    metadata_list_raw = list(dict(filter(lambda items: items[0] != "abstract", article_dict.items())) for article_dict in papers_json["paper_list"])
    st.write("Pulling external database complete.")
    abs_list = list()
    metadata_list = list()
    splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        chunk_size=500,
        chunk_overlap=100
    )
    for i in range(len(abs_list_raw)):
        splitted_text_list = splitter.split_text(abs_list_raw[i])
        for j in range(len(splitted_text_list)):
            abs_list.append(splitted_text_list[j])
            metadata_list.append(metadata_list_raw[i])
    if len(abs_list) == len(metadata_list):
        st.write(f"Data formatting complete.\n{len(abs_list)} documents has been detected.")
    else:
        st.error("Unknow error occured! length of abs list and metadata list doesn't match.")
    st.write("Embedding documents... This work requires almost 10 minutes.")
    vectordb_RAG = FAISS.from_texts(texts=abs_list, embedding=base_embedding, metadatas=metadata_list)
    vectordb_RAG.save_local(folder_path=faiss_path)
    st.write("RAG preparation complete!")
    return True

def Generate_context(_dict: dict) -> str:
    return _Generate_context(query= _dict["query"], how_many_search= _dict["how_many_search"])

def _Generate_context(query, how_many_search):
    on_file_path = os.getcwd()
    on_dir_path = os.path.dirname(on_file_path)
    vectordb_RAG = FAISS.load_local(folder_path=str(on_dir_path+"\\ForFAISS"), embeddings=base_embedding, allow_dangerous_deserialization=True)
    context_list = vectordb_RAG.similarity_search(query=query, k=how_many_search)
    context_list_modified = [item.page_content+" ("+item.metadata["article_name"]+","+item.metadata["journal"]+")" for item in context_list]
    context_str = "\n".join(context_list_modified)
    return context_str
def Generate_symptom(_dict: dict) -> str:
    symptom_str = f"""The stool color of my baby was {_dict["basic_info"]["color"].lower()}. The stool of my baby seemed to be {_dict["basic_info"]["blood"]}. The stool of my baby was {_dict["basic_info"]["form"]}"""
    symptom_str = symptom_str + "\n" + _dict["additional_context"]
    return symptom_str

def Activate_diagnosis_chain(_dict:dict):
    diagnosis_chain = {
        "symptoms": itemgetter("user_data") | RunnableLambda(Generate_symptom),
        "context": {
            "query": itemgetter("user_data") | RunnableLambda(Generate_symptom),
            "how_many_search": itemgetter("how_many_search")
        } | RunnableLambda(Generate_context),
    } | diagnosis_propmt | chat_model_diagnosis
    res = diagnosis_chain.invoke(_dict)
    return res

# 랭체인 구현
diagnosis_propmt = ChatPromptTemplate.from_messages([
    (
        "system",
        """<s>[INST]You are a helpful disease-diagnosis assistant.
        You have to diagnosis diseases based on patient's symptoms and given contexts, step by step, making a chain of thoughts.
        Do not make an answer on your own when you have no idea about patient's symptoms and given contexts. In that case, just say you don't know.
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
        "ai",
        """The patient could be diagnosed as common cold.
        In the patient's symptoms, headache, fever, dry-nose and cough are important signs. Not having dizziness is also important.
        Based on the article common coldology, published on Journal of KYUs, it is reported that when the patients have fever, headache and cough they could be diagnosed as common cold.<s>"""
    ),
    (
        "human",
        """[INST]Patient's symptoms:
        {symptoms}
        #
        Contexts:
        {contexts}
        #####
        Diagnosis patient's disease base on patient's symptoms and contexts above.[/INST]"""
    ),
])


# 스트림릿 구현
st.set_page_config(
    page_title="Azang Health"
)
st.title("Chatbot for you!")
if "RAG_prepare" not in st.session_state:
    st.session_state["RAG_prepare"] = "no"
if "progress" not in st.session_state:
    st.session_state["progress"] = ["Start_state"]
if "user_data" not in st.session_state:
    st.session_state["user_data"] = {}
if "user_instance" not in st.session_state:
    st.session_state.user_instance = ""
def Submit():
    st.session_state.user_instance = st.session_state.widget
    st.session_state.widget = ""

with st.sidebar:
    chosen_llm = st.selectbox(
        label="Choose your llm!",
        options=[
            "None",
            "Mistral-7B-Instruct-v0.2: Latest but not fine-tuned", 
            "BioGPT: fine-tuned but not latest"
        ],
        placeholder="choose an option!"
    )
    if chosen_llm != "None":
        chat_model_diagnosis = Choose_llm(chosen_llm, "d")
        chat_model_chating = Choose_llm(chosen_llm, "c")
        if chat_model_diagnosis and chat_model_chating:
            st.write("Model has been activated!")
    if st.session_state["RAG_prepare"] == "no":
        rag_prepare = st.button(
            label="Start preparation for RAG!",
            use_container_width= True
        )
        if rag_prepare:
            Prepare_for_RAG()
            st.session_state["RAG_prepare"] = "yes"
    if st.session_state["RAG_prepare"] == "yes":
        st.write("RAG has been activated!")

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
    elif not poop_form:
        st.error("You must tell me about poop_form!")
    elif not blood_form:
        st.error("You must tell me about blood form!")
    else:
        st.session_state["user_data"]["basic_info"] = {"color": poop_color, "form": poop_form, "blood": blood_form}
        st.session_state["progress"][0] = "information"
if st.session_state["progress"][0] != "Start_state":
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
    if st.session_state["progress"][0] != "user_qa_end":
        context_end = st.button("I am satisfied with my explanation.", use_container_width=True)
        if context_end:
            st.session_state["progress"][0] = "user_qa_end"
            st.rerun()
if st.session_state["progress"][0] == "user_qa_end":
    with st.chat_message("human"):
        st.write("I am satisfied with my explanation.")
    with st.chat_message("ai"):
        st.write("""OOOKAY!! Then it's my turn now.""")
        if st.session_state["RAG_prepare"] == "yes":
            st.write(Activate_diagnosis_chain({
                "user_data" : st.session_state["user_data"],
                "how_many_search" : 10
            }))

user_input = st.text_input("Send a message to your ai!", key="widget", on_change=Submit)
if st.session_state.user_instance and st.session_state["progress"][0] == "Start_state":
    st.error("Oh... you might forget to fill the form above! Can you double-check? I need some information about your baby's poop to help you!")
    st.session_state.user_instance = ""
if st.session_state.user_instance and st.session_state["progress"][0] == "information":
    st.session_state["user_data"]["additional_context"] =  st.session_state.user_instance
    st.session_state.user_instance = ""
    st.rerun()

col1, col2, col3 = st.columns(3)
with col3:
    clear_button = st.button(label="CLEAR", use_container_width=True)
if clear_button:
    st.session_state["progress"] = ["Start_state"]
    st.session_state["user_data"] = {}
    st.session_state.user_instance = ""
    st.rerun()
