import logging
import os
import requests
import time
from flask import Flask, render_template, request, redirect, url_for, jsonify, send_file
from flasgger import Swagger
from main import QAChatbot, DataIngestion
from config import models_used, pinecone_index_name, pinecone_key

app = Flask(__name__)
swagger = Swagger(app)

@app.before_request
def start_timer():
    request.start_time = time.time()

@app.after_request
def log_response_time(response):
    if hasattr(request, 'start_time'):
        response_time = (time.time() - request.start_time) * 1000  # in milliseconds
        app.logger.info(f"Response time: {response_time:.2f} ms")
    return response

@app.route("/")
def main():
    """
    Homepage
    ---
    responses:
      200:
        description: "Home page (Typical response time: ~10ms) on \n "
    """
    return render_template("home_page_2.html")



@app.route('/bot')
def bot():
    """
    Api to Try chatbot of any Registered chatbot
    ---
    parameters:
      - name: index
        in: query
        type: string
        required: false
    responses:
      200:
        description: "Bot page (Typical response time: ~10ms)"
    """
    index = request.args.get('index', 'default')
    available_models = list(models_used.keys())
    selected_model = 'llama'
    return render_template('chatbot.html', index=index, available_models=available_models, selected_model=selected_model)

@app.route('/handle_query', methods=['POST'])
def handle_query():
    """
    Actual API for Handling user query for the chatbot.
    ---
    parameters:
      - name: user_query
        in: formData
        type: string
        required: true
      - name: chat_model
        in: formData
        type: string
        required: true
      - name: index
        in: formData
        type: string
        required: false
    responses:
      200:
        description: "Query response (Typical response time: ~13m)"
    """
    try:
        user_query = request.form.get('user_query')
        chat_model = request.form.get('chat_model')
        index = request.form.get("index")
        qa_chatbot = QAChatbot(model_type=chat_model)
        response = qa_chatbot.chat(user_query, index)
        result = response.get("result", "")
        return jsonify({'result': result})
    except Exception as e:
        return jsonify({'result': 'Error App not registered'})

app.config['UPLOAD_FOLDER'] = 'static/uploads'

@app.route('/new_integration')
def index():
    """
    New Integration Page
    ---
    responses:
      200:
        description: "New Integration page (Typical response time: ~10ms)"
    """
    return render_template('new_integration.html')

@app.route('/check_index', methods=['POST'])
def check_index():
    """
    Check if the given index exists in Pinecone Db
    ---
    parameters:
      - name: title
        in: formData
        type: string
        required: true
    responses:
      200:
        description: "Index check result (Typical response time: ~2.3m)"
    """
    title = request.form.get('title')
    if title == "":
        return jsonify({'available': False})
    from pinecone import Pinecone
    pinecone_instance = Pinecone(api_key=pinecone_key)
    existing_indexes = pinecone_instance.list_indexes()
    existing_indexes = [index['name'] for index in existing_indexes] if existing_indexes else []
    if title in existing_indexes:
        return jsonify({'available': False})
    else:
        return jsonify({'available': True})

@app.route('/ingestion', methods=['POST'])
def ingestion():
    """
    Ingest data from various sources to Pinecone
    ---
    parameters:
      - name: title
        in: formData
        type: string
        required: true
      - name: tab_title
        in: formData
        type: string
        required: true
      - name: content
        in: formData
        type: string
        required: false
      - name: api_url
        in: formData
        type: string
        required: false
      - name: file
        in: formData
        type: file
        required: false
    responses:
      200:
        description: "Data ingestion result (Typical response time: ~27s)"
    """
    try:
        title = request.form.get('title')
        tab_title = request.form.get('tab_title')
        content = ""
        file_path = os.path.normpath(os.path.join(app.config['UPLOAD_FOLDER'], title + ".pdf"))

        if tab_title == 'Add context from PDF':
            pdf = request.files['file']
            pdf.save(file_path)
            import fitz  # PyMuPDF
            document = fitz.open(file_path)
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
        for line in lines:
            if line.strip().startswith("define('CHATBOT_INDEX',"):
                updated_lines.append(f"define('CHATBOT_INDEX', '{title}')\n")
            else:
                updated_lines.append(line)

        try:
            with open(new_file, 'w') as file:
                file.writelines(updated_lines)
        except Exception as e:
            return jsonify({'error': f'Error saving updated PHP file: {str(e)}'}) , 500

        try:
            return send_file(new_file, as_attachment=True)
        except Exception as e:
            return jsonify({'error': f'Error sending file to client: {str(e)}'}) , 500

        if title in existing_indexes:
            return jsonify({'success': True})
        else:
            return jsonify({'success': False})
    except Exception as e:
        return jsonify({'success': False})

@app.route('/reg_web')
def list_urls():
    """
    All Registered Websites for Chatbot and their chatbot link
    ---
    responses:
      200:
        description: "List of registered URLs (Typical response time: ~1.7s)"
    """
    from pinecone import Pinecone
    pinecone_instance = Pinecone(api_key=pinecone_key)
    existing_indexes = pinecone_instance.list_indexes()
    existing_indexes = [index['name'] for index in existing_indexes] if existing_indexes else []
    existing_indexes = [{"name": i, "url": f"/bot?index={i}"} for i in existing_indexes]
    return render_template('reg_web.html', urls=existing_indexes)

@app.route('/chatbot_plugin', methods=['GET'])
def update_chatbot_plugin():
    """
    Chatbot plugin with given index.
    ---
    parameters:
      - name: index
        in: query
        type: string
        required: true
    responses:
      200:
        description: "Chatbot plugin updated (Typical response time: ~20ms)"
    """
    title = request.args.get('index')
    if title is None:
        return jsonify({'error': 'Index parameter is missing.'}), 400

    original_file = os.path.normpath(os.path.join(app.config['UPLOAD_FOLDER'], 'chatbot_plugin.php'))
    new_file = os.path.normpath(os.path.join(app.config['UPLOAD_FOLDER'], f'chatbot_plugin_{title}.php'))

    try:
        with open(original_file, 'r') as file:
            lines = file.readlines()
    except FileNotFoundError:
        return jsonify({'error': 'Original PHP file not found.'}), 404

    updated_lines = []

def download_file(url, dest_path):
    new_path = dest_path + ".dw"
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(new_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        os.rename(new_path, dest_path)
        print(f"File downloaded successfully and saved to {dest_path}")
    else:
        print(f"Failed to download file. HTTP Status code: {response.status_code}")


def check_and_download_file(file_path, download_url):
    if not os.path.exists(file_path):
        print(f"LLAMA model does not exist. Downloading from {download_url}  ...")
        print("It one time process and it will take few minute as its downloading 4.21Gb data ....")
        print("Please wait...")
        print("or you can download model from above link and paste into /llm directory")

        download_file(download_url, file_path)
    else:
        print(f"File already exists at {file_path}")

check_and_download_file(
    'llms/llama-2-7b-chat.ggmlv3.q4_1.bin',
    'https://huggingface.co/TheBloke/Llama-2-7B-Chat-GGML/resolve/main/llama-2-7b-chat.ggmlv3.q4_1.bin?download=true')


if __name__ == "__main__":

    app.run()
