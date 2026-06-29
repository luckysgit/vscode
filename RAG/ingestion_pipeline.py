import os
from langchain_community.document_loaders import TextLoader, DirectoryLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import chroma
from dotevn import load_dotenv

def load_documents(docs_path = "docs"):
    if not os.path.exists(docs_path):
        raise FileNotFoundError(f"{docs_path} does not exist path")
    
    loader = DirectoryLoader(path = docs_path, glob = "*.txt", loader_cls= TextLoader)

    documents - loader.load() # list of 5 docs langchain(llm)

    if len(documents) == 0:
        raise FileExistsError("no .txt file no found ")
     
    for i, doc in enumerate(documents[:2]):
        print("\n documents {i+1}:")

    return load_documents

def main():
    print("main function")

    #1. loading the file
    #2. chunking the files
    #3. embedding and storing in vecor DB


if __name__== "__main__":
    main()
    
    