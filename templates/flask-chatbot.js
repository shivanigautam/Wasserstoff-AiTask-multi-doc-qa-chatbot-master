jQuery(document).ready(function($) {
    $('#flask-chatbot-popup-open').click(function() {
        $('#flask-chatbot-popup').show();
        $(this).hide();
    });

    $('#flask-chatbot-popup-close').click(function() {
        $('#flask-chatbot-popup').hide();
        $('#flask-chatbot-popup-open').show();
    });

    $('#flask-chatbot-popup-form').submit(function(event) {
        event.preventDefault();
        var userQuery = $('#user_query').val();
        var selectedModel = $('#chat_model').val();

        $('#display_user_query').text(userQuery);
        $('#display_selected_model').text(selectedModel);

        $.ajax({
            type: 'POST',
            url: 'http://127.0.0.1:5000/chatbot',
            data: { user_query: userQuery, chat_model: selectedModel },
            success: function(response) {
                $('#flask_chatbot_result').text(response.result);
            },
            error: function() {
                $('#flask_chatbot_result').text('Error processing your request.');
            }
        });

        return false;
    });
});
