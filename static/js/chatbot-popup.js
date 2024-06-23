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
        var index = $('#index').val();

        var userResult = `
            <div class="chatbot-result user">
                <p>${userQuery}</p>
            </div>
        `;
        $('#chatbot-popup-results').append(userResult);

        $.ajax({
            type: 'POST',
            url: '/handle_query',
            data: { user_query: userQuery, chat_model: selectedModel, index: index },
            success: function(response) {
                var serverResult = `
                    <div class="chatbot-result server">
                        <p>${response.result}</p>
                    </div>
                `;
                $('#chatbot-popup-results').append(serverResult);
                $('#user_query').val('');
            },
            error: function() {
                var errorResult = `
                    <div class="chatbot-result server">
                        <p>Error processing your request.</p>
                    </div>
                `;
                $('#chatbot-popup-results').append(errorResult);
            }
        });

        return false;
    });
});
