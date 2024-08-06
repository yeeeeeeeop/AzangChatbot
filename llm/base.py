import os
from langchain_openai.chat_models import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from utils.util import openai_api, gemini_api

class Chat_model:
    def __init__(self, purpose: str, language: str, main_path: str):
        self.__validate_purpose(purpose)
        self.__validate_language(language)
        self.__path = main_path
        if self.__purpose == "chat":
            self.__set_tools()
    
    def run(self, input: dict) -> dict:
        # model = ChatOpenAI(
        #     temperature=0.1,
        #     max_tokens=1000,
        #     api_key= openai_api,
        #     model="gpt-3.5-turbo-0125",
        #     )
        model = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash-latest",
            api_key= gemini_api,
            temperature=0.1,
            max_tokens=1000,
            convert_system_message_to_human=True
            )

        if self.__purpose == "diagnosis":
            from llm.chains import Activate_diagnosis_chain
            main_prompt, evaluate_each_prompt, diagnose_each_prompt, feature_prompt = self.__set_prompt_diagnosis()
            input["faiss_path"] = os.path.join(self.__path, "faiss", "abs_with_textbook")
            answer = Activate_diagnosis_chain(
                chat_model= model,
                main_prompt= main_prompt,
                evaluate_each_prompt= evaluate_each_prompt,
                diagnose_each_prompt= diagnose_each_prompt,
                feature_prompt= feature_prompt,
                _dict= input
                )

        if self.__purpose == "chat":
            from llm.chains import Activate_chat_chain
            from llm.prompts import agent_prompt
            answer = Activate_chat_chain(
                chat_model= model,
                agent_prompt= agent_prompt,
                path= self.__path,
                tools= self.__tools,
                _dict= input
                )

        if self.__langauge != "English":
            from llm.chains import Activate_translate_chain
            translate_prompt = self.__set_prompt_translate()
            answer_user_language = Activate_translate_chain(
                chat_model= model,
                main_prompt= translate_prompt,
                _dict = {
                    "language": self.__langauge,
                    "input": answer
                }
            )
            answer_dict = {"english": answer, "user_language": answer_user_language}
        else:
            answer_dict = {"english": answer, "user_language": answer}

        return answer_dict

    def __validate_purpose(self, purpose):
        if purpose in ["diagnosis", "chat", "to_eng"]:
            self.__purpose = purpose
        else:
            raise KeyError("Improper purpose")

    def __validate_language(self, langauge):
        if langauge in ["English", "Korean"]:
            self.__langauge = langauge
        else:
            raise KeyError("Improper langauge")

    def __set_tools(self):
        from llm.tool import Tools_for_chat
        self.__tools = Tools_for_chat(main_path=self.__path)

    def __set_prompt_diagnosis(self):
        from llm.prompts import diagnosis_dict, feature_extr_dict, chat_prompt_system
        main_prompt = chat_prompt_system(
            role=diagnosis_dict["role_setting_diagnosis"],
            question=diagnosis_dict["question_diagnosis"],
        )
        evaluate_each_prompt = chat_prompt_system(
            role=diagnosis_dict["role_setting_evaluate"],
            question=diagnosis_dict["question_evaluate"],
            example=diagnosis_dict["examples_evaluate"],
            ex_answer=diagnosis_dict["ex_answers_evaluate"],
        )
        diagnosis_each_prompt = chat_prompt_system(
            role=diagnosis_dict["role_setting_diag_each"],
            question=diagnosis_dict["question_diag_each"],
            example=diagnosis_dict["examples_diagnosis"],
            ex_answer=diagnosis_dict["ex_answers_diagnosis"],
            )
        feature_prompt = chat_prompt_system(
            role=feature_extr_dict["role"],
            question=feature_extr_dict["question"],
            )
        return main_prompt, evaluate_each_prompt, diagnosis_each_prompt, feature_prompt
    
    def __set_prompt_translate(self):
        from llm.prompts import translate_dict, chat_prompt_system
        translate_prompt = chat_prompt_system(
            role=translate_dict["role"],
            question=translate_dict["question"],
            )
        return translate_prompt
    
class Messages_translator:
    from llm.prompts import kor_to_eng_prompt
    __lang = "english"
    __trans = kor_to_eng_prompt | ChatGoogleGenerativeAI(temperature=0.1, api_key=gemini_api, model="gemini-1.5-flash-latest",  convert_system_message_to_human=True)

    def __init__(self, language: str, to_eng: bool | None = False):
        self.__lang = language
        if to_eng == True:
            self.from_lang = self.__lang
            self.to_lang = "english"
        else:
            self.from_lang = "english"
            self.to_lang = self.__lang

    def translate(self, *args):
        for_translated_list = list(args)
        list_length = len(for_translated_list)
        if self.__lang == "english":
            if list_length == 1:
                return for_translated_list[0]
            else:
                return for_translated_list
        else:
            translated_list = self.__translate_list(for_translated_list)
            if list_length == 1:
                return translated_list[0]
            else:
                return translated_list

    def __translate_text(self, _text: str):
        if type(_text) != str:
            raise TypeError("Only str could be translated.")
        trs = self.__trans
        res = trs.invoke({"input": _text})
        return res.content

    def __translate_list(self, _list: list) -> list:
        instance_list = list()
        for item in _list:
            if type(item) == str:
                item_trs = self.__translate_text(item)
            elif type(item) == list:
                item_trs = self.__translate_list(item)
            elif type(item) == dict:
                item_trs = self.__translate_dict(item)
            else:
                raise TypeError("How could...? You've got an error in list translation")
            instance_list.append(item_trs)
        return instance_list

    def __translate_dict(self, _dict: dict) -> dict:
        instance_dict = dict()
        dict_keys_list = list(_dict.keys())
        dict_values_list = list(_dict.values())
        for index, value in enumerate(dict_values_list):
            if type(value) == str:
                value_trs = self.__translate_text(value)
            elif type(value) == dict:
                value_trs = self.__translate_dict(value)
            elif type(value) == list:
                value_trs = self.__translate_list(value)
            else:
                raise TypeError("How could...? You've got an error in dict translation")
            instance_dict[f"{dict_keys_list[index]}"] = value_trs
        return instance_dict