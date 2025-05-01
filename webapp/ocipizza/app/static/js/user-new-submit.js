$(document).ready(function() {
    $('#id_form_telephone').mask('(99) 9999-9999?9').focusout(function (event) {  
        var target, phone, element;  
        
        target = (event.currentTarget) ? event.currentTarget : event.srcElement;                 
        phone = target.value.replace(/\D/g, '');
        
        element = $(target);  
        element.unmask();  

        if(phone.length > 10)
            element.mask('(99) 99999-999?9');  
        else 
            element.mask('(99) 9999-9999?9');                    
    });       
    
    $('#id_form').on('submit', function(e) {                
        e.preventDefault();

        if (this.checkValidity() === false)
            return;

        $.blockUI({    
            message: null,             
            overlayCSS: { backgroundColor: '#dee2e6' } 
        });   

        const jsonData = {
            email: $('#id_form_email').val(),
            password: $('#id_form_password').val(),
            name: $('#id_form_name').val(),
            telephone: $('#id_form_telephone').val()        
        };
    
        $.ajax({
            url: apiRegisterUrl,
            type: 'POST',       
            contentType: 'application/json',
            data: JSON.stringify(jsonData),    
            headers: {
                'X-CSRFToken': $('#id_csrf_token').val()
            },          
            success: function(resp) { 
                if (resp.status === 'success') {
                    setTimeout(function() {
                        window.location.href = `${homeUrl}?message=success`;
                    }, 2000);        
                }
                else {
                    $.unblockUI({});
                    $('#id_message_panel').removeClass('d-none');
                    alert('erro no cadastro');
                }                
            },
            error: function(xhr, textStatus, errorThrown) {   
                const jsonResp = JSON.parse(xhr.responseText);
                const respData = jsonResp.data;
                let html = '';

                $.unblockUI({});
                
                for (key in respData) {
                    html += `<p>${respData[key]}</p>`
                    
                    $('#id_form_' + key).val('');
                    $('#id_form_' + key).addClass('custom-form-invalid');
                    $('#id_form_' + key + '_message').addClass('d-block');

                //     $('#id_form_' + key).focus(function() {
                //         $('#id_form_' + key + '_message').addClass('d-none');
                //         $('#id_form_' + key).removeClass('custom-form-invalid');
                //     });
                }

                $('#id_message_panel').removeClass('d-none');                                 
                $('#id_message').append(html);   
                
                console.error(textStatus);            
            }
        });
    });

});