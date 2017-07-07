div = document.querySelector('#tabContent > form > fieldset:nth-child(9) > div');
all = div.querySelectorAll('a');
figs = [].filter.call(all, function(value, index, Arr) { return index % 3 == 2; });
titles = figs.map(function(f) { return f.innerText.trim(); });
console.log(titles.join('\n'));
