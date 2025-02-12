document.addEventListener('input', (event) => {
    const element = event.target;
    if (element.tagName === 'TD' && element.isContentEditable) {
        const columnIndex = element.cellIndex;
        if (columnIndex >= 3 && columnIndex <= 10) {
            validateNumber(element);
        }
        addNewRowIfNeeded(element);
        setTimeout(updateTotal, 700);
    }
});

document.addEventListener('DOMContentLoaded', () => {
    const dateElement = document.getElementById('date');
    const today = new Date().toISOString().split('T')[0];
    dateElement.value = today;

    const invoiceNumberElement = document.getElementById('invoice-number');
    if (invoiceNumberElement) {
        const approvedToggles = document.querySelectorAll('.approved-toggle');
        let hasApproved = false;
        approvedToggles.forEach(toggle => {
            if (toggle.checked) {
                hasApproved = true;
            }
        });
        if (hasApproved) {
            invoiceNumberElement.style.display = 'block';
        }
    }
});

function updateTotal() {
    const rows = document.querySelectorAll('tbody tr');
    rows.forEach(row => {
        const cells = row.querySelectorAll('td');
        const headLights = parseFloat(cells[3].innerText) || 0;
        const dents = parseFloat(cells[4].innerText) || 0;
        const chipsScratches = parseFloat(cells[5].innerText) || 0;
        const remediation = parseFloat(cells[6].innerText) || 0;
        const paintBody = parseFloat(cells[7].innerText) || 0;
        const parts = parseFloat(cells[8].innerText) || 0;
        const labor = parseFloat(cells[9].innerText) || 0;
        const total = headLights + dents + chipsScratches + remediation + paintBody + parts + labor;
        cells[10].innerText = total;
    });
}

function validateNumber(element) {
    const value = element.innerText;
    if (isNaN(value)) {
        element.innerText = value.slice(0, -1);
    }
}

function addNewRowIfNeeded(element) {
    const row = element.parentElement;
    const tbody = document.getElementById('invoice-items');
    const rows = tbody.querySelectorAll('tr');
    if (row === rows[rows.length - 1]) {
        const newRow = document.createElement('tr');
        for (let i = 0; i < 11; i++) {
            const newCell = document.createElement('td');
            if (i === 0) {
                const checkbox = document.createElement('input');
                checkbox.type = 'checkbox';
                checkbox.className = 'approved-toggle';
                newCell.appendChild(checkbox);
            } else {
                newCell.contentEditable = "true";
                if (i >= 3 && i <= 10) {
                    newCell.setAttribute('oninput', 'validateNumber(this)');
                }
            }
            newRow.appendChild(newCell);
        }
        tbody.appendChild(newRow);
    }
}

function toggleTheme(themeToggle) {
    const htmlElement = document.documentElement;
    if (themeToggle.checked) {
        htmlElement.setAttribute('data-theme', 'dark');
    } else {
        htmlElement.setAttribute('data-theme', 'light');
    }
}

function submitInvoice() {
    const rows = document.querySelectorAll('tbody tr');
    const invoiceNumberElement = document.getElementById('invoice-number');
    const nameElement = document.getElementById('name');
    const dateElement = document.getElementById('date');

    const name = nameElement.value.trim();
    const date = dateElement.value.trim();

    // Validate invoice number
    let invoiceNumber = null;
    try {
        invoiceNumber = parseFloat(invoiceNumberElement.innerText.split('INVOICE #')[1].trim());
    } catch (e) {}

    const data = {
        'INVOICE #': invoiceNumber,
        'NAME': name,
        'DATE': date,
        'invoiceItems': []
    };

    rows.forEach(row => {
        const cells = row.querySelectorAll('td');
        const rowData = {};
        const columnNames = ["APPROVED", "STOCK #", "DESCRIPTION", "HEAD LIGHTS", "DENTS", "CHIPS/SCRATCHES", "REMEDIATION", "PAINT & BODY", "PARTS", "LABOR", "TOTAL"];
        cells.forEach((cell, index) => {
            if (index === 0) {
                rowData[columnNames[index]] = cell.querySelector('.approved-toggle').checked;
            } else {
                rowData[columnNames[index]] = cell.innerText.trim();
            }
        });
        data['invoiceItems'].push(rowData);
    });

    // Send data to server
    fetch('/submit-invoice', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    }).then(response => response.json())
        .then(data => {
            console.log(data);
            const id = data['id'];
            const linkurl = `${window.location.origin}/invoice/${id}`;
            const linkContainer = document.getElementById('link-container');
            const invoiceLink = document.getElementById('invoice-link');
            invoiceLink.value = linkurl;
            linkContainer.style.display = 'inline-flex';
        })
        .catch(error => {
            alert('Failed to submit invoice');
            console.error('Error:', error);
        });
}

function copyLink() {
    const invoiceLink = document.getElementById('invoice-link');
    invoiceLink.select();
    invoiceLink.setSelectionRange(0, 99999); // For mobile devices

    navigator.clipboard.writeText(invoiceLink.value);
    const copyButton = document.getElementById('invoice-copy');
    copyButton.value = 'Success!';
    setTimeout(() => {
        copyButton.value = 'Copy';
    }, 2000);
}