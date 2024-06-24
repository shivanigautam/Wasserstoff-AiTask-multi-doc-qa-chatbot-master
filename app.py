import logging
import os

import requests
from flask import Flask, render_template, request, redirect, url_for, jsonify, send_file
from pinecone import list_indexes

from main import QAChatbot, DataIngestion
from config import models_used, pinecone_index_name, pinecone_key

app = Flask(__name__)


@app.route("/")
def main():
    return render_template("home_page_2.html")


@app.route("/data_ingest", methods=["GET", "POST"])
def data_ingest():
    if request.method == "POST":
        if "delete_kb" in request.form:
            # Delete knowledge base
            index_name = request.form["index_name"]
            if index_name == "":
                index_name = pinecone_index_name
            DataIngestion.delete_knowledgebase(index_name)
        else:
            # Data ingestion logic
            directory_path = request.form["directory_path"]
            file_path = request.form["file_path"]

            # Create knowledge base using the provided directory or file path
            data_ingest = DataIngestion(directory_path, file_path)
            data_ingest.run()
            return redirect(url_for("chatbot_route"))

    return render_template("data_ingest.html")


def pdf_ingetion(file_path, index_name, directory_path=""):

    data_ingest = DataIngestion(directory_path, file_path, index_name=index_name)
    data_ingest.run()
    return True



qa_chatbot = None


@app.route("/chatbot", methods=["GET", "POST"])
def chatbot_route():
    global qa_chatbot

    if request.method == "POST":
        selected_model = request.form["chat_model"]
        user_query = request.form["user_query"]

        # # Update the chatbot with the selected model
        qa_chatbot = QAChatbot(model_type=selected_model)
        #
        # # Get chatbot response based on the user's query
        response = qa_chatbot.chat(user_query)
        #
        # # Separate the response into result and top_3_matching_chunks
        result = response.get("result", "")
        top_3_matching_chunks = response.get("source_documents", [])

        ##  test code
        return render_template(
            "index.html",
            available_models=models_used.keys(),
            selected_model=qa_chatbot.model_type,
            user_query=user_query,
            result=result,
            top_3_matching_chunks=top_3_matching_chunks,
        )

    return render_template(
        "index.html",
        available_models=models_used.keys(),
        selected_model=qa_chatbot.model_type if qa_chatbot else "",
    )

@app.route("/both", methods=["GET", "POST"])
def bot_route():
    global qa_chatbot

    if request.method == "POST":
        selected_model = request.form["chat_model"]
        user_query = request.form["user_query"]
        index = request.args.get("index")
        print(index)

        # # Update the chatbot with the selected model
        qa_chatbot = QAChatbot(model_type=selected_model)
        #
        # # Get chatbot response based on the user's query
        response = qa_chatbot.chat(user_query, index)
        #
        # # Separate the response into result and top_3_matching_chunks
        result = response.get("result", "")
        top_3_matching_chunks = response.get("source_documents", [])
        # available_models = ['gpt, llm'],
        # selected_model = 'llm',
        # user_query = user_query,
        # result = "hi howw are you"+index,
        # top_3_matching_chunks = [5, 6, 7],
        return jsonify(result=result, top_3_matching_chunks=top_3_matching_chunks)



    return render_template(
        "index.html",
        available_models=models_used.keys(),
        selected_model=qa_chatbot.model_type if qa_chatbot else "",
    )


@app.route('/bot')
def bot():
    index = request.args.get('index', 'default')

    available_models = list(models_used.keys())
    selected_model = 'llama'
    return render_template('chatbot.html', index=index, available_models=available_models, selected_model=selected_model)

@app.route('/handle_query', methods=['POST'])
def handle_query():
    try:
        user_query = request.form.get('user_query')
        chat_model = request.form.get('chat_model')
        index = request.form.get("index")
        print(index)

        # # Update the chatbot with the selected model
        qa_chatbot = QAChatbot(model_type=chat_model)
        #
        # # Get chatbot response based on the user's query
        response = qa_chatbot.chat(user_query, index)
        #
        # # Separate the response into result and top_3_matching_chunks
        result = response.get("result", "")
        # top_3_matching_chunks = response.get("source_documents", [])

        # Process the query and return a response
        response = {
            'result': result[2:]
        }
        return jsonify(response)
    except Exception as e:
        response = {
            'result': 'Error App not registered'
        }
        return jsonify(response)




app.config['UPLOAD_FOLDER'] = 'static/uploads'

@app.route('/new_integration')
def index():
    return render_template('new_integration.html')

@app.route('/check_index', methods=['POST'])
def check_index():
    title = request.form.get('title')
    if title == "":
        return jsonify({'available': False})
    from pinecone import Pinecone
    pinecone_instance = Pinecone(api_key=pinecone_key)
    existing_indexes = pinecone_instance.list_indexes()
    existing_indexes = [index['name'] for index in existing_indexes] if existing_indexes else []
    # Check if the specified index is in the list of existing indexes
    if title in existing_indexes:
        return jsonify({'available': False})
    else:
        return jsonify({'available': True})

