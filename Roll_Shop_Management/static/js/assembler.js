document.getElementById('chokeRollBtnInner').addEventListener('click', () => {
    document.getElementById('rollButtons').style.display = 'block';
    document.getElementById('selectionForm').style.display = 'block';
    document.getElementById('dechokeSection').style.display = 'none';
    document.getElementById('selectRowBtn').style.display = 'inline-block';
    document.getElementById('dechokeBtn').style.display = 'none';
    document.getElementById('tableContainer').innerHTML = '';
});

document.getElementById('dechokeRollBtn').addEventListener('click', () => {
    document.getElementById('rollButtons').style.display = 'none';
    document.getElementById('selectionForm').style.display = 'none';
    document.getElementById('dechokeSection').style.display = 'block';
    document.getElementById('selectRowBtn').style.display = 'none';
    document.getElementById('dechokeBtn').style.display = 'inline-block';
    document.getElementById('tableContainer').innerHTML = '';
});

// Load Roll Data by Type
document.querySelectorAll('.roll-data-btn').forEach(button => {
    button.addEventListener('click', () => {
        let rollType = button.getAttribute('data-roll-type');
        if (rollType === 'ALL') rollType = '';
        fetch(`/get_roll_data?roll_type=${encodeURIComponent(rollType)}`)
            .then(response => response.json())
            .then(data => {
                renderRollTable(data);
            })
            .catch(err => {
                console.error('Error fetching roll data:', err);
                document.getElementById('tableContainer').innerHTML = "<p>Error loading data.</p>";
            });
    });
});

function renderRollTable(data) {
    if (data.length === 0) {
        document.getElementById('tableContainer').innerHTML = "<p>No data found for this selection.</p>";
        return;
    }

    let html = `<table border="1" cellpadding="5" cellspacing="0">
        <thead>
            <tr>
                <th>Select</th>
                <th>Vendor No</th>
                <th>Dia Min</th>
                <th>Dia Current</th>
                <th>Dia Max</th>
                <th>Roll Type</th>
            </tr>
        </thead><tbody>`;

    data.forEach((row, index) => {
        html += `<tr>
            <td><input type="radio" name="selectRow" value="${index}"></td>
            <td>${row.vendor_no || ''}</td>
            <td>${row.dia_min || ''}</td>
            <td>${row.dia_current || ''}</td>
            <td>${row.dia_max || ''}</td>
            <td>${row.roll_type || ''}</td>
        </tr>`;
    });

    html += "</tbody></table>";
    document.getElementById('tableContainer').innerHTML = html;
    window.rollTableData = data;
}

// Select Row from Roll Table
document.getElementById('selectRowBtn').addEventListener('click', () => {
    const selected = document.querySelector('input[name="selectRow"]:checked');
    if (!selected || !window.rollTableData) return;

    const rowData = window.rollTableData[parseInt(selected.value)];
    document.getElementById('vendorNo').value = rowData.vendor_no || '';
    document.getElementById('diaMin').value = rowData.dia_min || '';
    document.getElementById('diaCurrent').value = rowData.dia_current || '';
    document.getElementById('diaMax').value = rowData.dia_max || '';
    document.getElementById('rollType').value = rowData.roll_type || '';

    toggleFormButtons();
});

// Clear Form
document.getElementById('clearBtn').addEventListener('click', () => {
    ['vendorNo', 'diaMin', 'diaCurrent', 'diaMax', 'rollType', 'position'].forEach(id => {
        document.getElementById(id).value = '';
    });

    ['frontChock', 'backChock'].forEach(id => {
        document.getElementById(id).innerHTML = '';
        document.getElementById(id).style.display = 'none';
        document.getElementById(id + 'Label').style.display = 'none';
    });

    window.assembledRollsData = undefined;
    document.querySelectorAll('input[name="selectRow"]').forEach(r => r.checked = false);
    document.querySelectorAll('input[name="assembledSelect"]').forEach(r => r.checked = false);

    toggleFormButtons();
});

