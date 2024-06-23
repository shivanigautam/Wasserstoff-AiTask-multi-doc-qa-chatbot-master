import itertools
import os

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import (
    PyPDFLoader,
    Docx2txtLoader,
    DirectoryLoader,
)
from langchain_community.embeddings import HuggingFaceEmbeddings


def load_document_dir(directory):
    loader = DirectoryLoader(directory)
    docs = loader.load()
    return docs


def load_document(file_path):
    name, extension = os.path.splitext(file_path)

    if extension == ".pdf":
        print(f"Loading {file_path}")
        loader = PyPDFLoader(file_path)
    elif extension == ".docx":
        print(f"Loading {file_path}")
        loader = Docx2txtLoader(file_path)
    else:
        print("Document format is not supported!")
        return None

    docs = loader.load()
    return docs


def split_docs(docs, chunk_size=1024, chunk_overlap=50):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, chunk_overlap=chunk_overlap, length_function=len
    )
    return text_splitter.split_documents(docs)


def chunk_iterable(iterable, batch_size=100):
    it = iter(iterable)
    chunk = tuple(itertools.islice(it, batch_size))
    while chunk:
        yield chunk
        chunk = tuple(itertools.islice(it, batch_size))


def prepare_vectors_and_metadata(chunk, embed_model):
    vectors_and_metadata = []
    for i, doc in enumerate(chunk):
        doc_id = f"{doc.metadata['source']}-{i}"
        vector = embed_model.encode([doc.page_content])[0]
        metadata = {"text": doc.page_content, "source": doc.metadata["source"]}
        vectors_and_metadata.append((doc_id, vector, metadata))
    return vectors_and_metadata


def get_embeddings(model_name="sentence-transformers/all-MiniLM-L6-v2", device="cpu"):
    embeddings = HuggingFaceEmbeddings(
        model_name=model_name,
        model_kwargs={"device": device},
    )
    embed_dim = embeddings.client[1].word_embedding_dimension
    return embeddings, embed_dim
