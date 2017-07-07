function skipUp(row_selector) {
    var m = document.querySelector(row_selector + ' a');
    var id = setInterval(function() { m.click() }, 500);
    console.log(id);
    return function() { clearInterval(id); }
}
