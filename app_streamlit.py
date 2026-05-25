import streamlit as st
import pandas as pd
import numpy as np
import pickle
import json
import os
import plotly.graph_objects as go
import plotly.express as px

# ── KONFIGURASI HALAMAN ───────────────────────────────────
st.set_page_config(
    page_title="PadiSight",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── CUSTOM CSS ────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500&display=swap');

  html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
  }

  /* Background */
  .stApp { background-color: #f5f0e8; }

  /* Sidebar */
  [data-testid="stSidebar"] {
    background-color: #0f1c14;
  }
  [data-testid="stSidebar"] * { color: white !important; }
  [data-testid="stSidebar"] .stRadio label { color: rgba(255,255,255,0.7) !important; }
  [data-testid="stSidebar"] .stRadio label:hover { color: white !important; }

  /* Metric cards */
  [data-testid="metric-container"] {
    background: white;
    border-radius: 16px;
    padding: 16px;
    box-shadow: 0 2px 12px rgba(15,28,20,0.06);
  }

  /* Buttons */
  .stButton > button {
    background-color: #1a6b3c !important;
    color: white !important;
    border: none !important;
    border-radius: 100px !important;
    padding: 10px 28px !important;
    font-size: 0.95rem !important;
    font-weight: 500 !important;
    transition: all 0.2s !important;
    width: 100% !important;
  }
  .stButton > button:hover {
    background-color: #2d9e5f !important;
    transform: translateY(-1px) !important;
  }

  /* Input */
  .stSelectbox > div, .stNumberInput > div {
    border-radius: 10px !important;
  }

  /* Card style */
  .padisight-card {
    background: white;
    border-radius: 20px;
    padding: 24px;
    box-shadow: 0 2px 16px rgba(15,28,20,0.06);
    margin-bottom: 16px;
  }

  .hasil-card {
    background: #0f1c14;
    border-radius: 20px;
    padding: 28px;
    text-align: center;
    margin-bottom: 16px;
  }

  .badge {
    display: inline-block;
    background: rgba(26,107,60,0.1);
    border: 1px solid rgba(26,107,60,0.2);
    color: #1a6b3c;
    font-size: 0.8rem;
    font-weight: 500;
    padding: 4px 12px;
    border-radius: 100px;
    margin-bottom: 8px;
  }

  .rekom-item {
    background: rgba(26,107,60,0.04);
    border-left: 3px solid #5ac98a;
    border-radius: 8px;
    padding: 12px 14px;
    margin-bottom: 8px;
  }

  h1, h2, h3 { color: #0f1c14 !important; }

  /* Hide streamlit branding */
  #MainMenu { visibility: hidden; }
  footer { visibility: hidden; }
  header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ── LOAD MODEL & DATA ─────────────────────────────────────
@st.cache_resource
def load_models():
    base = os.path.dirname(os.path.abspath(__file__))

    with open(os.path.join(base, "model_xgboost.pkl"), "rb") as f:
        model_xgb = pickle.load(f)

    with open(os.path.join(base, "label_encoder_provinsi.pkl"), "rb") as f:
        le = pickle.load(f)

    df_forecast = pd.read_excel(os.path.join(base, "hasil_forecast_semua_provinsi.xlsx"))

    # Opsional
    try:
        df_historis = pd.read_excel(os.path.join(base, "rata_rata_historis_provinsi.xlsx"))
    except:
        df_historis = None

    try:
        import shap
        with open(os.path.join(base, "shap_explainer.pkl"), "rb") as f:
            shap_exp = pickle.load(f)
    except:
        shap_exp = None

    return model_xgb, le, df_forecast, df_historis, shap_exp

model_xgb, le, df_forecast, df_historis, shap_exp = load_models()

FITUR_IKLIM = ["GWETROOT", "PRECTOTCORR", "RH2M", "T2M", "WS2M"]
FITUR_MODEL = ["GWETROOT", "PRECTOTCORR", "RH2M", "T2M", "WS2M", "YEAR", "Provinsi_encoded"]
LABEL_IKLIM = {
    "GWETROOT"    : "Kelembaban Tanah",
    "PRECTOTCORR" : "Curah Hujan",
    "RH2M"        : "Kelembaban Udara",
    "T2M"         : "Suhu",
    "WS2M"        : "Kecepatan Angin",
}

# ── HELPER FUNCTIONS ──────────────────────────────────────
def kategori_produktivitas(nilai, avg_nasional):
    pct = (nilai / avg_nasional) * 100 if avg_nasional else 100
    if pct >= 115:
        return {"label": "Sangat Baik", "warna": "#1a6b3c", "icon": "🌟", "pct": round(pct, 1)}
    elif pct >= 100:
        return {"label": "Baik", "warna": "#2d9e5f", "icon": "✅", "pct": round(pct, 1)}
    elif pct >= 85:
        return {"label": "Cukup", "warna": "#e8c84a", "icon": "⚠️", "pct": round(pct, 1)}
    else:
        return {"label": "Rendah", "warna": "#e74c3c", "icon": "❌", "pct": round(pct, 1)}

def status_iklim(nilai_input, avg_prov):
    hasil = {}
    for f in FITUR_IKLIM:
        avg = avg_prov.get(f)
        if not avg or avg == 0:
            hasil[f] = {"status": "normal", "label": "Normal", "warna": "#4CAF50", "selisih_pct": 0}
            continue
        selisih_pct = ((nilai_input[f] - avg) / avg) * 100
        if selisih_pct > 10:
            hasil[f] = {"status": "di_atas", "label": "Di Atas Normal", "warna": "#2196F3", "selisih_pct": round(selisih_pct, 1)}
        elif selisih_pct < -10:
            hasil[f] = {"status": "di_bawah", "label": "Di Bawah Normal", "warna": "#FF9800", "selisih_pct": round(selisih_pct, 1)}
        else:
            hasil[f] = {"status": "normal", "label": "Normal", "warna": "#4CAF50", "selisih_pct": round(selisih_pct, 1)}
    return hasil

def rekomendasi(status_dict, kategori):
    rekoms = []
    gwet = status_dict.get("GWETROOT", {}).get("status")
    prec = status_dict.get("PRECTOTCORR", {}).get("status")
    rh   = status_dict.get("RH2M", {}).get("status")
    t2m  = status_dict.get("T2M", {}).get("status")
    ws   = status_dict.get("WS2M", {}).get("status")

    if gwet == "di_bawah" or prec == "di_bawah":
        rekoms.append(("💧", "Perhatikan Ketersediaan Air", "Kelembaban tanah atau curah hujan di bawah normal. Pertimbangkan optimalisasi irigasi dan varietas tahan kekeringan."))
    if gwet == "di_atas" and prec == "di_atas":
        rekoms.append(("🌊", "Waspadai Kelebihan Air", "Curah hujan dan kelembaban tanah di atas normal. Pastikan drainase lahan berfungsi baik."))
    if t2m == "di_atas":
        rekoms.append(("🌡️", "Suhu Tinggi", "Suhu di atas rata-rata historis. Pertimbangkan pengaturan waktu tanam atau varietas toleran suhu tinggi."))
    if rh == "di_atas":
        rekoms.append(("🍄", "Waspadai Risiko Penyakit", "Kelembaban udara tinggi meningkatkan risiko serangan jamur. Tingkatkan pengawasan hama penyakit."))
    if ws == "di_atas":
        rekoms.append(("💨", "Kecepatan Angin Tinggi", "Angin kencang dapat menyebabkan kerebahan tanaman. Pertimbangkan varietas batang kokoh."))
    if not rekoms:
        rekoms.append(("🌾", "Kondisi Optimal", "Kondisi iklim mendukung produktivitas yang baik. Pertahankan praktik budidaya yang sudah berjalan."))
    return rekoms

# ── SIDEBAR ───────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
        <div style='text-align:center; padding: 20px 0 10px'>
            <span style='font-size:2rem'>🌾</span>
            <h2 style='color:white; margin:8px 0 4px; font-size:1.5rem'>PadiSight</h2>
            <p style='color:rgba(255,255,255,0.5); font-size:0.8rem'>Sistem Prediksi Produktivitas Padi</p>
        </div>
        <hr style='border-color:rgba(255,255,255,0.1); margin:12px 0'>
    """, unsafe_allow_html=True)

    menu = st.radio(
        "Navigasi",
        ["🏠 Beranda", "🌾 Prediksi Produktivitas", "📈 Peramalan Tren"],
        label_visibility="collapsed"
    )

    st.markdown("""
        <hr style='border-color:rgba(255,255,255,0.1); margin:16px 0'>
        <div style='color:rgba(255,255,255,0.4); font-size:0.75rem; text-align:center'>
            Data: NASA POWER · BPS<br>
            Model: XGBoost · Prophet<br>
            2013 – 2025
        </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# HALAMAN BERANDA
# ══════════════════════════════════════════════════════════
if menu == "🏠 Beranda":
    st.markdown("""
        <div style='padding: 20px 0 10px'>
            <div class='badge'>Sistem Berbasis Machine Learning</div>
            <h1 style='font-size:2.8rem; font-weight:800; letter-spacing:-1px; margin:8px 0'>
                Prediksi <span style='color:#1a6b3c'>Produktivitas</span><br>Padi Indonesia
            </h1>
            <p style='color:#4a6355; font-size:1rem; max-width:520px; line-height:1.7'>
                Memanfaatkan data iklim NASA POWER dan algoritma XGBoost untuk memprediksi
                dan meramalkan produktivitas padi di 34 provinsi Indonesia.
            </p>
        </div>
    """, unsafe_allow_html=True)

    # Stats
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Provinsi", "34", "Indonesia")
    with col2:
        st.metric("Periode Data", "13 Tahun", "2013–2025")
    with col3:
        st.metric("Akurasi Model", "0.81", "R² XGBoost")
    with col4:
        st.metric("Proyeksi", "+5 Tahun", "ke Depan")

    st.markdown("<br>", unsafe_allow_html=True)

    # Fitur cards
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div class='padisight-card'>
            <div style='font-size:2rem; margin-bottom:12px'>🌾</div>
            <div style='font-size:0.75rem; font-weight:600; color:#2d9e5f; letter-spacing:1px; margin-bottom:6px'>01 — PREDIKSI</div>
            <h3 style='margin:0 0 8px; font-size:1.2rem'>Prediksi Produktivitas</h3>
            <p style='color:#4a6355; font-size:0.88rem; line-height:1.6; margin:0'>
                Input data iklim suatu provinsi, dapatkan prediksi produktivitas padi (kuintal/ha),
                analisis kondisi iklim, dan rekomendasi tindakan menggunakan model XGBoost.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class='padisight-card'>
            <div style='font-size:2rem; margin-bottom:12px'>📈</div>
            <div style='font-size:0.75rem; font-weight:600; color:#2d9e5f; letter-spacing:1px; margin-bottom:6px'>02 — PERAMALAN</div>
            <h3 style='margin:0 0 8px; font-size:1.2rem'>Peramalan Tren</h3>
            <p style='color:#4a6355; font-size:0.88rem; line-height:1.6; margin:0'>
                Lihat tren historis dan proyeksi produktivitas padi 5 tahun ke depan
                per provinsi menggunakan model Facebook Prophet.
            </p>
        </div>
        """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# HALAMAN PREDIKSI
# ══════════════════════════════════════════════════════════
elif menu == "🌾 Prediksi Produktivitas":
    st.markdown("""
        <div class='badge'>🌾 Fitur 01</div>
        <h1 style='font-size:2rem; font-weight:800; letter-spacing:-0.5px; margin:8px 0 4px'>
            Prediksi Produktivitas Padi
        </h1>
        <p style='color:#4a6355; margin-bottom:24px'>
            Masukkan data iklim suatu provinsi untuk mendapatkan prediksi produktivitas,
            analisis kondisi iklim, dan rekomendasi tindakan.
        </p>
    """, unsafe_allow_html=True)

    col_form, col_hasil = st.columns([1, 1.2], gap="large")

    with col_form:
        st.markdown("<div class='padisight-card'>", unsafe_allow_html=True)
        st.markdown("**📥 Input Data Iklim**")

        provinsi_list = sorted(list(le.classes_))
        provinsi_display = [p.capitalize() for p in provinsi_list]
        prov_idx  = st.selectbox("Provinsi", range(len(provinsi_list)),
                                  format_func=lambda i: provinsi_display[i])
        provinsi  = provinsi_list[prov_idx]

        tahun = st.number_input("Tahun", min_value=2013, max_value=2030, value=2025)

        c1, c2 = st.columns(2)
        with c1:
            gwetroot    = st.number_input("GWETROOT (Kel. Tanah)", min_value=0.0, max_value=1.0, value=0.85, step=0.001, format="%.3f")
            rh2m        = st.number_input("RH2M (Kel. Udara %)", min_value=0.0, max_value=100.0, value=85.0, step=0.01)
        with c2:
            prectotcorr = st.number_input("PRECTOTCORR (mm/hari)", min_value=0.0, value=7.5, step=0.001, format="%.3f")
            t2m         = st.number_input("T2M (Suhu °C)", value=26.0, step=0.01)

        ws2m = st.number_input("WS2M (Angin m/s)", min_value=0.0, value=1.4, step=0.01)

        st.markdown("---")
        st.markdown("**Opsional — Hitung Produksi Total**")
        luas_panen = st.number_input("Luas Panen (ha)", min_value=0.0, value=0.0, step=1000.0)

        prediksi_btn = st.button("🌾 Prediksi Sekarang")
        st.markdown("</div>", unsafe_allow_html=True)

    with col_hasil:
        if prediksi_btn:
            nilai_input = {
                "GWETROOT": gwetroot, "PRECTOTCORR": prectotcorr,
                "RH2M": rh2m, "T2M": t2m, "WS2M": ws2m
            }
            prov_encoded  = int(le.transform([provinsi])[0])
            fitur         = [[gwetroot, prectotcorr, rh2m, t2m, ws2m, tahun, prov_encoded]]
            produktivitas = float(model_xgb.predict(fitur)[0])

            # Rata-rata historis
            avg_prov     = {}
            avg_nasional = None
            if df_historis is not None:
                row = df_historis[df_historis['Provinsi'] == provinsi]
                if not row.empty:
                    avg_prov = {f: float(row.iloc[0].get(f, 0)) for f in FITUR_IKLIM + ['Produktivitas']}
                avg_nasional = float(df_historis['Produktivitas'].mean())

            kat       = kategori_produktivitas(produktivitas, avg_nasional or produktivitas)
            status    = status_iklim(nilai_input, avg_prov)
            rekoms    = rekomendasi(status, kat)
            produksi  = (produktivitas * luas_panen) / 10 if luas_panen > 0 else None

            # ── Hasil Utama ──
            st.markdown(f"""
            <div class='hasil-card'>
                <div style='font-size:0.72rem; font-weight:500; color:#5ac98a; letter-spacing:1px; text-transform:uppercase; margin-bottom:6px'>
                    Produktivitas Prediksi
                </div>
                <div style='font-size:3rem; font-weight:800; color:white; letter-spacing:-2px; line-height:1'>
                    {produktivitas:.2f} <span style='font-size:1rem; color:rgba(255,255,255,0.5); font-weight:400'>kuintal/ha</span>
                </div>
                <div style='font-size:0.82rem; color:rgba(255,255,255,0.4); margin-top:4px'>
                    {provinsi.capitalize()} · {tahun}
                </div>
                <div style='margin-top:12px; display:inline-block; background:{kat["warna"]}30; color:{kat["warna"]}; padding:6px 16px; border-radius:100px; font-size:0.82rem; font-weight:600'>
                    {kat["icon"]} {kat["label"]} · {kat["pct"]}% dari rata-rata nasional
                </div>
                {f'<div style="margin-top:16px; padding-top:16px; border-top:1px solid rgba(255,255,255,0.08)"><div style="font-size:0.7rem; color:rgba(255,255,255,0.4)">Estimasi Total Produksi</div><div style="font-size:1.5rem; font-weight:700; color:#e8c84a">{produksi:,.0f} ton</div></div>' if produksi else ''}
            </div>
            """, unsafe_allow_html=True)

            # ── Perbandingan + Status Iklim ──
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("<div class='padisight-card'>", unsafe_allow_html=True)
                st.markdown("**📊 Perbandingan Historis**")
                if avg_prov.get('Produktivitas'):
                    selisih     = produktivitas - avg_prov['Produktivitas']
                    selisih_pct = (selisih / avg_prov['Produktivitas']) * 100
                    arah        = "↑" if selisih >= 0 else "↓"
                    warna_arah  = "#2d9e5f" if selisih >= 0 else "#e74c3c"
                    st.markdown(f"""
                    <table style='width:100%; font-size:0.82rem; border-collapse:collapse'>
                        <tr><td style='color:#4a6355; padding:6px 0; border-bottom:1px solid rgba(26,107,60,0.06)'>Prediksi saat ini</td><td style='text-align:right; font-weight:600; border-bottom:1px solid rgba(26,107,60,0.06)'>{produktivitas:.2f} kw/ha</td></tr>
                        <tr><td style='color:#4a6355; padding:6px 0; border-bottom:1px solid rgba(26,107,60,0.06)'>Rata-rata historis provinsi</td><td style='text-align:right; font-weight:600; border-bottom:1px solid rgba(26,107,60,0.06)'>{avg_prov['Produktivitas']:.2f} kw/ha</td></tr>
                        <tr><td style='color:#4a6355; padding:6px 0; border-bottom:1px solid rgba(26,107,60,0.06)'>Rata-rata nasional</td><td style='text-align:right; font-weight:600; border-bottom:1px solid rgba(26,107,60,0.06)'>{avg_nasional:.2f} kw/ha</td></tr>
                        <tr><td style='color:#4a6355; padding:6px 0'>Selisih dari historis</td><td style='text-align:right; font-weight:600; color:{warna_arah}'>{arah} {abs(selisih):.2f} kw/ha ({abs(selisih_pct):.1f}%)</td></tr>
                    </table>
                    """, unsafe_allow_html=True)
                else:
                    st.caption("Data historis belum tersedia.")
                st.markdown("</div>", unsafe_allow_html=True)

            with c2:
                st.markdown("<div class='padisight-card'>", unsafe_allow_html=True)
                st.markdown("**🌡️ Status Kondisi Iklim**")
                for f, v in status.items():
                    selisih_str = f"+{v['selisih_pct']}%" if v['selisih_pct'] >= 0 else f"{v['selisih_pct']}%"
                    st.markdown(f"""
                    <div style='display:flex; align-items:center; gap:10px; padding:7px 10px; background:#f5f0e8; border-radius:8px; margin-bottom:6px'>
                        <div style='width:8px; height:8px; border-radius:50%; background:{v["warna"]}; flex-shrink:0'></div>
                        <div style='flex:1; font-size:0.8rem; color:#4a6355'>{LABEL_IKLIM[f]}</div>
                        <div>
                            <div style='font-size:0.75rem; font-weight:600; color:{v["warna"]}'>{v["label"]}</div>
                            <div style='font-size:0.7rem; color:#4a6355'>{selisih_str} dari historis</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

            # ── Rekomendasi ──
            st.markdown("<div class='padisight-card'>", unsafe_allow_html=True)
            st.markdown("**💡 Rekomendasi Tindakan**")
            for icon, judul, detail in rekoms:
                st.markdown(f"""
                <div class='rekom-item'>
                    <span style='font-size:1.2rem'>{icon}</span>
                    <strong style='font-size:0.85rem; color:#0f1c14'> {judul}</strong>
                    <p style='font-size:0.8rem; color:#4a6355; margin:4px 0 0; line-height:1.5'>{detail}</p>
                </div>
                """, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        else:
            st.markdown("""
            <div style='text-align:center; padding:60px 20px; color:#4a6355'>
                <div style='font-size:3rem; margin-bottom:12px'>🌾</div>
                <p>Isi form di kiri dan klik<br><strong>"Prediksi Sekarang"</strong></p>
            </div>
            """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# HALAMAN PERAMALAN
# ══════════════════════════════════════════════════════════
elif menu == "📈 Peramalan Tren":
    st.markdown("""
        <div class='badge'>📈 Fitur 02</div>
        <h1 style='font-size:2rem; font-weight:800; letter-spacing:-0.5px; margin:8px 0 4px'>
            Peramalan Tren Produktivitas
        </h1>
        <p style='color:#4a6355; margin-bottom:24px'>
            Lihat tren historis dan proyeksi produktivitas padi 5 tahun ke depan per provinsi
            menggunakan model Facebook Prophet.
        </p>
    """, unsafe_allow_html=True)

    provinsi_list    = sorted(df_forecast['Provinsi'].unique().tolist())
    provinsi_display = [p.capitalize() for p in provinsi_list]
    prov_idx         = st.selectbox("Pilih Provinsi", range(len(provinsi_list)),
                                     format_func=lambda i: provinsi_display[i])
    provinsi_sel     = provinsi_list[prov_idx]

    df_prov     = df_forecast[df_forecast['Provinsi'] == provinsi_sel].sort_values('Tahun')
    df_hist     = df_prov[df_prov['Is_Forecast'] == False]
    df_proj     = df_prov[df_prov['Is_Forecast'] == True]

    # ── Stats ──
    terakhir    = df_hist.iloc[-1] if not df_hist.empty else None
    proj_pertama = df_proj.iloc[0] if not df_proj.empty else None
    proj_last   = df_proj.iloc[-1] if not df_proj.empty else None
    peak        = df_proj.loc[df_proj['Proyeksi'].idxmax()] if not df_proj.empty else None

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Produktivitas Terakhir",
                  f"{terakhir['Aktual']:.2f} kw/ha" if terakhir is not None else "—",
                  f"Tahun {int(terakhir['Tahun'])}" if terakhir is not None else "")
    with c2:
        st.metric("Proyeksi Tahun Pertama",
                  f"{proj_pertama['Proyeksi']:.2f} kw/ha" if proj_pertama is not None else "—",
                  f"Tahun {int(proj_pertama['Tahun'])}" if proj_pertama is not None else "")
    with c3:
        if terakhir is not None and proj_last is not None:
            tren = ((proj_last['Proyeksi'] - terakhir['Aktual']) / terakhir['Aktual']) * 100
            st.metric("Tren 5 Tahun", f"{tren:+.1f}%", "dari tahun terakhir")
        else:
            st.metric("Tren 5 Tahun", "—")
    with c4:
        st.metric("Puncak Proyeksi",
                  f"{peak['Proyeksi']:.2f} kw/ha" if peak is not None else "—",
                  f"Tahun {int(peak['Tahun'])}" if peak is not None else "")

    # ── Chart Plotly ──
    st.markdown("<div class='padisight-card'>", unsafe_allow_html=True)

    fig = go.Figure()

    # Historis aktual
    fig.add_trace(go.Scatter(
        x=df_hist['Tahun'], y=df_hist['Aktual'],
        mode='lines+markers',
        name='Aktual',
        line=dict(color='#1a6b3c', width=2.5),
        marker=dict(size=6, color='#1a6b3c'),
    ))

    # Interval kepercayaan 95%
    fig.add_trace(go.Scatter(
        x=pd.concat([df_proj['Tahun'], df_proj['Tahun'][::-1]]),
        y=pd.concat([df_proj['Upper_95'], df_proj['Lower_95'][::-1]]),
        fill='toself',
        fillcolor='rgba(232,200,74,0.15)',
        line=dict(color='rgba(255,255,255,0)'),
        name='Interval 95%',
        showlegend=True
    ))

    # Proyeksi
    fig.add_trace(go.Scatter(
        x=df_proj['Tahun'], y=df_proj['Proyeksi'],
        mode='lines+markers',
        name='Proyeksi',
        line=dict(color='#e8c84a', width=2.5, dash='dash'),
        marker=dict(size=6, color='#e8c84a'),
    ))

    # Garis pemisah
    tahun_akhir = int(df_hist['Tahun'].max()) if not df_hist.empty else 2025
    fig.add_vline(x=tahun_akhir, line_dash="dot", line_color="gray", opacity=0.5)

    fig.update_layout(
        title=dict(
            text=f'Tren & Proyeksi Produktivitas — {provinsi_sel.capitalize()}',
            font=dict(size=14, color='#0f1c14')
        ),
        xaxis=dict(title='Tahun', gridcolor='rgba(0,0,0,0.04)', tickmode='linear'),
        yaxis=dict(title='Produktivitas (kuintal/ha)', gridcolor='rgba(0,0,0,0.04)'),
        plot_bgcolor='white',
        paper_bgcolor='white',
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        height=400,
        margin=dict(l=20, r=20, t=60, b=20)
    )

    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # ── Tabel ──
    st.markdown("**Data Historis & Proyeksi**")
    df_tabel = df_prov[['Tahun', 'Aktual', 'Proyeksi', 'Lower_95', 'Upper_95', 'Is_Forecast']].copy()
    df_tabel['Tipe']    = df_tabel['Is_Forecast'].apply(lambda x: '🔮 Proyeksi' if x else '📊 Historis')
    df_tabel['Aktual']  = df_tabel['Aktual'].apply(lambda x: f"{x:.2f}" if pd.notna(x) else '—')
    df_tabel['Proyeksi'] = df_tabel['Proyeksi'].apply(lambda x: f"{x:.2f}" if pd.notna(x) else '—')
    df_tabel['Lower_95'] = df_tabel['Lower_95'].apply(lambda x: f"{x:.2f}" if pd.notna(x) else '—')
    df_tabel['Upper_95'] = df_tabel['Upper_95'].apply(lambda x: f"{x:.2f}" if pd.notna(x) else '—')
    df_tabel = df_tabel[['Tahun', 'Tipe', 'Aktual', 'Proyeksi', 'Lower_95', 'Upper_95']]
    df_tabel.columns = ['Tahun', 'Tipe', 'Aktual (kw/ha)', 'Proyeksi (kw/ha)', 'Batas Bawah 95%', 'Batas Atas 95%']
    st.dataframe(df_tabel.sort_values('Tahun', ascending=False), use_container_width=True, hide_index=True)
