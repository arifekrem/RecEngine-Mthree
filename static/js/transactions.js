let transactions = [];
let editingTransactionId = null;

const tableBody = document.getElementById("transactionsTable");

const singleTransactionForm = document.getElementById("singleTransactionForm");
const BatchTransactionForm = document.getElementById("BatchTransactionForm");

const searchInput = document.getElementById("searchInput");

const singleTxSubmitButton = document.getElementById("singleTxSubmitButton");
const batchTxSubmitButton = document.getElementById("batchTxSubmitButton");

const txButtons = document.querySelectorAll(".txSelectionButton");

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

async function loadTransactions() {
    const response = await fetch("/api/display_transactions");
    transactions = await response.json();

    renderTransactions();
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

    singleTxSubmitButton.innerText = "Update Transaction";
}

async function deleteTransaction(id) {
    const confirmed = confirm("Are you sure you want to delete this transaction?");

    if (!confirmed) return;

    await fetch(`/delete_transaction/${id}`, {
        method: "DELETE"
    });

    loadTransactions();
}

searchInput.addEventListener("input", renderTransactions);

singleTransactionForm.addEventListener("submit", async function(event) {
    event.preventDefault();

    const transactionData = {
        customer_id: document.getElementById("customerId").value,
        business_id: document.getElementById("businessId").value,
        amount: document.getElementById("amount").value,
        received_at: document.getElementById("receivedAt").value
    };

    if (editingTransactionId) {
        const response = await fetch(`/update_transaction/${editingTransactionId}`, {
            method: "PUT",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(transactionData)
        });

        const data = await response.json();
        alert(data.message);

        editingTransactionId = null;
        singleTxSubmitButton.innerText = "Add Transaction";
    } else {
        const response = await fetch("/add_transaction", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(transactionData)
        });

        const data = await response.json();
        if (!response.ok) {
            const stage = data.failed_stage ? `\nStage: ${data.failed_stage}` : "";
            alert(`${data.error || data.message}${stage}`);
        } else {
            const stageSummary = data.stages
                ? Object.keys(data.stages).join(" → ")
                : "";
            console.log("Pipeline stages:", data.stages);
            alert(`${data.message}\nStages: ${stageSummary}`);
        }
    }

    singleTransactionForm.reset();
    loadTransactions();
});

loadTransactions();
