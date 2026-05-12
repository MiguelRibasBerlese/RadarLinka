(function () {
    const wrap  = document.getElementById('theme-toggle-wrap');
    const track = document.getElementById('theme-toggle-track');
    const icon  = document.getElementById('theme-toggle-icon');

    function applyTheme(dark) {
        document.body.classList.toggle('dark', dark);
        track.classList.toggle('dark', dark);
        icon.textContent = dark ? '🌙' : '☀️';
        localStorage.setItem('radar-theme', dark ? 'dark' : 'light');
    }

    const saved = localStorage.getItem('radar-theme');
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    applyTheme(saved ? saved === 'dark' : prefersDark);

    track.addEventListener('click', () => {
        applyTheme(!document.body.classList.contains('dark'));
    });
})();
