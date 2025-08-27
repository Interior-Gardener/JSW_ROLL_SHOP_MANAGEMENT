// STAND ASSEMBLY button does nothing on click
document.getElementById('standRollBtn').addEventListener('click', () => {
    // No action needed here per your request
});

// Clicking Stand-in Point shows the StandSection with View Assembled Rolls button
document.getElementById('StandinPointBtn').addEventListener('click', () => {
    document.getElementById('StandSection').style.display = 'block';

    // Hide Stand-out Section if visible
    const standOutSection = document.getElementById('StandOutSection');
    if (standOutSection) {
        standOutSection.style.display = 'none';
    }
});

// Clicking Stand-out Point shows a different section, no interference with Stand-in
document.getElementById('StandoutPointBtn').addEventListener('click', () => {
    const standSection = document.getElementById('StandSection');
    if (standSection) {
        standSection.style.display = 'none';
    }
    const standOutSection = document.getElementById('StandOutSection');
    if (standOutSection) {
        standOutSection.style.display = 'block';
    }

    // Trigger the fetch and show table automatically
    // document.getElementById('viewStatusAsblBtn').click();
});


// Clicking View Assembled Rolls fetches data and shows the table
document.getElementById('viewAssembledRollsBtn').addEventListener('click', () => {
    fetch('/get_assembled_rolls_for_stand')
        .then(response => response.json())
        .then(data => {
            if (data.length === 0) {
                document.getElementById('tableContainer').innerHTML = "<p>No assembled rolls found.</p>";

                // Hide message and button if no data
                document.getElementById('selectRowsMsg').style.display = 'none';
                document.getElementById('selectRowBtn').style.display = 'none';

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
                    <td><input type="checkbox" name="assembledSelect" value="${index}"></td>
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
            document.getElementById('tableContainer').style.display = 'block';
            document.getElementById('tableContainer').innerHTML = html;

            // Show the message and button when table is shown
            document.getElementById('selectRowsMsg').style.display = 'block';
            document.getElementById('selectRowBtn').style.display = 'inline-block';

            window.assembledRollsData = data;
        });
    const formSection = document.getElementById('formSection');
    formSection.style.display = 'block';
});


document.getElementById('selectRowBtn').addEventListener('click', () => {
    const checkboxes = document.querySelectorAll('input[name="assembledSelect"]:checked');
    const selectedCount = checkboxes.length;

    if (selectedCount !== 2) {
        alert("You must select exactly 2 rows.");
        return;
    }

    const selectedIndices = Array.from(checkboxes).map(cb => parseInt(cb.value));
    const selectedData = selectedIndices.map(index => window.assembledRollsData[index]);

    // Fill Left form
    document.getElementById('rollType1').value = selectedData[0].ROLL_TYPE || '';
    document.getElementById('vendorNo1').value = selectedData[0].VENDOR_NO || '';
    document.getElementById('diaCurrent1').value = selectedData[0].DIA_CURRENT || '';

    // Fill Right form
    document.getElementById('rollType2').value = selectedData[1].ROLL_TYPE || '';
    document.getElementById('vendorNo2').value = selectedData[1].VENDOR_NO || '';
    document.getElementById('diaCurrent2').value = selectedData[1].DIA_CURRENT || '';
});


document.addEventListener("change", (e) => {
    if (e.target.name === "assembledSelect") {
        const selected = document.querySelectorAll('input[name="assembledSelect"]:checked');
        if (selected.length > 2) {
            e.target.checked = false;
            alert("You can select only 2 rows at a time.");
        }
    }
});

function populateStandNos() {
    fetch('/get_free_stand_nos')
        .then(response => response.json())
        .then(data => {
            const standSelect = document.getElementById('standNo');
            // Clear current options except default
            standSelect.innerHTML = `<option value="" disabled selected>Select Stand No</option>`;

            if (data.length === 0) {
                const option = document.createElement('option');
                option.text = 'No free stands available';
                option.disabled = true;
                standSelect.appendChild(option);
                return;
            }

            data.forEach(no => {
                const option = document.createElement('option');
                option.value = no;
                option.text = no;
                standSelect.appendChild(option);
            });
        })
        .catch(error => {
            console.error('Error loading stand nos:', error);
        });
}

// Run on page load
document.addEventListener('DOMContentLoaded', () => {
    populateStandNos();
});

// AJAX form submission as per previous instructions (if you want)
document.getElementById('rollForm').addEventListener('submit', function (e) {
    e.preventDefault(); // Prevent default form submission

    const formData = {
        rollType1: document.getElementById('rollType1').value,
        vendorNo1: document.getElementById('vendorNo1').value,
        diaCurrent1: document.getElementById('diaCurrent1').value,
        standPosition1: document.getElementById('standPosition1').value,

        rollType2: document.getElementById('rollType2').value,
        vendorNo2: document.getElementById('vendorNo2').value,
        diaCurrent2: document.getElementById('diaCurrent2').value,
        standPosition2: document.getElementById('standPosition2').value,

        standNo: document.getElementById('standNo').value
    };

    // ❌ Reject if both stand positions are the same
    if (
        formData.standPosition1 === formData.standPosition2 &&
        formData.rollType1 === formData.rollType2
    ) {
        alert("Error: You cannot select the same Stand Position for the same Roll Type.");
        return;
    }
    const userConfirmed = confirm(`Are you sure you want to submit ${formData.rollType1} at ${formData.standPosition1} and ${formData.rollType2} at ${formData.standPosition2} in ${formData.standNo} Stand Assembly?`);
    if (!userConfirmed) {
        return;
    }
    fetch('/submit_roll', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
    })
        .then(res => res.json())
        .then(result => {
            if (result.success) {
                alert("Stand Assembly successful!");
                window.location.reload(); // 🔄 Refresh the page after success
            } else {
                alert("Failed to submit: " + result.message);
            }
        })
        .catch(err => {
            console.error("Submission error:", err);
            alert("Something went wrong. Please try again.");
        });
});

