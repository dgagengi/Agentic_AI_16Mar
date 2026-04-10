#####import libraries

import os
from dotenv import load_dotenv

# loaders 7 splitters
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

# vector database
from langchain_community.vectorstores import Chroma

# gemini moidel
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings

##### load env keys
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY","")
os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY

####### model
embedding = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")

### LLM Model
llm = ChatGoogleGenerativeAI(model="models/gemini-2.5-flash", temperature=0.3)

#### load resume
def load_resume(file_path):
    if file_path.endswith('.pdf'):
        loader = PyPDFLoader(file_path)
    elif file_path.endswith('.docx'):
        loader = Docx2txtLoader(file_path)
    elif file_path.endswith('.txt'):
        loader = TextLoader(file_path)
    else:
        raise ValueError("Unsupported file format. Please upload a PDF, DOCX, or TXT file.")
    
    return loader.load()

##### analyze resume
def analyze_resume(docs, job_description):
    # Combine all document chunks into a single string
    full_resume = "\n\n".join([doc.page_content for doc in docs])

    prompt = f"""

Compare this resume with job description . Give below details:-

1. Suitability Score (0-100): Based on how well the resume matches the job description in one line.
2. Skills Match: List the skills from the job description that are present in the resume in brief.
3. Experience Match: Analyze the work experience in the resume and how it aligns with the job requirements in brief.
4. Education Match: Evaluate the educational background in relation to the job requirements in brief.
5. Strengths: Highlight the strong points of the resume in relation to the job description in brief.
6. Weaknesses: Point out any areas where the resume may fall short in relation to the job description in brief.
7. Overall Analysis: Provide a summary of how well the resume matches the job description and any recommendations for improvement in two lines.

Job_Description: {job_description}

Resume: {full_resume}

"""     
    result = llm.invoke(prompt)
    return result.content.strip()

### store output in vector database
def store_to_vectorstore(docs, persist_directory="chroma_store"):
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = splitter.split_documents(docs)
    texts = [chunk.page_content for chunk in chunks]
    metadatas = [{"source": f"chunk_{i}"} for i in range(len(texts))]

    vectorstore = Chroma.from_texts(
        texts=texts, embedding=embedding, metadatas=metadatas, persist_directory=persist_directory)
    vectorstore.persist()
    return vectorstore

### query vector database
def run_self_query(query, persist_directory="chroma_store"):
    vectorstore = Chroma(
        persist_directory=persist_directory,
        embedding_function=embedding
    )

    retriever = vectorstore.as_retriever(
        search_kwargs={"k": 5},
        search_type="mmr"
    )

    docs = retriever.invoke(query)

    # Ensure safe extraction
    combined_docs = "\n\n".join([
        doc.page_content if hasattr(doc, "page_content") else str(doc)
        for doc in docs
    ])

    prompt = f"""
    Answer the query based only on the resume content.

    Query: {query}

    Resume Content:
    {combined_docs}
    """

    result = llm.invoke(prompt)

    return result.content.strip()

