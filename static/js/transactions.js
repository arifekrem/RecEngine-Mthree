let transactions = [];
let editingTransactionId = null;

const tableBody = document.getElementById("transactionsTable");
const form = document.getElementById("transactionForm");
const searchInput = document.getElementById("searchInput");
const submitButton = document.getElementById("submitTransactionBtn");
const formStatus = document.getElementById("formStatus");

function setFormStatus(message, isError = false) {
    if (!formStatus) return;
    formStatus.textContent = message;
    formStatus.className = isError ? "form-status error" : "form-status success";
}

async function parseJsonResponse(response) {
    const text = await response.text();
    if (!text) {
        return {};
    }
    try {
        return JSON.parse(text);
    } catch {
        throw new Error(
            `Server returned non-JSON (HTTP ${response.status}). Is the flask container running?`
        );
    }
}

async function loadTransactions() {
    try {
        const response = await fetch("/api/display_transactions");
        const data = await parseJsonResponse(response);

        if (!response.ok || !Array.isArray(data)) {
            transactions = [];
            setFormStatus(
                data.error || "Could not load transactions from the server.",
                true
            );
        } else {
            transactions = data;
        }

        renderTransactions();
    } catch (error) {
        transactions = [];
        renderTransactions();
        setFormStatus(error.message, true);
    }
}

function renderTransactions() {
    tableBody.innerHTML = "";

    const searchValue = searchInput.value;

    const filteredTransactions = transactions.filter(transaction =>
        transaction.transaction_id.toString().includes(searchValue)
    );

    filteredTransactions.forEach(transaction => {
        const row = document.createElement("tr");

        row.innerHTML = `
            <td>${transaction.transaction_id}</td>
            <td>${transaction.customer_id}</td>
            <td>${transaction.business_id}</td>
            <td>$${transaction.amount}</td>
            <td>${transaction.received_at}</td>
            <td>
                <button class="edit-btn" onclick="editTransaction(${transaction.transaction_id})">
                    Edit
                </button>

                <button class="delete-btn" onclick="deleteTransaction(${transaction.transaction_id})">
                    Delete
                </button>
            </td>
        `;

        tableBody.appendChild(row);
    });
}

function editTransaction(id) {
    const transaction = transactions.find(t => t.transaction_id === id);

    if (!transaction) return;

    editingTransactionId = id;

    document.getElementById("customerId").value = transaction.customer_id;
    document.getElementById("businessId").value = transaction.business_id;
    document.getElementById("amount").value = transaction.amount;

    const date = new Date(transaction.received_at);
    const formattedDate = date.toISOString().slice(0, 16);
    document.getElementById("receivedAt").value = formattedDate;

    submitButton.innerText = "Update Transaction";
    setFormStatus("");
}

async function deleteTransaction(id) {
    const confirmed = confirm("Are you sure you want to delete this transaction?");

    if (!confirmed) return;

    try {
        const response = await fetch(`/delete_transaction/${id}`, {
            method: "DELETE"
        });
        const data = await parseJsonResponse(response);
        if (!response.ok) {
            setFormStatus(data.error || data.message || "Delete failed.", true);
            return;
        }
        setFormStatus(data.message || "Transaction deleted.");
        await loadTransactions();
    } catch (error) {
        setFormStatus(error.message, true);
    }
}

searchInput.addEventListener("input", renderTransactions);

form.addEventListener("submit", async function(event) {
    event.preventDefault();

    if (!form.reportValidity()) {
        setFormStatus("Please fill in all required fields, including date and time.", true);
        return;
    }

    const transactionData = {
        customer_id: document.getElementById("customerId").value.trim(),
        business_id: document.getElementById("businessId").value.trim(),
        amount: document.getElementById("amount").value.trim(),
        received_at: document.getElementById("receivedAt").value.trim()
    };

    submitButton.disabled = true;
    setFormStatus("Saving transaction...");

    try {
        if (editingTransactionId) {
            const response = await fetch(`/update_transaction/${editingTransactionId}`, {
                method: "PUT",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(transactionData)
            });

            const data = await parseJsonResponse(response);
            if (!response.ok) {
                setFormStatus(data.error || data.message || "Update failed.", true);
                return;
            }

            setFormStatus(data.message || "Transaction updated.");
            editingTransactionId = null;
            submitButton.innerText = "Add Transaction";
            form.reset();
            await loadTransactions();
            return;
        }

        const response = await fetch("/add_transaction", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(transactionData)
        });

        const data = await parseJsonResponse(response);
        if (!response.ok) {
            const stage = data.failed_stage ? ` (stage: ${data.failed_stage})` : "";
            setFormStatus(`${data.error || data.message}${stage}`, true);
            return;
        }

        const stageSummary = data.stages
            ? Object.keys(data.stages).join(" → ")
            : "";
        setFormStatus(
            `${data.message}${stageSummary ? ` — ${stageSummary}` : ""}`
        );
        form.reset();
        await loadTransactions();
    } catch (error) {
        setFormStatus(error.message, true);
    } finally {
        submitButton.disabled = false;
    }
});

loadTransactions();
