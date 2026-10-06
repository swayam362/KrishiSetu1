/**
 * KrushiSetu Products Management & Dashboard Integration
 */

const ProductsManager = {
  // Upload crop image and return uploaded file path
  async uploadImage(fileInput) {
    const file = fileInput.files[0];
    if (!file) return null;

    const formData = new FormData();
    formData.append('image', file);

    const token = API.getToken();
    const response = await fetch('/api/products/upload-image', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`
      },
      body: formData
    });

    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.error || 'Failed to upload crop image.');
    }
    return data.image_url;
  },

  // Create new product
  async createProduct(formData, imageFile) {
    let imageUrl = null;
    if (imageFile && imageFile.files && imageFile.files[0]) {
      try {
        imageUrl = await this.uploadImage(imageFile);
      } catch (err) {
        showToast(`Image upload warning: ${err.message}. Using default crop image.`, 'warning');
      }
    }

    const payload = {
      crop_name: formData.get('crop_name'),
      category: formData.get('category'),
      quantity: parseFloat(formData.get('quantity')),
      unit: formData.get('unit') || 'kg',
      expected_price: parseFloat(formData.get('expected_price')),
      grade: formData.get('grade') || 'Grade A',
      harvest_date: formData.get('harvest_date') || new Date().toISOString().split('T')[0],
      description: formData.get('description') || '',
      organic: formData.get('organic') === 'true' || formData.get('organic') === 'on',
      images: imageUrl ? [imageUrl] : undefined
    };

    return await API.request('/api/products/', {
      method: 'POST',
      body: payload
    });
  },

  // Update existing product
  async updateProduct(productId, updates) {
    return await API.request(`/api/products/${productId}`, {
      method: 'PUT',
      body: updates
    });
  },

  // Delete product
  async deleteProduct(productId) {
    return await API.request(`/api/products/${productId}`, {
      method: 'DELETE'
    });
  },

  // Fetch farmer's own products
  async getMyProducts() {
    return await API.request('/api/products/farmer/my-products');
  },

  // Fetch public marketplace products
  async getMarketplaceProducts(params = {}) {
    const query = new URLSearchParams(params).toString();
    return await API.request(`/api/products/?${query}`, { includeAuth: false });
  },

  // Fetch single product details
  async getProductDetails(productId) {
    return await API.request(`/api/products/${productId}`, { includeAuth: false });
  }
};
