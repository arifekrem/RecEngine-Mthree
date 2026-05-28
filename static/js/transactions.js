let transactions = [
    {
        transaction_id: 1,
        customer_id: 101,
        business_id: 501,
        amount: 120.50,
        received_at: "2026-05-27 10:30"
    },
    {
        transaction_id: 2,
        customer_id: 102,
        business_id: 502,
        amount: 75.25,
        received_at: "2026-05-27 11:00"
    }
];

const tableBody = document.getElementById("transactionsTable");
const form = document.getElementById("transactionForm");
const searchInput = document.getElementById("searchInput");

function loadTransactions() {
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
                <button class="edit-btn" onclick="editTransaction(${transaction.transaction_id})">Edit</button>
                <button class="delete-btn" onclick="deleteTransaction(${transaction.transaction_id})">Delete</button>
            </td>
        `;

        tableBody.appendChild(row);
    });
}

searchInput.addEventListener("input", loadTransactions);

form.addEventListener("submit", function(event) {
    event.preventDefault();

    const newTransaction = {
        transaction_id: transactions.length + 1,
        customer_id: document.getElementById("customerId").value,
        business_id: document.getElementById("businessId").value,
        amount: document.getElementById("amount").value,
        received_at: document.getElementById("receivedAt").value
    };

    transactions.push(newTransaction);
    form.reset();
    loadTransactions();
});

function deleteTransaction(id) {
    const confirmed = confirm("Are you sure you want to delete this transaction?");

    if (!confirmed) {
        return;
    }

    transactions = transactions.filter(
        transaction => transaction.transaction_id !== id
    );

    loadTransactions();
}

function editTransaction(id) {
    const transaction = transactions.find(
        transaction => transaction.transaction_id === id
    );

    document.getElementById("customerId").value = transaction.customer_id;
    document.getElementById("businessId").value = transaction.business_id;
    document.getElementById("amount").value = transaction.amount;
    document.getElementById("receivedAt").value = transaction.received_at;

    transactions = transactions.filter(
        transaction => transaction.transaction_id !== id
    );

    loadTransactions();
}

loadTransactions();