document.addEventListener("DOMContentLoaded", () => {
    // Status labels to code map
    const statusMap = {
        "NEW": 100,
        "AVAILABLE FOR HERKULES-1": 201,
        "AVAILABLE FOR HERKULES-2": 202,
        "AVAILABLE FOR HERKULES-3": 203,
        "AVAILABLE FOR POMINI": 214,
        "AVAILABLE FOR MESTA": 215,
        "IN-PROCESS": 204,
        "GROUND": 205,
        "CHOKED": 206,
        "IN FRONT OF MILL": 207,
        "AT-MILL": 208,
        "MILL-OUT": 209,
        "DECHOKED": 210,
        "AVAILABLE FOR GRINDING": 211,
        "OUT OF SERVICE": 212,
        "HOLD": 213,
        "DISCARDED": 300
    };

    document.querySelectorAll(".btnstatus").forEach(button => {
        button.addEventListener("click", function () {
            const label = this.textContent.trim();
            const key = label.split('(')[0].trim();

            // Skip INCIRCULATION silently
            if (key === "INCIRCULATION") {
                return;
            }

            const code = statusMap[key];

            // Silently ignore unmapped buttons
            if (!code) {
                return;
            }

            const form = document.createElement('form');
            form.method = 'POST';
            form.action = '/crs.html';

            const input = document.createElement('input');
            input.type = 'hidden';
            input.name = 'status';
            input.value = code;

            form.appendChild(input);
            document.body.appendChild(form);
            form.submit();
        });
    });

    // Enter key search
    document.getElementById("searchInput").addEventListener("keydown", function (e) {
        if (e.key === "Enter") {
            e.preventDefault();
            searchTable();
        }
    });
});

function searchTable() {
    const input = document.getElementById("searchInput").value.trim().toLowerCase();
    const table = document.querySelector("table");
    if (!table) return;

    const headers = table.querySelectorAll("thead th");
    let vendorIndex = -1;

    headers.forEach((th, i) => {
        if (th.textContent.trim().toLowerCase() === "vendor no") {
            vendorIndex = i;
        }
    });

    if (vendorIndex === -1) {
        console.error("Vendor no column not found.");
        return;
    }

    const rows = table.querySelectorAll("tbody tr");

    rows.forEach(row => {
        const cells = row.querySelectorAll("td");
        const vendorCell = cells[vendorIndex]?.textContent.trim().toLowerCase();
        row.style.display = vendorCell.includes(input) ? "" : "none";
    });
}

document.addEventListener("DOMContentLoaded", () => {
    const updateForms = document.querySelectorAll("form"); // target all forms

    updateForms.forEach(form => {
        if (form.querySelector("select") && form.querySelector("button[type='submit']")) {
            form.addEventListener("submit", function (e) {
                const statusSelect = form.querySelector("select");
                const selectedOption = statusSelect?.options[statusSelect.selectedIndex].text;

                const confirmed = confirm(`Are you sure you want to change status to: ${selectedOption}?`);
                if (!confirmed) {
                    e.preventDefault(); // cancel form submission
                }
            });
        }
    });
});
