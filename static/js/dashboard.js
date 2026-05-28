const dashboardData = {
    totalTransactions: 120,
    matches: 105,
    mismatches: 15,
    pending: 8
};

document.getElementById("totalTransactions").innerText = dashboardData.totalTransactions;
document.getElementById("matches").innerText = dashboardData.matches;
document.getElementById("mismatches").innerText = dashboardData.mismatches;
document.getElementById("pending").innerText = dashboardData.pending;

const tableBody = document.getElementById("resultsTable");

function getStatusClass(status) {

    if(status === "Match") {
        return "match";
    }

    if(status === "AmountMismatch") {
        return "amount";
    }

    if(status === "MissingDownstream") {
        return "missing";
    }

    return "failed";
}


async function loadResults() {
    const response = await fetch("/api/display_recent_reconciliation_results");
    const results = await response.json();
    // Recent reconciliation results should empty previus reconciliation results
    tableBody.innerHTML = "";
    results.forEach(result => {
        const row = document.createElement("tr");

        row.innerHTML = `
            <td>${result.transaction_id}</td>
            <td>
                <span class="status ${getStatusClass(result.status)}">
            ${result.status}
                </span>
            </td>
            <td>${result.issue}</td>
        `;

        tableBody.appendChild(row);
    });   
}

loadResults();

const ctx = document.getElementById('transactionChart');

new Chart(ctx, {
    type: 'doughnut',

    data: {
        labels: ['Matches', 'Mismatches', 'Pending'],
        datasets: [{
            data: [105, 15, 8],
            backgroundColor: [
                '#16a34a',
                '#dc2626',
                '#f59e0b'
            ]
        }]
    },

    options: {
        responsive: true,
        maintainAspectRatio: true
    }
});