// Preview avatar before upload
document.addEventListener('DOMContentLoaded', function() {
    const avatarInput = document.getElementById('avatar');
    if (avatarInput) {
        avatarInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                // Check file size (2MB)
                if (file.size > 2 * 1024 * 1024) {
                    alert('File quá lớn! Vui lòng chọn file nhỏ hơn 2MB.');
                    e.target.value = '';
                    return;
                }
                
                // Check file type
                const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif'];
                if (!validTypes.includes(file.type)) {
                    alert('File không hợp lệ! Chỉ chấp nhận file ảnh.');
                    e.target.value = '';
                    return;
                }
            }
        });
    }
    
    // Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
});