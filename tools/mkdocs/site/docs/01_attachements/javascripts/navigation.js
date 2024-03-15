document.addEventListener('DOMContentLoaded', function () {
    const body = document.body;
    const toggleNavigationBtn = document.getElementById('toggle-navigation');
    const toggleTocBtn = document.getElementById('toggle-toc');

    function updateButtonText() {
        toggleNavigationBtn.textContent = body.classList.contains('hide-navigation') ? '>>> Show Navigation' : '<<< Hide Navigation';
        toggleTocBtn.textContent = body.classList.contains('hide-toc') ? 'Show TOC <<<' : 'Hide TOC >>>';
    }

    toggleNavigationBtn.addEventListener('click', function () {
        body.classList.toggle('hide-navigation');
        updateButtonText();
    });

    toggleTocBtn.addEventListener('click', function () {
        body.classList.toggle('hide-toc');
        updateButtonText();
    });

    updateButtonText(); // Initialize button text based on current state
});
