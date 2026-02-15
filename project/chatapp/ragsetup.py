from langchain.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain.llms import OpenAI
from langchain.schema import Document
import os


def build_vectordb(file_path="F:\projects\a_eccomerce\backend\project\chatapp\knowledgebase.pdf"):
    loader=TextLoader(file_path)
    doc=loader.load()

#lets embedd
    splitter=RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splited=splitter.split_documents(doc)

    #nowlets embedd
    embeddings=OpenAIEmbeddings()
    vectorstre= Chroma.from_documents(splited, embeddings)
    vectorstre.save_local(os.path.join(os.getcwd(), "vectordb"))
    return "vectorstore built"


def quey_vectorstore(query):
    embeddings = OpenAIEmbeddings()
    db= Chroma.load_local("vectordb", embeddings)

    LLM = OpenAI(temperature=0)
    retriever = db.as_retriever(search_kwargs={"k": 1})

    QA = RetrievalQA.from_chain_type(
        llm=LLM,retriever=retriever, chain_type="stuff")
    return QA.run(query)