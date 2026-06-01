let transactionChart;

async function loadDashboard() {
    const response = await fetch("/api/reconciliation_results");
    const results = await response.json();

    const totalTransactions = results.length;
    const matches = results.filter(r => r.status === "Match").length;
    const mismatches = results.filter(r => r.status !== "Match").length;

    document.getElementById("totalTransactions").innerText = totalTransactions;
    document.getElementById("matches").innerText = matches;
    document.getElementById("mismatches").innerText = mismatches;

    const tableBody = document.getElementById("resultsTable");
    tableBody.innerHTML = "";

    const recentResults = [...results].sort((a, b) => b.result_id - a.result_id).slice(0, 5);
    recentResults.forEach(result => {
        const row = document.createElement("tr");

        row.innerHTML = `
            <td>${result.transaction_id}</td>
            <td>
                <span class="status ${getStatusClass(result.status)}">
                    ${result.status}
                </span>
            </td>
            <td>${getDescription(result.status)}</td>
        `;

        tableBody.appendChild(row);
    });

    updateChart(matches, mismatches);
}

function updateChart(matches, mismatches) {
    const ctx = document.getElementById("transactionChart");

    if (transactionChart) {
        transactionChart.destroy();
    }

    transactionChart = new Chart(ctx, {
        type: "doughnut",
        data: {
            labels: ["Matches", "Mismatches"],
            datasets: [{
                data: [matches, mismatches],
                backgroundColor: ["#16a34a", "#dc2626"]
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true
        }
    });
}

function getStatusClass(status) {
    if (status === "Match") return "match";
    if (status === "AmountMismatch") return "amount";
    if (status === "MissingDownstream") return "missing";
    return "failed";
}

function getDescription(status) {
    if (status === "Match") return "Transaction matched across all systems";
    if (status === "AmountMismatch") return "Bank amount does not match original transaction";
    if (status === "MissingDownstream") return "Transaction is missing from one downstream table";
    if (status === "StatusMismatch") return "Processor, card network, and bank statuses do not match";
    if (status === "OrderMismatch") return "Transaction timestamps are not in the correct order";
    return "Unknown issue";
}

loadDashboard();
