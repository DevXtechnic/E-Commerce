/* DevXtechnic Main JavaScript */

document.addEventListener('DOMContentLoaded', function() {
    // --- AJAX Add to Cart ---
    document.querySelectorAll('.add-to-cart-form').forEach(form => {
        form.addEventListener('submit', function(e) {
            // Only intercept for product card forms, not detail page
            if (form.classList.contains('detail-form')) return;

            e.preventDefault();
            const formData = new FormData(form);
            const btn = form.querySelector('.btn-add-cart');
            const originalText = btn.innerHTML;

            btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Adding...';
            btn.disabled = true;

            fetch(form.action, {
                method: 'POST',
                body: formData,
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    // Update cart badge
                    const badge = document.getElementById('cart-badge');
                    if (badge) {
                        badge.textContent = data.cart_count;
                        badge.classList.add('bounce');
                        setTimeout(() => badge.classList.remove('bounce'), 500);
                    }
                    btn.innerHTML = '<i class="fas fa-check"></i> Added!';
                    btn.style.background = '#28a745';
                    setTimeout(() => {
                        btn.innerHTML = originalText;
                        btn.style.background = '';
                        btn.disabled = false;
                    }, 1500);
                }
            })
            .catch(() => {
                btn.innerHTML = originalText;
                btn.disabled = false;
            });
        });
    });

    // --- Auto-dismiss alerts ---
    document.querySelectorAll('.alert').forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            alert.style.transform = 'translateY(-10px)';
            setTimeout(() => alert.remove(), 300);
        }, 4000);
    });

    // --- Sticky navbar shadow on scroll ---
    const navbar = document.getElementById('main-navbar');
    if (navbar) {
        window.addEventListener('scroll', () => {
            if (window.scrollY > 10) {
                navbar.style.boxShadow = '0 4px 20px rgba(0,0,0,0.1)';
            } else {
                navbar.style.boxShadow = '0 1px 3px rgba(0,0,0,0.06)';
            }
        });
    }

    // --- Animate elements on scroll ---
    const observerOptions = { threshold: 0.1, rootMargin: '0px 0px -40px 0px' };
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    document.querySelectorAll('.product-card, .category-card, .trust-item, .about-card, .crm-stat-card, .dash-card').forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(20px)';
        el.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
        observer.observe(el);
    });
});

// --- Add bounce animation CSS dynamically ---
const style = document.createElement('style');
style.textContent = `
    @keyframes bounce {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.4); }
    }
    .bounce { animation: bounce 0.4s ease; }
`;
document.head.appendChild(style);
