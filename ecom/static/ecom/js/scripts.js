document.addEventListener('DOMContentLoaded', function () {
    const updateAddToCartUrl = (productId) => {
        const quantityInput = document.querySelector(`input.quantity[data-product-id="${productId}"]`);
        const addToCartBtn = document.querySelector(`a.add-to-cart-btn[data-product-id="${productId}"]`);
        const quantity = quantityInput.value;
        const baseUrl = addToCartBtn.dataset.cartUrl;
        addToCartBtn.href = `${baseUrl}?quantity=${quantity}`;
    };

    const updateAddToOrderUrl = (productId) => {
        const quantityInput = document.querySelector(`input.quantity[data-product-id="${productId}"]`);
        const addToOrderBtn = document.querySelector(`a.add-to-order-btn[data-product-id="${productId}"]`);
        const quantity = quantityInput.value;
        const baseUrl = addToOrderBtn.dataset.orderUrl;
        addToOrderBtn.href = `${baseUrl}?quantity=${quantity}`;
    };

    document.querySelectorAll('.btn-minus').forEach(button => {
        button.addEventListener('click', () => {
            const productId = button.getAttribute('data-product-id');
            const quantityInput = document.querySelector(`input.quantity[data-product-id="${productId}"]`);
            if (quantityInput.value > 1) {
                quantityInput.value = parseInt(quantityInput.value) - 1;
                updateAddToCartUrl(productId);
                updateAddToOrderUrl(productId);
            }
        });
    });

    document.querySelectorAll('.btn-plus').forEach(button => {
        button.addEventListener('click', () => {
            const productId = button.getAttribute('data-product-id');
            const quantityInput = document.querySelector(`input.quantity[data-product-id="${productId}"]`);
            quantityInput.value = parseInt(quantityInput.value) + 1;
            updateAddToCartUrl(productId);
            updateAddToOrderUrl(productId);
        });
    });

    // Ensure URLs are updated on initial page load
    document.querySelectorAll('input.quantity').forEach(input => {
        const productId = input.getAttribute('data-product-id');
        updateAddToCartUrl(productId);
        updateAddToOrderUrl(productId);
    });
});
