    function buscar() {
    let val_two_search = document.getElementById('query').value
    
    $.ajax({
          url: '/requestinvertedindex',
          type: 'POST',
          contentType: 'application/json',
          data : JSON.stringify({
            "query":val_two_search
          }),
          dataType:'json',
          success: function(data){
            results = document.getElementById("results");
            results.innerHTML = "";
            var datos = JSON.parse(data)
	          
              for (tweet of datos) {
   		twttr.widgets.createTweet(tweet, results, 
                  {
                    conversation : 'none',
                    cards        : 'hidden',
                    linkColor    : '#cc0000',
                    theme        : 'light'
                  });
              }
          },   
          error: function(data){
              console.log(data);
          }
        });
  }





