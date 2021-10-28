$.ajaxSetup({ cache: false });

function setInputFilter(textbox, inputFilter) {
  ["input", "keydown", "keyup", "mousedown", "mouseup", "select", "contextmenu", "drop"].forEach(function(event) {
    textbox.addEventListener(event, function() {
      if (inputFilter(this.value)) {
        this.oldValue = this.value;
        this.oldSelectionStart = this.selectionStart;
        this.oldSelectionEnd = this.selectionEnd;
      } else if (this.hasOwnProperty("oldValue")) {
        this.value = this.oldValue;
        this.setSelectionRange(this.oldSelectionStart, this.oldSelectionEnd);
      } else {
        this.value = "";
      }
    });
  });
}

function getPrice(ofCurr, elementToUpdate, showChange=false){
  var price;
  const oldPrice = parseFloat(elementToUpdate.textContent.slice(1));
  if(!isNaN(elementToUpdate.textContent.slice(1)) && showChange){
    showChange = true;
  } else {
    showChange = false;
  }
  url = 'https://api.coinbase.com/v2/exchange-rates?currency='+ofCurr;
  $.get(url, function(data, status){
    price = parseFloat(data.data.rates.USD);
    elementToUpdate.textContent = '$'+ parseFloat(price).toFixed(2);
  });
  if(showChange){
    console.log('price: '+price+', old price: '+oldPrice);
    var percentChange = ((price / oldPrice) - 1)*100;
    console.log(percentChange+'%');
    document.getElementById(elementToUpdate.id+'-change-symb').className = (percentChange >= 0) ? 'fa fa-long-arrow-up' : 'fa fa-long-arrow-down';
    document.getElementById(elementToUpdate.id+'-change').textContent = percentChange.toFixed(2)+'%';
  }

}

async function dealValue(hasC, wantsC){
  const usdOfHas = await CBrate(hasC, "USD");
  const usdOfWants = await CBrate(wantsC, "USD");

  return (usdOfHas / usdOfWants).toFixed(5);
}

async function CBrate(ofCurr, toCurr){
  url = 'https://api.coinbase.com/v2/exchange-rates?currency='+ofCurr;
  rates = await $.get(url, function(data, status){return data.data.rates;});
  return rates.data.rates[toCurr];
}

function setCookie(cname, cvalue, exdays) {
  var d = new Date();
  d.setTime(d.getTime() + (exdays*24*60*60*1000));
  var expires = "expires="+ d.toUTCString();
  document.cookie = cname + "=" + cvalue + ";" + expires + ";path=/";
}

function getCookie(cname) {
  var name = cname + "=";
  var decodedCookie = decodeURIComponent(document.cookie);
  var ca = decodedCookie.split(';');
  for(var i = 0; i <ca.length; i++) {
    var c = ca[i];
    while (c.charAt(0) == ' ') {
      c = c.substring(1);
    }
    if (c.indexOf(name) == 0) {
      return c.substring(name.length, c.length);
    }
  }
  return "";
}