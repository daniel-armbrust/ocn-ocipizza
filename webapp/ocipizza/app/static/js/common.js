//
// js/common.js
//

function formatPriceToBRL(price) {
    return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(price);
 }

 function popUpMessage(title, message) {
    $('#id_modal_title').html('');
    $('#id_modal_title').append(title);

    $('#id_modal_message_text').html('');
    $('#id_modal_message_text').append(message);    

    $('#id_modal_message').modal('show');    
 }

 function getStateCity(zipcode, apiHost, callback) {     
      const url = `${apiHost}/${zipcode}`;

      $.ajax({
            url: url,
            method: 'GET',            
            success: function(data) {               
               callback(data);
            },
            error: function(xhr, status, error) {               
               console.error('Error:', error);
               callback(xhr);
            }
      });    
 }

 function validateAndsubmitButton() {
   $.blockUI({message: null, overlayCSS: { backgroundColor: '#dee2e6' }}); 

   const forms = document.querySelectorAll('.needs-validation');
   let status = false;

   for (let i = 0 ; i < forms.length ; i++) {
       if (forms[i].checkValidity()) {
           status = true;         
       } 

       forms[i].classList.add('was-validated');
   }

   if (status) {
      document.getElementById('id_form').submit(); 
      return true;
   }      
   else {
     $.unblockUI({});
     return false;
   }      
}