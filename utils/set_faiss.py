import os
import json
from langchain.vectorstores.faiss import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai.embeddings import OpenAIEmbeddings
from utils.util import openai_api

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

def Split_and_format_documents(abs_list_raw: list, metadata_list_raw:list | None = None, doc_size: int = 500):
    abs_list = list()
    metadata_list = list()
    splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        chunk_size= doc_size,
        chunk_overlap= 50
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
        embedding= OpenAIEmbeddings(api_key=openai_api),
        metadatas= metadata_list if metadata_list != [] else None
        )
    vectordb_RAG.save_local(folder_path=faiss_path)

def RAG_prepare(main_path, faiss_path):

    #텍스트북 벡터저장
    text = Read_text(os.path.join(main_path, "resource", "Textbook_of_pediatric_gastrointestinal_and_hepatology_nutrition.txt"))
    textbook_list, _ = Split_and_format_documents(
        abs_list_raw=[text],
        metadata_list_raw=None,
        )
    Generate_local_faiss(
        abs_list=textbook_list,
        metadata_list=[],
        faiss_path=os.path.join(faiss_path, "textbook")
        )
    
    #논문 초록 벡터저장
    papers_json = Read_json(os.path.join(main_path, "resource", "Entrez_selected_for_RAG.json"))
    abs_list_raw = [item["abstract"] for item in papers_json["paper_list"]]
    metadata_list_raw = [dict(filter(lambda items: items[0] != "abstract", article_dict.items())) for article_dict in papers_json["paper_list"]]
    abs_list, metadata_list = Split_and_format_documents(
        abs_list_raw=abs_list_raw,
        metadata_list_raw=metadata_list_raw,
        )
    Generate_local_faiss(
        abs_list=abs_list, 
        metadata_list=metadata_list, 
        faiss_path=os.path.join(faiss_path, "pubmed_abs_infant_feces")
        )
    
    #초록 + 교과서 벡터저장
    abs_list_raw.append(text)
    text_and_abs_list, _ = Split_and_format_documents(
        abs_list_raw=abs_list_raw,
        metadata_list_raw=None,
        )
    Generate_local_faiss(
        abs_list=text_and_abs_list,
        metadata_list=[],
        faiss_path=os.path.join(faiss_path, "abs_with_textbook")
        )