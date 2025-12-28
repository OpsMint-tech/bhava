// ========================================
// Global State Management
// ========================================
let currentStep = 1;
const totalSteps = 4;
let formData = {
    basicDetails: {},
    personalDetails: {},
    documents: {},
    ocrResults: {}  // Store OCR extraction results
};

// API Configuration
const API_CONFIG = {
    baseURL: 'http://localhost:8000',  // FastAPI backend URL (updated to port 8000)
    endpoints: {
        // File upload endpoints
        pan: '/api/v1/ocr/upload/pan',
        aadhaar: '/api/v1/ocr/upload/ind_aadhaar',
        voterid: '/api/v1/ocr/upload/voterid',
        processAll: '/api/ocr/process-all'
    }
};

// ========================================
// Step Navigation Functions
// ========================================
function nextStep() {
    if (validateCurrentStep()) {
        saveCurrentStepData();

        if (currentStep < totalSteps) {
            currentStep++;
            updateStepDisplay();

            // If moving to review step, populate review data
            if (currentStep === 4) {
                populateReviewData();
            }
        }
    }
}

function prevStep() {
    if (currentStep > 1) {
        currentStep--;
        updateStepDisplay();
    }
}

function updateStepDisplay() {
    // Update form steps
    document.querySelectorAll('.form-step').forEach(step => {
        step.classList.remove('active');
    });
    document.querySelector(`.form-step[data-step="${currentStep}"]`).classList.add('active');

    // Update progress stepper
    document.querySelectorAll('.step').forEach((step, index) => {
        step.classList.remove('active', 'completed');
        const stepNumber = index + 1;

        if (stepNumber < currentStep) {
            step.classList.add('completed');
        } else if (stepNumber === currentStep) {
            step.classList.add('active');
        }
    });

    // Scroll to top smoothly
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// ========================================
// Validation Functions
// ========================================
function validateCurrentStep() {
    const currentStepElement = document.querySelector(`.form-step[data-step="${currentStep}"]`);
    const inputs = currentStepElement.querySelectorAll('input[required], select[required]');
    let isValid = true;

    inputs.forEach(input => {
        const formGroup = input.closest('.form-group');

        if (!input.value.trim()) {
            formGroup.classList.add('error');
            isValid = false;
        } else if (input.type === 'email' && !isValidEmail(input.value)) {
            formGroup.classList.add('error');
            isValid = false;
        } else if (input.pattern && !new RegExp(input.pattern).test(input.value)) {
            formGroup.classList.add('error');
            isValid = false;
        } else if (input.type === 'file' && !input.files.length) {
            formGroup.classList.add('error');
            isValid = false;
        } else {
            formGroup.classList.remove('error');
        }
    });

    return isValid;
}

function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

function isValidPAN(pan) {
    const panRegex = /^[A-Z]{5}[0-9]{4}[A-Z]{1}$/;
    return panRegex.test(pan);
}

function isValidAadhar(aadhar) {
    const aadharRegex = /^[0-9]{12}$/;
    return aadharRegex.test(aadhar);
}

function isValidIFSC(ifsc) {
    const ifscRegex = /^[A-Z]{4}0[A-Z0-9]{6}$/;
    return ifscRegex.test(ifsc);
}

// ========================================
// Data Management Functions
// ========================================
function saveCurrentStepData() {
    switch (currentStep) {
        case 1:
            formData.basicDetails = {
                firstName: document.getElementById('firstName').value,
                lastName: document.getElementById('lastName').value,
                email: document.getElementById('email').value,
                phone: document.getElementById('phone').value,
                dob: document.getElementById('dob').value
            };
            break;
        case 2:
            formData.personalDetails = {
                pan: document.getElementById('pan').value.toUpperCase(),
                aadhar: document.getElementById('aadhar').value,
                accountNumber: document.getElementById('accountNumber').value,
                ifsc: document.getElementById('ifsc').value.toUpperCase(),
                bankName: document.getElementById('bankName').value
            };
            break;
        case 3:
            formData.documents = {
                panFile: document.getElementById('panFile').files[0]?.name || '',
                aadharFile: document.getElementById('aadharFile').files[0]?.name || '',
                bankFile: document.getElementById('bankFile').files[0]?.name || ''
            };
            break;
    }

    // Save to localStorage for persistence
    localStorage.setItem('kycFormData', JSON.stringify(formData));
}

function loadSavedData() {
    const saved = localStorage.getItem('kycFormData');
    if (saved) {
        formData = JSON.parse(saved);
        // Optionally populate form fields with saved data
    }
}

function populateReviewData() {
    const reviewContainer = document.getElementById('reviewData');

    const reviewHTML = `
        <div class="form-group">
            <label>Full Name</label>
            <input type="text" value="${formData.basicDetails.firstName} ${formData.basicDetails.lastName}" readonly>
        </div>
        <div class="form-group">
            <label>Email</label>
            <input type="text" value="${formData.basicDetails.email}" readonly>
        </div>
        <div class="form-group">
            <label>Phone</label>
            <input type="text" value="${formData.basicDetails.phone}" readonly>
        </div>
        <div class="form-group">
            <label>Date of Birth</label>
            <input type="text" value="${formatDate(formData.basicDetails.dob)}" readonly>
        </div>
        <div class="form-group">
            <label>PAN Card</label>
            <input type="text" value="${formData.personalDetails.pan}" readonly>
        </div>
        <div class="form-group">
            <label>Aadhar Card</label>
            <input type="text" value="${maskAadhar(formData.personalDetails.aadhar)}" readonly>
        </div>
        <div class="form-group">
            <label>Bank Account</label>
            <input type="text" value="${maskAccountNumber(formData.personalDetails.accountNumber)}" readonly>
        </div>
        <div class="form-group">
            <label>IFSC Code</label>
            <input type="text" value="${formData.personalDetails.ifsc}" readonly>
        </div>
        <div class="form-group">
            <label>Bank Name</label>
            <input type="text" value="${formData.personalDetails.bankName}" readonly>
        </div>
    `;

    reviewContainer.innerHTML = reviewHTML;
}

// ========================================
// File Upload Functions
// ========================================
async function handleFileUpload(input, previewId) {
    const file = input.files[0];
    const preview = document.getElementById(previewId);

    if (file) {
        // Validate file size (5MB max)
        if (file.size > 5 * 1024 * 1024) {
            alert('File size must be less than 5MB');
            input.value = '';
            return;
        }

        // Show preview
        preview.classList.add('active');
        preview.querySelector('.file-preview-name').textContent = file.name;

        // Remove error state
        input.closest('.form-group').classList.remove('error');

        // Trigger OCR extraction based on input ID
        if (input.id === 'panFile') {
            await extractPANData(file);
        } else if (input.id === 'aadharFile') {
            await extractAadhaarData(file);
        } else if (input.id === 'bankFile') {
            await extractVoterIDData(file);
        }
    }
}

function removeFile(inputId, previewId) {
    const input = document.getElementById(inputId);
    const preview = document.getElementById(previewId);

    input.value = '';
    preview.classList.remove('active');
    preview.querySelector('.file-preview-name').textContent = '';

    // Clear OCR results for this document
    const docType = inputId.replace('File', '').toLowerCase();
    if (formData.ocrResults[docType]) {
        delete formData.ocrResults[docType];
        hideOCRResult(docType);
    }
}

// ========================================
// OCR Integration Functions
// ========================================
async function extractPANData(file) {
    try {
        showOCRLoading('pan');

        const uploadFormData = new FormData();
        uploadFormData.append('file', file);

        const response = await fetch(`${API_CONFIG.baseURL}${API_CONFIG.endpoints.pan}`, {
            method: 'POST',
            body: uploadFormData
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const result = await response.json();

        if (result.success) {
            formData.ocrResults.pan = result.data;
            displayOCRResult('pan', result.data);
        } else {
            showOCRError('pan', 'Failed to extract PAN data');
        }
    } catch (error) {
        console.error('PAN extraction error:', error);
        showOCRError('pan', error.message);
    }
}

async function extractAadhaarData(file) {
    try {
        showOCRLoading('aadhaar');

        const uploadFormData = new FormData();
        uploadFormData.append('file', file);

        const response = await fetch(`${API_CONFIG.baseURL}${API_CONFIG.endpoints.aadhaar}`, {
            method: 'POST',
            body: uploadFormData
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const result = await response.json();

        if (result.success) {
            formData.ocrResults.aadhaar = result.data;
            displayOCRResult('aadhaar', result.data);
        } else {
            showOCRError('aadhaar', 'Failed to extract Aadhaar data');
        }
    } catch (error) {
        console.error('Aadhaar extraction error:', error);
        showOCRError('aadhaar', error.message);
    }
}

async function extractVoterIDData(file) {
    try {
        showOCRLoading('voterid');

        const uploadFormData = new FormData();
        uploadFormData.append('file', file);

        const response = await fetch(`${API_CONFIG.baseURL}${API_CONFIG.endpoints.voterid}`, {
            method: 'POST',
            body: uploadFormData
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const result = await response.json();

        if (result.success) {
            formData.ocrResults.voterid = result.data;
            displayOCRResult('voterid', result.data);
        } else {
            showOCRError('voterid', 'Failed to extract voter ID data');
        }
    } catch (error) {
        console.error('Voter ID extraction error:', error);
        showOCRError('voterid', error.message);
    }
}

function showOCRLoading(docType) {
    const resultDiv = document.getElementById(`${docType}OcrResult`);
    if (resultDiv) {
        resultDiv.innerHTML = `
            <div class="ocr-loading">
                <div class="spinner"></div>
                <p>Extracting data from ${docType} document...</p>
            </div>
        `;
        resultDiv.classList.add('active');
    }
}

function displayOCRResult(docType, data) {
    const resultDiv = document.getElementById(`${docType}OcrResult`);
    if (!resultDiv) return;

    let html = '<div class="ocr-result-card"><h4>✓ Extracted Data</h4><div class="ocr-data">';

    // Format data based on document type
    if (docType === 'pan' && data) {
        html += `
            ${data.name ? `<div class="ocr-field"><span>Name:</span> <strong>${data.name}</strong></div>` : ''}
            ${data.pan_no ? `<div class="ocr-field"><span>PAN Number:</span> <strong>${data.pan_no}</strong></div>` : ''}
            ${data.date_of_birth ? `<div class="ocr-field"><span>Date of Birth:</span> <strong>${data.date_of_birth}</strong></div>` : ''}
            ${data.fathers_name ? `<div class="ocr-field"><span>Father's Name:</span> <strong>${data.fathers_name}</strong></div>` : ''}
        `;
    } else if (docType === 'aadhaar' && data) {
        html += `
            ${data.name ? `<div class="ocr-field"><span>Name:</span> <strong>${data.name}</strong></div>` : ''}
            ${data.aadhar_no ? `<div class="ocr-field"><span>Aadhaar Number:</span> <strong>${data.aadhar_no}</strong></div>` : ''}
            ${data.date_of_birth ? `<div class="ocr-field"><span>Date of Birth:</span> <strong>${data.date_of_birth}</strong></div>` : ''}
            ${data.full_address ? `<div class="ocr-field"><span>Address:</span> <strong>${data.full_address}</strong></div>` : ''}
            ${data.gender ? `<div class="ocr-field"><span>Gender:</span> <strong>${data.gender}</strong></div>` : ''}
        `;
    } else if (docType === 'voterid' && data) {
        html += `
            ${data.name ? `<div class="ocr-field"><span>Name:</span> <strong>${data.name}</strong></div>` : ''}
            ${data.voter_id ? `<div class="ocr-field"><span>Voter ID:</span> <strong>${data.voter_id}</strong></div>` : ''}
            ${data.date_of_birth ? `<div class="ocr-field"><span>Date of Birth:</span> <strong>${data.date_of_birth}</strong></div>` : ''}
            ${data.age ? `<div class="ocr-field"><span>Age:</span> <strong>${data.age}</strong></div>` : ''}
            ${data.gender ? `<div class="ocr-field"><span>Gender:</span> <strong>${data.gender}</strong></div>` : ''}
            ${data.full_address ? `<div class="ocr-field"><span>Address:</span> <strong>${data.full_address}</strong></div>` : ''}
            ${data.fathers_name ? `<div class="ocr-field"><span>Father's Name:</span> <strong>${data.fathers_name}</strong></div>` : ''}
        `;
    }

    html += '</div></div>';
    resultDiv.innerHTML = html;
    resultDiv.classList.add('active', 'success');
}

function showOCRError(docType, message) {
    const resultDiv = document.getElementById(`${docType}OcrResult`);
    if (resultDiv) {
        resultDiv.innerHTML = `
            <div class="ocr-error-card">
                <h4>✗ Extraction Failed</h4>
                <p>${message}</p>
                <small>Please try uploading a clearer image or contact support.</small>
            </div>
        `;
        resultDiv.classList.add('active', 'error');
    }
}

function hideOCRResult(docType) {
    const resultDiv = document.getElementById(`${docType}OcrResult`);
    if (resultDiv) {
        resultDiv.classList.remove('active', 'success', 'error');
        resultDiv.innerHTML = '';
    }
}

// ========================================
// Form Submission & Verification
// ========================================
function submitForm() {
    const submitButton = event.target;
    submitButton.classList.add('loading');
    submitButton.disabled = true;

    // Simulate verification process
    setTimeout(() => {
        const isEligible = verifyKYC();
        submitButton.classList.remove('loading');
        submitButton.disabled = false;

        showModal(isEligible);
    }, 2000);
}

function verifyKYC() {
    // Verification Logic
    const checks = {
        panValid: isValidPAN(formData.personalDetails.pan),
        aadharValid: isValidAadhar(formData.personalDetails.aadhar),
        ifscValid: isValidIFSC(formData.personalDetails.ifsc),
        ageValid: isAgeValid(formData.basicDetails.dob),
        documentsUploaded: formData.documents.panFile &&
            formData.documents.aadharFile &&
            formData.documents.bankFile,
        phoneValid: formData.basicDetails.phone.length === 10,
        emailValid: isValidEmail(formData.basicDetails.email)
    };

    // Check if all validations pass
    const allChecksPass = Object.values(checks).every(check => check === true);

    // Store verification result
    formData.verificationResult = {
        eligible: allChecksPass,
        checks: checks,
        timestamp: new Date().toISOString()
    };

    return allChecksPass;
}

function isAgeValid(dob) {
    const birthDate = new Date(dob);
    const today = new Date();
    let age = today.getFullYear() - birthDate.getFullYear();
    const monthDiff = today.getMonth() - birthDate.getMonth();

    if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
        age--;
    }

    return age >= 18; // Must be 18 or older
}

// ========================================
// Modal Functions
// ========================================
function showModal(isEligible) {
    const modal = document.getElementById('modal');
    const modalOverlay = document.getElementById('modalOverlay');
    const modalIcon = document.getElementById('modalIcon');
    const modalTitle = document.getElementById('modalTitle');
    const modalMessage = document.getElementById('modalMessage');

    if (isEligible) {
        modal.classList.remove('error');
        modal.classList.add('success');
        modalIcon.textContent = '✓';
        modalTitle.textContent = 'Verification Successful!';
        modalMessage.innerHTML = `
            <strong>Congratulations ${formData.basicDetails.firstName}!</strong><br><br>
            Your KYC verification has been completed successfully. All your documents and information have been verified.<br><br>
            <strong>You are now eligible to proceed with our services.</strong>
        `;
    } else {
        modal.classList.remove('success');
        modal.classList.add('error');
        modalIcon.textContent = '✗';
        modalTitle.textContent = 'Verification Failed';
        modalMessage.innerHTML = `
            <strong>Sorry ${formData.basicDetails.firstName},</strong><br><br>
            We couldn't verify your KYC details. Please check the following:<br><br>
            • Ensure all document formats are correct<br>
            • Verify that you're 18 years or older<br>
            • Check PAN, Aadhar, and IFSC codes are valid<br><br>
            Please update your information and try again.
        `;
    }

    modalOverlay.classList.add('active');
}

function closeModal() {
    const modalOverlay = document.getElementById('modalOverlay');
    modalOverlay.classList.remove('active');

    // If verification was successful, optionally reset the form or redirect
    if (formData.verificationResult?.eligible) {
        // Optionally reset form after successful verification
        // resetForm();
    }
}

// ========================================
// Utility Functions
// ========================================
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-IN', {
        day: '2-digit',
        month: 'short',
        year: 'numeric'
    });
}

function maskAadhar(aadhar) {
    if (!aadhar) return '';
    return 'XXXX XXXX ' + aadhar.slice(-4);
}

function maskAccountNumber(accountNumber) {
    if (!accountNumber) return '';
    return 'XXXXXX' + accountNumber.slice(-4);
}

function resetForm() {
    document.getElementById('kycForm').reset();
    currentStep = 1;
    formData = {
        basicDetails: {},
        personalDetails: {},
        documents: {}
    };
    localStorage.removeItem('kycFormData');
    updateStepDisplay();

    // Clear file previews
    document.querySelectorAll('.file-preview').forEach(preview => {
        preview.classList.remove('active');
    });
}

// ========================================
// Real-time Input Validation
// ========================================
function initializeInputListeners() {
    // Add real-time validation
    document.querySelectorAll('input').forEach(input => {
        input.addEventListener('blur', function () {
            const formGroup = this.closest('.form-group');

            if (this.hasAttribute('required') && !this.value.trim()) {
                formGroup.classList.add('error');
            } else if (this.pattern && this.value && !new RegExp(this.pattern).test(this.value)) {
                formGroup.classList.add('error');
            } else {
                formGroup.classList.remove('error');
            }
        });

        input.addEventListener('input', function () {
            const formGroup = this.closest('.form-group');
            if (formGroup.classList.contains('error') && this.value.trim()) {
                formGroup.classList.remove('error');
            }
        });
    });

    // Format Aadhar input with spaces
    const aadharInput = document.getElementById('aadhar');
    if (aadharInput) {
        aadharInput.addEventListener('input', function (e) {
            let value = e.target.value.replace(/\s/g, '');
            if (value.length > 12) {
                value = value.slice(0, 12);
            }
            e.target.value = value;
        });
    }
}

// ========================================
// Keyboard Navigation
// ========================================
function initializeKeyboardNavigation() {
    document.addEventListener('keydown', function (e) {
        // Allow Enter to move to next step (except in textarea)
        if (e.key === 'Enter' && e.target.tagName !== 'TEXTAREA' && e.target.type !== 'file') {
            e.preventDefault();
            if (currentStep < totalSteps) {
                nextStep();
            }
        }
    });
}

// ========================================
// Initialization
// ========================================
document.addEventListener('DOMContentLoaded', function () {
    loadSavedData();
    initializeInputListeners();
    initializeKeyboardNavigation();

    // Close modal on overlay click
    document.getElementById('modalOverlay').addEventListener('click', function (e) {
        if (e.target === this) {
            closeModal();
        }
    });

    console.log('eKYC Form initialized successfully');
});
