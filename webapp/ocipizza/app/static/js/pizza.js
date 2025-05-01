//
// js/pizza.js
//

function listOfPizzas(remoteHost) {
   const url = remoteHost + '/pizzas';
   
   $.ajax({
      url: url,
      type: 'GET', 
      dataType: 'json', 
      contentType: 'application/json; charset=utf-8',    
      success: function(resp) {  

         $('#app').empty(); 

         if (resp.status !== 'success') {
            $('#app').append(`
               <div class="row">               
                  <div class="col-sm-12 col-md-12 d-flex justify-content-center pt-4">
                     <br><br>
                     <h3 class="text-danger fw-bold fst-italic">
                        Erro ao carregar os dados! Por favor, tente novamente mais tarde.
                     </h3>
                  </div>
               </div>`); 
            return;
         }         
         
         let count = 0;
         let html = '';

         $.each(resp.data, function(i, pizza) {                                      
              
              if (count === 0) {
                 html += '<br><div class="row">';  
                 count++;                                        
              }   
              else if (count === 3) {             
                 html += '</div><br><div class="row">';
                 count = 1;
              }
              else {
                 count++;    
              }  

              let price = formatPriceToBRL(pizza.price);

              html += `
                  <div class="col-sm-4 col-md-4 pb-4">
                     <a href="javascript:void(0)" class="text-decoration-none text-dark" onclick="showPizzaDetails('${remoteHost}',${pizza.id});">
                        <div class="card h-100 text-center pizza-card">
                              <img src="${pizza.image}" class="card-img-top" alt="${pizza.name}">
                              <div class="card-body d-flex flex-column">
                                 <h4 class="card-title text-capitalize">${pizza.name}</h4>
                                 <p class="card-text text-uppercase">${pizza.description}</p>
                                 <p class="h2 text-success" style="margin-top: auto;"> <b> ${price} </b> </p>
                              </div>
                        </div>
                     </a>                
                  </div>`;                         
         });

         $('#app').append(html);                  
      },
      error: function(xhr, textStatus, errorThrown) {                    
         console.error(textStatus);            
      }
   });
}

function showPizzaDetails(remoteHost, pizzaId) {   
   const url = remoteHost + '/pizzas/' + pizzaId;
   
   $.ajax({
      url: url,
      type: 'GET', 
      dataType: 'json', 
      contentType: 'application/json; charset=utf-8',    
      success: function(resp) {           
         
         if (resp.status !== 'success') {            
            alert('ERRO! Não foi possível obter dados da pizza.');         
            return;
         }

         const price = formatPriceToBRL(resp.data.price);
                  
         $('#id_modal_pizza_details_title').html('');
         $('#id_modal_pizza_details_title').append(resp.data.name);
         
         $('#id_modal_pizza_details_image').attr('src', resp.data.image);
         $('#id_modal_pizza_details_image').attr('title', resp.data.name);
         $('#id_modal_pizza_details_image').attr('alt', resp.data.name);
         
         $('#id_modal_pizza_details_description').html('');
         $('#id_modal_pizza_details_description').append(resp.data.description);

         $('#id_modal_pizza_details_price').html('');
         $('#id_modal_pizza_details_price').append(price);

         $('#id_modal_pizza_details_id').html('');
         $('#id_modal_pizza_details_id').val(resp.data.id);

         $('#id_modal_pizza_details').modal('show');
      },
      error: function(xhr, textStatus, errorThrown) {                    
         console.error(textStatus);            
      }
   });
}

function updatePizzaCartItemCount() {
   const sessionStorageKeys = Object.keys(sessionStorage);
   const cartItemCount = sessionStorageKeys.length;

   if (cartItemCount > 0) {
       $('#id_mainmenu_cart_item_count').html('');
       $('#id_mainmenu_cart_item_count').append(cartItemCount);

       $('#id_menuitem_cart_item_count').html('');
       $('#id_menuitem_cart_item_count').append(cartItemCount);
   }
   else {
       $('#id_mainmenu_cart_item_count').html('');
       $('#id_mainmenu_cart_item_count').append('0');      
   }
}

function addPizzaCart() {
   const pizzaId = $('#id_modal_pizza_details_id').val();

   sessionStorage.setItem(pizzaId, pizzaId);

   updatePizzaCartItemCount();

   $('#id_modal_pizza_details').modal('toggle');  
   
   popUpMessage('Pizza', 'Obbaaa! Sua pizza foi adicionada ao carrinho.');
}

