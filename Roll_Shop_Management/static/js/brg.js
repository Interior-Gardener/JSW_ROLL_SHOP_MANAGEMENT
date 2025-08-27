// FULL UPDATED brg.js
document.addEventListener("DOMContentLoaded", () => {
    let currentSearchMode = null;

    const bearingDeassembleBtn = document.getElementById("bearingDeassembleBtn");
    const bearingAssembleBtn = document.getElementById("bearingAssembleBtn");
    const deassembleChockBtn = document.getElementById("deassembleChockBtn");
    const viewServiceBearingsBtn = document.getElementById("viewServiceBearingsBtn");
    const putInServiceBtn = document.getElementById("putInServiceBtn");

    const submitChockBtn = document.getElementById("submitChockBtn");
    const submitBrgBtn = document.getElementById("submitBrgBtn");
    const submitServiceBtn = document.getElementById("submitServiceBtn");

    const chockSection = document.getElementById("chockSection");
    const brgSection = document.getElementById("brgSection");
    const serviceBrgSection = document.getElementById("serviceBrgSection");

    const container = document.querySelector(".container");
    const assembleSection = document.createElement("div");
    assembleSection.id = "assembleSection";
    assembleSection.style.display = "none";
    assembleSection.innerHTML = `
        <h2 style="margin-top: 30px;">CHOCK ASSEMBLE</h2>
        <div class="chock-search-wrapper" style="margin-bottom: 10px;">
            <input type="text" class="chock-search-input" id="searchChock" placeholder="Search CHOCK..." />
            <button type="button" class="chock-search-btn" id="searchChockBtn">Search</button>
        </div>

        <div id="assembleChockTable" style="max-height: 400px; overflow-y: auto; overflow-x: auto; margin-top: 20px; border: 1px solid #ccc; border-radius: 8px;"></div>


        <h2 style="margin-top: 30px;">BEARING ASSEMBLE</h2>
        <div class="brg-search-wrapper" style="margin-bottom: 10px;">
            <input type="text" class="brg-search-input" id="searchBearing" placeholder="Search BEARING..." />
            <button type="button" class="brg-search-btn" id="searchBearingBtn">Search</button>
        </div>

        <div id="assembleBrgTable" style="max-height: 400px; overflow-y: auto; overflow-x: auto; margin-top: 20px; border: 1px solid #ccc; border-radius: 8px;;"></div>
        <button class= "btnkaltu" id="submitAssembleBtn" disabled style="display: none; margin-top: 20px;">Assemble CHOCK & BRG</button>
    `;

    container.appendChild(assembleSection);

    assembleSection.querySelector("#submitAssembleBtn").addEventListener("click", submitAssembly);

    bearingDeassembleBtn?.addEventListener("click", () => { });
    // deassembleChockBtn?.addEventListener("click", () => showSection("CHOCK"));
    bearingAssembleBtn?.addEventListener("click", () => showAssembleSection());

    // viewServiceBearingsBtn?.addEventListener("click", () => {
    //     showSection("SERVICE");
    //     fetchServiceBrgs("SERVICE");
    // });

    // putInServiceBtn?.addEventListener("click", () => {
    //     showSection("FREE");
    //     fetchServiceBrgs("FREE");
    // });
    deassembleChockBtn?.addEventListener("click", () => {
        currentSearchMode = "CHOCK";
        clearSearchFilter();
        searchContainer.style.display = "flex";

        // Show only chockSection and hide others
        chockSection.style.display = "block";
        brgSection.style.display = "none";           // hide bearing table
        serviceBrgSection.style.display = "none";    // hide service bearing table
        assembleSection.style.display = "none";      // ADD THIS LINE TO HIDE ASSEMBLE SECTION

        fetchChockData();
    });





    putInServiceBtn?.addEventListener("click", () => {
        currentSearchMode = "BRG";
        clearSearchFilter();
        searchContainer.style.display = "flex";
        showSection("FREE");
        fetchServiceBrgs("FREE");
    });

    viewServiceBearingsBtn?.addEventListener("click", () => {
        currentSearchMode = "BRG";
        clearSearchFilter();
        searchContainer.style.display = "flex";
        showSection("SERVICE");
        fetchServiceBrgs("SERVICE");
    });


    submitChockBtn?.addEventListener("click", submitChockSelection);
    submitBrgBtn?.addEventListener("click", submitBrgSelection);
    submitServiceBtn?.addEventListener("click", () => {
        const selected = document.querySelector('input[name="service_brg_select"]:checked');
        if (!selected) return alert("Select a BRG");

        const currentStatus = submitServiceBtn.dataset.statusType;
        // Toggle status
        const targetStatus = currentStatus === "SERVICE" ? "FREE" : "SERVICE";

        fetch("/brg/update_brg_status", {  // assuming you update backend for dynamic status update
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ brg_no: selected.value, target_status: targetStatus }),
        })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    alert("Updated successfully");
                    fetchServiceBrgs(currentStatus);  // Refresh old status list
                } else {
                    alert(data.error || "Failed");
                }
            })
            .catch(() => alert("Server error"));
    });

    function showSection(type) {
        chockSection.style.display = "none";
        brgSection.style.display = "none";
        assembleSection.style.display = "none";
        serviceBrgSection.style.display = "none";

        if (type === "CHOCK") {
            chockSection.style.display = "block";
            fetchChockData();
        } else if (type === "BRG") {
            brgSection.style.display = "block";
            fetchBrgData();
        } else if (type === "SERVICE" || type === "FREE") {
            serviceBrgSection.style.display = "block";
        }
    }

    function showAssembleSection() {
        showSection("");
        assembleSection.style.display = "block";
        fetchAssembleData();
    }

    function fetchChockData() {
        console.log("Fetching CHOCK data...");
        fetch("/brg/get_chock_data")
            .then(r => r.json())
            .then(data => {
                console.log("CHOCK data received:", data);
                renderTable(data, "tableDisplayChock", "CHOCK");
            })
            .catch(e => console.error("Error fetching CHOCK data:", e));
    }


    function fetchBrgData() {
        fetch("/brg/get_brg_data")
            .then(r => r.json())
            .then(data => renderTable(data, "tableDisplayBrg", "BRG"));
    }

    function fetchServiceBrgs(type = "SERVICE") {
        const url = type === "FREE" ? "/brg/get_free_brg" : "/brg/get_service_brg";

        fetch(url)
            .then(r => r.json())
            .then(data => {
                const container = document.getElementById("serviceBrgTable");
                const label = type === "SERVICE" ? "Mark as FREE" : "Put in SERVICE";

                if (!data.length) {
                    container.innerHTML = `<p>No bearings with status "${type}"</p>`;
                    submitServiceBtn.style.display = "none";
                    return;
                }

                let html = `<h2>${type} BEARINGS</h2><table border="1"><thead><tr><th>Select</th>`;
                Object.keys(data[0]).forEach(k => html += `<th>${k}</th>`);
                html += "</tr></thead><tbody>";

                data.forEach(r => {
                    html += `<tr><td><input type="radio" name="service_brg_select" value="${r.BRG_NO}"></td>`;
                    Object.values(r).forEach(v => html += `<td>${v ?? ''}</td>`);
                    html += `</tr>`;
                });

                html += `</tbody></table>`;
                container.innerHTML = html;

                submitServiceBtn.textContent = label;
                submitServiceBtn.style.display = "none";
                submitServiceBtn.disabled = true;
                submitServiceBtn.dataset.statusType = type;

                container.querySelectorAll('input[name="service_brg_select"]').forEach(radio => {
                    radio.addEventListener("change", () => {
                        submitServiceBtn.style.display = "inline-block";
                        submitServiceBtn.disabled = false;
                    });
                });
            });
    }

    function renderTable(data, id, title) {
        const container = document.getElementById(id);
        if (!data || !data.length) {
            container.innerHTML = `<p>No ${title} data</p>`;
            return;
        }

        let html = `<h2>${title} TABLE</h2><table border="1"><thead><tr><th>Select</th>`;
        Object.keys(data[0]).forEach(k => html += `<th>${k}</th>`);
        html += `</tr></thead><tbody>`;

        data.forEach(r => {
            const radioName = title.toLowerCase() + "_select";
            const idVal = r[title === "CHOCK" ? "CHOCK_NO" : "BRG_NO"];
            html += `<tr><td><input type="radio" name="${radioName}" value="${idVal}"></td>`;
            Object.values(r).forEach(v => html += `<td>${v ?? ""}</td>`);
            html += "</tr>";
        });

        html += "</tbody></table>";
        container.innerHTML = html;

        const btn = document.getElementById(title === "CHOCK" ? "submitChockBtn" : "submitBrgBtn");
        btn.disabled = true;
        btn.style.display = "none";

        container.querySelectorAll(`input[name="${title.toLowerCase()}_select"]`).forEach(r => {
            r.addEventListener("change", () => {
                btn.disabled = false;
                btn.style.display = "inline-block";
            });
        });
    }

    function submitChockSelection() {
        const selected = document.querySelector('input[name="chock_select"]:checked');
        if (!selected) return alert("Please select a CHOCK");
        fetch("/brg/update_chock", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ id: selected.value }),
        })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    alert("CHOCK update successful");
                    fetchChockData();
                    fetchBrgData();
                } else alert(data.error);
            });
    }

    function submitBrgSelection() {
        const selected = document.querySelector('input[name="brg_select"]:checked');
        if (!selected) return alert("Please select a BRG");
        fetch("/brg/update_brg", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ id: selected.value }),
        })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    alert("BRG update successful");
                    fetchBrgData();
                } else alert(data.error);
            });
    }

    function fetchAssembleData() {
        fetch("/brg/get_assemble_data")
            .then(r => r.json())
            .then(data => renderAssembleTables(data.chock, data.brg));
    }

    function renderAssembleTables(chockData, brgData) {
        const chock = document.getElementById("assembleChockTable");
        const brg = document.getElementById("assembleBrgTable");
        const submit = document.getElementById("submitAssembleBtn");

        chock.innerHTML = generateTable(chockData, "assemble_chock_select", ["CHOCK_NO", "POSITION", "SIDE"]);
        brg.innerHTML = generateTable(brgData, "assemble_brg_select", ["BRG_NO", "BRG_TYPE", "KM"]);

        submit.disabled = true;
        submit.style.display = "none";

        document.querySelectorAll('input[name="assemble_chock_select"]').forEach(r => r.addEventListener("change", check));
        document.querySelectorAll('input[name="assemble_brg_select"]').forEach(r => r.addEventListener("change", check));

        function check() {
            const chSel = document.querySelector('input[name="assemble_chock_select"]:checked');
            const brSel = document.querySelector('input[name="assemble_brg_select"]:checked');
            if (chSel && brSel) {
                submit.disabled = false;
                submit.style.display = "inline-block";
            }
        }
    }

    function generateTable(data, name, cols) {
        if (!data.length) return "<p>No data</p>";
        let html = "<table border='1'><thead><tr><th>Select</th>";
        cols.forEach(c => html += `<th>${c}</th>`);
        html += "</tr></thead><tbody>";
        data.forEach(r => {
            html += `<tr><td><input type="radio" name="${name}" value="${r[cols[0]]}"></td>`;
            cols.forEach(c => html += `<td>${r[c] ?? ""}</td>`);
            html += "</tr>";
        });
        html += "</tbody></table>";
        return html;
    }

    function submitAssembly() {
        const chock = document.querySelector('input[name="assemble_chock_select"]:checked');
        const brg = document.querySelector('input[name="assemble_brg_select"]:checked');
        if (!chock || !brg) return alert("Select CHOCK and BRG");
        fetch("/brg/submit_assembly", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ chock_no: chock.value, brg_no: brg.value }),
        })
            .then(r => r.json())
            .then(data => {
                if (data.success) {
                    alert("Assembled!");
                    fetchAssembleData();
                } else alert(data.error || "Failed");
            });
    }

    function searchTable() {
        const input = document.getElementById("searchBar").value.trim().toLowerCase();
        if (!input) return;

        const chockVisible = document.getElementById("chockSection")?.style.display === "block";
        const brgVisible = document.getElementById("brgSection")?.style.display === "block";
        const serviceVisible = document.getElementById("serviceBrgSection")?.style.display === "block";

        if (chockVisible) {
            // Deassemble (CHOCK/BEARING) table (which has BRG_NO and CHOCK_NO columns)
            const container = document.getElementById("tableDisplayChock");
            if (!container) return;

            const table = container.querySelector("table");
            if (!table) return;

            const headers = table.querySelectorAll("thead th");
            let chockNoIndex = -1;
            let brgNoIndex = -1;

            // Find indexes of CHOCK_NO and BRG_NO columns dynamically
            headers.forEach((th, i) => {
                const headerText = th.textContent.trim().toLowerCase();
                if (headerText === "chock_no") chockNoIndex = i;
                else if (headerText === "brg_no") brgNoIndex = i;
            });

            if (chockNoIndex === -1 && brgNoIndex === -1) return; // no relevant columns

            const rows = table.querySelectorAll("tbody tr");

            rows.forEach(row => {
                const cells = row.querySelectorAll("td");
                const chockText = chockNoIndex !== -1 ? (cells[chockNoIndex]?.textContent.trim().toLowerCase() || "") : "";
                const brgText = brgNoIndex !== -1 ? (cells[brgNoIndex]?.textContent.trim().toLowerCase() || "") : "";

                // Show row if input matches either CHOCK_NO or BRG_NO
                const match = chockText.includes(input) || brgText.includes(input);
                row.style.display = match ? "" : "none";
            });

        } else if (brgVisible) {
            // BRG section: search only BRG_NO column
            filterTable("tableDisplayBrg", "BRG_NO");
        } else if (serviceVisible) {
            // Service section: search only BRG_NO column
            filterTable("serviceBrgTable", "BRG_NO");
        }

        // Utility function to filter single column table
        function filterTable(containerId, columnName) {
            const container = document.getElementById(containerId);
            if (!container) return;

            const table = container.querySelector("table");
            if (!table) return;

            const headers = table.querySelectorAll("thead th");
            let colIndex = -1;

            headers.forEach((th, i) => {
                if (th.textContent.trim().toLowerCase() === columnName.toLowerCase()) {
                    colIndex = i;
                }
            });

            if (colIndex === -1) return;

            const rows = table.querySelectorAll("tbody tr");
            rows.forEach(row => {
                const cells = row.querySelectorAll("td");
                const cellText = cells[colIndex]?.textContent.trim().toLowerCase();
                row.style.display = (cellText && cellText.includes(input)) ? "" : "none";
            });
        }
    }



    function clearSearchFilter() {
        const searchInput = document.getElementById("searchBar");
        searchInput.value = "";

        let tableContainerId = "";

        if (currentSearchMode === "CHOCK") {
            tableContainerId = "tableDisplayChock";
        } else if (currentSearchMode === "BRG") {
            if (serviceBrgSection.style.display === "block") {
                tableContainerId = "serviceBrgTable";
            } else if (brgSection.style.display === "block") {
                tableContainerId = "tableDisplayBrg";
            } else {
                tableContainerId = "serviceBrgTable";
            }
        } else {
            return;
        }

        const container = document.getElementById(tableContainerId);
        if (!container) return;

        const table = container.querySelector("table");
        if (!table) return;

        const rows = table.querySelectorAll("tbody tr");
        rows.forEach(row => {
            row.style.display = "";
        });
    }
    document.getElementById("searchBtn").addEventListener("click", searchTable);
    document.getElementById("searchBar").addEventListener("keydown", function (e) {
        if (e.key === "Enter") searchTable();
    });

    document.getElementById("searchChockBtn").addEventListener("click", () => {
        const input = document.getElementById("searchChock").value.trim().toLowerCase();
        if (!input) return;

        const container = document.getElementById("assembleChockTable");
        const table = container.querySelector("table");
        if (!table) return;

        const chockNoIndex = [...table.querySelectorAll("thead th")].findIndex(th => th.textContent.trim().toLowerCase() === "chock_no");
        if (chockNoIndex === -1) return;

        table.querySelectorAll("tbody tr").forEach(row => {
            const cellText = row.querySelectorAll("td")[chockNoIndex]?.textContent.trim().toLowerCase() || "";
            row.style.display = cellText.includes(input) ? "" : "none";
        });
    });

    document.getElementById("searchBearingBtn").addEventListener("click", () => {
        const input = document.getElementById("searchBearing").value.trim().toLowerCase();
        if (!input) return;

        const container = document.getElementById("assembleBrgTable");
        const table = container.querySelector("table");
        if (!table) return;

        const brgNoIndex = [...table.querySelectorAll("thead th")].findIndex(th => th.textContent.trim().toLowerCase() === "brg_no");
        if (brgNoIndex === -1) return;

        table.querySelectorAll("tbody tr").forEach(row => {
            const cellText = row.querySelectorAll("td")[brgNoIndex]?.textContent.trim().toLowerCase() || "";
            row.style.display = cellText.includes(input) ? "" : "none";
        });
    });
    document.getElementById("searchChock").addEventListener("keydown", (e) => {
        if (e.key === "Enter") document.getElementById("searchChockBtn").click();
    });

    document.getElementById("searchBearing").addEventListener("keydown", (e) => {
        if (e.key === "Enter") document.getElementById("searchBearingBtn").click();
    });


});

const searchContainer = document.getElementById("searchContainer");

// Hide on BEARING ASSEMBLE click
document.getElementById("bearingAssembleBtn").addEventListener("click", () => {
    searchContainer.style.display = "none";
});

// Show on FREE FROM SERVICE BEARINGS click
document.getElementById("viewServiceBearingsBtn").addEventListener("click", () => {
    searchContainer.style.display = "flex";  // or "block" depending on your CSS
});

// Show on BEARING DEASSEMBLE click (optional)
document.getElementById("bearingDeassembleBtn").addEventListener("click", () => {
    searchContainer.style.display = "flex";  // or "block"
});

document.getElementById("putInServiceBtn").addEventListener("click", () => {
    searchContainer.style.display = "flex";  // or "block"
});

document.getElementById("deassembleChockBtn").addEventListener("click", () => {
    searchContainer.style.display = "flex";  // or "block"
});


