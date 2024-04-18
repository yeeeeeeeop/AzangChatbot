import json
from langchain.vectorstores.faiss import FAISS
from langchain_community.embeddings.huggingface import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter

hf_embedding = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    model_kwargs={"device": "cpu"}
)

def Read_json(file_path):
    with open(file_path, "r") as f:
        try:
            papers_json = json.load(f)
        except:
            raise KeyError("JSON file has not been found. Please check your file path.")
    return papers_json

def Split_and_format_documents(abs_list_raw, metadata_list_raw):
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
    return abs_list, metadata_list

def Generate_local_faiss(abs_list, metadata_list, faiss_path):
    vectordb_RAG = FAISS.from_texts(texts=abs_list, embedding=hf_embedding, metadatas=metadata_list)
    vectordb_RAG.save_local(folder_path=faiss_path)

def Generate_context(_dict: dict) -> str:
    vectordb_RAG = FAISS.load_local(folder_path=_dict["faiss_path"], embeddings=hf_embedding, allow_dangerous_deserialization=True)
    context_list = vectordb_RAG.similarity_search(query=_dict["query"], k=_dict["how_many_search"])
    context_list_modified = [item.page_content+" ("+item.metadata["article_name"]+","+item.metadata["journal"]+")" for item in context_list]
    context_str = "\n".join(context_list_modified)
    return context_str

def Generate_symptom(_dict: dict) -> str:
    symptom_str = f"""The stool color of my baby was {_dict["basic_info"]["color"].lower()}. The stool of my baby seemed to be {_dict["basic_info"]["blood"]}. The stool of my baby was {_dict["basic_info"]["form"]}"""
    symptom_str = symptom_str + "\n" + _dict["additional_context"]
    return symptom_str