import os
import asyncio
import logging
from PIL import Image

from vector_retriever import VectorRetriever
from helpers import get_postgre_database


# based on text, be able to answer any questions
# put the text into a vector space with Postgre and llama2 embedding function
# nearest neighbor, use as context for question retrival/answering?
# 

# ask questions based on the text, and score the answer!
# different complexities for the type of question?
# might have to play around...


from quart import Quart, render_template, websocket, current_app, request, jsonify
from quart_cors import cors

from image_to_text import getText
from store_doc import store_doc
from agent import Agent

app = Quart(__name__)
app = cors(app)
app.logger.setLevel(logging.DEBUG)

# start the vector retriever
connection_string = get_postgre_database("legal_docs")
collection = "image_embeddings"
vector_retriever = VectorRetriever(conn_string=connection_string, collection=collection)
agent = Agent(model="mistral-openorca:latest", vector_retriever=vector_retriever)
text = ""


@app.route('/embed_text', methods=['post'])
async def embed_text():
    print("In the embed text function")
    data = await request.files
    media = data.getlist('files')
    print(media)
    
    response = jsonify({})
    response.headers['Access-Control-Allow-Origin'] = '*'
    request.headers["Access-Control-Allow-Methods"] = "GET, POST, PATCH, PUT, DELETE, OPTIONS"
    request.headers["Access-Control-Allow-Headers"] = "Origin, Content-Type, X-Auth-Token"

    if not media:
        response.status_code = 100
        return response
    
    text = getText(media)
    print("Text output: ", text)
    await store_doc(connection_string, collection, text)
    print("Doc has been stored!")
    response.status_code = 200

    return response


@app.route('/answer_question', methods=['get'])
async def answer_question():
    question = request.args.get('question')
    if question is None:
        return "Invalid question"
    
    result = agent.answer_question(question)
    response = jsonify({'result': result})
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PATCH, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Origin, Content-Type, X-Auth-Token"

    if result is None:
        response, 100
        return response
        
    print(result)
    return response, 200

@app.route('/prompt_question', methods=['get'])
async def prompt_question():
    question_type = request.args.get('question_type')

    result = await asyncio.create_task(agent.generate_questions_from_text(question_type=question_type, context=text))
    response = jsonify({'result': result})
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PATCH, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Origin, Content-Type, X-Auth-Token"
    
    if result is None:
        response, 100
        return response
    
    print(result)

    return response, 200


@app.route('/')
async def main():
    return "Main package"

if __name__ == '__main__':
    app.run(debug=True)





# original
# DB_PASSWORD = os.environ["SUPABASE_PASSWORD"]
# DB_DBUSER = os.environ["SUPABASE_DBUSER"]
# DB_DATABASE = os.environ["SUPABASE_DATABASE"]
# DB_HOST = os.environ["SUPABASE_HOST"]
# DB_PORT = os.environ["SUPABASE_PORT"]

# connection_url = 'postgresql+psycopg2://user:password@localhost:5432/db_name'
# DB_CONN_STRING = (
#     f"postgresql://{DB_DBUSER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_DATABASE}"
# )


# if __name__ == '__main__':
    # output = getText("input/")
    # print(output)
    # collection = 'legal_docs'
    # retriever = VectorRetriever(conn_string=DB_CONN_STRING, collection=collection)

    # documents = retriever.get_docs("lol the query")
    # print(documents)