function removePizzaCart(index, pizzaId) {
   $(`#id_pizza_${index}`).remove();
   $('#id_flash_message').remove();

   sessionStorage.removeItem(pizzaId);

   updatePizzaCartItemCount(); 
   listPizzaCart(apiHost);

   popUpMessage('Pizza', 'Pizza removida do carrinho!');   
}

function listPizzaCart(remoteHost) {  
   let listOfPizza = new Array();
   let pizzaId;
   let url;
   let html;
   let totalPrice = 0;

   if (sessionStorage.length <= 0) {
      $('#app').empty();

      $('#app').append(`
          <div class="row">               
               <div class="col-sm-12 col-md-12 d-flex justify-content-center pt-4">
                   <br><br>
                   <h3 class="h2 fw-bold fst-italic">
                        Não há pizza(s) no carrinho.
                   </h3>
               </div>
          </div>`);
      
      $('#id_delivery_options').addClass('invisible');

      setTimeout(function() {
         window.location.href = webHost;
      }, 2000);

      return;
   }

   for (let i = 0 ; i < sessionStorage.length ; i++) {
      pizzaId = sessionStorage.key(i);
      url = remoteHost + '/pizzas/' + pizzaId;

      $.ajax({
          url: url,
          type: 'GET', 
          dataType: 'json', 
          contentType: 'application/json; charset=utf-8',   
          async: false,
          success: function(resp) {
             if (resp.status === 'success') {
               totalPrice += resp.data.price;
               let price = formatPriceToBRL(resp.data.price);
               listOfPizza.push(`
                  <div id="id_pizza_${i}">
                     <hr> 
                     <div class="row">
                         <div class="col-6 text-start">
                             <p class="text-left text-capitalize fs-5">${resp.data.name}</p>
                         </div>
                         <div class="col-6 text-end">
                             <p class="fs-5">${price} &nbsp;&nbsp;
                                <a href="javascript:void(0)" class="text-decoration-none" onclick="removePizzaCart(${i},${pizzaId});">
                                   <i class="fa-solid fa-trash-can text-primary"></i> 
                                </a> &nbsp;&nbsp;
                             </p>
                         </div>
                     </div>
                  </div>`);            
             }
             else {
               // TODO: display error message.
               listOfPizza = [];               
             }
          },   
          error: function(xhr, textStatus, errorThrown) {                    
            console.error(textStatus);            
         }          
      });   

      if (listOfPizza.length <= 0)
         break;  
   }  

   if (listOfPizza.length <= 0) {
      console.log(listOfPizza);
      // TODO: display error message
      return;
   }

   $('#app').empty(); 

   html = `<br><div class="row"><div class="col-sm-2 col-md-2"><p>&nbsp;</p></div>
           <div class="col-sm-8 col-md-8 d-flex justify-content-center">
           <div class="card w-100 rounded">
           <div class="card-body rounded" style="border-top: 5px solid gray;">
           <h5 class="card-title fw-bold fs-4">Resumo do Pedido</h5>`;
   
   for (let i = 0 ; i < listOfPizza.length ; i++) {
      html += `<span class=""> ${listOfPizza[i]}`      
   }

   totalPrice = formatPriceToBRL(totalPrice);

   html += `<hr><div class="row"><div class="col-6 text-start">
            <h5 class="card-title fs-4 fw-bold">Subtotal</h5></div>
            <div class="col-6 text-end">
            <p class="fs-3 fw-bold text-success">${totalPrice} &nbsp;&nbsp;</p>
            </div></div></div>`;              

   $('#app').append(html);

   $('#id_delivery_options').removeClass('invisible');
}

function pizzaDeliveryOptions() {
   const zipcode = $('#id_input_zipcode').val();
   const zipcodeEndpoint = apiHost + '/locations/zipcodes';   

   if (! $('#id_zipcode_notfound_message').hasClass('d-none'))
      $('#id_zipcode_notfound_message').addClass('d-none');
   
   getStateCity(zipcode, zipcodeEndpoint, function(resp) {
       if (resp.status === 'success') {
           const state = resp.data.state.toUpperCase();

           let city = resp.data.city;
           city = city.charAt(0).toUpperCase() + city.slice(1);

           $('#id_state').val(state);
           $('#id_city').val(city);
           $('#id_zipcode').val(zipcode);

           $('#id_delivery_options_modal').modal('toggle');
           $('#id_your_address_modal').modal('show');
       }  
       else {           
           $('#id_zipcode_notfound_message').removeClass('d-none');
       }      
   });
}