// Load Chocks
document.getElementById("position").addEventListener("change", () => {
    const pos = document.getElementById("position").value;
    if (!pos) return;

    fetch(`/get_chocks?position=${encodeURIComponent(pos)}&side=FRONT`)
        .then(res => res.json())
        .then(data => {
            const frontSelect = document.getElementById("frontChock");
            frontSelect.innerHTML = `<option value="">--Select Front Chock--</option>` +
                data.map(ch => `<option value="${ch}">${ch}</option>`).join("");
            frontSelect.style.display = "inline-block";
            document.getElementById("frontChockLabel").style.display = "inline-block";

            document.getElementById("backChock").style.display = "none";
            document.getElementById("backChockLabel").style.display = "none";

            toggleFormButtons();
        });
});

document.getElementById("frontChock").addEventListener("change", () => {
    const pos = document.getElementById("position").value;
    if (!pos) return;

    fetch(`/get_chocks?position=${encodeURIComponent(pos)}&side=BACK`)
        .then(res => res.json())
        .then(data => {
            const backSelect = document.getElementById("backChock");
            backSelect.innerHTML = `<option value="">--Select Back Chock--</option>` +
                data.map(ch => `<option value="${ch}">${ch}</option>`).join("");
            backSelect.style.display = "inline-block";
            document.getElementById("backChockLabel").style.display = "inline-block";

            toggleFormButtons();
        });
});

