// Main JavaScript for the matching app
document.addEventListener('DOMContentLoaded', function() {
    
    // Auto-hide flash messages after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            setTimeout(() => {
                alert.remove();
            }, 300);
        }, 5000);
    });
    
    // Like button functionality
    const likeButtons = document.querySelectorAll('[data-like-user]');
    likeButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const userId = this.dataset.likeUser;
            likeUser(userId, this);
        });
    });
    
    // Chat functionality
    const chatForm = document.getElementById('chat-form');
    if (chatForm) {
        chatForm.addEventListener('submit', function(e) {
            // Form will submit normally, can be enhanced for AJAX later
        });
    }
    
    // Auto-refresh matches count (for future enhancement)
    function refreshMatchCount() {
        // Placeholder for real-time updates
    }
    
    // Like user function
    function likeUser(userId, button) {
        button.disabled = true;
        button.textContent = 'Liking...';
        
        fetch(`/like/${userId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            },
            credentials: 'same-origin'
        })
        .then(response => response.json())
        .then(data => {
            if (data.liked) {
                button.textContent = data.match_created ? '💕 Matched!' : '❤️ Liked';
                button.classList.add('bg-green-600');
                
                if (data.match_created) {
                    showMatchNotification(data.message);
                }
            }
        })
        .catch(error => {
            console.error('Error:', error);
            button.disabled = false;
            button.textContent = '❤️ Like';
        });
    }
    
    // Show match notification
    function showMatchNotification(message) {
        const notification = document.createElement('div');
        notification.className = 'fixed top-4 right-4 bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded z-50';
        notification.innerHTML = `
            <strong>🎉 ${message}</strong>
            <button onclick="this.parentElement.remove()" class="float-right ml-4 text-green-700 hover:text-green-900">×</button>
        `;
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 5000);
    }
    
    // Get CSRF token
    function getCSRFToken() {
        const token = document.querySelector('meta[name=csrf-token]');
        return token ? token.getAttribute('content') : '';
    }
    
});

// Utility functions
function showLoading(element) {
    element.classList.add('loading');
}

function hideLoading(element) {
    element.classList.remove('loading');
}