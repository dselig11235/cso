buttons = document.querySelectorAll('#tabContent > form > fieldset:nth-child(8) > table:nth-child(5) > tbody:nth-child(1) > tr > td:nth-child(2) > table > tbody:nth-child(2) > tr a');
buttons = [].slice.call(buttons);
function clickIt() {
    buttons[0].click();
    buttons.splice(0, 1);
    if(buttons.length !== 0) {
        setTimeout(clickIt, 500);
    }
}
clickIt();
