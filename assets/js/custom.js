
document.getElementById('cvFloatBtn').onclick = function() {
    document.getElementById('cvSlidePanel').classList.add('active');
};
document.getElementById('cvSlideClose').onclick = function() {
    document.getElementById('cvSlidePanel').classList.remove('active');
};
// Optional: Close panel when clicking outside
window.addEventListener('click', function(e) {
    const panel = document.getElementById('cvSlidePanel');
    const btn = document.getElementById('cvFloatBtn');
    if (!panel.contains(e.target) && !btn.contains(e.target)) {
        panel.classList.remove('active');
    }
});
