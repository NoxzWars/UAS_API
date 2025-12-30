const API_BASE_URL = "http://127.0.0.1:5000";

// ========== AUTH ==========

const tokenKey = "cuaca_token";
const roleKey = "cuaca_role";
const usernameKey = "cuaca_username";

const authSection = document.getElementById("auth-section");
const dashboard = document.getElementById("dashboard");
const adminSection = document.getElementById("admin-section");
const userInfo = document.getElementById("user-info");

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

    loadCuaca();
  } else {
    authSection.classList.remove("d-none");
    dashboard.classList.add("d-none");
  }
}

// Login
document.getElementById("btn-login").addEventListener("click", async () => {
  const username = document.getElementById("login-username").value.trim();
  const password = document.getElementById("login-password").value.trim();
  const msg = document.getElementById("auth-message");

  msg.textContent = "Memproses...";
  try {
    const res = await fetch(`${API_BASE_URL}/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password })
    });

    const data = await res.json();
    if (!res.ok) {
      msg.textContent = data.message || "Login gagal";
      msg.classList.add("text-danger");
      msg.classList.remove("text-success");
      return;
    }

    localStorage.setItem(tokenKey, data.token);
    localStorage.setItem(roleKey, data.role);
    localStorage.setItem(usernameKey, data.username);

    msg.textContent = "Login berhasil";
    msg.classList.remove("text-danger");
    msg.classList.add("text-success");

    setAuthUI();
  } catch (err) {
    msg.textContent = "Terjadi kesalahan koneksi";
    msg.classList.add("text-danger");
  }
});

// Register
document.getElementById("btn-register").addEventListener("click", async () => {
  const username = document.getElementById("login-username").value.trim();
  const password = document.getElementById("login-password").value.trim();
  const msg = document.getElementById("auth-message");

  if (!username || !password) {
    msg.textContent = "Isi username dan password terlebih dahulu";
    msg.classList.add("text-danger");
    return;
  }

  msg.textContent = "Mendaftarkan user...";
  try {
    const res = await fetch(`${API_BASE_URL}/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password })
    });

    const data = await res.json();
    if (!res.ok) {
      msg.textContent = data.message || "Registrasi gagal";
      msg.classList.add("text-danger");
      msg.classList.remove("text-success");
      return;
    }

    msg.textContent = data.message;
    msg.classList.remove("text-danger");
    msg.classList.add("text-success");
  } catch (err) {
    msg.textContent = "Terjadi kesalahan koneksi";
    msg.classList.add("text-danger");
  }
});

// Logout
document.getElementById("btn-logout").addEventListener("click", () => {
  localStorage.removeItem(tokenKey);
  localStorage.removeItem(roleKey);
  localStorage.removeItem(usernameKey);
  setAuthUI();
});

// ========== DATA KOTA & CUACA ==========

async function loadKotaDropdown() {
  const token = localStorage.getItem(tokenKey);
  const select = document.getElementById("cuaca-kota-id");
  select.innerHTML = "";

  const res = await fetch(`${API_BASE_URL}/kota`, {
    headers: {
      "Authorization": `Bearer ${token}`
    }
  });

  if (!res.ok) return;

  const data = await res.json();
  data.forEach(kota => {
    const opt = document.createElement("option");
    opt.value = kota.kota_id;
    opt.textContent = kota.nama_kota;
    select.appendChild(opt);
  });
}