document.getElementById('viewStatusAsblBtn').addEventListener('click', () => {
    fetch('/get_status_asbl')
        .then(response => response.json())
        .then(data => {
            const container = document.getElementById('statusAsblTableContainer');
            if (!data || data.length === 0) {
                container.innerHTML = "<p>No records found in status_asbl table.</p>";
                return;
            }

            let html = `<table border="1" cellpadding="5" cellspacing="0">
                <thead>
                    <tr>
                        <th>Select</th>`; // Add column for radio buttons

            Object.keys(data[0]).forEach(col => {
                html += `<th>${col}</th>`;
            });

            html += `</tr></thead><tbody>`;

            data.forEach((row, index) => {
                html += `<tr>
                    <td><input type="checkbox" name="statusSelect" value="${index}"></td>`;

                Object.values(row).forEach(val => {
                    html += `<td>${val === null ? '' : val}</td>`;
                });

                html += "</tr>";
            });

            html += "</tbody></table>";
            container.style.display = 'block';
            container.innerHTML = html;


            // Store the data globally for later use (e.g., on Submit button click)
            window.statusAsblData = data;
        })
        .catch(err => {
            console.error("Error fetching status_asbl data:", err);
            document.getElementById('statusAsblTableContainer').innerHTML = "<p>Error loading data.</p>";
        });
});

document.getElementById('submitStandOutBtn').addEventListener('click', () => {
    const checkboxes = document.querySelectorAll('input[name="statusSelect"]:checked');
    if (checkboxes.length === 0) {
        alert("Please select at least one row.");
        return;
    }

    const selectedData = Array.from(checkboxes).map(cb => {
        const index = parseInt(cb.value);
        return window.statusAsblData[index];
    });

    fetch('/stand_out_action', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(selectedData)
    })
        .then(res => res.json())
        .then(result => {
            if (result.success) {
                alert("Stand De-Assembly successful!");
                window.location.reload(); // 🔄 Refresh the page after success
            } else {
                alert("Failed to submit: " + result.message);
            }
        })
        .catch(err => {
            console.error("Error during Stand-out:", err);
            alert("Something went wrong during Stand-out.");
        });
});
// Listen for checkbox changes in status ASBL table
document.addEventListener("change", function (e) {
    if (e.target.name === "statusSelect") {
        const anySelected = document.querySelectorAll('input[name="statusSelect"]:checked').length > 0;
        document.getElementById('submitStandOutBtn').style.display = anySelected ? 'inline-block' : 'none';
    }
});
