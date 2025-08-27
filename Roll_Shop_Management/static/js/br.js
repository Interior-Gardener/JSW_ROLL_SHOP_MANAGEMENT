function searchTable() {
        const input = document.getElementById("searchInput").value.trim().toLowerCase();
        const table = document.querySelector(".table");
        const rows = table.querySelectorAll("tbody tr");

        // Find the index of "Vendor no" column (case-insensitive match)
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

        // Filter rows based on vendor no match
        rows.forEach(row => {
            const cells = row.querySelectorAll("td");
            const vendorCell = cells[vendorIndex]?.textContent.trim().toLowerCase();
            if (vendorCell && vendorCell.includes(input)) {
                row.style.display = "";
            } else {
                row.style.display = "none";
            }
        });
    }

    // Optional: allow pressing "Enter" to trigger search
    document.getElementById("searchInput").addEventListener("keydown", function(e) {
        if (e.key === "Enter") {
            searchTable();
        }
    });