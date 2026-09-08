// MahaDBT Scholarship Tracker Main JavaScript

document.addEventListener('DOMContentLoaded', function () {
    // Auto-dismiss alerts after 6 seconds
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(function (alert) {
        setTimeout(function () {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            if (bsAlert) {
                bsAlert.close();
            }
        }, 6000);
    });

    // File input preview and size check
    const fileInput = document.querySelector('input[type="file"]');
    if (fileInput) {
        fileInput.addEventListener('change', function () {
            if (this.files && this.files[0]) {
                const maxBytes = 16 * 1024 * 1024; // 16MB
                if (this.files[0].size > maxBytes) {
                    alert('File size exceeds the 16MB limit. Please choose a smaller file.');
                    this.value = '';
                }
            }
        });
    }
});
