$(document).ready(function() {
    const Toast = Swal.mixin({
        toast: true,
        position: 'top-end',
        showConfirmButton: false,
        timer: 20000,
        timerProgressBar: true,
    });

    function generatecartId() {
        let cartId = localStorage.getItem('cartId');
        if (!cartId) {
            cartId = "";
            for (let i = 0; i < 10; i++) {
                cartId += Math.floor(Math.random() * 10);
            }
            localStorage.setItem('cartId', cartId);
        }
        return cartId;
    }

    $(document).on("click", ".add_to_cart", function() {
        const button_el = $(this);
        let quantityInput = document.getElementById("quantity");
        let quantity = parseInt(quantityInput.value);

        const id = button_el.attr("data-id");
        const size = $("input[name='size']:checked").val() || '';
        const color = $("input[name='color']:checked").val() || '';
        const cart_Id = generatecartId();

        $.ajax({
            url: "/add_to_cart/",
            data: {
                id: id,
                quantity: quantity,
                size: size,
                color: color,
                cart_id: cart_Id
            },
            beforeSend: function() {
                button_el.html("Adding to cart <i class='fa fa-spinner fa-spin ms-2'></i>");
            },
            success: function(response) {
                console.log(response);
                Toast.fire({
                    icon: 'success',
                    title: response.message,
                });
                button_el.html("Add to cart <i class='fa fa-shopping fa-spin ms-2'></i>");
                $(".total_cart_items").text(quantity);
            },
            error: function(xhr, status, error) {
                console.log("Error status", xhr.status);
                console.log("Error Text", xhr.statusText);

                let error_message;
                try {
                    error_message = JSON.parse(xhr.responseText);
                } catch (e) {
                    error_message = { error: "An unexpected error occurred" };
                }
                Toast.fire({
                    icon: "error",
                    title: error_message?.error,
                });
            }
        });
        console.log(cart_Id, id, quantity, size, color);
    });





    $(document).on("click", ".update_cart_qty", function() {
    const button_el = $(this);
    const update_type = button_el.attr("data-update_type");
    const item_id = button_el.attr("data-item_id");
    const product_id = button_el.attr("data-product_id");
    let qty = parseInt($(".item-qty-" + item_id).val()); // Get current quantity
    const cart_Id = generatecartId(); // Ensure this function is defined

    // Update quantity based on the button clicked
    if (update_type === 'increase') {
        qty;
    } else if (update_type === 'decrease') {
        qty = Math.max(1, qty); // Ensure quantity doesn't go below 1
    }
    $(".item-qty-" + item_id).val(qty); // Update the input field

    // Get size and color (if applicable)
    const size = $(".item_div_" + item_id).find("input[name='size']:checked").val() || '';
    const color = $(".item_div_" + item_id).find("input[name='color']:checked").val() || '';

    console.log(update_type, item_id, product_id, qty, cart_Id);

    $.ajax({
        url: "/add_to_cart/",
        data: {
            id: product_id,
            quantity: qty,
            size: size,
            color: color,
            cart_id: cart_Id
        },
        beforeSend: function() {
            button_el.html("<i class='fa fa-spinner fa-spin ms-2'></i>");
        },
        success: function(response) {
            console.log(response);
            Toast.fire({
                icon: 'success',
                title: response.message,
            });

            // Reset the button state
            if (update_type === 'increase') {
                button_el.html("<i class='fa fa-plus'></i>");
            } else if (update_type === 'decrease') {
                button_el.html("<i class='fa fa-minus'></i>");
            }

            // Update the UI
            $(".item_sub_total_" + item_id).text(response.item_sub_total);
            $(".cart_sub_total").text(response.cart_sub_total); // Ensure this selector is correct
        },
        error: function(xhr, status, error) {
            console.log("Error status", xhr.status);
            console.log("Error Text", xhr.statusText);

            let error_message;
            try {
                error_message = JSON.parse(xhr.responseText);
            } catch (e) {
                error_message = { error: "An unexpected error occurred" };
            }
            Toast.fire({
                icon: "error",
                title: error_message?.error,
            });

            // Reset the button state on error
            if (update_type === 'increase') {
                button_el.html("<i class='fa fa-plus'></i>");
            } else if (update_type === 'decrease') {
                button_el.html("<i class='fa fa-minus'></i>");
            }
        }
    });
});

    // $(document).on("click", ".update_cart_qty", function() {
    //     const button_el = $(this);
    //     const update_type = button_el.attr("data-update_type");
    //     const item_id = button_el.attr("data-item_id");
    //     const product_id = button_el.attr("data-product_id");
    //     const previous_qty = parseInt(button_el.attr("data-item_qty")); // Parse as integer
    //     const cart_Id = generatecartId();
    //     let qty = previous_qty; // Use let instead of const
    
    //     console.log(update_type, item_id, product_id, previous_qty, qty, cart_Id);
    
    //     // Update the quantity based on the update_type
    //     if (update_type === 'increase') {
    //         qty += 1;
    //     } else if (update_type === 'decrease') {
    //         qty = Math.max(1, qty - 1); // Ensure quantity doesn't go below 1
    //     }
    
    //     // Update the quantity in the input field
    //     $(".item-qty-" + item_id).val(qty);
    
    //     // Send AJAX request to update the cart
    //     $.ajax({
    //         url: "/add_to_cart/",
    //         method: "GET", // Ensure this matches your backend
    //         data: {
    //             item_id: item_id,
    //             product_id: product_id,
    //             qty: qty, // Send the updated quantity
    //             cart_id: cart_Id
    //         },
    //         beforeSend: function() {
    //             button_el.prop("disabled", true).html("<i class='fa fa-spinner fa-spin ms-2'></i>");
    //         },
    //         success: function(response) {
    //             console.log(response);
    //             Toast.fire({
    //                 icon: 'success',
    //                 title: response.message,
    //             });
    
    //             // Update the subtotal and total cart items
    //             $(".item_sub_total_" + item_id).text(response.item_sub_total);
    //             $(".cart_sub_total").text(response.cart_sub_total);
    //         },
    //         error: function(xhr) {
    //             console.log("Error status", xhr.status);
    //             console.log("Error Text", xhr.statusText);
    
    //             let error_message;
    //             try {
    //                 error_message = JSON.parse(xhr.responseText);
    //             } catch (e) {
    //                 error_message = { error: "An unexpected error occurred" };
    //             }
    //             Toast.fire({
    //                 icon: "error",
    //                 title: error_message?.error || "Failed to update cart",
    //             });
    //         },
    //         complete: function() {
    //             button_el.prop("disabled", false).html(update_type === 'increase' ? "+" : "-");
    //         }
    //     });
    // });

    
    $(document).ready(function() {
        $(document).on("click", ".delete_cart_item", function() {
            const button_el = $(this);
            const item_id = button_el.attr("data-item_id");
            const cart_Id = generatecartId(); // Ensure this function is defined and works correctly
    
            $.ajax({
                url: "/delete_cart_item/",
                data: {
                    item_id: item_id,
                    cart_id: cart_Id
                },
                beforeSend: function() {
                    button_el.html("Removing <i class='fa fa-spinner fa-spin ms-2'></i>");
                },
                success: function(response) {
                    console.log(response);
                    Toast.fire({
                        icon: 'success',
                        title: response.message,
                    });
                    
                    $(".total_cart_items").text(response.total_cart_items);
                    $(".cart_sub_total").text(response.cart_sub_total);
                    $(".item_div_" + item_id).addClass("d-none");
                },
                error: function(xhr) {
                    console.log("Error status", xhr.status);
                    console.log("Error Text", xhr.statusText);
    
                    let error_message;
                    try {
                        error_message = JSON.parse(xhr.responseText);
                    } catch (e) {
                        error_message = { error: "An unexpected error occurred" };
                    }
                    Toast.fire({
                        icon: "error",
                        title: error_message?.error,
                    });
                }
            });
        });
    });



    $(document).on("click", ".remove_from_wishlist", function (e) {
        e.preventDefault();
        const button = $(this);
        const item_id = button.attr("data-item_id");
    
        $.ajax({
            url: `/remove_from_wishlist/${item_id}/`,
            method: "GET", // Ensure this matches your view's expected method
            beforeSend: function () {
                button.html("<i class='fas fa-spinner fa-spin'></i>");
            },
            success: function (response) {
                // Remove the card from the DOM
                button.closest(".col-lg-3").remove();
                Toast.fire({
                    icon: "success",
                    title: "Item removed from wishlist",
                });
                
                $(".total_cart_items").text(response.total_cart_items);
                $(".cart_sub_total").text(response.cart_sub_total);
                $(".item_div_" + item_id).addClass("d-none");
            },
            error: function (xhr) {
                console.log("Error status", xhr.status);
                console.log("Error Text", xhr.statusText);
    
                let error_message;
                try {
                    error_message = JSON.parse(xhr.responseText);
                } catch (e) {
                    error_message = { error: "An unexpected error occurred" };
                }
                Toast.fire({
                    icon: "error",
                    title: error_message?.error || "An unexpected error occurred",
                });
            },
        });
    });


    $(document).ready(function () {
        // Initialize Toast (assuming you're using SweetAlert2 for Toast notifications)
        const Toast = Swal.mixin({
            toast: true,
            position: 'top-end',
            showConfirmButton: false,
            timer: 3000,
            timerProgressBar: true,
            didOpen: (toast) => {
                toast.addEventListener('mouseenter', Swal.stopTimer);
                toast.addEventListener('mouseleave', Swal.resumeTimer);
            }
        });
    
        // Add to Wishlist Click Event
        $(document).on("click", ".add_to_wishlist", function () {
            const button = $(this);
            const product_id = button.attr("data-product_id"); // Get product ID from data attribute
            console.log("Product ID:", product_id);
    
            // Disable the button to prevent multiple clicks
            button.prop("disabled", true);
    
            // Show loading spinner
            const heartIcon = button.find("i"); // Get the <i> element inside the button
            heartIcon.removeClass("far fa-heart").addClass("fas fa-spinner fa-spin");
    
            // AJAX request to add product to wishlist
            $.ajax({
                url: `add_to_wishlist/${product_id}/`, // URL to your Django view
                method: "GET", // Use GET or POST based on your backend implementation
                dataType: "json", // Expect JSON response
                success: function (response) {
                    console.log("Response:", response);
    
                    // Update button icon to indicate success
                    heartIcon.removeClass("fas fa-spinner fa-spin").addClass("fas fa-heart");
    
                    // Show Toast notification based on response
                    if (response.message === "User is not logged in") {
                        Toast.fire({
                            icon: "warning",
                            title: response.message,
                        });
                        // Revert to the empty heart icon if the user is not logged in
                        heartIcon.removeClass("fas fa-heart").addClass("far fa-heart");
                    } else {
                        Toast.fire({
                            icon: "success",
                            title: response.message,
                        });
                    }
                },
                error: function (xhr, status, error) {
                    console.error("Error:", error);
    
                    // Update button icon to indicate failure
                    heartIcon.removeClass("fas fa-spinner fa-spin").addClass("far fa-heart");
    
                    // Show error Toast notification
                    Toast.fire({
                        icon: "error",
                        title: "An error occurred while adding to wishlist.",
                    });
                },
                complete: function () {
                    // Re-enable the button after the request is complete
                    button.prop("disabled", false);
                }
            });
        });
    });
//already exists


});


