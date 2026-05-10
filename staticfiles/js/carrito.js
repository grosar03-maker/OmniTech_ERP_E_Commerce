/**
 * OmniTech Cart System
 * Manejo del carrito de compras con AJAX
 */

document.addEventListener('DOMContentLoaded', function() {
    actualizarContadorCarrito();
});

/**
 * Actualiza el contador del carrito en el navbar
 */
function actualizarContadorCarrito() {
    fetch('/carrito/')
        .then(response => response.text())
        .then(html => {
            const parser = new DOMParser();
            const doc = parser.parseFromString(html, 'text/html');
            const cartCount = doc.querySelector('#cartCount');
            if (cartCount) {
                document.getElementById('cartCount').textContent = cartCount.textContent;
            }
        })
        .catch(() => {});
}

/**
 * Agrega un producto al carrito
 */
function agregarAlCarrito(productoId, tipo, cantidad = 1) {
    const data = {
        producto_id: productoId,
        tipo: tipo,
        cantidad: cantidad
    };

    fetch('/carrito/agregar/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            document.getElementById('cartCount').textContent = data.carrito_count;
            mostrarToast(data.message, 'success');
            
            const cartBtn = document.querySelector('.cart-btn');
            if (cartBtn) {
                cartBtn.classList.add('pulse');
                setTimeout(() => cartBtn.classList.remove('pulse'), 500);
            }
        } else {
            mostrarToast(data.error || 'Error al agregar al carrito', 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        mostrarToast('Error al procesar la solicitud', 'error');
    });
}

/**
 * Actualiza la cantidad de un producto en el carrito
 */
function actualizarCantidad(productoId, tipo, cantidad) {
    if (cantidad < 1) {
        eliminarItem(productoId, tipo);
        return;
    }

    const data = {
        producto_id: productoId,
        tipo: tipo,
        cantidad: cantidad
    };

    fetch('/carrito/actualizar/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            location.reload();
        } else {
            mostrarToast(data.error || 'Error al actualizar', 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        mostrarToast('Error al procesar la solicitud', 'error');
    });
}

/**
 * Elimina un producto del carrito
 */
function eliminarItem(productoId, tipo) {
    const data = {
        producto_id: productoId,
        tipo: tipo
    };

    fetch('/carrito/eliminar/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            location.reload();
        } else {
            mostrarToast(data.error || 'Error al eliminar', 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        mostrarToast('Error al procesar la solicitud', 'error');
    });
}

/**
 * Vacía el carrito completamente
 */
function vaciarCarrito() {
    if (!confirm('¿Estás seguro de que quieres vaciar el carrito?')) {
        return;
    }

    fetch('/carrito/vaciar/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({})
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            location.reload();
        } else {
            mostrarToast(data.error || 'Error al vaciar', 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        mostrarToast('Error al procesar la solicitud', 'error');
    });
}

/**
 * Obtiene el token CSRF de las cookies
 */
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

/**
 * Muestra un toast notification
 */
function mostrarToast(message, type = 'info') {
    const container = document.querySelector('.messages-container') || createMessagesContainer();
    
    const toast = document.createElement('div');
    toast.className = `message ${type} glass-message`;
    toast.innerHTML = `
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            ${type === 'success' ? '<polyline points="20 6 9 17 4 12"/>' : ''}
            ${type === 'error' ? '<circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/>' : ''}
            ${type === 'warning' ? '<circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>' : ''}
        </svg>
        <span>${message}</span>
    `;
    
    container.appendChild(toast);
    
    setTimeout(() => {
        toast.style.animation = 'slideOut 0.3s ease forwards';
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

/**
 * Crea el contenedor de mensajes si no existe
 */
function createMessagesContainer() {
    const container = document.createElement('div');
    container.className = 'messages-container';
    container.style.cssText = 'position: fixed; top: 80px; right: 16px; z-index: 1001; display: flex; flex-direction: column; gap: 8px;';
    document.body.appendChild(container);
    return container;
}

/**
 * Animación de salida para toasts
 */
const styleSheet = document.createElement('style');
styleSheet.textContent = `
    @keyframes slideOut {
        to {
            opacity: 0;
            transform: translateX(100px);
        }
    }
    
    .cart-btn.pulse {
        animation: pulse 0.5s ease;
    }
    
    @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.2); }
    }
`;
document.head.appendChild(styleSheet);

/**
 * Formateador de precios
 */
function formatPrice(price) {
    return '$' + parseFloat(price).toLocaleString('es-CL');
}

/**
 * Animación de scroll suave para enlaces internos
 */
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
        const href = this.getAttribute('href');
        if (href === '#') return;
        
        e.preventDefault();
        const target = document.querySelector(href);
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth'
            });
        }
    });
});

/**
 * Lazy loading para imágenes
 */
if ('IntersectionObserver' in window) {
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                if (img.dataset.src) {
                    img.src = img.dataset.src;
                    img.removeAttribute('data-src');
                }
                observer.unobserve(img);
            }
        });
    });

    document.querySelectorAll('img[data-src]').forEach(img => {
        imageObserver.observe(img);
    });
}
