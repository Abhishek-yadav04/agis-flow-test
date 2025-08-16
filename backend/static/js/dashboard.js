// AgisFL Enterprise Dashboard JavaScript
// This file serves as a placeholder for tests
// The actual frontend is served from the React app in /frontend

console.log('AgisFL Enterprise Dashboard loaded');

// Placeholder functions for test compatibility
function showNotification(message, type = 'info') {
    console.log(`[${type.toUpperCase()}] ${message}`);
}

function updateConnectionStatus(status) {
    console.log(`Connection status: ${status}`);
}

function reconnectWebSocket() {
    console.log('Attempting to reconnect WebSocket...');
}

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        showNotification,
        updateConnectionStatus,
        reconnectWebSocket
    };
}
