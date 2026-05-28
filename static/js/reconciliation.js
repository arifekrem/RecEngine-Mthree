const reconciliationResults = [
    {
        transaction_id: 1,
        status: "Match",
        description: "Transaction matched across all systems",
        date: "2026-05-27"
    },
    {
        transaction_id: 2,
        status: "AmountMismatch",
        description: "Bank amount does not match original transaction",
        date: "2026-05-27"
    },
    {
        transaction_id: 3,
        status: "MissingDownstream",
        description: "Transaction is missing from bank records",
        date: "2026-05-28"
    },
    {
        transaction_id: 4,
        status: "StatusMismatch",
        description: "Processor success but bank failed",
        date: "2026-05-28"
    }
];

const runBtn = document.getElementById("runBtn");
const table = document.getElementById("reconciliationTable");
const emptyMessage = document.getElementById("emptyMessage");

runBtn.addEventListener("click", function() {
    displayResults(reconciliationResults);
});

function displayResults(results) {
    table.innerHTML = "";
    emptyMessage.innerText = "";

    if (results.length === 0) {
        emptyMessage.innerText =
            "No mismatches found. All systems reconciled successfully.";
        return;
    }

    results.forEach(result => {
        const row = document.createElement("tr");

        row.innerHTML = `
            <td>${result.transaction_id}</td>
            <td>
                <span class="status ${getStatusClass(result.status)}">
                    ${result.status}
                </span>
            </td>
            <td>${result.description}</td>
        `;

        table.appendChild(row);
    });
}

function filterResults(type) {
    if (type === "All") {
        displayResults(reconciliationResults);
        return;
    }

    if (type === "Mismatch") {
        const mismatches = reconciliationResults.filter(
            result => result.status !== "Match"
        );

        displayResults(mismatches);
        return;
    }

    const filtered = reconciliationResults.filter(
        result => result.status === type
    );

    displayResults(filtered);
}

function applyDateFilter() {
    const selectedDate = document.getElementById("dateFilter").value;

    const filtered = reconciliationResults.filter(
        result => result.date === selectedDate
    );

    displayResults(filtered);
}

function getStatusClass(status) {
    if (status === "Match") return "match";
    if (status === "AmountMismatch") return "amount";
    if (status === "MissingDownstream") return "missing";
    return "failed";
}