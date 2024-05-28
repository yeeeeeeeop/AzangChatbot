from langchain_openai.chat_models import ChatOpenAI
from langchain.memory import ConversationSummaryBufferMemory

class Chat_model():

    def __init__(self, api_key):
        self.__api = api_key
        self.__set_memory()
    
    def run(self, purpose: str, input: dict):
        self.__validate_purpose(purpose)
        model = ChatOpenAI(
            temperature=0.1,
            max_tokens=1000,
            api_key= self.__api,
            model="gpt-3.5-turbo-0125",
            )

        if self.__purpose == "diagnosis":
            from llm.chains import Activate_diagnosis_chain
            main_prompt, evaluate_each_prompt, diagnose_each_prompt, feature_prompt, translate_prompt = self.__set_prompt_diagnosis()
            answer = Activate_diagnosis_chain(
                chat_model= model,
                main_prompt= main_prompt,
                evaluate_each_prompt= evaluate_each_prompt,
                diagnose_each_prompt= diagnose_each_prompt,
                feature_prompt= feature_prompt,
                translate_prompt= translate_prompt,
                _dict= input
                )

        if self.__purpose == "chat":
            from llm.chains import Activate_chat_chain
            main_prompt, translate_prompt = self.__set_prompt_chat()
            answer = Activate_chat_chain(
                chat_model= model,
                main_prompt= main_prompt,
                translate_prompt= translate_prompt,
                _dict= input
                )

        if self.__purpose == "to_eng":
            from llm.chains import Activate_translate_chain
            main_prompt = self.__set_prompt_to_eng()
            answer = Activate_translate_chain(
                chat_model= model,
                main_prompt= main_prompt,
                _dict= input
                )

        return answer

    def add_memory(self, chat_memory: list):
        for item in chat_memory:
            self.__memory.save_context(
                inputs= {"input": item["input"]},
                outputs= {"output": item["output"]}
                )

    def __validate_purpose(self, purpose):
        if purpose in ["diagnosis", "chat", "to_eng"]:
            self.__purpose = purpose
        else:
            raise KeyError("Improper purpose")

    def __set_memory(self):
        self.__memory = ConversationSummaryBufferMemory(
            human_prefix= "user",
            ai_prefix= "assistant",
            llm= ChatOpenAI(temperature=0.1, api_key=self.__api, model="gpt-3.5-turbo-0125"),
            input_key= "input",
            output_key= "output",
            return_messages= True,
            max_token_limit= 2000,
        )

    def __set_prompt_diagnosis(self):
        from llm.prompts import diagnosis_dict, feature_extr_dict, translate_dict, chat_prompt_system
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
        translate_prompt = chat_prompt_system(
            role=translate_dict["role"],
            question=translate_dict["question"],
            )
        return main_prompt, evaluate_each_prompt, diagnosis_each_prompt, feature_prompt, translate_prompt

    def __set_prompt_chat(self):
        from llm.prompts import chat_dict, translate_dict, chat_prompt_system
        main_prompt = chat_prompt_system(
            role=chat_dict["role"],
            question=chat_dict["question"],
            chat_logs= self.__memory.load_memory_variables({})["history"]
            )
        translate_prompt = chat_prompt_system(
            role=translate_dict["role"],
            question=translate_dict["question"],
            )
        return main_prompt, translate_prompt

    def __set_prompt_to_eng(self):
        from llm.prompts import translate_dict, chat_prompt_system
        main_prompt = chat_prompt_system(
            role=translate_dict["role_to_eng"],
            question=translate_dict["question_to_eng"],
            )
        return main_prompt