import os
import streamlit as st
from utils.util import Setting_language, Setting_session_state, User_input_below, Clear, Format_form, chat_model

def Setting():
    st.set_page_config(
        page_title="aIkNow Healthcare"
    )
    Setting_session_state()
    Setting_language()
    global main_path, faiss_path
    main_path = os.getcwd()
    faiss_path = os.path.join(main_path, "faiss")

def main():
    st.title(st.session_state.system_messages["title"])
    
    # 대화 로그 출력
    if st.session_state.memory:
        for item in st.session_state.memory:
            st.chat_message(name=item["role"]).write(item["content"])

    # phase 1: progress = start
    # 유저한테서 기본적인 정보 받아옴
    if st.session_state.progress == "start":
        with st.form(key="lock"):
            password = st.text_input(
                label="해당 프로젝트 팀 이름을 영어로 적으시오",
                type= "password"
            )
            lock_pass = st.form_submit_button()
        if lock_pass:
            if password == st.secrets["name"]:
                st.session_state.progess = "form"
                st.rerun()

    if st.session_state.progress == "form":
        with st.chat_message("assistant"):
            st.write(st.session_state.ai_messages["intro"])
        if st.session_state.user_input_instance:
            st.error(st.session_state.system_messages["send_to_ai"]["error"])
            st.session_state.user_input_instance = ""
        form_item_list = list(Format_form.form_choices_dict.keys())
        if st.session_state.form_index == "":
            form_num = st.slider(
                label=st.session_state.system_messages["choose_number_of_data"],
                min_value=1,
                max_value=7,
                step=1,
                value=1,
            )
            num_button = st.button(label="submit!")
            if num_button:
                st.session_state.form_index = int(form_num)
                st.session_state.user_data["info_list"] = []
                st.rerun()
        elif st.session_state.form_index != 0:
            if st.session_state.user_data["info_list"] != []:
                for item in st.session_state.user_data["info_list"]:
                    with st.chat_message("user"):
                        st.write(item)
            with st.chat_message("assistant"):
                st.write(f"{st.session_state.form_index} "+st.session_state.system_messages["left_form_num"])
            with st.form(key=f"form_number_{st.session_state.form_index}"):
                time_data = st.text_input(
                    label=st.session_state.system_messages["time_data"]
                )
                for item in form_item_list:
                    if item == "property_info":
                        continue
                    st.radio(
                        label=st.session_state.system_messages["form"][item]["request"],
                        options=Format_form(item).format_form_options(),
                        format_func=Format_form(item).format_form_choices,
                        key= item + str(st.session_state.form_index),
                        horizontal= True
                    )
                st.multiselect(
                    label=st.session_state.system_messages["form"]["property_info"]["request"],
                    options=Format_form("property_info").format_form_options(),
                    default=Format_form("property_info").format_form_options()[0],
                    format_func=Format_form("property_info").format_form_choices,
                    key= "property_info" + str(st.session_state.form_index)
                )
                basic_information_submitted = st.form_submit_button()
            if basic_information_submitted:
                info_str = Format_form.format_form_result(
                    args_list=[st.session_state[item + str(st.session_state.form_index)] for item in form_item_list]
                    )
                each_info = f"""<TIME DATA>
                {time_data}
                <DESCRIPTION>
                {info_str}
                -
                """
                st.session_state.user_data["info_list"].append(each_info)
                st.session_state.form_index -= 1
                st.rerun()
        else:
            st.session_state.user_data["basic_info"] = "\n\n".join(st.session_state.user_data["info_list"])
            st.session_state.memory.append({"role": "assistant", "content": st.session_state.ai_messages["intro"]})
            st.session_state.progress = "add_info"
            st.rerun()
    
    # phase 2: progress = information
    # 유저한테 조금 더 디테일한 정보 받아옴
    if st.session_state.progress == "add_info":
        with st.chat_message("user"):
            st.markdown("*form submitted*")
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
                st.session_state.user_data["symptoms"] = st.session_state.user_data["basic_info"]+"\n"+st.session_state.user_data["additional_context"]
                st.session_state.memory.append({"role": "user", "content": st.session_state.user_data["additional_context_ulang"]})    
                st.session_state.progress = "chain"
                st.rerun()
        
    # phase 3: progess = chain
    # 유저에게 모든 필요한 정보를 다 받은 경우. 검색 dataset 크기 조정 후 진단 체인 실행
    if st.session_state.progress == "chain":
        if st.session_state.user_input_instance:
            st.session_state.user_input_instance = ""
        with st.chat_message("assistant"):
            st.write(st.session_state.ai_messages["chain"])
        start_diagnosis = st.button(
            label=st.session_state.system_messages["chain"]["start"],
            use_container_width= True
        )
        if start_diagnosis:
            diagnosis_input_dict= {
                "symptoms" : st.session_state.user_data["symptoms"],
                "how_many_search" : 15,
                "faiss_path": os.path.join(faiss_path, "abs_with_textbook"),
            }
            with st.status(label="Making diagnosis"):
                st.session_state.diagnosis = chat_model.run(
                    purpose= "diagnosis",
                    input= diagnosis_input_dict
                    )
            st.session_state.memory.append({"role": "assistant", "content": st.session_state.diagnosis["user_language"]})
            st.session_state.progress = "chat"
            st.rerun()

    # phase 4: progress = chat
    # 진단 기반으로 챗봇 구현
    if st.session_state.progress == "chat":
        if st.session_state.chat_memory:
            chat_model.add_memory(st.session_state.chat_memory)
        if st.session_state.user_input_instance:
            chat_input = {
                "symptoms":st.session_state.user_data["symptoms"],
                "query": st.session_state.user_input_instance,
                "diagnosis": st.session_state.diagnosis["english"],
                "faiss_path": os.path.join(faiss_path, "abs_with_textbook")}
            chat_answer = chat_model.run(
                purpose="chat",
                input= chat_input
            )
            st.session_state.chat_memory.append({"input": st.session_state.user_input_instance, "output": chat_answer["english"]})
            st.session_state.memory.append({"role": "user", "content": st.session_state.user_data["chat_input_ulang"]})
            st.session_state.memory.append({"role": "assistant", "content": chat_answer["user_language"]})
            st.session_state.user_input_instance = ""
            st.rerun()

    # 하단 입력 공간과 대화 초기화 버튼
    User_input_below()
    Clear()


if __name__ == "__main__":
    Setting()
    main()
