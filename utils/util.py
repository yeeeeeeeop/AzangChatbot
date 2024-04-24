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
        chunk_size=300,
        chunk_overlap=30
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


def Add_diagnostic_contexts(_dict: dict) -> dict:
    vectordb_RAG = FAISS.load_local(folder_path=_dict["faiss_path"], embeddings=hf_embedding, allow_dangerous_deserialization=True)
    context_list = vectordb_RAG.similarity_search(query=_dict["symptoms"], k=_dict["how_many_search"])
    context_list_modified = [item.page_content.lower()+" ("+item.metadata["article_name"]+","+item.metadata["journal"]+")" for item in context_list]
    _dict["context_list"] = context_list_modified
    del _dict["how_many_search"]
    del _dict["faiss_path"]
    return _dict

def Add_chat_context(_dict: dict):
    vectordb_RAG = FAISS.load_local(folder_path=_dict["faiss_path"], embeddings=hf_embedding, allow_dangerous_deserialization=True)
    retriever = vectordb_RAG.as_retriever(
        search_type = "similarity_score_threshold",
        search_kwargs= {"k": 3, "score_threshold": 0.7}
        )
    question = _dict["diagnosis"][:720] +"\n\n\n"+ _dict["query"]
    _dict["context"] = retriever.invoke(question)
    del _dict["faiss_path"]
    return _dict