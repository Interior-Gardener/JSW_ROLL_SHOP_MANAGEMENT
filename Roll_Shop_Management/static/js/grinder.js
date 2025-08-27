 document.addEventListener("DOMContentLoaded", () => {
    const statusMap = {
        "AVAILABLE FOR HERKULES-1": 201,
        "AVAILABLE FOR HERKULES-2": 202,
        "AVAILABLE FOR HERKULES-3": 203,
        "AVAILABLE FOR POMINI": 214,
        "AVAILABLE FOR MESTA": 215,
        "HOLD": 213,
        "IN-PROCESS": 204
    };

    const mainDropdown = document.querySelector('.dropdown-wrapper > button span');

   
    // 🌟 Handle dropdown option clicks
    document.querySelectorAll(".btnstatus").forEach(button => {
        button.addEventListener("click", function () {
            const label = this.textContent.trim();
            const key = label.split('(')[0].trim();

            // Save clean label to localStorage
            const cleanLabel = label.replace(/ ▼+$/, '');
            // localStorage.setItem("selectedStatus", cleanLabel);

            // Update dropdown label safely
            if (mainDropdown) {
                mainDropdown.textContent = cleanLabel + ' ▼';
            }

            // Silently ignore INCIRCULATION (no form submit)
            if (key === "INCIRCULATION" || key.startsWith("INCIRCULATION")) {
                return;
            }

            const code = statusMap[key];
            if (!code) return;

            const form = document.createElement('form');
            form.method = 'POST';
            form.action = '/grinder.html';

            const input = document.createElement('input');
            input.type = 'hidden';
            input.name = 'status';
            input.value = code;

            form.appendChild(input);
            document.body.appendChild(form);
            form.submit();
        });
    });

    // Show inspection form
    const showFormBtn = document.getElementById("showInspectionFormBtn");
    const formContainer = document.getElementById("inspectionFormContainer");

    if (showFormBtn && formContainer) {
        showFormBtn.addEventListener("click", () => {
            formContainer.style.display = "block";
            showFormBtn.style.display = "none";

            const submitBtn = document.getElementById("submitBtn");
            if (submitBtn) {
                submitBtn.style.display = "inline-block";
            }
        });
    }

    // Confirm submission
    const form = document.querySelector('form');
    if (form) {
        form.addEventListener("submit", function (e) {
            const label = document.querySelector('.btn.submit')?.innerText || "Mark Selected";
            const confirmMessage = `Are you sure you want to ${label}?`;
            if (!confirm(confirmMessage)) {
                e.preventDefault();
            }
        });
    }

    // Search functionality
    const searchInput = document.getElementById("searchInput");
    if (searchInput) {
        searchInput.addEventListener("keydown", function (e) {
            if (e.key === "Enter") {
                e.preventDefault();
                searchTable();
            }
        });
    }
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

    if (vendorIndex === -1) return;

    const rows = table.querySelectorAll("tbody tr");
    rows.forEach(row => {
        const cells = row.querySelectorAll("td");
        const vendorCell = cells[vendorIndex]?.textContent.trim().toLowerCase();
        row.style.display = vendorCell.includes(input) ? "" : "none";
    });
}

function calculateAverage() {
    let sum = 0;
    let count = 0;
    for (let i = 1; i <= 10; i++) {
        const val = parseFloat(document.getElementById(`hardness${i}`).value);
        if (!isNaN(val)) {
            sum += val;
            count++;
        }
    }
    const avg = count ? (sum / count).toFixed(5) : "";
    document.getElementById("averageHardness").value = avg;
}
