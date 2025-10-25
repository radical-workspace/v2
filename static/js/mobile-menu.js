// Minimal mobile menu JS placeholder to support menu toggling
document.addEventListener('DOMContentLoaded', function () {
    var toggles = document.querySelectorAll('.nav-mobile-trigger');
    toggles.forEach(function (btn) {
        btn.addEventListener('click', function () {
            var target = document.getElementById('navbarNav');
            if (!target) return;
            target.classList.toggle('hidden');
            target.classList.toggle('block');
        });
    });
});
