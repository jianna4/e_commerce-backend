from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
#from langchain.chains import RetrievalQA
#from langchain_openai import ChatOpenAI
from langchain_core.documents import Document
import os

from dotenv import load_dotenv
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

loader=PyPDFLoader(r"F:\projects\a_eccomerce\backend\project\chatapp\knowledgebase.pdf")
doc=loader.load()

#letssplit
splitter=RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
splited=splitter.split_documents(doc)

 #nowlets embedd
embeddings=OpenAIEmbeddings()
vectorstore= Chroma.from_documents(splited, embeddings, persist_directory="chroma_db")
vectorstore.persist()
print(f"Vectorstore built and saved in {os.path.join(os.getcwd(), 'chroma_db')}")


