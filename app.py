import os
import streamlit as st
from llm.base import llm_list, Chat_model
from utils.streamlit import *

def Setting():
    st.set_page_config(
        page_title="aIkNow Healthcare"
    )
    Setting_session_state()
    Setting_language()
    global main_path, faiss_path
    main_path = os.getcwd()
    faiss_path = os.path.join(main_path, "ForFAISS")
    if not os.path.isdir(faiss_path):
        os.mkdir(faiss_path)

def Sidebar():
    global chat_model, user_language
    with st.sidebar:
        # 언어 설정
        user_language = st.selectbox(
            label= "LANGUAGE",
            options= ["english", "korean"],
            index= 0,
            key="user_language",
            on_change=Cache_language_status
        )

        # ai 모델 설정
        chosen_llm = st.selectbox(
            label=st.session_state.system_messages["choice"],
            options=llm_list,
        )
        api_token = st.text_input(label=st.session_state.system_messages["write"], placeholder="HuggingfaceHub or OpenAI", type="password")
        chat_model = None
        load_model = st.button(
            label=st.session_state.system_messages["model"]["request"],
            use_container_width=True,
            )
        if chosen_llm == "None" or not api_token:
            st.session_state.model_prepare = False
        if load_model and chosen_llm != "None" and api_token:
            st.session_state.model_prepare = True
        if st.session_state.model_prepare == True and chosen_llm != "None" and api_token:
            chat_model = Chat_model(chosen_llm, api_token)
            if chat_model:
                st.write("LLM "+st.session_state.system_messages["complete"])
        
        # RAG를 위한 데이터베이스 생성.
        # 1회 설정 후에는 재설정하지 않아도 괜찮도록 구현
        if st.session_state.RAG_prepare == False:
            rag_prepare = st.button(
                label=st.session_state.system_messages["RAG"]["request"],
                use_container_width= True
            )
            if rag_prepare:
                if not os.path.isfile(os.path.join(faiss_path, "index.faiss")):
                    Prepare_for_RAG(main_path, faiss_path)
                st.session_state.RAG_prepare = True
                st.rerun()
        if st.session_state.RAG_prepare == True:
            st.write("RAG "+st.session_state.system_messages["complete"])

