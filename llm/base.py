from langchain_community.llms.huggingface_endpoint import HuggingFaceEndpoint
from langchain_community.chat_models.huggingface import ChatHuggingFace
from langchain.memory import ConversationSummaryBufferMemory
from langchain_core.messages import HumanMessage, SystemMessage

llm_list = [
            "None",
            "Mistral (7b/instruct/v0.2)",
            "Zephyr (7b/beta)",
            "Gemma (7b/instruct/v1.1)",
            "Mistral (7b/instruct/v0.1)"
            ]

class Chat_model():
    llms = {
        "Zephyr (7b/beta)": "HuggingFaceH4/zephyr-7b-beta",
        "Gemma (7b/instruct/v1.1)": "google/gemma-1.1-7b-it",
        "(Bad perfomance) Falcon (7b/instruct)": "tiiuae/falcon-7b-instruct",
        "Mistral (7b/instruct/v0.2)": "mistralai/Mistral-7B-Instruct-v0.2",
        "Mistral (7b/instruct/v0.1)": "mistralai/Mistral-7B-Instruct-v0.1"
    }

    def __init__(self, llm: str, api_key: str):
        self.__llm = Chat_model.llms[llm]
        self.__api = api_key
        self.__categorize_model()
        self.__set_memory()
    
    def run(self, purpose: str, input: dict, *args, **kwargs):
        self.__validate_purpose(purpose)
        model = self.__set_model()

        if self.__purpose == "diagnosis":
            from llm.chains import Activate_diagnosis_chain
            main_prompt, evaluate_each_prompt, diagnose_each_prompt = self.__set_prompt_diagnosis()
            answer = Activate_diagnosis_chain(
                chat_model= model,
                main_prompt= main_prompt,
                evaluate_each_prompt= evaluate_each_prompt,
                diagnose_each_prompt= diagnose_each_prompt,
                _dict= input
            )

        if self.__purpose == "chat":
            from llm.chains import Activate_chat_chain
            main_prompt = self.__set_prompt_chat()
            answer = Activate_chat_chain(
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
        if purpose == "diagnosis":
            self.__purpose = purpose
        elif purpose == "chat":
            self.__purpose = purpose
        else:
            raise KeyError("Only two purposes are permitted: diagnosis or chat")

    def __categorize_model(self):
        if self.__llm in ["HuggingFaceH4/zephyr-7b-beta"]:
            self.__category = "chat_with_system"
        if self.__llm in ["google/gemma-1.1-7b-it",
                          "mistralai/Mistral-7B-Instruct-v0.2",
                          "mistralai/Mistral-7B-Instruct-v0.1"]:
            self.__category = "chat_without_system"
        if self.__llm in ["tiiuae/falcon-7b-instruct"]:
            self.__category = "unable_chat"

    def __set_llm(self):
        llm =  HuggingFaceEndpoint(
            repo_id= self.__llm,
            temperature= 0.1,
            huggingfacehub_api_token= self.__api,
            )
        return llm
    def __set_model(self):
        llm = self.__set_llm()
        model = ChatHuggingFace(llm=llm)
        return model
    
    def __set_memory(self):
        if self.__category == "chat_with_system":
            summary_cls = SystemMessage
        if self.__category == "chat_without_system":
            summary_cls = HumanMessage
        self.__memory = ConversationSummaryBufferMemory(
            human_prefix= "user",
            ai_prefix= "assistant",
            llm= self.__set_llm(),
            input_key= "input",
            output_key= "output",
            summary_message_cls= summary_cls,
            return_messages= True,
            max_token_limit= 2000,
        )

    def __set_prompt_chat(self):
        from llm.prompts import chat_dict, formatter_dict
        formatter = None
        chat_logs = self.__memory.load_memory_variables({})["history"]
        if self.__category == "chat_with_system":
            from llm.prompts import chat_prompt_system as pt
        if self.__category == "chat_without_system":
            from llm.prompts import chat_prompt_no_system as pt
        if self.__category == "unable_chat":
            from llm.prompts import template_prompt as pt
            formatter = formatter_dict[self.__llm],
        main_prompt = pt(
            role=chat_dict["role_chat"],
            question=chat_dict["question_chat"],
            example= None,
            ex_answer= None,
            formatter= formatter,
            chat_logs= chat_logs
        )
        return main_prompt

    def __set_prompt_diagnosis(self):
        from llm.prompts import diagnosis_dict, formatter_dict
        formatter = None
        if self.__category == "chat_with_system":
            from llm.prompts import chat_prompt_system as pt
        if self.__category == "chat_without_system":
            from llm.prompts import chat_prompt_no_system as pt
        if self.__category == "unable_chat":
            from llm.prompts import template_prompt as pt
            formatter = formatter_dict[self.__llm],
        main_prompt = pt(
            role=diagnosis_dict["role_setting_diagnosis"],
            question=diagnosis_dict["question_diagnosis"],
            example= None,
            ex_answer= None,
            formatter= formatter,
            chat_logs= None
        )
        evaluate_each_prompt = pt(
            role=diagnosis_dict["role_setting_evaluate"],
            question=diagnosis_dict["question_evaluate"],
            example=diagnosis_dict["examples_evaluate"],
            ex_answer=diagnosis_dict["ex_answers_evaluate"],
            formatter= formatter,
            chat_logs= None
        )
        diagnosis_each_prompt = pt(
            role=diagnosis_dict["role_setting_diag_each"],
            question=diagnosis_dict["question_diag_each"],
            example=diagnosis_dict["examples_diagnosis"],
            ex_answer=diagnosis_dict["ex_answers_diagnosis"],
            formatter= formatter,
            chat_logs= None)
        return main_prompt, evaluate_each_prompt, diagnosis_each_prompt
