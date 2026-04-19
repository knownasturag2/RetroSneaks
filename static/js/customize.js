document.addEventListener('DOMContentLoaded', function() {
    // Elements
    const shoeSelect = document.getElementById('id_shoe');
    const baseColorSelect = document.getElementById('id_base_color');
    const accentColorSelect = document.getElementById('id_accent_color');
    const patternSelect = document.getElementById('id_sole_pattern');
    const quantityInput = document.getElementById('id_quantity');
    const priceDisplay = document.getElementById('total-price');
    const basePrice = document.getElementById('base-price');
    const customizationPrice = document.getElementById('customization-price');
    const shoeImage = document.getElementById('shoe-preview');

    // Color circles
    const baseColorCircles = document.querySelectorAll('.base-color-circle');
    const accentColorCircles = document.querySelectorAll('.accent-color-circle');
    const patternButtons = document.querySelectorAll('.pattern-btn');

    // Function to update price
    function updatePrice() {
        const shoeId = shoeSelect.value;
        const baseColorId = baseColorSelect.value;
        const accentColorId = accentColorSelect.value;
        const patternId = patternSelect.value;
        const quantity = quantityInput.value;

        if (!shoeId) {
            return;
        }

        // Make AJAX request to get price
        fetch(`/api/calculate-customization-price/?shoe_id=${shoeId}&base_color_id=${baseColorId}&accent_color_id=${accentColorId}&pattern_id=${patternId}&quantity=${quantity}`)
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    console.error(data.error);
                    return;
                }

                // Update price displays
                basePrice.textContent = `$${data.base_price.toFixed(2)}`;
                customizationPrice.textContent = `$${data.customization_price.toFixed(2)}`;
                priceDisplay.textContent = `$${data.total_price.toFixed(2)}`;
            })
            .catch(error => {
                console.error('Error calculating price:', error);
            });
    }

    // Function to update shoe image
    function updateShoeImage() {
        const shoeId = shoeSelect.value;

        if (!shoeId) {
            shoeImage.src = '/static/img/placeholder.png';
            return;
        }

        // Fetch the image URL from the server
        fetch(`/api/get-shoe-image/?shoe_id=${shoeId}`)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    shoeImage.src = data.image_url;
                } else {
                    console.error(data.error);
                    shoeImage.src = '/static/img/placeholder.png';
                }
            })
            .catch(error => {
                console.error('Error fetching shoe image:', error);
                shoeImage.src = '/static/img/placeholder.png';
            });
    }

    // Add event listeners
    if (shoeSelect) {
        shoeSelect.addEventListener('change', function() {
            updatePrice();
            updateShoeImage();
        });
    }

    if (baseColorSelect) {
        baseColorSelect.addEventListener('change', updatePrice);
    }

    if (accentColorSelect) {
        accentColorSelect.addEventListener('change', updatePrice);
    }

    if (patternSelect) {
        patternSelect.addEventListener('change', updatePrice);
    }

    if (quantityInput) {
        quantityInput.addEventListener('change', updatePrice);
    }

    // Color circle selection
    baseColorCircles.forEach(circle => {
        circle.addEventListener('click', function() {
            // Remove selected class from all circles
            baseColorCircles.forEach(c => c.classList.remove('selected'));
            // Add selected class to clicked circle
            this.classList.add('selected');
            // Update hidden input value
            baseColorSelect.value = this.dataset.colorId;
            // Update price
            updatePrice();
        });
    });

    accentColorCircles.forEach(circle => {
        circle.addEventListener('click', function() {
            // Remove selected class from all circles
            accentColorCircles.forEach(c => c.classList.remove('selected'));
            // Add selected class to clicked circle
            this.classList.add('selected');
            // Update hidden input value
            accentColorSelect.value = this.dataset.colorId;
            // Update price
            updatePrice();
        });
    });

    patternButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Remove selected class from all buttons
            patternButtons.forEach(b => b.classList.remove('selected'));
            // Add selected class to clicked button
            this.classList.add('selected');
            // Update hidden input value
            patternSelect.value = this.dataset.patternId;
            // Update price
            updatePrice();
        });
    });

    // Initialize
    if (shoeSelect && shoeSelect.value) {
        updatePrice();
        updateShoeImage();
    }
});