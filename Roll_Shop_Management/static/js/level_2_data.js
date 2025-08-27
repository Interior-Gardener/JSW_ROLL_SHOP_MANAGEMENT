function searchTable() {
    const input = document.getElementById("searchInput").value.trim().toLowerCase();
    const table = document.querySelector("table");
    if (!table) return;

    const headers = table.querySelectorAll("thead th");
    let vendorIndex = -1;
    headers.forEach((th, i) => {
        if (th.textContent.trim().toLowerCase() === "vendor no" || th.textContent.trim().toLowerCase() === "vendor_no") {
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

// ✅ Trigger search on Enter key
document.addEventListener("DOMContentLoaded", () => {
    const input = document.getElementById("searchInput");
    if (input) {
        input.addEventListener("keydown", (e) => {
            if (e.key === "Enter") {
                e.preventDefault();  // prevent form submission if any
                searchTable();
            }
        });
    }
});