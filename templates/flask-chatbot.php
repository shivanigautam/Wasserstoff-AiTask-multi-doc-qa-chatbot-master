<?php
/**
 * Plugin Name: Flask Chatbot
 * Description: A simple chatbot that communicates with a Flask API.
 * Version: 1.0
 * Author: Your Name
 */

function flask_chatbot_enqueue_scripts() {
    wp_enqueue_style('flask-chatbot-style', plugins_url('flask-chatbot.css', __FILE__));
    wp_enqueue_script('flask-chatbot-script', plugins_url('flask-chatbot.js', __FILE__), array('jquery'), null, true);
}
add_action('wp_enqueue_scripts', 'flask_chatbot_enqueue_scripts');

function flask_chatbot_html() {
    ?>
    <div id="flask-chatbot-popup">
        <div id="flask-chatbot-popup-header">
            <h1>Chatbot</h1>
            <button id="flask-chatbot-popup-close">X</button>
        </div>
        <form id="flask-chatbot-popup-form" method="post">
            <label for="chat_model">Select Model:</label>
            <select name="chat_model" id="chat_model">
                <option value="model1">Model 1</option>
                <option value="model2">Model 2</option>
                <!-- Add more models as needed -->
            </select>

            <label for="user_query">User Query:</label>
            <input type="text" name="user_query" id="user_query" required>

            <button type="submit">Submit Query</button>
        </form>
        <div id="flask-chatbot-popup-result">
            <p>User Query: <span id="display_user_query"></span></p>
            <p>Selected Model: <span id="display_selected_model"></span></p>
            <p>Chatbot Result: <span id="flask_chatbot_result"></span></p>
        </div>
    </div>
    <button id="flask-chatbot-popup-open">Open Chatbot</button>
    <?php
}
add_action('wp_footer', 'flask_chatbot_html');
?>
