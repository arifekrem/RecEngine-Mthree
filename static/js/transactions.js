let transactions = [];
let editingTransactionId = null;
let selectedTransactionId = null;

const tableBody = document.getElementById("transactionsTable");

const singleTransactionForm = document.getElementById("singleTransactionForm");
const BatchTransactionForm = document.getElementById("BatchTransactionForm");

const searchInput = document.getElementById("searchInput");

const singleTxSubmitButton = document.getElementById("singleTxSubmitButton");
const batchTxSubmitButton = document.getElementById("batchTxSubmitButton");

const txButtons = document.querySelectorAll(".txSelectionButton");

const formStatus = document.getElementById("formStatus");
const pipelineInspectLabel = document.getElementById("pipelineInspectLabel");
const flowSteps = [
    document.getElementById("flowStep1"),
    document.getElementById("flowStep2"),
    document.getElementById("flowStep3"),
    document.getElementById("flowStep4"),
];

const FLOW_STATE_CLASS = {
    inactive: "flow-step--inactive",
    success: "flow-step--success",
    error: "flow-step--error",
};

txButtons.forEach(btn => {
	btn.addEventListener('click', () => {
		
		tabs = document.querySelectorAll(".transactionOption")
		tabs.forEach(tab => {tab.classList.add("hidden")})
		
		currentTab = document.getElementById(btn.dataset.target)
		currentTab.classList.remove("hidden")
		
	})
	
});

async function addTransactionBatch(event){
    event.preventDefault();

    const simulationData = {
        total_records: Number(document.getElementById("total_records").value),
        chaos_ratio: Number(document.getElementById("chaos_ratio").value),
    };


    const res = await fetch("/add_transaction_batch", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(simulationData)
    });

    const data = await res.json();
    console.log(data);
    if (res.ok) {
        BatchTransactionForm.reset();
        loadTransactions();
    }
}

BatchTransactionForm.addEventListener('submit', addTransactionBatch)

function setFormStatus(message, isError = false) {
    if (!formStatus) return;
    formStatus.textContent = message;
    formStatus.className = isError ? "form-status error" : "form-status success";
}

function setPipelineLabel(message) {
    if (pipelineInspectLabel) {
        pipelineInspectLabel.textContent = message;
    }
}

function resetFlowSteps() {
    flowSteps.forEach((step) => {
        if (step) {
            step.className = `flow-step ${FLOW_STATE_CLASS.inactive}`;
        }
    });
    setPipelineLabel("Select a transaction from the table to inspect its pipeline.");
}

function amountsMatch(transactionAmount, bankAmount) {
    return Number(transactionAmount).toFixed(4) === Number(bankAmount).toFixed(4);
}

function computeFlowStepStates(pipeline) {
    const states = ["inactive", "inactive", "inactive", "inactive"];

    if (!pipeline?.found || !pipeline.transaction) {
        return states;
    }

    states[0] = "success";

    const processor = pipeline.processor_records?.[0];
    if (!processor) {
        return states;
    }

    if (processor.status !== "Success") {
        return states;
    }
    states[1] = "success";

    const network = pipeline.card_network_records?.[0];
    if (!network) {
        return states;
    }

    if (network.status === "Success") {
        states[2] = "success";
    } else if (network.status === "Failed") {
        states[2] = "error";
    } else {
        return states;
    }

    const bank = pipeline.bank_transaction_records?.[0];
    if (!bank) {
        return states;
    }

    if (amountsMatch(pipeline.transaction.amount, bank.amount)) {
        states[3] = "success";
    } else {
        states[3] = "error";
    }

    return states;
}

function applyFlowStepStates(states) {
    flowSteps.forEach((step, index) => {
        if (!step) return;
        const state = states[index] || "inactive";
        step.className = `flow-step ${FLOW_STATE_CLASS[state]}`;
    });
}

