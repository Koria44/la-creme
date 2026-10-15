/**
 * LA CREME - Pastelería Artesanal
 * Manejo interactivo del Carrito de Compras (AJAX + Toasts + Fallback progresivo)
 */

document.addEventListener('DOMContentLoaded', function () {
    // Inicializar tooltips y popovers de Bootstrap si existen
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Función auxiliar para obtener el token CSRF de las cookies
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    const csrftoken = getCookie('csrftoken');

    // Función global para mostrar Toast de Bootstrap
    window.mostrarToast = function (mensaje, tipo = 'success') {
        const container = document.getElementById('toast-container-flotante');
        if (!container) return;

        const iconos = {
            'success': 'bi-check-circle-fill text-success',
            'warning': 'bi-exclamation-triangle-fill text-warning',
            'danger': 'bi-x-circle-fill text-danger',
            'info': 'bi-info-circle-fill text-info',
        };
        const icono = iconos[tipo] || iconos['info'];

        const toastId = 'toast-' + Date.now();
        const toastHtml = `
            <div id="${toastId}" class="toast align-items-center border-0 shadow-lg mb-2" role="alert" aria-live="assertive" aria-atomic="true">
                <div class="d-flex bg-white rounded">
                    <div class="toast-body d-flex align-items-center gap-2">
                        <i class="bi ${icono} fs-5"></i>
                        <span class="fw-semibold text-dark">${mensaje}</span>
                    </div>
                    <button type="button" class="btn-close me-2 m-auto" data-bs-dismiss="toast" aria-label="Cerrar"></button>
                </div>
            </div>
        `;
        container.insertAdjacentHTML('beforeend', toastHtml);

        const toastEl = document.getElementById(toastId);
        const bsToast = new bootstrap.Toast(toastEl, { delay: 3500 });
        bsToast.show();

        toastEl.addEventListener('hidden.bs.toast', function () {
            toastEl.remove();
        });
    };

    // Función para actualizar contador de carrito en el Navbar
    function actualizarContadorNavbar(totalItems) {
        const badges = document.querySelectorAll('.js-cart-count');
        badges.forEach(badge => {
            badge.textContent = totalItems;
            if (totalItems > 0) {
                badge.classList.remove('d-none');
            } else {
                badge.classList.add('d-none');
            }
        });
    }

    // 1. Interceptar formularios de AGREGAR AL CARRITO (.js-form-agregar-carrito)
    document.addEventListener('submit', function (e) {
        const form = e.target.closest('.js-form-agregar-carrito');
        if (!form) return;

        e.preventDefault();
        const submitBtn = form.querySelector('button[type="submit"]');
        const originalHtml = submitBtn ? submitBtn.innerHTML : '';

        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-1" role="status" aria-hidden="true"></span> Agregando...';
        }

        const formData = new FormData(form);

        fetch(form.action, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': csrftoken,
            }
        })
        .then(response => {
            if (!response.ok) throw new Error('Error en la respuesta del servidor');
            return response.json();
        })
        .then(data => {
            if (data.success) {
                mostrarToast(data.mensaje, 'success');
                actualizarContadorNavbar(data.total_items);

                if (submitBtn) {
                    submitBtn.innerHTML = '<i class="bi bi-check2"></i> ¡Agregado!';
                    setTimeout(() => {
                        submitBtn.disabled = false;
                        submitBtn.innerHTML = originalHtml;
                    }, 1800);
                }
            } else {
                mostrarToast(data.mensaje, 'warning');
                if (submitBtn) {
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = originalHtml;
                }
            }
        })
        .catch(err => {
            console.warn('Fallback a envío regular:', err);
            form.submit(); // Si falla fetch, envío normal progresivo
        });
    });

    // 2. Interceptar formularios de ACTUALIZAR CANTIDAD en el carrito (.js-form-actualizar-carrito)
    document.addEventListener('change', function (e) {
        const input = e.target.closest('.js-input-cantidad-carrito');
        if (!input) return;

        const form = input.closest('form');
        if (!form) return;

        const formData = new FormData(form);
        const filaProducto = input.closest('tr');

        fetch(form.action, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': csrftoken,
            }
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                mostrarToast(data.mensaje, 'info');
                actualizarContadorNavbar(data.total_items);

                // Actualizar subtotal en la fila
                if (filaProducto) {
                    const subtotalEl = filaProducto.querySelector('.js-item-subtotal');
                    if (subtotalEl) {
                        subtotalEl.textContent = '$' + Number(data.subtotal).toLocaleString('es-CL') + ' CLP';
                    }
                }

                // Actualizar total general
                const totalEl = document.querySelector('.js-cart-grand-total');
                if (totalEl) {
                    totalEl.textContent = '$' + Number(data.total_precio).toLocaleString('es-CL') + ' CLP';
                }

                if (data.cantidad === 0 && filaProducto) {
                    filaProducto.remove();
                }
            } else {
                mostrarToast(data.mensaje, 'warning');
            }
        })
        .catch(() => {
            form.submit();
        });
    });

    // 3. Interceptar ELIMINAR del carrito (.js-form-eliminar-carrito)
    document.addEventListener('submit', function (e) {
        const form = e.target.closest('.js-form-eliminar-carrito');
        if (!form) return;

        e.preventDefault();
        const fila = form.closest('tr');

        fetch(form.action, {
            method: 'POST',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': csrftoken,
            }
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                mostrarToast(data.mensaje, 'info');
                actualizarContadorNavbar(data.total_items);

                if (fila) {
                    fila.style.transition = 'all 0.3s ease';
                    fila.style.opacity = '0';
                    setTimeout(() => {
                        fila.remove();
                        // Si ya no quedan filas, recargar página para mostrar mensaje de carrito vacío
                        const tabla = document.querySelector('.tabla-carrito tbody');
                        if (tabla && tabla.children.length === 0) {
                            window.location.reload();
                        }
                    }, 300);
                }

                const totalEl = document.querySelector('.js-cart-grand-total');
                if (totalEl) {
                    totalEl.textContent = '$' + Number(data.total_precio).toLocaleString('es-CL') + ' CLP';
                }
            }
        })
        .catch(() => {
            form.submit();
        });
    });

    // 4. Ajuste rápido de stock en panel (.js-form-ajuste-stock)
    document.addEventListener('submit', function (e) {
        const form = e.target.closest('.js-form-ajuste-stock');
        if (!form) return;

        e.preventDefault();
        const btn = form.querySelector('button[type="submit"]');
        const originalText = btn ? btn.innerHTML : '';
        if (btn) btn.innerHTML = '<span class="spinner-border spinner-border-sm"></span>';

        const formData = new FormData(form);

        fetch(form.action, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': csrftoken,
            }
        })
        .then(res => res.json())
        .then(data => {
            if (btn) btn.innerHTML = originalText;
            if (data.success) {
                mostrarToast(data.mensaje, 'success');
                const badgeEl = form.closest('tr')?.querySelector('.js-stock-badge');
                if (badgeEl) {
                    badgeEl.textContent = data.nuevo_stock + ' un.';
                    if (data.esta_agotado) {
                        badgeEl.className = 'badge bg-danger js-stock-badge';
                    } else if (data.stock_bajo) {
                        badgeEl.className = 'badge bg-warning text-dark js-stock-badge';
                    } else {
                        badgeEl.className = 'badge bg-success js-stock-badge';
                    }
                }
            } else {
                mostrarToast(data.mensaje, 'danger');
            }
        })
        .catch(() => {
            form.submit();
        });
    });
});
