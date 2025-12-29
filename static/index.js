document.addEventListener('input', (event) => {
    const element = event.target;
    if (element.tagName === 'TD' && element.isContentEditable) {
        // Only validate numbers for parts and labor cells
        if (element.classList.contains('parts-cell') || element.classList.contains('labor-cell')) {
            validateNumber(element);
        }
        addNewRowIfNeeded(element);
        setTimeout(updateTotal, 700);
    }
});

// Client-side image compression helper. Attempts to resize and re-encode to JPEG.
async function compressImage(file, maxWidth = 1600, quality = 0.8) {
    // If file is already very small, skip
    try {
        if (file.size < 100 * 1024) return file; // <100KB skip
        // try createImageBitmap path (faster)
        const bitmap = await createImageBitmap(file);
        const ratio = Math.min(1, maxWidth / bitmap.width);
        const width = Math.round(bitmap.width * ratio);
        const height = Math.round(bitmap.height * ratio);
        const canvas = document.createElement('canvas');
        canvas.width = width;
        canvas.height = height;
        const ctx = canvas.getContext('2d');
        ctx.drawImage(bitmap, 0, 0, width, height);
        return await new Promise((resolve) => {
            canvas.toBlob((blob) => {
                if (!blob) return resolve(file);
                // If compressed blob is bigger than original, keep original
                if (blob.size >= file.size) return resolve(file);
                const newName = file.name.replace(/\.[^.]+$/, '.jpg');
                const newFile = new File([blob], newName, { type: blob.type || 'image/jpeg' });
                resolve(newFile);
            }, 'image/jpeg', quality);
        });
    } catch (e) {
        // Fallback using Image element (older browsers or decoding failure)
        return new Promise((resolve) => {
            const img = new Image();
            img.onload = () => {
                try {
                    const ratio = Math.min(1, maxWidth / img.width);
                    const width = Math.round(img.width * ratio);
                    const height = Math.round(img.height * ratio);
                    const canvas = document.createElement('canvas');
                    canvas.width = width;
                    canvas.height = height;
                    const ctx = canvas.getContext('2d');
                    ctx.drawImage(img, 0, 0, width, height);
                    canvas.toBlob((blob) => {
                        if (!blob) return resolve(file);
                        if (blob.size >= file.size) return resolve(file);
                        const newName = file.name.replace(/\.[^.]+$/, '.jpg');
                        const newFile = new File([blob], newName, { type: blob.type || 'image/jpeg' });
                        resolve(newFile);
                    }, 'image/jpeg', quality);
                } catch (err) {
                    resolve(file);
                }
            };
            img.onerror = () => resolve(file);
            img.src = URL.createObjectURL(file);
        });
    }
}

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

    // Picture upload button logic
    document.querySelectorAll('.picture-upload-btn').forEach((btn, idx) => {
        btn.addEventListener('click', function() {
            const row = btn.closest('tr');
            const input = row.querySelector('.picture-input');
            input.click();
        });
    });

    document.querySelectorAll('.picture-input').forEach((input, idx) => {
        input.addEventListener('change', async function() {
            const file = input.files[0];
            if (!file) return;
            const row = input.closest('tr');
            const preview = row.querySelector('.picture-preview');
            const urlInput = row.querySelector('.picture-url');
            // Compress image client-side before upload
            let uploadFile = file;
            try {
                uploadFile = await compressImage(file, 1600, 0.8);
            } catch (e) {
                uploadFile = file;
            }
            // Upload to backend
            const formData = new FormData();
            formData.append('file', uploadFile, uploadFile.name);
            const resp = await fetch('/upload-picture', { method: 'POST', body: formData });
            if (resp.ok) {
                const data = await resp.json();
                urlInput.value = data.url;
                preview.src = data.url;
                preview.style.display = 'inline-block';
            } else {
                alert('Failed to upload image');
            }
        });
    });
});

