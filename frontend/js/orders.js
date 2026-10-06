/**
 * KrushiSetu Orders, Messaging & Reviews Client Manager
 */

const OrdersManager = {
  // Fetch orders for current authenticated user
  async getOrders() {
    return await API.request('/api/orders/');
  },

  // Fetch single order details
  async getOrder(orderId) {
    return await API.request(`/api/orders/${orderId}`);
  },

  // Place new order (Buyer)
  async placeOrder(productId, quantity, deliveryAddress, logisticsPref) {
    return await API.request('/api/orders/', {
      method: 'POST',
      body: {
        product_id: productId,
        quantity: parseFloat(quantity),
        delivery_address: deliveryAddress,
        logistics_preference: logisticsPref
      }
    });
  },

  // Update order status (Farmer: Accept/Reject/Processing/Shipped; Buyer: Cancel/Delivered)
  async updateStatus(orderId, newStatus) {
    return await API.request(`/api/orders/${orderId}/status`, {
      method: 'PATCH',
      body: { status: newStatus }
    });
  }
};

const MessagesManager = {
  // Send message
  async sendMessage(recipientId, content, productId = '', orderId = '') {
    return await API.request('/api/messages/send', {
      method: 'POST',
      body: {
        recipient_id: recipientId,
        content: content,
        product_id: productId,
        order_id: orderId
      }
    });
  },

  // Get conversations
  async getConversations() {
    return await API.request('/api/messages/conversations');
  },

  // Get thread with specific user
  async getThread(otherUserId) {
    return await API.request(`/api/messages/thread/${otherUserId}`);
  }
};

const ReviewsManager = {
  // Submit verified review for delivered/completed order
  async submitReview(orderId, rating, comment) {
    return await API.request('/api/reviews/', {
      method: 'POST',
      body: {
        order_id: orderId,
        rating: parseInt(rating, 10),
        comment: comment
      }
    });
  },

  // Get product reviews
  async getProductReviews(productId) {
    return await API.request(`/api/reviews/product/${productId}`, { includeAuth: false });
  },

  // Get farmer reviews
  async getFarmerReviews(farmerId) {
    return await API.request(`/api/reviews/farmer/${farmerId}`, { includeAuth: false });
  }
};
