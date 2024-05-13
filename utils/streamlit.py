import streamlit as st
from llm.base import Chat_model
from utils.messages import UI_messages, Messages_translator
from utils.util import RAG_prepare

def Setting_session_state():
    if "RAG_prepare" not in st.session_state:
        st.session_state.RAG_prepare = False
    if "model_prepare" not in st.session_state:
        st.session_state.model_prepare = False
    if "lang_changed" not in st.session_state:
        st.session_state.lang_changed = True
    if "progress" not in st.session_state:
        st.session_state.progress = "start"
    if "diagnosis" not in st.session_state:
        st.session_state.diagnosis = {}
    if "user_input_instance" not in st.session_state:
        st.session_state.user_input_instance = ""
    if "form_index" not in st.session_state:
        st.session_state.form_index = ""
    if "user_data" not in st.session_state:
        st.session_state.user_data = {}
    if "system_messages" not in st.session_state:
        st.session_state.system_messages = {}
    if "ai_messages" not in st.session_state:
        st.session_state.ai_messages = {}
    if "user_messages" not in st.session_state:
        st.session_state.user_messages = {}
    if "memory" not in st.session_state: #user language로 저장
        st.session_state.memory = [] #[{"role": "ai/user", "content": "something"}]
    if "chat_memory" not in st.session_state: #영어로 저장
        st.session_state.chat_memory = [] #[{"role": "ai/user", "content": "something"}]

def Setting_language():
    if st.session_state.lang_changed == True:
        if "user_language" not in st.session_state:
            ui = UI_messages("english")
        else:
            ui = UI_messages("english")
        st.session_state.system_messages = ui.system_messages()
        st.session_state.ai_messages = ui.ai_messages()
        st.session_state.user_messages = ui.user_messages()
        st.session_state.lang_changed = False

def Cache_language_status():
    st.session_state.lang_changed = True


def User_input_below():
    def Submit():
        ulang_2_eng = Messages_translator("english", to_eng=True)
        st.session_state.user_input_instance = ulang_2_eng.translate(st.session_state.widget)
        if st.session_state.progress == "add_info":
            st.session_state.user_data["additional_context_ulang"] = st.session_state.widget
        if st.session_state.progress == "chat":
            st.session_state.user_data["chat_input_ulang"] = st.session_state.widget
        st.session_state.widget = ""
    below_input_bar = st.text_input(
        label=st.session_state.system_messages["send_to_ai"]["request"],
        key="widget",
        on_change=Submit
        )

def Clear():
    col1, col2, col3 = st.columns(3)
    with col3:
        clear_button = st.button(label=st.session_state.system_messages["reset"], use_container_width=True)
    if clear_button:
        st.session_state.progress = "start"
        st.session_state.user_data = {}
        st.session_state.user_input_instance = ""
        st.session_state.memory = []
        st.session_state.chat_memory = []
        st.session_state.diagnosis = {}
        st.session_state.form_index = ""
        st.rerun()

@st.cache_data(show_spinner="WAIT...")
def Prepare_for_RAG(main_path, faiss_path):
    RAG_prepare(main_path, faiss_path)

class Format_form:
    form_choices_dict, form_suffix_dict = UI_messages.format_messages_for_form()

    def __init__(self, label:str):
        if self.validate_label(label):
            self.label = label

    def validate_label(self, label: str):
        if label not in self.form_choices_dict:
            raise KeyError("Wrong label")
        else:
            return True
        
    def format_form_options(self):
        label_index = list(self.form_choices_dict.keys()).index(self.label)
        options_list = list(self.form_choices_dict.values())[label_index]
        res_list = list()
        for i in range(len(options_list)):
            res_list.append(str(label_index)+str(i))
        return res_list
    
    def format_form_choices(self, num):
        return st.session_state.system_messages["form"][self.label]["contents"][int(num[1])]

    @classmethod
    def format_form_result(cls, args_list: list):
        label_keys_list = list(cls.form_choices_dict.keys())
        suffix = cls.form_suffix_dict
        text: str = ""
        for item in args_list:
            if type(item) == list:
                label_key = label_keys_list[int(item[0][0])]
                content = ", ".join(cls.form_choices_dict[label_key][int(num[1])] for num in item)
            if type(item) == str:
                label_key = label_keys_list[int(item[0])]
                content = cls.form_choices_dict[label_key][int(item[1])]
            text += suffix[label_key].format(contents= content)+"\n"
        return text
