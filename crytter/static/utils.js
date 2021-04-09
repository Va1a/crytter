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

function getPrice(ofCurr, elementToUpdate){
  url = 'https://api.coinbase.com/v2/exchange-rates?currency='+ofCurr;
  $.get(url, function(data, status){
    elementToUpdate.textContent = '$'+Math.round( data.data.rates.USD * 1000 + Number.EPSILON ) / 1000;
  });
}

async function dealValue(hasC, wantsC){
  const usdOfHas = await CBrate(hasC, "USD");
  const usdOfWants = await CBrate(wantsC, "USD");

  return Math.round((usdOfHas / usdOfWants) * 100 + Number.EPSILON ) / 100;
}

async function CBrate(ofCurr, toCurr){
  url = 'https://api.coinbase.com/v2/exchange-rates?currency='+ofCurr;
  rates = await $.get(url, function(data, status){return data.data.rates;});
  console.log(rates.data.rates[toCurr]);
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