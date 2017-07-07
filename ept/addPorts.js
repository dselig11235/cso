function addPorts(records) {
    var addButton = document.querySelector('#tabContent > form > fieldset:nth-child(8) > table:nth-child(5) > tbody:nth-child(1) > tr > td:nth-child(2) > table > tbody:nth-child(3) a');
    var rows = document.querySelectorAll('.RowdiscoveredOpenPorts');    
    var discovered = [].map.call(rows, function(r) {
        return [r.querySelector('input[name="eptOpenPortIPs"]').value, r.querySelector('input[name="eptOpenPortPorts"]').value, r.querySelector('input[name="eptOpenPortIdentifiedTypeVersions"]').value];
    });
    records.forEach(function(rec) {
        rec[1] = rec[1].toUpperCase();
        var matchPosition = discovered.findIndex(function(r) {
            return r[0] == rec[0] && r[1] == rec[1];
        });
        var version_input;
        if(matchPosition < 0) {
            addButton.click();
            var newrows = rows[0].parentNode.children;
            var newrow = newrows[newrows.length -1 ];
            newrow.querySelector('input[name="eptOpenPortIPs"]').value = rec[0];
            newrow.querySelector('input[name="eptOpenPortPorts"]').value = rec[1];
            version_input = newrow.querySelector('input[name="eptOpenPortIdentifiedTypeVersions"]');
            version_input.value = rec[3];
        } else {
            version_input = rows[matchPosition].querySelector('input[name="eptOpenPortIdentifiedTypeVersions"]');
            if(version_input.value == '') {
                rows[matchPosition].querySelector('input[name="eptOpenPortIdentifiedTypeVersions"]').value = rec[3];
            }
        }
        if(version_input.value == '-') {
            if(rec[2] == 'tcpwrapped') {
                version_input.value = 'TCP Wrapped';
            } else if(rec[2].startsWith('isakmp')) {
                version_input.value = 'ISAKMP';
            } else {
                version_input.value = rec[2];
            }
        }
    });
}