// Tambah Kota (Admin)
document.getElementById("btn-add-kota").addEventListener("click", async () => {
  const nama = document.getElementById("add-nama-kota").value.trim();
  const msg = document.getElementById("kota-message");
  const token = localStorage.getItem(tokenKey);

  if (!nama) {
    msg.textContent = "Nama kota tidak boleh kosong";
    msg.classList.add("text-danger");
    return;
  }

  msg.textContent = "Menyimpan...";
  try {
    const res = await fetch(`${API_BASE_URL}/kota`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${token}`
      },
      body: JSON.stringify({ nama_kota: nama })
    });

    const data = await res.json();
    if (!res.ok) {
      msg.textContent = data.message || "Gagal menambah kota";
      msg.classList.add("text-danger");
      msg.classList.remove("text-success");
      return;
    }

    msg.textContent = data.message;
    msg.classList.remove("text-danger");
    msg.classList.add("text-success");
    document.getElementById("add-nama-kota").value = "";
    loadKotaDropdown();
  } catch (err) {
    msg.textContent = "Terjadi kesalahan koneksi";
    msg.classList.add("text-danger");
  }
});

// Tambah Cuaca (Admin)
document.getElementById("btn-add-cuaca").addEventListener("click", async () => {
  const token = localStorage.getItem(tokenKey);
  const kotaId = document.getElementById("cuaca-kota-id").value;
  const suhu = document.getElementById("cuaca-suhu").value;
  const kelembapan = document.getElementById("cuaca-kelembapan").value;
  const kondisi = document.getElementById("cuaca-kondisi").value.trim();
  const msg = document.getElementById("cuaca-message");

  if (!kotaId || !suhu || !kelembapan || !kondisi) {
    msg.textContent = "Lengkapi semua field cuaca";
    msg.classList.add("text-danger");
    return;
  }

  msg.textContent = "Menyimpan...";
  try {
    const res = await fetch(`${API_BASE_URL}/cuaca`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${token}`
      },
      body: JSON.stringify({
        kota_id: parseInt(kotaId),
        suhu: parseFloat(suhu),
        kelembapan: parseFloat(kelembapan),
        kondisi
      })
    });

    const data = await res.json();
    if (!res.ok) {
      msg.textContent = data.message || "Gagal menambah data cuaca";
      msg.classList.add("text-danger");
      msg.classList.remove("text-success");
      return;
    }

    msg.textContent = data.message;
    msg.classList.remove("text-danger");
    msg.classList.add("text-success");

    document.getElementById("cuaca-suhu").value = "";
    document.getElementById("cuaca-kelembapan").value = "";
    document.getElementById("cuaca-kondisi").value = "";

    loadCuaca();
  } catch (err) {
    msg.textContent = "Terjadi kesalahan koneksi";
    msg.classList.add("text-danger");
  }
});

// Filter Cuaca
document.getElementById("filter-form").addEventListener("submit", e => {
  e.preventDefault();
  loadCuaca();
});

// Load Data Cuaca
async function loadCuaca() {
  const token = localStorage.getItem(tokenKey);
  const list = document.getElementById("cuaca-list");
  const msg = document.getElementById("cuaca-list-message");

  list.innerHTML = "";
  msg.textContent = "Memuat data...";

  const params = new URLSearchParams();
  const kota = document.getElementById("filter-kota").value.trim();
  const kondisi = document.getElementById("filter-kondisi").value.trim();
  const suhuMin = document.getElementById("filter-suhu-min").value;
  const suhuMax = document.getElementById("filter-suhu-max").value;

  if (kota) params.append("kota", kota);
  if (kondisi) params.append("kondisi", kondisi);
  if (suhuMin) params.append("suhu_min", suhuMin);
  if (suhuMax) params.append("suhu_max", suhuMax);

  try {
    const res = await fetch(`${API_BASE_URL}/cuaca?${params.toString()}`, {
      headers: {
        "Authorization": `Bearer ${token}`
      }
    });

    const data = await res.json();

    if (!res.ok) {
      msg.textContent = data.message || "Data tidak ditemukan";
      msg.classList.add("text-warning");
      return;
    }

    msg.textContent = "";
    data.forEach(item => {
      const col = document.createElement("div");
      col.className = "col-md-4";

      const card = document.createElement("div");
      card.className = "weather-card";

      card.innerHTML = `
        <div class="d-flex justify-content-between align-items-center mb-2">
          <div class="weather-city">${item.nama_kota}</div>
          <small class="small-label">${new Date(item.tanggal_input).toLocaleString()}</small>
        </div>
        <div class="d-flex justify-content-between align-items-center">
          <div class="weather-temp">${item.suhu.toFixed(1)}°C</div>
          <div class="text-end">
            <div>Kelembapan: ${item.kelembapan.toFixed(1)}%</div>
            <div>Kondisi: <strong>${item.kondisi}</strong></div>
            <div class="small-label">Input oleh: ${item.username}</div>
          </div>
        </div>
      `;

      col.appendChild(card);
      list.appendChild(col);
    });
  } catch (err) {
    msg.textContent = "Terjadi kesalahan koneksi";
    msg.classList.add("text-danger");
  }
}

// Inisialisasi saat halaman dibuka
setAuthUI();