// Submit Form
document.getElementById('rollForm').addEventListener('submit', function (e) {
    e.preventDefault();

    if (!isFormComplete()) {
        alert("Please fill all required fields before assembling.");
        return;
    }

    const data = {
        vendorNo: document.getElementById('vendorNo').value,
        diaMin: document.getElementById('diaMin').value,
        diaCurrent: document.getElementById('diaCurrent').value,
        diaMax: document.getElementById('diaMax').value,
        rollType: document.getElementById('rollType').value,
        position: document.getElementById('position').value,
        frontChock: document.getElementById('frontChock').value || null,
        backChock: document.getElementById('backChock').value || null
    };

    fetch('/assemble_roll', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(result => {
        if (result.status === 'success') {
            alert('Roll Assembled Successfully');
            location.reload();
        } else {
            alert('Error: ' + result.message);
        }
    })
    .catch(err => console.error('Error:', err));
});

// View Assembled Rolls (Dechoke)
document.getElementById('viewAssembledRollsBtn').addEventListener('click', () => {
    fetch('/get_assembled_rolls')
        .then(response => response.json())
        .then(data => {
            if (data.length === 0) {
                document.getElementById('tableContainer').innerHTML = "<p>No assembled rolls found.</p>";
                return;
            }

            let html = `<table border="1" cellpadding="5" cellspacing="0">
                <thead>
                    <tr>
                        <th>Select</th>
                        <th>Roll Type</th>
                        <th>Vendor No</th>
                        <th>Dia Min</th>
                        <th>Dia Current</th>
                        <th>Dia Max</th>
                        <th>Position</th>
                        <th>Front Chock</th>
                        <th>Back Chock</th>
                    </tr>
                </thead><tbody>`;

            data.forEach((row, index) => {
                html += `<tr>
                    <td><input type="radio" name="assembledSelect" value="${index}"></td>
                    <td>${row.ROLL_TYPE}</td>
                    <td>${row.VENDOR_NO}</td>
                    <td>${row.DIA_MIN}</td>
                    <td>${row.DIA_CURRENT}</td>
                    <td>${row.DIA_MAX}</td>
                    <td>${row.POSITION}</td>
                    <td>${row.FRONT_CHOCK}</td>
                    <td>${row.BACK_CHOCK}</td>
                </tr>`;
            });

            html += "</tbody></table>";
            document.getElementById('tableContainer').innerHTML = html;
            window.assembledRollsData = data;
        });
});

// Dechoke
document.getElementById('dechokeBtn').addEventListener('click', () => {
    const selected = document.querySelector('input[name="assembledSelect"]:checked');
    if (!selected || !window.assembledRollsData) {
        alert('Please select a roll to dechoke.');
        return;
    }

    const confirmed = confirm('Are you sure you want to dechoke the selected roll?');
    if (!confirmed) return;

    const rowData = window.assembledRollsData[parseInt(selected.value)];

    const data = {
        vendor_no: rowData.VENDOR_NO,
        front_chock: rowData.FRONT_CHOCK,
        back_chock: rowData.BACK_CHOCK
    };

    fetch('/dechoke_roll', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(result => {
        if(result.status === 'success') {
            alert('Dechoke operation completed successfully.');
            location.reload();
        } else {
            alert('Error: ' + result.message);
        }
    });
});

// Utility: Form Validation
function isFormComplete() {
    const vendorNo = document.getElementById('vendorNo').value.trim();
    const diaMin = document.getElementById('diaMin').value.trim();
    const diaCurrent = document.getElementById('diaCurrent').value.trim();
    const diaMax = document.getElementById('diaMax').value.trim();
    const rollType = document.getElementById('rollType').value.trim();
    const position = document.getElementById('position').value.trim();
    const frontChock = document.getElementById('frontChock').value.trim();
    const backChock = document.getElementById('backChock').value.trim();

    return vendorNo && diaMin && diaCurrent && diaMax && rollType && position && frontChock && backChock;
}

function toggleFormButtons() {
    const submitBtn = document.querySelector('#rollForm button[type="submit"]');
    const clearBtn = document.getElementById('clearBtn');

    if (isFormComplete()) {
        submitBtn.style.display = 'inline-block';
        clearBtn.style.display = 'inline-block';
    } else {
        submitBtn.style.display = 'none';
        clearBtn.style.display = 'inline-block';
    }
}

// Watch fields to toggle form buttons
document.addEventListener('DOMContentLoaded', () => {
    toggleFormButtons();
});

['vendorNo', 'diaMin', 'diaCurrent', 'diaMax', 'rollType', 'position', 'frontChock', 'backChock'].forEach(id => {
    document.getElementById(id).addEventListener('input', toggleFormButtons);
    document.getElementById(id).addEventListener('change', toggleFormButtons);
});

// Search Roll Table
function searchTableByVendor() {
    const input = document.getElementById("searchBar").value.trim().toLowerCase();
    const table = document.querySelector("#tableContainer table");
    if (!table) return;

    const headers = table.querySelectorAll("thead th");
    let vendorIndex = -1;

    headers.forEach((th, i) => {
        if (th.textContent.trim().toLowerCase() === "vendor no") {
            vendorIndex = i;
        }
    });

    if (vendorIndex === -1) return;

    const rows = table.querySelectorAll("tbody tr");
    rows.forEach(row => {
        const cells = row.querySelectorAll("td");
        const vendorCell = cells[vendorIndex]?.textContent.trim().toLowerCase();
        row.style.display = vendorCell.includes(input) ? "" : "none";
    });
}

document.getElementById("searchBtn").addEventListener("click", searchTableByVendor);
document.getElementById("searchBar").addEventListener("keydown", function (event) {
    if (event.key === "Enter") {
        event.preventDefault();
        searchTableByVendor();
    }
});

//for dechoke search bar
function searchDechokeTableByVendor() {
    const input = document.getElementById("dechokeSearchBar").value.trim().toLowerCase();
    const table = document.querySelector("#tableContainer table");
    if (!table) return;

    const headers = table.querySelectorAll("thead th");
    let vendorIndex = -1;

    headers.forEach((th, i) => {
        if (th.textContent.trim().toLowerCase() === "vendor no") {
            vendorIndex = i;
        }
    });

    if (vendorIndex === -1) return;

    const rows = table.querySelectorAll("tbody tr");
    rows.forEach(row => {
        const cells = row.querySelectorAll("td");
        const vendorCell = cells[vendorIndex]?.textContent.trim().toLowerCase();
        row.style.display = vendorCell.includes(input) ? "" : "none";
    });
}

document.getElementById("dechokeSearchBtn").addEventListener("click", searchDechokeTableByVendor);
document.getElementById("dechokeSearchBar").addEventListener("keydown", function (event) {
    if (event.key === "Enter") {
        event.preventDefault();
        searchDechokeTableByVendor();
    }
});


document.querySelectorAll(".roll-data-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
        // Remove "selected" class from all buttons
        document.querySelectorAll(".roll-data-btn").forEach((b) => b.classList.remove("selected"));
        
        // Add "selected" class to the clicked button
        btn.classList.add("selected");
    });
});

