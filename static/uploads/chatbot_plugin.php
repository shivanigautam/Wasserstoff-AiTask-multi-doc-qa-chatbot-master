<?php
/*
Plugin Name: Flask Chatbot Integration
Plugin URI: https://example.com
Description: Integrates a Flask-based chatbot with WordPress.
Version: 1.0
Author: Your Name
Author URI: https://example.com
*/

// Constants
define('CHATBOT_INDEX', ''); // Replace with your unique title

// Enqueue necessary scripts and styles
function flask_chatbot_enqueue_scripts() {
    wp_enqueue_script('jquery');
    $flask_url = 'http://127.0.0.1:5000'; // Replace with your Flask app URL

    // Inline CSS
    $custom_css = "
        #chatbot-popup {
            display: none;
            position: fixed;
            bottom: 10px;
            right: 10px;
            width: 300px;
            background-color: #fff;
            border: 1px solid #ccc;
            border-radius: 5px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
        }

        #chatbot-popup-header {
            padding: 10px;
            background-color: #4682b4;
            color: #fff;
            border-top-left-radius: 5px;
            border-top-right-radius: 5px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        #chatbot-popup-results {
            padding: 10px;
            max-height: 300px;
            overflow-y: auto;
        }

        #chatbot-popup-form {
            padding: 10px;
            border-top: 1px solid #ccc;
            display: flex;
            flex-direction: column;
        }

        #chatbot-popup-form input,
        #chatbot-popup-form select,
        #chatbot-popup-form button {
            margin-bottom: 10px;
        }

        #chatbot-popup-open {
            position: fixed;
            bottom: 10px;
            right: 10px;
            padding: 10px 20px;
            background-color: #4682b4;
            color: #fff;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }

        #chatbot-popup-open:hover {
            background-color: #5a9bd4;
        }

        .chatbot-result {
            padding: 5px;
            border-radius: 5px;
            margin-bottom: 5px;
        }

        .chatbot-result.user {
            background-color: #e0f7fa;
            text-align: right;
        }

        .chatbot-result.server {
            background-color: #f0f4c3;
            text-align: left;
        }
    ";
    wp_add_inline_style('wp_enqueue_style', $custom_css);

    // Inline JavaScript
    $custom_js = "
        jQuery(document).ready(function($) {
            $('#chatbot-popup-open').click(function() {
                $('#chatbot-popup').show();
                $(this).hide();
            });

            $('#chatbot-popup-close').click(function() {
                $('#chatbot-popup').hide();
                $('#chatbot-popup-open').show();
            });

            $('#chatbot-popup-form').submit(function(event) {
                event.preventDefault();
                var userQuery = $('#user_query').val();
                var selectedModel = $('#chat_model').val();
                var index = '" . CHATBOT_INDEX . "'; // Use constant index

                var userResult = `
                    <div class='chatbot-result user'>
                        <p>${userQuery}</p>
                    </div>
                `;
                $('#chatbot-popup-results').append(userResult);

                $.ajax({
                    type: 'POST',
                    url: '$flask_url/handle_query?index=' + index, // Send index as query param
                    data: { user_query: userQuery, chat_model: selectedModel },
                    success: function(response) {
                        var serverResult = `
                            <div class='chatbot-result server'>
                                <p>${response.result}</p>
                            </div>
                        `;
                        $('#chatbot-popup-results').append(serverResult);
                        $('#user_query').val('');
                    },
                    error: function() {
                        var errorResult = `
                            <div class='chatbot-result server'>
                                <p>Error processing your request.</p>
                            </div>
                        `;
                        $('#chatbot-popup-results').append(errorResult);
                    }
                });

                return false;
            });
        });
    ";
    wp_add_inline_script('wp_enqueue_script', $custom_js);
}
add_action('wp_enqueue_scripts', 'flask_chatbot_enqueue_scripts');

// Add the chatbot HTML to the footer
function flask_chatbot_html() {
    $flask_url = 'http://127.0.0.1:5000'; // Replace with your Flask app URL
    ?>
    <div id="chatbot-popup">
        <div id="chatbot-popup-header">
            <h1>Chatbot</h1>
            <button id="chatbot-popup-close">X</button>
        </div>
        <div id="chatbot-popup-results">
            <!-- Results will be appended here -->
        </div>
        <form id="chatbot-popup-form" method="post">
            <input type="text" name="user_query" id="user_query" placeholder="Type your query here..." required>
            <select name="chat_model" id="chat_model">
                <option value="llama">Llama</option>
                <option value="gpt">GPT</option>
            </select>
            <button type="submit">Send</button>
        </form>
    </div>
    <button id="chatbot-popup-open">Chat with us</button>
    <script>
        var flask_url = "<?php echo $flask_url; ?>";
    </script>
    <?php
}
add_action('wp_footer', 'flask_chatbot_html');

// Handle AJAX request to Flask backend
function flask_chatbot_ajax_handler() {
    if (isset($_POST['user_query'])) {
        $user_query = sanitize_text_field($_POST['user_query']);
        $selected_model = sanitize_text_field($_POST['chat_model']);
        $index = CHATBOT_INDEX; // Get constant index

        // Send request to Flask backend with index as query param
        $response = wp_remote_post($flask_url . '/handle_query?index=' . $index, array(
            'body' => array(
                'user_query' => $user_query,
                'chat_model' => $selected_model,
            ),
        ));

        if (is_wp_error($response)) {
            echo json_encode(array('error' => 'Error processing request.'));
        } else {
            $body = wp_remote_retrieve_body($response);
            echo $body;
        }
    } else {
        echo json_encode(array('error' => 'Invalid request.'));
    }
    wp_die();
}
add_action('wp_ajax_flask_chatbot_ajax', 'flask_chatbot_ajax_handler');
add_action('wp_ajax_nopriv_flask_chatbot_ajax', 'flask_chatbot_ajax_handler');
