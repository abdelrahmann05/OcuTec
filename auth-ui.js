// تعريف المسارات الأساسية
const ROUTES = {
    HOME: '/',
    LOGIN: '/login.html',
    SIGNUP: '/signup.html',  // تعديل المسار
    DASHBOARD: '/dashboard/Dshboard.html'
};

document.addEventListener("DOMContentLoaded", () => {
  const loginBtn = document.getElementById('login-btn');
  const signupBtn = document.getElementById('signup-btn');
  const adminLink = document.getElementById('admin-dashboard-link');

  const token = localStorage.getItem("token");
  const email = localStorage.getItem("email"); // كنا خزناه بعد تسجيل الدخول

  if (token && email) {
    console.log("✅ مستخدم مسجل الدخول:", email);

    if (loginBtn) loginBtn.style.display = 'none';
    if (signupBtn) signupBtn.style.display = 'none';

    if (adminLink) {
      const adminEmails = ["bassantmajdi@gmail.com"];
      adminLink.style.display = adminEmails.includes(email) ? 'flex' : 'none';
    }

    // لو المستخدم على login.html، نحوله للرئيسية
    if (window.location.pathname.includes('login.html')) {
      window.location.href = ROUTES.HOME;
    }

    // إضافة زر تسجيل الخروج للمستخدمين المسجلين
    const logoutBtn = document.createElement('button');
    logoutBtn.textContent = 'Log out';
    logoutBtn.onclick = logout;
    document.querySelector('.nav').appendChild(logoutBtn);

  } else {
    console.log("❌ لا يوجد مستخدم مسجل");

    if (loginBtn) loginBtn.style.display = 'flex';
    if (signupBtn) signupBtn.style.display = 'flex';
    if (adminLink) adminLink.style.display = 'none';
  }
});

// Handle signup form submission
document.addEventListener('DOMContentLoaded', () => {
    const signupForm = document.getElementById('signup-form');
    if (signupForm) {
        signupForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const formData = {
                email: document.getElementById('email').value,
                password: document.getElementById('password').value,
                firstName: document.getElementById('fn').value,
                lastName: document.getElementById('ln').value,
                dateOfBirth: `${document.getElementById('yy').value}-${
                    String(document.getElementById('mm').value).padStart(2, '0')}-${
                    String(document.getElementById('dd').value).padStart(2, '0')}`
            };

            try {
                const response = await fetch('/api/signup', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(formData)
                });

                const data = await response.json();

                if (response.ok) {
                    alert('تم التسجيل بنجاح!');
                    window.location.href = '/login/login.html';
                } else {
                    alert(data.detail || 'حدث خطأ أثناء التسجيل');
                }
            } catch (error) {
                console.error('Error:', error);
                alert('حدث خطأ في الاتصال بالخادم');
            }
        });
    }
    if (signupForm) {
        signupForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const firstName = document.getElementById('fn').value;
            const lastName = document.getElementById('ln').value;
            const day = document.getElementById('dd').value;
            const month = document.getElementById('mm').value;
            const year = document.getElementById('yy').value;
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            
            try {
                const response = await fetch('/signup', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        firstName,
                        lastName,
                        dateOfBirth: `${year}-${month.padStart(2, '0')}-${day.padStart(2, '0')}`,
                        email,
                        password
                    })
                });

                if (response.ok) {
                    alert('تم التسجيل بنجاح! يمكنك الآن تسجيل الدخول.');
                    window.location.href = ROUTES.LOGIN;
                } else {
                    const data = await response.json();
                    alert(data.detail || 'حدث خطأ أثناء التسجيل. يرجى المحاولة مرة أخرى.');
                }
            } catch (error) {
                console.error('Error:', error);
                alert('حدث خطأ أثناء التسجيل. يرجى المحاولة مرة أخرى.');
            }
        });
    }
});

// إضافة وظيفة تسجيل الخروج
function logout() {
    localStorage.removeItem("token");
    localStorage.removeItem("email");
    window.location.href = ROUTES.HOME;
}
