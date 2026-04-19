document.addEventListener('DOMContentLoaded', function() {
    // Quantity buttons
    const minusBtns = document.querySelectorAll('.quantity-btn.decrease');
    const plusBtns = document.querySelectorAll('.quantity-btn.increase');
    const removeBtns = document.querySelectorAll('.remove-item-btn');

    // Function to update cart item quantity
    function updateCartItemQuantity(itemId, action) {
        const quantityEl = document.querySelector(`#quantity-${itemId}`);
        let quantity = parseInt(quantityEl.textContent);
        
        if (action === 'increase') {
            quantity += 1;
        } else if (action === 'decrease' && quantity > 1) {
            quantity -= 1;
        } else if (action === 'decrease' && quantity <= 1) {
            return; // Don't decrease below 1
        }
        
        quantityEl.textContent = quantity;
        
        const formData = new FormData();
        formData.append('quantity', quantity);

        // Get CSRF token
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

        // Make AJAX request
        fetch(`/cart/update/${itemId}/`, {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': csrfToken
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Update item total price
                document.getElementById(`item-total-${itemId}`).textContent = `$${data.item_total.toFixed(2)}`;

                // Update cart subtotal
                document.getElementById('subtotal').textContent = `$${data.cart_subtotal.toFixed(2)}`;

                // Update cart total
                document.getElementById('total').textContent = `$${data.cart_total.toFixed(2)}`;
            } else {
                console.error(data.error);
                // Revert quantity change if there was an error
                quantityEl.textContent = action === 'increase' ? quantity - 1 : quantity + 1;
            }
        })
        .catch(error => {
            console.error('Error updating cart:', error);
            // Revert quantity change if there was an error
            quantityEl.textContent = action === 'increase' ? quantity - 1 : quantity + 1;
        });
    }

    // Add event listeners to minus buttons
    minusBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const itemId = this.dataset.itemId;
            updateCartItemQuantity(itemId, 'decrease');
        });
    });

    // Add event listeners to plus buttons
    plusBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const itemId = this.dataset.itemId;
            updateCartItemQuantity(itemId, 'increase');
        });
    });

    // Add event listeners to remove buttons
    removeBtns.forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            
            const itemId = this.dataset.itemId;
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
            
            if (confirm('Are you sure you want to remove this item from your cart?')) {
                // Create a form and submit it
                const form = document.createElement('form');
                form.method = 'POST';
                form.action = `/cart/remove/${itemId}/`;
                
                const csrfInput = document.createElement('input');
                csrfInput.type = 'hidden';
                csrfInput.name = 'csrfmiddlewaretoken';
                csrfInput.value = csrfToken;
                
                form.appendChild(csrfInput);
                document.body.appendChild(form);
                form.submit();
            }
        });
    });
});