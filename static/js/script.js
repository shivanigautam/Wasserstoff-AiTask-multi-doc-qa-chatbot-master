jQuery(document).ready(function($) {
    function showLoader(loaderId) {
        $(loaderId).show();
    }

    function hideLoader(loaderId) {
        $(loaderId).hide();
    }

    function validateTitle(title) {
        // Title should not be empty and should not contain special characters or spaces
        var regex = /^[a-z0-9-]+$/;
        if (!title) {
            return "Title cannot be empty";
        } else if (!regex.test(title)) {
            return "Title cannot contain special characters & spaces. Only lowercase and the special character ['-'] are allowed";
        }
        return null;
    }

    function validateDirectContent(content) {
        // Direct content should have at least 300 words
        var wordCount = content.trim().split(/\s+/).length;
        if (wordCount < 300) {
            return "Content must be at least 300 words";
        }
        return null;
    }

    function clearErrorMessages() {
        $('.error-message').text('');
    }

    $('#check-now').click(function() {
        clearErrorMessages();

        var title = $('#title').val();
        var titleError = validateTitle(title);
        if (titleError) {
            $('#title-status').text(titleError).css('color', 'red');
            return;
        }

        console.log('Check Now button clicked');
        console.log('Title:', title);
        showLoader('#loader');

        $.ajax({
            url: '/check_index',
            method: 'POST',
            data: { title: title },
            success: function(response) {
                console.log('Response received:', response);
                hideLoader('#loader');
                if (response.available) {
                    $('#title-status').text('Title available').css('color', 'green');
                    $('#content-section').show();
                    $('#title').prop('disabled', true);
                    $('#check-now').prop('disabled', true);
                } else {
                    $('#title-status').text('Already used, try another title').css('color', 'red');
                }
            },
            error: function(error) {
                console.log('Error:', error);
                hideLoader('#loader');
            }
        });
    });

    $('.tab-button').click(function() {
        var tabId = $(this).data('tab');
        $('.tab-content').hide();
        $('#' + tabId).show();
    });

    function handleSubmission(formData, loaderId, successMessage, errorId) {
        clearErrorMessages();
        showLoader(loaderId);
        disableAllInputs();
        $.ajax({
            url: '/ingestion',
            method: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            success: function(response) {
                hideLoader(loaderId);
                if (response.success) {
                    $('#modal-message').text(successMessage);
                    $('#success-modal').show();
                    $('#chatbot-link').attr('href', '/bot?index=' + $('#title').val());
                    $('#plugin-link').attr('href', '/chatbot_plugin?index=' + $('#title').val());
                } else {
                    $(errorId).text('Error while Integration').css('color', 'red');
                    enableAllInputs();
                }
            },
            error: function(error) {
                hideLoader(loaderId);
                $(errorId).text('Error while Integration').css('color', 'red');
                enableAllInputs();
                console.log('Error:', error);
            }
        });
    }

    function disableAllInputs() {
        $('input, button, textarea').prop('disabled', true);
    }

    function enableAllInputs() {
        $('input, button, textarea').prop('disabled', false);
    }

    $('#submit-pdf').click(function() {
        clearErrorMessages();

        var formData = new FormData();
        formData.append('title', $('#title').val());
        formData.append('tab_title', 'Add context from PDF');
        formData.append('file', $('#pdf-file')[0].files[0]);
        handleSubmission(formData, '#pdf-loader', 'Ingestion successful!', '#pdf-error');
    });

    $('#submit-api').click(function() {
        clearErrorMessages();

        var formData = new FormData();
        formData.append('title', $('#title').val());
        formData.append('tab_title', 'Add context from API');
        formData.append('api_url', $('#api-url').val());
        handleSubmission(formData, '#api-loader', 'Ingestion successful!', '#api-error');
    });

    $('#submit-direct').click(function() {
        clearErrorMessages();

        var content = $('#direct-content').val();
        var contentError = validateDirectContent(content);
        if (contentError) {
            $('#direct-error').text(contentError).css('color', 'red');
            return;
        }

        var formData = new FormData();
        formData.append('title', $('#title').val());
        formData.append('tab_title', 'Add direct context');
        formData.append('content', content);
        handleSubmission(formData, '#direct-loader', 'Ingestion successful!', '#direct-error');
    });

    $('#close-modal').click(function() {
        $('#success-modal').hide();
        $('#title').val('');
        $('#title-status').text('');
        $('#title').prop('disabled', false);
        $('#check-now').prop('disabled', false);
        $('#pdf-file').val('');
        $('#api-url').val('');
        $('#direct-content').val('');
        $('.error-message').text('');
        enableAllInputs();
        $('#content-section').hide();
    });
});