function updateTotal() {
    const rows = document.querySelectorAll('tbody tr');
    rows.forEach(row => {
        const partsCell = row.querySelector('.parts-cell');
        const laborCell = row.querySelector('.labor-cell');
        const totalCell = row.querySelector('.total-cell');
        if (partsCell && laborCell && totalCell) {
            const parts = parseFloat(partsCell.innerText) || 0;
            const labor = parseFloat(laborCell.innerText) || 0;
            totalCell.innerText = parts + labor;
        }
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
        // 13 columns: APPROVED, COMMENTS, STOCK #, DESCRIPTION, PICTURE, HEAD LIGHTS, DENTS, CHIPS/SCRATCHES, PAINT TOUCH UP, PAINT & BODY, PARTS, LABOR, TOTAL
        for (let i = 0; i < 13; i++) {
            const newCell = document.createElement('td');
            if (i === 0) {
                const checkbox = document.createElement('input');
                checkbox.type = 'checkbox';
                checkbox.className = 'approved-toggle';
                newCell.appendChild(checkbox);
            } else if (i === 1) {
                newCell.contentEditable = "true";
                newCell.className = 'comments-cell';
            } else if (i === 4) {
                // Picture upload
                const fileInput = document.createElement('input');
                fileInput.type = 'file';
                fileInput.accept = 'image/*,.heic';
                fileInput.className = 'picture-input';
                fileInput.style.display = 'none';
                const btn = document.createElement('button');
                btn.type = 'button';
                btn.className = 'picture-upload-btn';
                btn.textContent = 'Upload';
                const img = document.createElement('img');
                img.className = 'picture-preview';
                img.style.display = 'none';
                img.style.maxWidth = '60px';
                img.style.maxHeight = '60px';
                const urlInput = document.createElement('input');
                urlInput.type = 'hidden';
                urlInput.className = 'picture-url';
                newCell.appendChild(fileInput);
                newCell.appendChild(btn);
                newCell.appendChild(img);
                newCell.appendChild(urlInput);
                // Add event listeners
                btn.addEventListener('click', function() { fileInput.click(); });
                fileInput.addEventListener('change', async function() {
                    const file = fileInput.files[0];
                    if (!file) return;
                    // Compress before upload
                    let uploadFile = file;
                    try {
                        uploadFile = await compressImage(file, 1600, 0.8);
                    } catch (e) {
                        uploadFile = file;
                    }
                    const formData = new FormData();
                    formData.append('file', uploadFile, uploadFile.name);
                    const resp = await fetch('/upload-picture', { method: 'POST', body: formData });
                    if (resp.ok) {
                        const data = await resp.json();
                        urlInput.value = data.url;
                        img.src = data.url;
                        img.style.display = 'inline-block';
                    } else {
                        alert('Failed to upload image');
                    }
                });
            } else if (i >= 5 && i <= 9) {
                // Checkbox columns
                const checkbox = document.createElement('input');
                checkbox.type = 'checkbox';
                if (i === 5) checkbox.className = 'head-lights-toggle';
                if (i === 6) checkbox.className = 'dents-toggle';
                if (i === 7) checkbox.className = 'scratches-toggle';
                if (i === 8) checkbox.className = 'chips-toggle';
                if (i === 9) checkbox.className = 'paint-body-toggle';
                newCell.appendChild(checkbox);
            } else if (i === 10) {
                newCell.contentEditable = "true";
                newCell.className = 'parts-cell';
            } else if (i === 11) {
                newCell.contentEditable = "true";
                newCell.className = 'labor-cell';
            } else if (i === 12) {
                newCell.className = 'total-cell';
            } else if (i === 3) {
                newCell.contentEditable = "true";
                newCell.className = 'description-cell';
            } else {
                newCell.contentEditable = "true";
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
    let rows = document.querySelectorAll('tbody tr');
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

    // Remove last row if empty
    const lastRowCells = Array.from(rows[rows.length - 1].querySelectorAll('td'));
    const lastRowData = lastRowCells.slice(1,).map(cell => cell.innerText.trim());
    if (lastRowData.every(cell => cell === '' || cell === '0.0' || cell === '0')) {
        rows = Array.from(rows).slice(0, -1);
    }

    rows.forEach(row => {
        const cells = row.querySelectorAll('td');
        const rowData = {};
        // ["APPROVED", "COMMENTS", "STOCK #", "DESCRIPTION", "PICTURE", ...]
        rowData["APPROVED"] = cells[0].querySelector('.approved-toggle')?.checked || false;
        rowData["COMMENTS"] = cells[1].innerText.trim();
        rowData["STOCK #"] = cells[2].innerText.trim();
        rowData["DESCRIPTION"] = cells[3].innerText.trim();
        rowData["PICTURE_URL"] = cells[4].querySelector('.picture-url')?.value || '';
        rowData["HEAD LIGHTS"] = cells[5].querySelector('.head-lights-toggle')?.checked || false;
        rowData["DENTS"] = cells[6].querySelector('.dents-toggle')?.checked || false;
        // separate CHIPS and SCRATCHES to match template
        rowData["SCRATCHES"] = cells[7].querySelector('.scratches-toggle')?.checked || false;
        rowData["CHIPS"] = cells[8].querySelector('.chips-toggle')?.checked || false;
        rowData["REMEDIATION"] = false; // no remediation column in current UI
        rowData["PAINT & BODY"] = cells[9].querySelector('.paint-body-toggle')?.checked || false;
        rowData["PARTS"] = cells[10].innerText.trim();
        rowData["LABOR"] = cells[11].innerText.trim();
        rowData["TOTAL"] = (parseFloat(rowData["PARTS"]) || 0) + (parseFloat(rowData["LABOR"]) || 0);
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

function printInvoice() {
    const header = document.querySelector('header.container');
    const table = document.querySelector('main.container table');
    if (!header && !table) return;
    const content = (header ? header.outerHTML : '') + (table ? table.outerHTML : '');

    const html = '<!doctype html><html><head><meta charset="utf-8"><title>Print</title>' +
        '<link rel="stylesheet" href="/static/css/pico.slate.css">' +
        '<link rel="stylesheet" href="/static/index.css">' +
        '</head><body class="printScreen">' + content + '</body></html>';

    const w = window.open('', '_blank');
    if (!w) {
        alert('Unable to open print window (popup blocked). Please allow popups and try again.');
        return;
    }
    w.document.open();
    w.document.write(html);
    w.document.close();
    // Try to trigger print after short delay; user can also use browser UI
    setTimeout(() => {
        try {
            w.focus();
            w.print();
        } catch (e) {
            // ignore
        }
    }, 700);
}