function highlightSelectedRow(transactionId) {
    document.querySelectorAll("#transactionsTable tr").forEach((row) => {
        row.classList.toggle(
            "row-selected",
            Number(row.dataset.transactionId) === Number(transactionId)
        );
    });
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

async function inspectTransaction(transactionId) {
    selectedTransactionId = transactionId;
    highlightSelectedRow(transactionId);
    setPipelineLabel(`Inspecting transaction #${transactionId}...`);

    try {
        const response = await fetch(`/transaction_pipeline/${transactionId}`);
        const pipeline = await parseJsonResponse(response);

        if (!response.ok || !pipeline.found) {
            resetFlowSteps();
            setPipelineLabel(
                pipeline.error || `Could not load pipeline for transaction #${transactionId}.`,
            );
            return;
        }

        applyFlowStepStates(computeFlowStepStates(pipeline));
        setPipelineLabel(`Pipeline view for transaction #${transactionId}`);
    } catch (error) {
        resetFlowSteps();
        setPipelineLabel(error.message);
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

        if (selectedTransactionId) {
            highlightSelectedRow(selectedTransactionId);
        }
    } catch (error) {
        transactions = [];
        renderTransactions();
        setFormStatus(error.message, true);
    }
}

function renderTransactions() {
    tableBody.innerHTML = "";

    const searchValue = searchInput.value;

    const filteredTransactions = transactions.filter((transaction) =>
        transaction.transaction_id.toString().includes(searchValue)
    );

    filteredTransactions.forEach((transaction) => {
        const row = document.createElement("tr");
        row.dataset.transactionId = transaction.transaction_id;

        row.innerHTML = `
            <td>${transaction.transaction_id}</td>
            <td>${transaction.customer_id}</td>
            <td>${transaction.business_id}</td>
            <td>$${transaction.amount}</td>
            <td>${transaction.received_at}</td>
            <td>
                <button type="button" class="inspect-btn" data-action="inspect">
                    Inspect
                </button>
                <button type="button" class="edit-btn" data-action="edit">
                    Edit
                </button>
                <button type="button" class="delete-btn" data-action="delete">
                    Delete
                </button>
            </td>
        `;

        row.addEventListener("click", (event) => {
            if (event.target.closest("button")) return;
            inspectTransaction(transaction.transaction_id);
        });

        row.querySelector('[data-action="inspect"]').addEventListener("click", (event) => {
            event.stopPropagation();
            inspectTransaction(transaction.transaction_id);
        });

        row.querySelector('[data-action="edit"]').addEventListener("click", (event) => {
            event.stopPropagation();
            editTransaction(transaction.transaction_id);
        });

        row.querySelector('[data-action="delete"]').addEventListener("click", (event) => {
            event.stopPropagation();
            deleteTransaction(transaction.transaction_id);
        });

        tableBody.appendChild(row);
    });
}

function editTransaction(id) {
    const transaction = transactions.find((t) => t.transaction_id === id);

    if (!transaction) return;

    editingTransactionId = id;
    inspectTransaction(id);

    document.getElementById("customerId").value = transaction.customer_id;
    document.getElementById("businessId").value = transaction.business_id;
    document.getElementById("amount").value = transaction.amount;

    const date = new Date(transaction.received_at);
    const formattedDate = date.toISOString().slice(0, 16);
    document.getElementById("receivedAt").value = formattedDate;

    singleTxSubmitButton.innerText = "Update Transaction";
    setFormStatus("");
}

async function deleteTransaction(id) {
    const confirmed = confirm("Are you sure you want to delete this transaction?");

    if (!confirmed) return;

    try {
        const response = await fetch(`/delete_transaction/${id}`, {
            method: "DELETE",
        });
        const data = await parseJsonResponse(response);
        if (!response.ok) {
            setFormStatus(data.error || data.message || "Delete failed.", true);
            return;
        }

        if (Number(selectedTransactionId) === Number(id)) {
            selectedTransactionId = null;
            resetFlowSteps();
        }

        setFormStatus(data.message || "Transaction deleted.");
        await loadTransactions();
    } catch (error) {
        setFormStatus(error.message, true);
    }
}

searchInput.addEventListener("input", renderTransactions);

singleTransactionForm.addEventListener("submit", async function (event) {
    event.preventDefault();

    if (!form.reportValidity()) {
        setFormStatus("Please fill in all required fields, including date and time.", true);
        return;
    }

    const transactionData = {
        customer_id: document.getElementById("customerId").value.trim(),
        business_id: document.getElementById("businessId").value.trim(),
        amount: document.getElementById("amount").value.trim(),
        received_at: document.getElementById("receivedAt").value.trim(),
    };

    submitButton.disabled = true;
    setFormStatus("Saving transaction...");

    try {
        if (editingTransactionId) {
            const response = await fetch(`/update_transaction/${editingTransactionId}`, {
                method: "PUT",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(transactionData),
            });

            const data = await parseJsonResponse(response);
            if (!response.ok) {
                setFormStatus(data.error || data.message || "Update failed.", true);
                return;
            }

            setFormStatus(data.message || "Transaction updated.");
            const updatedId = editingTransactionId;
            editingTransactionId = null;
            submitButton.innerText = "Add Transaction";
            form.reset();
            await loadTransactions();
            await inspectTransaction(updatedId);
            return;
        }

        const response = await fetch("/add_transaction", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(transactionData),
        });

        const data = await parseJsonResponse(response);
        if (!response.ok) {
            const stage = data.failed_stage ? ` (stage: ${data.failed_stage})` : "";
            setFormStatus(`${data.error || data.message}${stage}`, true);
            return;
        }

        const stageSummary = data.stages ? Object.keys(data.stages).join(" → ") : "";
        setFormStatus(`${data.message}${stageSummary ? ` — ${stageSummary}` : ""}`);
        form.reset();
        await loadTransactions();
        if (data.transaction_id) {
            await inspectTransaction(data.transaction_id);
        }
    } catch (error) {
        setFormStatus(error.message, true);
    } finally {
        singleTxSubmitButton.disabled = false;
    }
});

resetFlowSteps();
loadTransactions();
