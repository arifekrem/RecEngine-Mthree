let reconciliationResults = [];

const MISMATCH_STATUSES = new Set([
    "MissingDownstream",
    "AmountMismatch",
    "StatusMismatch",
    "OrderMismatch",
]);

const runBtn = document.getElementById("runBtn");
const table = document.getElementById("reconciliationTable");
const emptyMessage = document.getElementById("emptyMessage");

runBtn.addEventListener("click", async function() {
    await fetch("/api/run_reconciliation");
    await loadReconciliationResults();
});

async function loadReconciliationResults() {
    const response = await fetch("/api/reconciliation_results");
    reconciliationResults = await response.json();

    displayResults(reconciliationResults);
}

function displayResults(results) {
    table.innerHTML = "";
    emptyMessage.innerText = "";

    if (!results || results.length === 0) {
        emptyMessage.innerText =
            "No reconciliation results yet. Run reconciliation after loading transactions.";
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
            <td>${getDescription(result.status)}</td>
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
        displayResults(
            reconciliationResults.filter(result => MISMATCH_STATUSES.has(result.status))
        );
        return;
    }

    displayResults(
        reconciliationResults.filter(result => result.status === type)
    );
}

function applyDateFilter() {
    alert("Date filter needs received_at in reconciliation_results first.");
}

function getStatusClass(status) {
    if (status === "Match") return "match";
    if (status === "Pending") return "pending";
    if (status === "AmountMismatch") return "amount";
    if (status === "MissingDownstream") return "missing";
    return "failed";
}

function getDescription(status) {
    if (status === "Match") return "Transaction matched across all systems";
    if (status === "Pending") {
        return "Transaction is in-flight; waiting on downstream pipeline stages";
    }
    if (status === "AmountMismatch") return "Bank amount does not match original transaction";
    if (status === "MissingDownstream") return "Transaction is missing from one downstream table";
    if (status === "StatusMismatch") return "Processor, card network, and bank statuses do not match";
    if (status === "OrderMismatch") return "Transaction timestamps are not in the correct order";

    return "Unknown reconciliation issue";
}

loadReconciliationResults();
