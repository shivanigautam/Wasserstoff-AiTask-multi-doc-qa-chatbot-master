$(document).ready(function() {
    $('#check-now').click(function() {
        var title = $('#title').val();
        console.log('Check Now button clicked');  // Log the button click
        console.log('Title:', title);  // Log the title value

        $.ajax({
            url: '/check_index',
            method: 'POST',
            data: { title: title },
            success: function(response) {
                console.log('Response received:', response);  // Log the response
                if (response.available) {
                    $('#title-status').text('Title available').css('color', 'green');
                    $('#content-section').show();
                } else {
                    $('#title-status').text('Already used, try another title').css('color', 'red');
                }
            },
            error: function(error) {
                console.log('Error:', error);  // Log any errors
            }
        });
    });

    $('.tab-button').click(function() {
        var tabId = $(this).data('tab');
        $('.tab-content').hide();
        $('#' + tabId).show();
    });

    $('#submit-pdf').click(function() {
        var formData = new FormData();
        formData.append('title', $('#title').val());
        formData.append('tab_title', 'Add context from PDF');
        formData.append('file', $('#pdf-file')[0].files[0]);
        $.ajax({
            url: '/ingestion',
            method: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            success: function(response) {
                if (response.success) {
                    $('#success-modal').show();
                    $('#chatbot-link').attr('href', '/chatbot?index=' + $('#title').val());
                }
            }
        });
    });

    $('#submit-api').click(function() {
        var formData = {
            title: $('#title').val(),
            tab_title: 'Add context from API',
            api_url: $('#api-url').val()
        };
        $.ajax({
            url: '/ingestion',
            method: 'POST',
            data: formData,
            success: function(response) {
                if (response.success) {
                    $('#success-modal').show();
                    $('#chatbot-link').attr('href', '/chatbot?index=' + $('#title').val());
                }
            }
        });
    });

    $('#submit-direct').click(function() {
        var formData = {
            title: $('#title').val(),
            tab_title: 'Add direct context',
            content: $('#direct-content').val()
        };
        $.ajax({
            url: '/ingestion',
            method: 'POST',
            data: formData,
            success: function(response) {
                if (response.success) {
                    $('#success-modal').show();
                    $('#chatbot-link').attr('href', '/chatbot?index=' + $('#title').val());
                }
            }
        });
    });
});
