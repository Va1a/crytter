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

  return Math.round((usdOfHas / usdOfWants) * 1000 + Number.EPSILON ) / 1000;
}

async function CBrate(ofCurr, toCurr){
  url = 'https://api.coinbase.com/v2/exchange-rates?currency='+ofCurr;
  rates = await $.get(url, function(data, status){return data.data.rates;});
  console.log(rates.data.rates[toCurr]);
  return rates.data.rates[toCurr];
}