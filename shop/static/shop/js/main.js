/* DevBazzar — Main JavaScript */

document.addEventListener('DOMContentLoaded', function() {

  // =============================================
  // THEME TOGGLE
  // =============================================
  const html = document.documentElement;
  const themeToggle = document.getElementById('theme-toggle');

  const savedTheme = localStorage.getItem('devbazzar-theme');
  if (savedTheme) {
    html.setAttribute('data-theme', savedTheme);
  } else {
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    html.setAttribute('data-theme', prefersDark ? 'dark' : 'light');
  }

  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', function(e) {
    if (!localStorage.getItem('devbazzar-theme')) {
      html.setAttribute('data-theme', e.matches ? 'dark' : 'light');
    }
  });

  if (themeToggle) {
    themeToggle.addEventListener('click', function() {
      const current = html.getAttribute('data-theme');
      const next = current === 'dark' ? 'light' : 'dark';
      html.setAttribute('data-theme', next);
      localStorage.setItem('devbazzar-theme', next);
    });
  }

  // =============================================
  // PROMO CAROUSEL
  // =============================================
  if (typeof Swiper !== 'undefined') {
    new Swiper('.promo-swiper', {
      loop: true,
      autoplay: {
        delay: 5000,
        disableOnInteraction: false,
      },
      navigation: {
        nextEl: '.swiper-button-next',
        prevEl: '.swiper-button-prev',
      },
      pagination: {
        el: '.swiper-pagination',
        clickable: true,
      },
      effect: 'slide',
      speed: 600,
    });
  }

  // =============================================
  // SEARCH SUGGESTIONS
  // =============================================
  function initSuggestions(inputId, dropdownId) {
    var input = document.getElementById(inputId);
    var dropdown = document.getElementById(dropdownId);
    if (!input || !dropdown) return;

    var debounceTimer = null;
    var activeIndex = -1;
    var currentSuggestions = [];
    var currentQuery = '';

    function fetchSuggestions(query) {
      if (query.length < 2) {
        hideDropdown();
        return;
      }
      currentQuery = query;
      fetch('/suggestions/?q=' + encodeURIComponent(query))
        .then(function(res) { return res.json(); })
        .then(function(data) {
          currentSuggestions = data.suggestions || [];
          renderDropdown();
        })
        .catch(function() { hideDropdown(); });
    }

    function highlightMatch(text, query) {
      var idx = text.toLowerCase().indexOf(query.toLowerCase());
      if (idx === -1) return escapeHtml(text);
      var before = escapeHtml(text.substring(0, idx));
      var match = '<strong>' + escapeHtml(text.substring(idx, idx + query.length)) + '</strong>';
      var after = escapeHtml(text.substring(idx + query.length));
      return before + match + after;
    }

    function escapeHtml(text) {
      var div = document.createElement('div');
      div.appendChild(document.createTextNode(text));
      return div.innerHTML;
    }

    function renderDropdown() {
      if (currentSuggestions.length === 0) {
        hideDropdown();
        return;
      }
      var html = '';
      for (var i = 0; i < currentSuggestions.length; i++) {
        var s = currentSuggestions[i];
        if (s.category_header) {
          html += '<div class="suggestion-category-header">' + escapeHtml(s.category_header) + '</div>';
          continue;
        }
        var iconClass = s.type === 'brand' ? 'fa-store' : 'fa-search';
        html += '<a href="' + s.url + '" class="search-suggestion-item" data-index="' + i + '">';
        html += '<i class="fas ' + iconClass + ' suggestion-icon"></i>';
        html += '<span class="suggestion-text">' + highlightMatch(s.text, currentQuery) + '</span>';
        html += '</a>';
      }
      dropdown.innerHTML = html;
      dropdown.classList.add('open');
      activeIndex = -1;
    }

    function hideDropdown() {
      dropdown.classList.remove('open');
      dropdown.innerHTML = '';
      activeIndex = -1;
      currentSuggestions = [];
    }

    input.addEventListener('input', function() {
      clearTimeout(debounceTimer);
      debounceTimer = setTimeout(function() {
        fetchSuggestions(input.value.trim());
      }, 250);
    });

    input.addEventListener('keydown', function(e) {
      var items = dropdown.querySelectorAll('.search-suggestion-item');
      if (!items.length) return;

      if (e.key === 'ArrowDown') {
        e.preventDefault();
        activeIndex = Math.min(activeIndex + 1, items.length - 1);
        updateActiveItem(items);
      } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        activeIndex = Math.max(activeIndex - 1, 0);
        updateActiveItem(items);
      } else if (e.key === 'Enter' && activeIndex >= 0 && items[activeIndex]) {
        e.preventDefault();
        window.location.href = items[activeIndex].href;
      } else if (e.key === 'Escape') {
        hideDropdown();
        input.blur();
      }
    });

    function updateActiveItem(items) {
      for (var i = 0; i < items.length; i++) {
        items[i].classList.remove('active');
      }
      if (activeIndex >= 0 && items[activeIndex]) {
        items[activeIndex].classList.add('active');
        items[activeIndex].scrollIntoView({ block: 'nearest' });
      }
    }

    dropdown.addEventListener('click', function(e) {
      var item = e.target.closest('.search-suggestion-item');
      if (item) hideDropdown();
    });

    document.addEventListener('click', function(e) {
      if (!input.contains(e.target) && !dropdown.contains(e.target)) {
        hideDropdown();
      }
    });
  }

  initSuggestions('search-input', 'search-suggestions');
  initSuggestions('mobile-search-input', 'mobile-search-suggestions');

  // =============================================
  // MOBILE SEARCH OVERLAY
  // =============================================
  const searchToggle = document.getElementById('search-toggle');
  const mobileSearch = document.getElementById('mobile-search');
  const searchBackdrop = document.getElementById('search-backdrop');
  const searchClose = document.getElementById('search-close-btn');

  function openSearch() {
    mobileSearch.classList.add('open');
    searchBackdrop.classList.add('open');
    document.body.style.overflow = 'hidden';
    document.body.style.position = 'fixed';
    document.body.style.width = '100%';
    document.body.style.top = '-' + window.scrollY + 'px';
    setTimeout(function() {
      var inp = mobileSearch.querySelector('input');
      if (inp) inp.focus();
    }, 100);
  }

  function closeSearch() {
    mobileSearch.classList.remove('open');
    searchBackdrop.classList.remove('open');
    var scrollY = document.body.style.top;
    document.body.style.overflow = '';
    document.body.style.position = '';
    document.body.style.width = '';
    document.body.style.top = '';
    if (scrollY) {
      window.scrollTo(0, parseInt(scrollY || '0', 10) * -1);
    }
  }

  if (searchToggle && mobileSearch) {
    searchToggle.addEventListener('click', function(e) {
      e.stopPropagation();
      openSearch();
    });
  }

  if (searchClose) {
    searchClose.addEventListener('click', closeSearch);
  }

  if (searchBackdrop) {
    searchBackdrop.addEventListener('click', closeSearch);
  }

  // Escape key closes search
  document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape' && mobileSearch && mobileSearch.classList.contains('open')) {
      closeSearch();
    }
  });

  // =============================================
  // MOBILE FILTER TOGGLE
  // =============================================
  const filterToggle = document.getElementById('filter-toggle');
  const sidebar = document.getElementById('shop-sidebar');
  const filterBackdrop = document.getElementById('filter-backdrop');

  if (filterToggle && sidebar && filterBackdrop) {
    filterToggle.addEventListener('click', function() {
      sidebar.classList.toggle('open');
      filterBackdrop.classList.toggle('open');
      document.body.style.overflow = sidebar.classList.contains('open') ? 'hidden' : '';
    });

    filterBackdrop.addEventListener('click', function() {
      sidebar.classList.remove('open');
      filterBackdrop.classList.remove('open');
      document.body.style.overflow = '';
    });
  }

  // =============================================
  // MOBILE MENU (category nav)
  // =============================================
  const mobileMenuBtn = document.getElementById('mobile-menu-btn');
  const categoryNav = document.querySelector('.category-nav');

  if (mobileMenuBtn && categoryNav) {
    mobileMenuBtn.addEventListener('click', function() {
      categoryNav.classList.toggle('open');
    });
  }

  // =============================================
  // STICKY NAVBAR SHADOW
  // =============================================
  const navbar = document.getElementById('main-navbar');

  if (navbar) {
    const onScroll = function() {
      if (window.scrollY > 10) {
        navbar.classList.add('scrolled');
      } else {
        navbar.classList.remove('scrolled');
      }
    };

    window.addEventListener('scroll', onScroll, { passive: true });
    // Check initial state
    onScroll();
  }

  // =============================================
  // AJAX ADD TO CART
  // =============================================
  document.querySelectorAll('.add-to-cart-form').forEach(function(form) {
    // Skip detail page forms (they submit normally)
    if (form.classList.contains('no-ajax')) return;

    form.addEventListener('submit', function(e) {
      e.preventDefault();
      const formData = new FormData(form);
      const btn = form.querySelector('.btn-add-cart');
      const originalText = btn.innerHTML;

      btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
      btn.disabled = true;

      fetch(form.action, {
        method: 'POST',
        body: formData,
        headers: { 'X-Requested-With': 'XMLHttpRequest' }
      })
      .then(function(res) { return res.json(); })
      .then(function(data) {
        if (data.success) {
          const badge = document.getElementById('cart-badge');
          if (badge) {
            badge.textContent = data.cart_count;
            badge.classList.remove('bounce');
            // Force reflow
            void badge.offsetWidth;
            badge.classList.add('bounce');
          }
          btn.innerHTML = '<i class="fas fa-check"></i> Added!';
          btn.style.background = '#10B981';
          setTimeout(function() {
            btn.innerHTML = '<i class="fas fa-shopping-bag"></i> Add to Cart';
            btn.style.background = '';
            btn.disabled = false;
          }, 1500);
        }
      })
      .catch(function() {
        btn.innerHTML = originalText;
        btn.disabled = false;
      });
    });
  });

  // =============================================
  // AUTO-DISMISS ALERTS
  // =============================================
  document.querySelectorAll('.alert').forEach(function(alert) {
    setTimeout(function() {
      alert.style.opacity = '0';
      alert.style.transform = 'translateY(-10px)';
      alert.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
      setTimeout(function() {
        if (alert.parentNode) alert.remove();
      }, 300);
    }, 4000);
  });

  // =============================================
  // SCROLL ANIMATIONS (Intersection Observer)
  // =============================================
  const observerOptions = {
    threshold: 0.05,
    rootMargin: '0px 0px -30px 0px'
  };

  const observer = new IntersectionObserver(function(entries) {
    entries.forEach(function(entry) {
      if (entry.isIntersecting) {
        entry.target.style.opacity = '1';
        entry.target.style.transform = 'translateY(0)';
        observer.unobserve(entry.target);
      }
    });
  }, observerOptions);

  document.querySelectorAll(
    '.product-card, .category-card, .trust-item, .about-card, .crm-stat-card, .dash-card, .review-card, .cart-item'
  ).forEach(function(el) {
    el.style.opacity = '0';
    el.style.transform = 'translateY(20px)';
    el.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
    observer.observe(el);
  });

  // =============================================
  // GALLERY ZOOM ON PRODUCT DETAIL
  // =============================================
  const galleryMain = document.querySelector('.gallery-main');

  if (galleryMain) {
    galleryMain.addEventListener('click', function() {
      this.classList.toggle('zoomed');
    });

    galleryMain.addEventListener('mousemove', function(e) {
      if (!this.classList.contains('zoomed')) return;
      const rect = this.getBoundingClientRect();
      const x = ((e.clientX - rect.left) / rect.width) * 100;
      const y = ((e.clientY - rect.top) / rect.height) * 100;
      this.querySelector('img').style.transformOrigin = x + '% ' + y + '%';
    });

    galleryMain.addEventListener('mouseleave', function() {
      if (this.classList.contains('zoomed')) {
        this.querySelector('img').style.transformOrigin = 'center center';
      }
    });
  }

  // =============================================
  // QUANTITY INPUT VALIDATION
  // =============================================
  document.querySelectorAll('.qty-control input[type="number"]').forEach(function(input) {
    input.addEventListener('change', function() {
      var min = parseInt(this.getAttribute('min')) || 1;
      var max = parseInt(this.getAttribute('max')) || 999;
      var val = parseInt(this.value);
      if (isNaN(val) || val < min) this.value = min;
      if (val > max) this.value = max;
    });
  });

  // =============================================
  // Add bounce keyframes once (in case CSS didn't cover it)
  // =============================================
  if (!document.getElementById('bounce-style')) {
    var style = document.createElement('style');
    style.id = 'bounce-style';
    style.textContent = `
      @keyframes bounce {
        0%, 100% { transform: scale(1); }
        40% { transform: scale(1.35); }
        60% { transform: scale(0.9); }
        80% { transform: scale(1.1); }
      }
    `;
    document.head.appendChild(style);
  }
});
