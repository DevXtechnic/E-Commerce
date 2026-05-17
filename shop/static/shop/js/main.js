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
    var promoSwiper = new Swiper('.promo-swiper', {
      loop: true,
      autoplay: {
        delay: 6000,
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
      speed: 700,
      on: {
        init: function() {
          startProgress(this);
        },
        slideChangeTransitionStart: function() {
          resetProgress(this);
          startProgress(this);
        },
        autoplayStop: function() {
          pauseProgress(this);
        },
        autoplayStart: function() {
          resumeProgress(this);
        }
      }
    });

    function startProgress(swiper) {
      var bars = document.querySelectorAll('.promo-progress-bar');
      bars.forEach(function(bar) { bar.classList.remove('active'); });
      var activeSlide = swiper.slides[swiper.activeIndex];
      if (activeSlide) {
        var bar = activeSlide.querySelector('.promo-progress-bar');
        if (bar) {
          void bar.offsetWidth;
          bar.classList.add('active');
        }
      }
    }
    function resetProgress(swiper) {
      var bars = document.querySelectorAll('.promo-progress-bar');
      bars.forEach(function(bar) { bar.classList.remove('active'); });
    }
    function pauseProgress(swiper) {
      var bars = document.querySelectorAll('.promo-progress-bar');
      bars.forEach(function(bar) { bar.style.animationPlayState = 'paused'; });
    }
    function resumeProgress(swiper) {
      var bars = document.querySelectorAll('.promo-progress-bar');
      bars.forEach(function(bar) { bar.style.animationPlayState = 'running'; });
    }
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

  if (filterToggle && sidebar) {
    filterToggle.addEventListener('click', function() {
      sidebar.classList.toggle('open');
      if (filterBackdrop) filterBackdrop.classList.toggle('open');
      document.body.style.overflow = sidebar.classList.contains('open') ? 'hidden' : '';
    });
  }

  if (filterBackdrop && sidebar) {
    filterBackdrop.addEventListener('click', function() {
      sidebar.classList.remove('open');
      filterBackdrop.classList.remove('open');
      document.body.style.overflow = '';
    });
  }

  // =============================================
  // AJAX ADD TO CART
  // =============================================
  var qtyInput = document.getElementById('qty');
  var addToCartQty = document.getElementById('add-to-cart-qty');
  var buyNowQty = document.getElementById('buy-now-qty');
  if (qtyInput && addToCartQty && buyNowQty) {
    function syncQty() {
      addToCartQty.value = qtyInput.value;
      buyNowQty.value = qtyInput.value;
    }
    qtyInput.addEventListener('input', syncQty);
    qtyInput.addEventListener('change', syncQty);
  }

  document.querySelectorAll('.add-to-cart-form').forEach(form => {
    form.addEventListener('submit', function(e) {
      if (form.classList.contains('buy-now-form')) return;

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

  // =============================================
  // AUTO-DISMISS ALERTS
  // =============================================
  document.querySelectorAll('.alert').forEach(alert => {
    setTimeout(() => {
      alert.style.opacity = '0';
      alert.style.transform = 'translateY(-10px)';
      setTimeout(() => alert.remove(), 300);
    }, 4000);
  });

  // =============================================
  // NAVBAR SCROLL SHADOW
  // =============================================
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

  // =============================================
  // SCROLL ANIMATIONS
  // =============================================
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

// =============================================
// BOUNCE ANIMATION
// =============================================
const bounceStyle = document.createElement('style');
bounceStyle.textContent = `
  @keyframes bounce {
    0%, 100% { transform: scale(1); }
    50% { transform: scale(1.4); }
  }
  .bounce { animation: bounce 0.4s ease; }
`;
document.head.appendChild(bounceStyle);

// =============================================
// CART STOCK POLLING & TIMER
// =============================================
(function() {
  var cartItemsEl = document.querySelector('.cart-items');
  if (!cartItemsEl) return;

  var pollInterval = 10000;
  var pollTimer = null;
  var countdownTimer = null;

  function formatTime(secs) {
    var m = Math.floor(secs / 60);
    var s = secs % 60;
    return m + ':' + (s < 10 ? '0' : '') + s;
  }

  function updateTimers() {
    document.querySelectorAll('.cart-item-timer').forEach(function(el) {
      var secs = parseInt(el.dataset.seconds) || 0;
      if (secs > 0) {
        secs--;
        el.dataset.seconds = secs;
        var display = el.querySelector('.timer-display');
        if (display) display.textContent = formatTime(secs);
        if (secs <= 300) {
          el.classList.add('timer-urgent');
        }
        if (secs <= 0) {
          location.reload();
        }
      }
    });
  }

  function checkStock() {
    fetch('/cart/check-stock/', {
      headers: { 'X-Requested-With': 'XMLHttpRequest' }
    })
    .then(function(res) { return res.json(); })
    .then(function(data) {
      if (!data.success) return;

      data.changes.forEach(function(change) {
        var itemEl = document.getElementById('cart-item-' + change.item_id);
        if (!itemEl) return;

        if (!change.is_available) {
          itemEl.classList.add('cart-item-unavailable');
          var imgWrap = itemEl.querySelector('.cart-item-img');
          if (imgWrap && !imgWrap.querySelector('.stock-badge-out')) {
            var badge = document.createElement('div');
            badge.className = 'stock-badge stock-badge-out';
            badge.textContent = 'Out of Stock';
            imgWrap.appendChild(badge);
          }
          var infoEl = itemEl.querySelector('.cart-item-info');
          if (infoEl && !infoEl.querySelector('.cart-item-warning')) {
            var warn = document.createElement('span');
            warn.className = 'cart-item-warning';
            warn.innerHTML = '<i class="fas fa-exclamation-circle"></i> Stock no longer available';
            infoEl.appendChild(warn);
          }
          var qtyForm = itemEl.querySelector('.cart-qty-form');
          if (qtyForm) {
            qtyForm.querySelectorAll('button, input').forEach(function(el) {
              el.disabled = true;
            });
          }
        } else if (change.available < change.requested) {
          var qtyInput = itemEl.querySelector('input[name="quantity"]');
          if (qtyInput) {
            qtyInput.max = change.available;
            if (parseInt(qtyInput.value) > change.available) {
              qtyInput.value = change.available;
              qtyForm = itemEl.querySelector('.cart-qty-form');
              if (qtyForm) qtyForm.submit();
            }
          }
          var imgWrap = itemEl.querySelector('.cart-item-img');
          if (imgWrap) {
            var existingBadge = imgWrap.querySelector('.stock-badge-low');
            if (existingBadge) {
              existingBadge.textContent = 'Only ' + change.available + ' left!';
            } else if (!imgWrap.querySelector('.stock-badge-out')) {
              var badge = document.createElement('div');
              badge.className = 'stock-badge stock-badge-low';
              badge.textContent = 'Only ' + change.available + ' left!';
              imgWrap.appendChild(badge);
            }
          }
        }
      });

      data.removed_ids.forEach(function(id) {
        var itemEl = document.getElementById('cart-item-' + id);
        if (itemEl) {
          itemEl.style.opacity = '0';
          itemEl.style.transform = 'translateX(-20px)';
          setTimeout(function() { itemEl.remove(); }, 300);
        }
      });

      var badgeEl = document.getElementById('cart-badge');
      if (badgeEl && data.cart_count !== undefined) {
        badgeEl.textContent = data.cart_count;
      }

      if (data.removed_ids.length > 0 || data.changes.length > 0) {
        location.reload();
      }
    })
    .catch(function() {});
  }

  countdownTimer = setInterval(updateTimers, 1000);
  pollTimer = setInterval(checkStock, pollInterval);

  window.addEventListener('beforeunload', function() {
    if (pollTimer) clearInterval(pollTimer);
    if (countdownTimer) clearInterval(countdownTimer);
  });
})();

// =============================================
// NOTIFICATION SYSTEM
// =============================================
(function() {
  var notifBtn = document.getElementById('notif-btn');
  var notifDropdown = document.getElementById('notif-dropdown');
  var notifBadge = document.getElementById('notif-badge');
  var notifList = document.getElementById('notif-dropdown-list');
  var notifMarkAll = document.getElementById('notif-mark-all');
  var markAllPage = document.getElementById('mark-all-read-page');
  if (!notifBtn) return;

  var toastQueue = [];
  var activeToasts = [];
  var MAX_VISIBLE = window.innerWidth < 768 ? 1 : 3;
  var notifPollTimer = null;

  // Dropdown toggle
  notifBtn.addEventListener('click', function(e) {
    e.stopPropagation();
    notifDropdown.classList.toggle('open');
    if (notifDropdown.classList.contains('open')) {
      loadDropdownNotifs();
    }
  });

  document.addEventListener('click', function(e) {
    if (notifDropdown && !notifDropdown.contains(e.target) && e.target !== notifBtn) {
      notifDropdown.classList.remove('open');
    }
  });

  // Mark all read
  if (notifMarkAll) {
    notifMarkAll.addEventListener('click', function() {
      fetch('/notifications/mark-all-read/', { method: 'POST', headers: { 'X-CSRFToken': getCsrfToken() } })
        .then(function() {
          updateBadge(0);
          loadDropdownNotifs();
        });
    });
  }
  if (markAllPage) {
    markAllPage.addEventListener('click', function() {
      fetch('/notifications/mark-all-read/', { method: 'POST', headers: { 'X-CSRFToken': getCsrfToken() } })
        .then(function() { location.reload(); });
    });
  }

  function loadDropdownNotifs() {
    fetch('/notifications/?format=json', { headers: { 'X-Requested-With': 'XMLHttpRequest' } })
      .then(function(res) { return res.json(); })
      .then(function(data) {
        if (!data || !data.notifications || data.notifications.length === 0) {
          notifList.innerHTML = '<div class="notif-dropdown-empty">No notifications</div>';
          return;
        }
        var html = '';
        data.notifications.slice(0, 10).forEach(function(n) {
          html += '<a class="notif-dropdown-item' + (n.is_read ? '' : ' unread') + '" href="' + (n.link || '#') + '" data-id="' + n.id + '">' +
            '<div class="notif-dropdown-icon"><i class="fas ' + n.icon + '"></i></div>' +
            '<div class="notif-dropdown-body">' +
            '<h4>' + escapeHtml(n.title) + '</h4>' +
            '<p>' + escapeHtml(n.message) + '</p>' +
            '<time>' + n.created_at + '</time>' +
            '</div></a>';
        });
        notifList.innerHTML = html;

        notifList.querySelectorAll('.notif-dropdown-item').forEach(function(item) {
          item.addEventListener('click', function() {
            var id = this.dataset.id;
            if (id) {
              fetch('/notifications/mark-read/' + id + '/', { method: 'POST', headers: { 'X-CSRFToken': getCsrfToken() } });
            }
            setTimeout(function() { notifDropdown.classList.remove('open'); }, 200);
          });
        });
      })
      .catch(function() {});
  }

  // Toast engine
  function showToast(type, title, message, icon, id) {
    var container = document.querySelector('.toast-container');
    if (!container) {
      container = document.createElement('div');
      container.className = 'toast-container';
      document.body.appendChild(container);
    }

    if (activeToasts.length >= MAX_VISIBLE) {
      toastQueue.push({ type: type, title: title, message: message, icon: icon, id: id });
      return;
    }

    var toast = document.createElement('div');
    toast.className = 'toast toast-' + type;
    toast.dataset.id = id || '';
    toast.innerHTML =
      '<div class="toast-icon"><i class="fas ' + icon + '"></i></div>' +
      '<div class="toast-body"><h4>' + escapeHtml(title) + '</h4><p>' + escapeHtml(message) + '</p></div>' +
      '<button class="toast-close" title="Dismiss">&times;</button>' +
      '<div class="toast-progress"></div>';

    container.appendChild(toast);
    activeToasts.push(toast);

    var closeBtn = toast.querySelector('.toast-close');
    closeBtn.addEventListener('click', function() { dismissToast(toast); });
    toast.addEventListener('click', function(e) {
      if (e.target === closeBtn || closeBtn.contains(e.target)) return;
      dismissToast(toast);
    });

    setTimeout(function() { dismissToast(toast); }, 6000);
  }

  function dismissToast(toast) {
    if (!toast.parentNode) return;
    toast.classList.add('toast-out');
    setTimeout(function() {
      if (toast.parentNode) toast.parentNode.removeChild(toast);
      var idx = activeToasts.indexOf(toast);
      if (idx > -1) activeToasts.splice(idx, 1);
      if (toastQueue.length > 0) {
        var next = toastQueue.shift();
        showToast(next.type, next.title, next.message, next.icon, next.id);
      }
    }, 300);
  }

  // Poll for new toasts
  function pollNewToasts() {
    fetch('/notifications/new/', { headers: { 'X-Requested-With': 'XMLHttpRequest' } })
      .then(function(res) { return res.json(); })
      .then(function(data) {
        if (data.toasts && data.toasts.length > 0) {
          data.toasts.forEach(function(t) {
            showToast(t.type, t.title, t.message, t.icon, t.id);
          });
          updateBadgeFromServer();
        }
      })
      .catch(function() {});
  }

  function updateBadgeFromServer() {
    fetch('/notifications/unread-count/', { headers: { 'X-Requested-With': 'XMLHttpRequest' } })
      .then(function(res) { return res.json(); })
      .then(function(data) { updateBadge(data.count); })
      .catch(function() {});
  }

  function updateBadge(count) {
    if (!notifBadge) return;
    if (count > 0) {
      notifBadge.textContent = count > 99 ? '99+' : count;
      notifBadge.style.display = 'flex';
    } else {
      notifBadge.style.display = 'none';
    }
  }

  function getCsrfToken() {
    var el = document.querySelector('[name=csrfmiddlewaretoken]');
    return el ? el.value : '';
  }

  function escapeHtml(str) {
    var div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
  }

  // Initial load
  updateBadgeFromServer();
  pollNewToasts();
  notifPollTimer = setInterval(pollNewToasts, 15000);

  window.addEventListener('beforeunload', function() {
    if (notifPollTimer) clearInterval(notifPollTimer);
  });
})();

// =============================================
// NOTIFICATION PAGE - Mark individual read
// =============================================
(function() {
  var markBtns = document.querySelectorAll('.notif-card-mark');
  markBtns.forEach(function(btn) {
    btn.addEventListener('click', function() {
      var id = this.dataset.id;
      var card = document.getElementById('notif-card-' + id);
      fetch('/notifications/mark-read/' + id + '/', { method: 'POST', headers: { 'X-CSRFToken': getCsrfToken() } })
        .then(function() {
          if (card) card.classList.remove('notif-unread');
          btn.remove();
        });
    });
  });

  function getCsrfToken() {
    var el = document.querySelector('[name=csrfmiddlewaretoken]');
    return el ? el.value : '';
  }
})();
