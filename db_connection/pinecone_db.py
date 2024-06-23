import pinecone
from pinecone import Pinecone, PodSpec

from config import *
from utils import chunk_iterable, prepare_vectors_and_metadata


class PineconeDB:

    def __init__(self, index_name, dim=384):
        self.dim = dim
        self.index_name = index_name
        try:
            self.pinecone_instance = Pinecone(api_key=pinecone_key)
            if index_name not in self.list_indexes():
                self._create_index()
        except pinecone.exceptions.PineconeException as e:
            print(f"Error initializing Pinecone: {e}")

    def _create_index(self):
        try:
            print(f"Creating index {self.index_name} ...")
            self.pinecone_instance.create_index(
                name=self.index_name,
                dimension=self.dim,
                metric="cosine",
                spec=PodSpec(environment="gcp-starter"),
            )
            print(self.pinecone_instance.describe_index(self.index_name))
            print(f"Index {self.index_name} successfully created ...")
        except pinecone.exceptions.PineconeException as e:
            print(f"Error creating Pinecone index: {e}")

    def upsert_to_pinecone(self, vectors_and_metadata):
        try:
            index = self.pinecone_instance.Index(self.index_name)
            index.upsert(vectors=vectors_and_metadata)
        except pinecone.exceptions.PineconeException as e:
            print(f"PineconeException while upserting: {str(e)}")
            raise
        except Exception as e:
            print(f"Error while upserting: {str(e)}")
            raise

    def query_db(self, query_vector):
        try:
            index = self.pinecone_instance.Index(self.index_name)
            return index.query(
                vector=query_vector,
                top_k=3,
                include_values=False,
                include_metadata=True,
            )
        except pinecone.exceptions.PineconeException as pe:
            print(f"PineconeException while querying: {str(pe)}")
            raise
        except Exception as e:
            print(f"Error while querying: {str(e)}")
            raise

    def fetch_embeddings(self, embeddings):
        from langchain_community.vectorstores import Pinecone

        try:
            vector_store = Pinecone.from_existing_index(self.index_name, embeddings)
            return vector_store
        except Exception as e:
            print(f"Error while fetching embeddings from {self.index_name}, Error: {e}")
            return []

    def insert_embeddings(self, chunks, embeddings):
        from langchain_community.vectorstores import Pinecone

        try:
            vector_store = Pinecone.from_documents(
                chunks, embeddings, index_name=self.index_name
            )
            return vector_store
        except Exception as e:
            print(f"Error while inserting embeddings in {self.index_name}, Error: {e}")
            return []

    def process_and_upsert_to_pinecone(self, dataset, embed_model, batch_size=100):
        count = 0
        for ids_vectors_chunk in chunk_iterable(dataset, batch_size=batch_size):
            vectors_and_metadata = prepare_vectors_and_metadata(
                ids_vectors_chunk, embed_model
            )
            try:
                self.upsert_to_pinecone(vectors_and_metadata)
                count += 1
                print(
                    f"Completed inserting chunk {count}. Total chunk count is {count}"
                )
            except Exception as e:
                print(f"Error while upserting: {str(e)}")

    def list_indexes(self):
        return self.pinecone_instance.list_indexes().names()

    def delete_pinecone_index(self, index_name="all"):
        try:
            if index_name == "all":
                self._delete_all_indexes()
            else:
                self._delete_single_index(index_name)
        except pinecone.exceptions.PineconeException as e:
            print(f"Error during Pinecone operation: {e}")

    def _delete_all_indexes(self):
        try:
            indexes = self.pinecone_instance.list_indexes().names()
            print("Deleting all indexes ... ")
            for index in indexes:
                self.pinecone_instance.delete_index(index)
            print(f"Successfully deleted all the indexes")
        except pinecone.exceptions.PineconeException as e:
            print(f"Error deleting all Pinecone indexes: {e}")

    def _delete_single_index(self, index_name):
        try:
            print(f"Deleting index {index_name} ...", end="")
            self.pinecone_instance.delete_index(index_name)
            print(f"Successfully deleted the index with name {self.index_name}")
        except pinecone.exceptions.PineconeException as e:
            print(f"Error deleting Pinecone index: {e}")
