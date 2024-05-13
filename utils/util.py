import os
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
def Read_text(file_path):
    with open(file_path, "r") as f:
        try:
            text = f.read()
        except:
            raise KeyError("TXT file has not been found. Please check your file path.")
    return text

def Split_and_format_documents(abs_list_raw: list, metadata_list_raw:list | None = None, doc_size: int = 300):
    abs_list = list()
    metadata_list = list()
    splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        chunk_size= doc_size,
        chunk_overlap= 30
    )
    for i in range(len(abs_list_raw)):
        splitted_text_list = splitter.split_text(abs_list_raw[i])
        if metadata_list_raw is not None:
            for j in range(len(splitted_text_list)):
                abs_list.append(splitted_text_list[j])
                metadata_list.append(metadata_list_raw[i])
        else:
            abs_list = splitted_text_list.copy()
    return abs_list, metadata_list

def Generate_local_faiss(abs_list: list, metadata_list: list, faiss_path: str):
    vectordb_RAG = FAISS.from_texts(
        texts= abs_list, 
        embedding= hf_embedding, 
        metadatas= metadata_list if metadata_list != [] else None
        )
    vectordb_RAG.save_local(folder_path=faiss_path)

def RAG_prepare(main_path, faiss_path):
    """
    If metadata needed,
    abs_list_raw = list(items["abstract"] for items in papers_json["paper_list"])
    metadata_list_raw = list(dict(filter(lambda items: items[0] != "abstract", article_dict.items())) for article_dict in papers_json["paper_list"])
    abs_list, metadata_list = Split_and_format_documents(abs_list_raw, metadata_list_raw)
    Generate_local_faiss(abs_list, metadata_list, faiss_path)
    """
    papers_json = Read_json(os.path.join(main_path, "resource", "Entrez_selected_for_RAG.json"))
    text = Read_text(os.path.join(main_path, "resource", "Textbook_of_pediatric_gastrointestinal_and_hepatology_nutrition.txt"))
    abss = [item["abstract"] for item in papers_json["paper_list"]]
    abss.append(text)
    abs_list, _ = Split_and_format_documents(
        abs_list_raw=abss,
        metadata_list_raw=None,
        doc_size=700)
    Generate_local_faiss(
        abs_list=abs_list,
        metadata_list=[],
        faiss_path=os.path.join(faiss_path, "abs_with_textbook")
    )
    textbook_list, _ = Split_and_format_documents(
        abs_list_raw=[text],
        metadata_list_raw=None,
        doc_size=500
        )
    Generate_local_faiss(
        abs_list=textbook_list,
        metadata_list=[],
        faiss_path=os.path.join(faiss_path, "textbook")
    )

def Add_diagnostic_contexts(_dict: dict) -> dict:
    vectordb_RAG = FAISS.load_local(folder_path=_dict["faiss_path"], embeddings=hf_embedding, allow_dangerous_deserialization=True)
    context_list = vectordb_RAG.similarity_search(query=_dict["formatted_sx"], k=_dict["how_many_search"])
    if "article_name" in context_list[0].metadata:
        context_list_modified = [item.page_content.lower()+" ("+item.metadata["article_name"]+","+item.metadata["journal"]+")" for item in context_list]
    else:
        context_list_modified = [item.page_content for item in context_list]
    _dict["context_list"] = context_list_modified
    del _dict["how_many_search"]
    del _dict["faiss_path"]
    del _dict["formatted_sx"]
    return _dict

def Add_chat_context(_dict: dict):
    vectordb_RAG = FAISS.load_local(folder_path=_dict["faiss_path"], embeddings=hf_embedding, allow_dangerous_deserialization=True)
    retriever = vectordb_RAG.as_retriever(
        search_type = "similarity_score_threshold",
        search_kwargs= {"k": 3, "score_threshold": 0.3}
        )
    question = _dict["diagnosis"][:720] +"\n\n\n"+ _dict["query"]
    _dict["context"] = [item.page_content for item in retriever.invoke(question)]
    del _dict["faiss_path"]
    return _dict

def Add_feature_context(_dict: dict):
    vectordb_RAG = FAISS.load_local(folder_path=_dict["faiss_path"], embeddings=hf_embedding, allow_dangerous_deserialization=True)
    retriever = vectordb_RAG.as_retriever(
        search_type = "similarity",
        search_kwargs= {"k": 4}
        )
    _dict["context"] = [item.page_content for item in retriever.invoke(_dict["query"])]
    del _dict["faiss_path"]
    return _dict