def main():
    st.title(st.session_state.system_messages["title"])
    
    # 대화 로그 출력
    if st.session_state.memory:
        for item in st.session_state.memory:
            st.chat_message(name=item["role"]).write(item["content"])

    # phase 1: progress = start
    # 유저한테서 기본적인 정보 받아옴
    if st.session_state.progress == "start":
        with st.chat_message("assistant"):
            st.write(st.session_state.ai_messages["intro"])
        if st.session_state.user_input_instance:
            st.error(st.session_state.system_messages["send_to_ai"]["error"])
            st.session_state.user_input_instance = ""
        form_num = st.slider(
            label=st.session_state.system_messages["choose_number_of_data"],
            min_value=1,
            max_value=7,
            step=1,
            value=1,
        )
        form_item_list = list(Format_form.form_choices_dict.keys())
        for i in range(form_num):
            if i < len(st.session_state.form_index):
                st.info(f"""{st.session_state.user_data[f"info_{i}"]}""")
            else:
                with st.form(key=f"form_number_{i}"):
                    for item in form_item_list:
                        st.radio(
                            label=st.session_state.system_messages["form"][item]["request"],
                            options=Format_form(item).format_form_options(),
                            format_func=Format_form(item).format_form_choices,
                            key= item + str(i),
                            horizontal= True
                        )
                    basic_information_submitted = st.form_submit_button()
                if basic_information_submitted:
                    st.session_state.user_data[f"info_{i}"] = Format_form.format_form_result(
                        args_list=[st.session_state[item + str(i)] for item in form_item_list]
                        )
                    st.session_state.form_index += "."
                    st.rerun()
        if len(st.session_state.form_index) == form_num:
            st.session_state.user_data["basic_info"] = "\n\n".join([st.session_state.user_data[f"info_{i}"] for i in range(form_num)])
            st.session_state.memory.append({"role": "assistant", "content": st.session_state.ai_messages["intro"]})
            st.session_state.memory.append({"role": "user", "content": st.session_state.user_data["basic_info"]})
            st.session_state.progress = "information"
            st.rerun()
    
    # phase 2: progress = information
    # 유저한테 조금 더 디테일한 정보 받아옴
    if st.session_state.progress == "information":
        with st.chat_message("assistant"):
            st.write(st.session_state.ai_messages["form_submitted"])
        if st.session_state.user_input_instance:
            st.session_state.user_data["additional_context"] =  st.session_state.user_input_instance
            st.session_state.user_input_instance = ""
            st.rerun()
        if "additional_context" in st.session_state.user_data:
            with st.chat_message("user"):
                st.write(st.session_state.user_data["additional_context_ulang"])
            with st.chat_message("assistant"):
                st.write(st.session_state.ai_messages["check_user_input"])
            user_confirmed = st.button(
                label=st.session_state.user_messages["user_confirmed"],
                use_container_width=True
                )
            if user_confirmed:
                st.session_state.memory.append({"role": "assistant", "content": st.session_state.ai_messages["form_submitted"]})
                st.session_state.memory.append({"role": "user", "content": st.session_state.user_data["additional_context_ulang"]})    
                st.session_state.user_data["symptoms"] = st.session_state.user_data["basic_info"]+"\n"+st.session_state.user_data["additional_context"]
                st.session_state.progress = "chain"
                st.rerun()

    # phase 3: progess = chain
    # 유저에게 모든 필요한 정보를 다 받은 경우. 검색 dataset 크기 조정 후 진단 체인 실행
    if st.session_state.progress in "chain":
        with st.chat_message("assistant"):
            st.write(st.session_state.ai_messages["chain"])
        how_many_search = st.slider(
            label=st.session_state.system_messages["chain"]["num"],
            min_value=10,
            max_value=70,
            value=15,
            step= 1,
        )
        start_diagnosis = st.button(
            label=st.session_state.system_messages["chain"]["start"],
            use_container_width= True
        )
        if start_diagnosis:
            if st.session_state.RAG_prepare == True and chat_model:
                diagnosis_input_dict= {
                    "symptoms" : st.session_state.user_data["symptoms"],
                    "how_many_search" : how_many_search,
                    "faiss_path": faiss_path,
                    "language": st.session_state.user_language
                }
                with st.status(label="Making diagnosis"):
                    st.session_state.diagnosis = chat_model.run(
                        purpose= "diagnosis",
                        input= diagnosis_input_dict
                        )
                st.session_state.memory.append({"role": "assistant", "content": st.session_state.diagnosis})
                st.session_state.progress = "chat"
                st.rerun()
            elif st.session_state.RAG_prepare == False:
                st.error(st.session_state.system_messages["RAG"]["error"])
            else:
                st.error(st.session_state.system_messages["model"]["error"])
                st.session_state.model_prepare = False

    # phase 4: progress = chat
    # 진단 기반으로 챗봇 구현
    if st.session_state.progress == "chat":
        if chat_model and st.session_state.chat_memory:
            chat_model.add_memory(st.session_state.chat_memory)
        elif st.session_state.chat_memory:
            st.error(st.session_state.system_messages["model"]["error"])
            st.session_state.model_prepare = False
        if st.session_state.user_input_instance:
            chat_input = {
                "symptoms":st.session_state.user_data["symptoms"],
                "query": st.session_state.user_input_instance,
                "diagnosis": st.session_state.diagnosis,
                "faiss_path": faiss_path}
            chat_answer = chat_model.run(
                purpose="chat",
                input= chat_input
            )
            st.session_state.chat_memory.append({"input": st.session_state.user_input_instance, "output": chat_answer})
            st.session_state.memory.append({"role": "user", "content": st.session_state.user_data["chat_input_ulang"]})
            st.session_state.memory.append({"role": "assistant", "content": chat_answer})
            st.session_state.user_input_instance = ""
            st.rerun()

    # 하단 입력 공간과 대화 초기화 버튼
    User_input_below()
    Clear()


if __name__ == "__main__":
    Setting()
    Sidebar()
    main()
