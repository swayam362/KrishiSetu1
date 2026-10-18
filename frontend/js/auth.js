/**
 * KrushiSetu Authentication Logic (Login & Register)
 * Connected to secure Flask Backend & JWT
 */

document.addEventListener('DOMContentLoaded', () => {
  // Check if session expired message is needed
  const urlParams = new URLSearchParams(window.location.search);
  if (urlParams.get('expired') === '1') {
    showToast('Your session has expired. Please sign in again.', 'error');
  }

  // Auto-select role from query param if provided (e.g. ?role=buyer)
  const roleParam = urlParams.get('role');
  if (roleParam) {
    const targetBtn = document.querySelector(`.role-select-btn[data-role="${roleParam}"]`);
    if (targetBtn) {
      targetBtn.click();
    }
  }

  // Role selector buttons
  const roleButtons = document.querySelectorAll('.role-select-btn');
  const roleInput = document.getElementById('selected-role');
  const dynamicFarmerFields = document.querySelectorAll('.farmer-only-field');
  const dynamicBuyerFields = document.querySelectorAll('.buyer-only-field');

  if (roleButtons.length > 0) {
    roleButtons.forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.preventDefault();
        roleButtons.forEach(b => b.classList.remove('active', 'btn-primary'));
        roleButtons.forEach(b => b.classList.add('btn-outline'));
        
        btn.classList.add('active', 'btn-primary');
        btn.classList.remove('btn-outline');
        
        const selected = btn.getAttribute('data-role');
        if (roleInput) roleInput.value = selected;

        // Toggle role specific fields
        if (selected === 'farmer') {
          dynamicFarmerFields.forEach(f => f.style.display = 'block');
          dynamicBuyerFields.forEach(f => f.style.display = 'none');
        } else {
          dynamicFarmerFields.forEach(f => f.style.display = 'none');
          dynamicBuyerFields.forEach(f => f.style.display = 'block');
        }
      });
    });
  }

  // Handle Login Form Submission
  const loginForm = document.getElementById('login-form');
  const loginBtn = document.getElementById('login-submit-btn');
  const loginErrorBox = document.getElementById('login-error-box');

  if (loginForm) {
    loginForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      if (loginErrorBox) loginErrorBox.style.display = 'none';

      const email = document.getElementById('email').value.trim();
      const password = document.getElementById('password').value;
      const role = roleInput ? roleInput.value : 'farmer';

      if (loginBtn) {
        loginBtn.disabled = true;
        loginBtn.innerText = 'Authenticating...';
      }

      try {
        const response = await API.login({
          identifier: email,
          password: password,
          role: role
        });

        API.setToken(response.token);
        KrushiAuth.setUser(response.user);

        showToast(`Welcome back, ${response.user.full_name || 'User'}!`, 'success');
        
        setTimeout(() => {
          if (response.user.role === 'admin') {
            window.location.href = 'admin-dashboard.html';
          } else if (response.user.role === 'buyer') {
            window.location.href = 'buyer-dashboard.html';
          } else {
            window.location.href = 'farmer-dashboard.html';
          }
        }, 600);

      } catch (err) {
        if (loginErrorBox) {
          loginErrorBox.innerText = err.message || 'Login failed. Please verify credentials.';
          loginErrorBox.style.display = 'block';
        }
        showToast(err.message || 'Login failed.', 'error');
      } finally {
        if (loginBtn) {
          loginBtn.disabled = false;
          loginBtn.innerText = 'Sign In to Dashboard →';
        }
      }
    });
  }

  // Handle Register Form Submission
  const registerForm = document.getElementById('register-form');
  const registerBtn = document.getElementById('register-submit-btn');
  const regErrorBox = document.getElementById('reg-error-box');

  if (registerForm) {
    registerForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      if (regErrorBox) regErrorBox.style.display = 'none';

      const role = roleInput ? roleInput.value : 'farmer';
      const fullName = document.getElementById('fullName').value.trim();
      const email = document.getElementById('regEmail').value.trim();
      const phone = document.getElementById('regPhone').value.trim();
      const password = document.getElementById('regPassword').value;
      const state = document.getElementById('regState').value.trim();
      const district = document.getElementById('regDistrict').value.trim();

      const payload = {
        role,
        full_name: fullName,
        email,
        phone,
        password,
        state,
        district
      };

      if (role === 'farmer') {
        payload.village = document.getElementById('regVillage')?.value.trim() || '';
        payload.farm_size_acres = document.getElementById('farmSize')?.value.trim() || '';
        payload.primary_crops = document.getElementById('primaryCrops')?.value.trim() || '';
      } else {
        payload.business_name = document.getElementById('businessName')?.value.trim() || '';
        payload.city = document.getElementById('regCity')?.value.trim() || '';
        payload.gstin = document.getElementById('gstin')?.value.trim() || '';
      }

      if (registerBtn) {
        registerBtn.disabled = true;
        registerBtn.innerText = 'Creating Account...';
      }

      try {
        const response = await API.register(payload);

        API.setToken(response.token);
        KrushiAuth.setUser(response.user);

        showToast(`Registration complete! Welcome ${response.user.full_name}!`, 'success');

        setTimeout(() => {
          if (response.user.role === 'buyer') {
            window.location.href = 'buyer-dashboard.html';
          } else {
            window.location.href = 'farmer-dashboard.html';
          }
        }, 600);

      } catch (err) {
        if (regErrorBox) {
          regErrorBox.innerText = err.message || 'Registration failed.';
          regErrorBox.style.display = 'block';
        }
        showToast(err.message || 'Registration failed.', 'error');
      } finally {
        if (registerBtn) {
          registerBtn.disabled = false;
          registerBtn.innerText = 'Complete Registration →';
        }
      }
    });
  }
});
