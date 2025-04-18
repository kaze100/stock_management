document.addEventListener('DOMContentLoaded', function() {
    // Set width for all category progress bars
    const progressBars = document.querySelectorAll('.category-progress');
    progressBars.forEach(function(bar) {
        const width = bar.getAttribute('data-width');
        if (width) {
            bar.style.width = width + '%';
        }
    });
});
