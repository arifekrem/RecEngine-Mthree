const dashboardData = {
    totalTransactions: 120,
    matches: 105,
    mismatches: 15,
    pending: 8
};

const results = [
    { transactionId: 1, status: "Match", issue: "None" },
    { transactionId: 2, status: "AmountMismatch", issue: "Bank amount is different" },
    { transactionId: 3, status: "MissingDownstream", issue: "Missing bank record" },
    { transactionId: 4, status: "StatusMismatch", issue: "Processor success but bank failed" }
];

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


results.forEach(result => {
    const row = document.createElement("tr");

    row.innerHTML = `
        <td>${result.transactionId}</td>
        <td>
            <span class="status ${getStatusClass(result.status)}">
        ${result.status}
            </span>
        </td>
        <td>${result.issue}</td>
    `;

    tableBody.appendChild(row);
});

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