@app.route('/ingestion', methods=['POST'])
def ingestion():
    try:
        title = request.form.get('title')
        tab_title = request.form.get('tab_title')
        content = ""
        file_path = os.path.normpath(os.path.join(app.config['UPLOAD_FOLDER'], title + ".pdf"))

        if tab_title == 'Add context from PDF':
            pdf = request.files['file']
            pdf.save(file_path)
            import fitz  # PyMuPDF
            # Open the PDF file
            document = fitz.open(file_path)
            # Iterate through the pages
            for page_num in range(document.page_count):
                page = document.load_page(page_num)
                text = page.get_text("text")
                content += text
            document.close()

        elif tab_title == 'Add context from API':
            api_url = request.form.get('api_url')
            head_response = requests.head(api_url, timeout=5)
            if head_response.status_code != 200:
                return jsonify({'success': False})
            # Make a GET request to the validated URL
            get_response = requests.get(api_url, timeout=5)
            content = get_response.text
            if content == "":
                content = get_response.json()["data"]

        elif tab_title == 'Add direct context':
            content = request.form.get('content')

        if content == "":
            raise Exception("Empty data")
        if not isinstance(content, str):
            raise Exception("unexpected data")
        obj = DataIngestion(file_path=file_path, index_name=title)
        obj.split_embed_store(content)

        from pinecone import Pinecone
        pinecone_instance = Pinecone(api_key=pinecone_key)
        existing_indexes = pinecone_instance.list_indexes()
        existing_indexes = [index['name'] for index in existing_indexes] if existing_indexes else []

        # Check if the specified index is in the list of existing indexes
        if title in existing_indexes:
            return jsonify({'success': True})
        else:
            return jsonify({'success': False})
    except Exception as e:
        return jsonify({'success': False})

@app.route('/reg_web')
def list_urls():
    from pinecone import Pinecone
    pinecone_instance = Pinecone(api_key=pinecone_key)
    existing_indexes = pinecone_instance.list_indexes()
    existing_indexes = [index['name'] for index in existing_indexes] if existing_indexes else []
    existing_indexes = [{"name":i,"url":r"/bot?index="+str(i)} for i in existing_indexes]
    return render_template('reg_web.html', urls=existing_indexes)



@app.route('/chatbot_plugin', methods=[ 'GET'])
def update_chatbot_plugin():
    # Receive title from request parameters
    title = request.args.get('index')

    if title is None:
        return jsonify({'error': 'Index parameter is missing.'}), 400

    # Define filenames
    original_file = os.path.normpath(os.path.join(app.config['UPLOAD_FOLDER'], 'chatbot_plugin.php'))
    new_file = os.path.normpath(os.path.join(app.config['UPLOAD_FOLDER'], f'chatbot_plugin_{title}.php'))

    # Read the original PHP file
    try:
        with open(original_file, 'r') as file:
            lines = file.readlines()
    except FileNotFoundError:
        return jsonify({'error': 'Original PHP file not found.'}), 404

    # Update the line with CHATBOT_INDEX
    updated_lines = []
    for line in lines:
        if line.strip().startswith("define('CHATBOT_INDEX',"):
            updated_lines.append(f"define('CHATBOT_INDEX', '{title}')\n")
        else:
            updated_lines.append(line)

    # Save updated content to a new PHP file
    try:
        with open(new_file, 'w') as file:
            file.writelines(updated_lines)
    except Exception as e:
        return jsonify({'error': f'Error saving updated PHP file: {str(e)}'}), 500

    # Prepare response to download the file
    try:
        return send_file(new_file, as_attachment=True)
    except Exception as e:
        return jsonify({'error': f'Error sending file to client: {str(e)}'}), 500

def download_file(url, dest_path):
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(dest_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        print(f"File downloaded successfully and saved to {dest_path}")
    else:
        print(f"Failed to download file. HTTP Status code: {response.status_code}")


def check_and_download_file(file_path, download_url):
    if not os.path.exists(file_path):
        print(f"LLAMA model does not exist. Downloading from {download_url}  ...")
        print("It one time process and it will take few minute as its downloading 4.21Gb data ....")
        print("Please wait...")

        download_file(download_url, file_path)
    else:
        print(f"File already exists at {file_path}")

check_and_download_file(
    'llms/llama-2-7b-chat.ggmlv3.q4_1.bin',
    'https://huggingface.co/TheBloke/Llama-2-7B-Chat-GGML/resolve/main/llama-2-7b-chat.ggmlv3.q4_1.bin?download=true')


if __name__ == "__main__":

    app.run()
