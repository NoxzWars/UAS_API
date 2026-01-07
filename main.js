const API_BASE_URL = "http://127.0.0.1:5000";

// ================= AUTH =================
const tokenKey = "cuaca_token";
const roleKey = "cuaca_role";
const usernameKey = "cuaca_username";

const authSection = document.getElementById("auth-section");
const dashboard = document.getElementById("dashboard");
const adminSection = document.getElementById("admin-section");
const userInfo = document.getElementById("user-info");

// ================= AUTH UI =================
function setAuthUI() {
  const token = localStorage.getItem(tokenKey);
  const role = localStorage.getItem(roleKey);
  const username = localStorage.getItem(usernameKey);

  if (token) {
    authSection.classList.add("d-none");
    dashboard.classList.remove("d-none");
    userInfo.textContent = `Login sebagai: ${username} (${role})`;

    if (role === "admin") {
      adminSection.classList.remove("d-none");
      loadKotaDropdown();
    } else {
      adminSection.classList.add("d-none");
    }

    loadCuaca(); // load awal TANPA filter
  } else {
    authSection.classList.remove("d-none");
    dashboard.classList.add("d-none");
  }
}

// ================= LOGIN =================
document.getElementById("btn-login").addEventListener("click", async () => {
  const username = document.getElementById("login-username").value.trim();
  const password = document.getElementById("login-password").value.trim();
  const msg = document.getElementById("auth-message");

  msg.textContent = "Memproses login...";

  try {
    const res = await fetch(`${API_BASE_URL}/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password })
    });

    const data = await res.json();
    if (!res.ok) {
      msg.textContent = data.message || "Login gagal";
      msg.className = "text-danger";
      return;
    }

    localStorage.setItem(tokenKey, data.token);
    localStorage.setItem(roleKey, data.role);
    localStorage.setItem(usernameKey, data.username);

    msg.textContent = "Login berhasil";
    msg.className = "text-success";
    setAuthUI();
  } catch {
    msg.textContent = "Terjadi kesalahan koneksi";
    msg.className = "text-danger";
  }
});

// ================= LOGOUT =================
document.getElementById("btn-logout").addEventListener("click", () => {
  localStorage.clear();
  setAuthUI();
});

// ================= LOAD KOTA =================
async function loadKotaDropdown() {
  const token = localStorage.getItem(tokenKey);
  const select = document.getElementById("cuaca-kota-id");
  if (!select) return;

  select.innerHTML = "";

  const res = await fetch(`${API_BASE_URL}/kota`, {
    headers: { Authorization: `Bearer ${token}` }
  });

  if (!res.ok) return;

  const data = await res.json();
  data.forEach(kota => {
    select.innerHTML += `<option value="${kota.kota_id}">${kota.nama_kota}</option>`;
  });
}

// ================= LOAD CUACA (DENGAN FILTER) =================
async function loadCuaca(filter = {}) {
  const token = localStorage.getItem(tokenKey);
  const list = document.getElementById("cuaca-list");
  const msg = document.getElementById("cuaca-list-message");

  list.innerHTML = "";
  msg.textContent = "Memuat data...";

  const params = new URLSearchParams();
  if (filter.kota) params.append("kota", filter.kota);
  if (filter.kondisi) params.append("kondisi", filter.kondisi);
  if (filter.suhuMin) params.append("suhu_min", filter.suhuMin);
  if (filter.suhuMax) params.append("suhu_max", filter.suhuMax);

  const url =
    params.toString().length > 0
      ? `${API_BASE_URL}/cuaca?${params.toString()}`
      : `${API_BASE_URL}/cuaca`;

  try {
    const res = await fetch(url, {
      headers: { Authorization: `Bearer ${token}` }
    });

    const data = await res.json();

    if (!res.ok || data.length === 0) {
      msg.textContent = "Data tidak ditemukan";
      return;
    }

    msg.textContent = "";
    data.forEach(item => {
      list.innerHTML += `
        <div class="col-md-4">
          <div class="weather-card">
            <div class="weather-city">${item.nama_kota}</div>
            <div class="weather-temp">${item.suhu.toFixed(1)}°C</div>
            <div>Kelembapan: ${item.kelembapan.toFixed(1)}%</div>
            <div>Kondisi: <b>${item.kondisi}</b></div>
            <div class="small-label">Input: ${item.username}</div>
          </div>
        </div>
      `;
    });
  } catch {
    msg.textContent = "Terjadi kesalahan koneksi";
  }
}

// ================= FILTER EVENT =================
document.getElementById("filter-form").addEventListener("submit", e => {
  e.preventDefault();

  loadCuaca({
    kota: document.getElementById("filter-kota").value.trim(),
    kondisi: document.getElementById("filter-kondisi").value.trim(),
    suhuMin: document.getElementById("filter-suhu-min").value,
    suhuMax: document.getElementById("filter-suhu-max").value
  });
});

// ================= CHATBOT =================
document.getElementById("chat-send").addEventListener("click", async () => {
  const input = document.getElementById("chat-input");
  const box = document.getElementById("chat-box");
  const message = input.value.trim();
  if (!message) return;

  box.innerHTML += `<div><b>Kamu:</b> ${message}</div>`;
  input.value = "";

  const res = await fetch(`${API_BASE_URL}/chatbot`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${localStorage.getItem(tokenKey)}`
    },
    body: JSON.stringify({ message })
  });

  const data = await res.json();
  box.innerHTML += `<div><b>Bot:</b> ${data.reply}</div>`;
  box.scrollTop = box.scrollHeight;
});

// ================= INIT =================
setAuthUI();
