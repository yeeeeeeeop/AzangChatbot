from langchain_community.llms.huggingface_endpoint import HuggingFaceEndpoint
from langchain_community.chat_models.huggingface import ChatHuggingFace

llm_list = [
            "None",
            "Mistral-7B-Instruct-v0.2: Latest but not fine-tuned", 
            "BioGPT: fine-tuned but not latest"
            ]

def choose_llm_for_chatmodel(chosen_llm, api_token):
    if chosen_llm == "Mistral-7B-Instruct-v0.2: Latest but not fine-tuned":
        llm =  HuggingFaceEndpoint(
            repo_id="mistralai/Mistral-7B-Instruct-v0.2",
            temperature= 0.1,
            huggingfacehub_api_token=api_token,
        )
    if chosen_llm == "BioGPT: fine-tuned but not latest":
        llm =  HuggingFaceEndpoint(
            repo_id="microsoft/BioGPT-Large",
            temperature= 0.1,
            huggingfacehub_api_token=api_token,
        )
    chat_model = ChatHuggingFace(llm=llm)
    return chat_model