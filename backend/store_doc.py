import os
import psycopg2

from langchain_community.document_loaders import PyPDFLoader, UnstructuredPDFLoader, PyPDFium2Loader
from langchain_community.document_loaders import PyPDFDirectoryLoader, DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter, CharacterTextSplitter
from langchain.docstore.document import Document
from langchain.vectorstores.pgvector import PGVector
from langchain_community.embeddings import OllamaEmbeddings
from dotenv import load_dotenv
from helpers import get_postgre_database

import asyncio


# filepath = './data/CompaniesAct2013.pdf'
# filepath = './data/resume.pdf'
# loader = PyPDFLoader(filepath)
# documents = loader.load()


async def store_doc(db_connection: str, collection: str, text_segment: str):
    # loader = TextSegmentLoader(text_segment)
    # documents = loader.load()
    embeddings = OllamaEmbeddings(model="llama2")
    print("Connection string: %s", db_connection)

    text_splitter = CharacterTextSplitter()
    texts = text_splitter.split_text(text_segment)
    # Create multiple documents
    documents = [Document(page_content=t) for t in texts]
    # print(documents)

    conn = psycopg2.connect(db_connection)
    cur = conn.cursor()
    table_create_command = f"""
        DELETE FROM langchain_pg_embedding;
    """
    cur.execute(table_create_command)
    # cur.execute("CREATE EXTENSION IF NOT EXISTS vector")
    cur.close()
    conn.commit()

    # print(conn)
    # table_create_command = f"""
    # CREATE TABLE {collection} (
    #             id bigserial primary key, 
    #             embedding vector(1536)
    #             );
    # """
    # cur.execute(table_create_command)
    # cur.close()
    # conn.commit()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1100,
        chunk_overlap=150,
        length_function=len,
        is_separator_regex=False,
    )

    pages = splitter.split_documents(documents)
    # # print(pages)
    print("Number of chunks = ", len(pages))
    print(pages)

    PGVector.from_documents(
        embedding=embeddings,
        documents=pages,
        collection_name=collection,
        connection_string=db_connection,
        pre_delete_collection=True,
    )
    # ca_store = PGVector(
    #     collection_name=collection,
    #     connection_string=db_connection,
    #     embedding_function=embeddings,
    # )
    # ca_store.add_documents(pages)
    print("Added pages!")


if __name__ == '__main__':
    connection_string = get_postgre_database("legal_docs")
    collection = "image_embeddings"
    asyncio.run(store_doc(connection_string, collection, "ok2 this is a asldkfjasldkfjaslkdfjalskdfjalskdfjalskfjasdldkfjasklfjlkasdfjklasjdflkajsdfklasdjfklasjdfklasjfklasjdfklasjdfklasfjklasdfjklasfjkladsjfkladsjfklasjfklasjfklasjdfklasjdfklasjfklasjfklasjdfklasjdflkasjdfklajsfklasjdflkajslfkajskldfjalksdfjlaksdfjklasdfjlksdadjflkasfjlkasdfjklasfjksaldfjlkasdjfklsadfjdasklfjklasfjklasdfjkasldfjadklsfjdkaslfjksaldfjlkasfjlasdkfjsadlkfjksaldfjlksadfjklsadfjlksdfjlsadkfj"))