/* OpenSphere - Frontend Interactive Logic */

document.addEventListener('DOMContentLoaded', () => {
    // Auto hide flash alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            alert.style.transition = 'opacity 0.5s ease';
            setTimeout(() => alert.remove(), 500);
        }, 5000);
    });

    // Initialize Dashboard Charts if analytics element exists
    const statusCanvas = document.getElementById('statusChart');
    const priorityCanvas = document.getElementById('priorityChart');

    if (statusCanvas && priorityCanvas && window.analyticsData) {
        // Status Doughnut Chart
        new Chart(statusCanvas, {
            type: 'doughnut',
            data: {
                labels: ['Open', 'In Progress', 'Resolved', 'Closed'],
                datasets: [{
                    data: window.analyticsData.status,
                    backgroundColor: ['#6366f1', '#f59e0b', '#10b981', '#6b7280'],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { labels: { color: '#9ca3af' } }
                }
            }
        });

        // Priority Bar Chart
        new Chart(priorityCanvas, {
            type: 'bar',
            data: {
                labels: ['Low', 'Medium', 'High', 'Critical'],
                datasets: [{
                    label: 'Issues Count',
                    data: window.analyticsData.priority,
                    backgroundColor: ['#34d399', '#facc15', '#fb923c', '#f87171'],
                    borderRadius: 6
                }]
            },
            options: {
                responsive: true,
                scales: {
                    x: { ticks: { color: '#9ca3af' }, grid: { display: false } },
                    y: { ticks: { color: '#9ca3af', stepSize: 1 }, grid: { color: 'rgba(255,255,255,0.05)' } }
                },
                plugins: {
                    legend: { display: false }
                }
            }
        });
    }

    // HTML5 Drag and Drop for Kanban Columns
    const kanbanCards = document.querySelectorAll('.kanban-card');
    const kanbanCols = document.querySelectorAll('.kanban-column');

    kanbanCards.forEach(card => {
        card.addEventListener('dragstart', (e) => {
            e.dataTransfer.setData('text/plain', card.dataset.issueId);
            card.classList.add('dragging');
        });

        card.addEventListener('dragend', () => {
            card.classList.remove('dragging');
        });
    });

    kanbanCols.forEach(col => {
        col.addEventListener('dragover', (e) => {
            e.preventDefault();
            col.style.borderColor = '#6366f1';
        });

        col.addEventListener('dragleave', () => {
            col.style.borderColor = 'rgba(255, 255, 255, 0.1)';
        });

        col.addEventListener('drop', (e) => {
            e.preventDefault();
            col.style.borderColor = 'rgba(255, 255, 255, 0.1)';
            const issueId = e.dataTransfer.getData('text/plain');
            const targetStatus = col.dataset.status;
            const draggedCard = document.querySelector(`[data-issue-id="${issueId}"]`);

            if (draggedCard && targetStatus) {
                // Update UI visually
                col.querySelector('.kanban-card-container').appendChild(draggedCard);

                // Call Backend API
                fetch('/api/issues/update-status', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ issue_id: parseInt(issueId), status: targetStatus })
                })
                .then(res => res.json())
                .then(data => {
                    if (!data.success) {
                        alert('Failed to update issue status: ' + data.error);
                    }
                })
                .catch(err => console.error('Kanban API Error:', err));
            }
        });
    });
});
