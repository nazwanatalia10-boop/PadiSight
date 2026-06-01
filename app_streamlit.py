import streamlit as st
import pandas as pd
import numpy as np
import pickle
import os
import plotly.graph_objects as go

st.set_page_config(
    page_title="PadiSight",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,600;0,700;1,400;1,600&family=DM+Sans:opsz,wght@9..40,300;9..40,400;9..40,500;9..40,600;9..40,700&display=swap');

  :root {
    --ink:        #0a1208;
    --ink-soft:   #2d4035;
    --ink-faint:  #6b8878;
    --leaf:       #0f4a28;
    --leaf-mid:   #1a6b3c;
    --leaf-light: #2d9e5f;
    --gold:       #c9973a;
    --gold-light: #e2b554;
    --gold-pale:  #f7edce;
    --cream:      #f0ebe0;
    --white:      #ffffff;
  }

  html, body, [class*="css"], .stApp, p, span, label, input {
    font-family: 'DM Sans', sans-serif !important;
  }
  div { font-family: inherit !important; }

  #MainMenu, footer, header,
  [data-testid="stToolbar"],
  [data-testid="stDecoration"],
  [data-testid="stStatusWidget"],
  .stAppDeployButton { display: none !important; visibility: hidden !important; }

  button[aria-label="Close sidebar"],
  button[aria-label="Open sidebar"],
  [data-testid="collapsedControl"],
  [data-testid="stSidebarCollapseButton"] {
    display: none !important; visibility: hidden !important;
    opacity: 0 !important; pointer-events: none !important;
    width: 0 !important; height: 0 !important;
    position: absolute !important; left: -9999px !important;
  }

  .stApp {
    background: linear-gradient(135deg, #f8f5ee 0%, #eef5ef 40%, #f8f5ee 100%);
  }

  .stMainBlockContainer, [data-testid="stMainBlockContainer"],
  .block-container, [data-testid="block-container"] {
    padding-left: 2rem !important;
    padding-right: 2rem !important;
    padding-top: 0.8rem !important;
    padding-bottom: 0.8rem !important;
    max-width: 100% !important;
  }
  [data-testid="stHorizontalBlock"] { gap: 0.8rem !important; align-items: stretch !important; }
  [data-testid="stVerticalBlock"] { gap: 0.6rem !important; }
  [data-testid="stElementContainer"] { margin-bottom: 0 !important; }

  /* ═══ SIDEBAR ═══ */
  [data-testid="stSidebar"] {
    background: linear-gradient(180deg,
      #0a1509 0%, #0d1c0e 30%, #0a1812 60%, #091408 100%) !important;
    border-right: 1px solid rgba(201,151,58,0.12) !important;
    min-width: 260px !important;
    max-width: 260px !important;
    width: 260px !important;
  }
  /* Paksa sidebar content tidak punya padding bawaan Streamlit */
  [data-testid="stSidebar"] > div:first-child,
  [data-testid="stSidebar"] [data-testid="stSidebarContent"] {
    padding: 0 !important;
    width: 100% !important;
  }
  [data-testid="stSidebar"] * { color: white !important; }

  /* Nav radio wrapper */
  [data-testid="stSidebar"] .stRadio > div {
    gap: 4px !important;
    display: flex !important;
    flex-direction: column !important;
    width: 100% !important;
  }
  /* Setiap nav item — SATU BARIS, tidak wrap */
  [data-testid="stSidebar"] .stRadio label {
    display: flex !important;
    align-items: center !important;
    gap: 10px !important;
    padding: 11px 20px !important;
    border-radius: 12px !important;
    cursor: pointer !important;
    transition: all 0.22s ease !important;
    font-size: 0.88rem !important;
    font-weight: 500 !important;
    color: rgba(255,255,255,0.55) !important;
    border: 1px solid transparent !important;
    margin: 1px 12px !important;
    width: calc(100% - 24px) !important;
    box-sizing: border-box !important;
    white-space: nowrap !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
    line-height: 1.2 !important;
  }
  [data-testid="stSidebar"] .stRadio label:hover {
    background: rgba(255,255,255,0.06) !important;
    color: rgba(255,255,255,0.85) !important;
    border-color: rgba(201,151,58,0.15) !important;
  }
  [data-testid="stSidebar"] .stRadio label:has(input:checked) {
    background: linear-gradient(135deg,
      rgba(26,107,60,0.35) 0%, rgba(15,74,40,0.25) 100%) !important;
    color: #e2b554 !important;
    border-color: rgba(201,151,58,0.25) !important;
  }
  /* Sembunyikan radio bullet bawaan */
  [data-testid="stSidebar"] .stRadio [data-baseweb="radio"] > div:first-child {
    display: none !important;
  }
  /* Sembunyikan label teks widget radio */
  [data-testid="stRadio"] label[data-testid="stWidgetLabel"],
  [data-testid="stSidebar"] .stRadio [data-testid="stWidgetLabel"] {
    display: none !important;
    height: 0 !important;
    margin: 0 !important;
    padding: 0 !important;
  }
  /* Pastikan div.stRadio tidak punya margin berlebih */
  [data-testid="stSidebar"] [data-testid="stRadio"] {
    width: 100% !important;
    padding: 0 !important;
    margin: 0 !important;
  }

  /* ═══ METRIC CARDS ═══ */
  [data-testid="metric-container"] {
    background: #ffffff !important; border-radius: 18px !important;
    padding: 12px 16px 10px !important; border-top: 3px solid var(--leaf-mid) !important;
    border-left: 1px solid rgba(15,74,40,0.14) !important;
    border-right: 1px solid rgba(15,74,40,0.14) !important;
    border-bottom: 1px solid rgba(201,151,58,0.18) !important;
    box-shadow: 0 4px 24px rgba(10,18,8,0.09), 0 1px 4px rgba(10,18,8,0.05) !important;
    transition: transform 0.25s ease, box-shadow 0.25s ease !important;
  }
  [data-testid="metric-container"]:hover {
    transform: translateY(-3px) !important;
    box-shadow: 0 10px 32px rgba(10,18,8,0.12), 0 2px 8px rgba(201,151,58,0.08) !important;
  }

  /* ═══ WHITE CARD (border container) ═══ */
  [data-testid="stVerticalBlockBorderWrapper"] {
    background: #ffffff !important; border-radius: 20px !important;
    box-shadow: 0 4px 28px rgba(0,0,0,0.11), 0 1px 6px rgba(0,0,0,0.07) !important;
    border: none !important; transition: box-shadow 0.25s ease, transform 0.25s ease !important;
  }
  [data-testid="stVerticalBlockBorderWrapper"]:hover {
    box-shadow: 0 8px 36px rgba(0,0,0,0.13), 0 2px 10px rgba(0,0,0,0.07) !important;
    transform: translateY(-2px) !important;
  }
  [data-testid="stVerticalBlockBorderWrapper"] > div { background-color: #ffffff !important; }
  [data-testid="stVerticalBlockBorderWrapper"] [data-testid="stVerticalBlock"] {
    padding: 4px 6px !important;
  }

  /* Input & select — field area */
  [data-baseweb="select"] > div, [data-baseweb="base-input"] {
    background-color: #f8faf9 !important;
    border: 1px solid rgba(15,74,40,0.18) !important;
    border-radius: 10px !important;
  }
  [data-baseweb="select"] > div:focus-within,
  [data-baseweb="base-input"]:focus-within {
    border-color: rgba(26,107,60,0.5) !important;
    box-shadow: 0 0 0 3px rgba(26,107,60,0.08) !important;
  }

  /* Tombol +/- number input — latar putih */
  [data-testid="stNumberInput"] button,
  [data-testid="stNumberInput"] [data-testid="stNumberInputStepDown"],
  [data-testid="stNumberInput"] [data-testid="stNumberInputStepUp"],
  .stNumberInput button {
    background-color: #ffffff !important;
    background: #ffffff !important;
    border: 1px solid rgba(15,74,40,0.18) !important;
    color: #0a1208 !important;
    box-shadow: none !important;
    border-radius: 8px !important;
  }
  [data-testid="stNumberInput"] button:hover,
  .stNumberInput button:hover {
    background-color: #f0f5f2 !important;
    background: #f0f5f2 !important;
    border-color: rgba(26,107,60,0.35) !important;
  }
  /* Pastikan ikon +/- berwarna gelap (bukan putih di atas putih) */
  [data-testid="stNumberInput"] button svg,
  [data-testid="stNumberInput"] button p,
  .stNumberInput button svg {
    color: #0a1208 !important;
    fill: #0a1208 !important;
    stroke: #0a1208 !important;
  }

  /* Label input — turun sedikit */
  .stSelectbox label p,
  .stNumberInput label p,
  [data-testid="stWidgetLabel"] p {
    font-weight: 600 !important;
    font-size: 0.58rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.6px !important;
    color: #0a1208 !important;
    margin-bottom: 2px !important;
    margin-top: 6px !important;
    display: block !important;
  }

  /* Button */
  .stButton > button {
    background: linear-gradient(135deg, #0f4a28 0%, #1a6b3c 55%, #226644 100%) !important;
    color: white !important; border: none !important; border-radius: 12px !important;
    padding: 12px 28px !important; font-weight: 600 !important; font-size: 0.92rem !important;
    width: 100% !important; box-shadow: 0 4px 16px rgba(15,74,40,0.30) !important;
    transition: all 0.22s ease !important;
  }
  .stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 24px rgba(15,74,40,0.40) !important;
  }

  /* Page fade-in */
  @keyframes pageFadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to   { opacity: 1; transform: translateY(0); }
  }
  [data-testid="stVerticalBlock"] > * { animation: pageFadeIn 0.30s cubic-bezier(0.25,0.8,0.25,1) both; }
  [data-testid="stVerticalBlock"] > *:nth-child(1) { animation-delay: 0.00s; }
  [data-testid="stVerticalBlock"] > *:nth-child(2) { animation-delay: 0.04s; }
  [data-testid="stVerticalBlock"] > *:nth-child(3) { animation-delay: 0.08s; }
  [data-testid="stVerticalBlock"] > *:nth-child(4) { animation-delay: 0.12s; }
  [data-testid="stVerticalBlock"] > *:nth-child(5) { animation-delay: 0.16s; }
  [data-testid="stVerticalBlock"] > *:nth-child(n+6) { animation-delay: 0.20s; }

  /* Shared components */
  .badge {
    display: inline-flex; align-items: center; gap: 6px;
    background: rgba(15,74,40,0.07); border: 1.5px solid rgba(15,74,40,0.20);
    color: var(--leaf-mid) !important; font-size: 0.68rem; font-weight: 700;
    padding: 5px 14px; border-radius: 100px; margin-bottom: 16px;
    text-transform: uppercase; letter-spacing: 1.3px;
  }
  .section-label {
    font-size: 0.68rem; font-weight: 700; text-transform: uppercase;
    letter-spacing: 1.2px; color: var(--ink-faint); margin-bottom: 14px;
    display: flex; align-items: center; gap: 8px;
  }
  .section-label::after {
    content: ''; flex: 1; height: 1px;
    background: linear-gradient(90deg, rgba(201,151,58,0.30), transparent);
  }
  .hasil-card {
    background: linear-gradient(145deg, #060e07 0%, #0d1a0f 40%, #0f2a17 100%);
    border-radius: 22px; padding: 22px 26px; text-align: center; margin-bottom: 14px;
    border: 1px solid rgba(201,151,58,0.22);
    box-shadow: 0 12px 40px rgba(6,14,7,0.30), inset 0 1px 0 rgba(201,151,58,0.10);
    position: relative; overflow: hidden;
  }
  .hasil-card::before {
    content: ''; position: absolute; top: -60px; right: -60px;
    width: 200px; height: 200px;
    background: radial-gradient(circle, rgba(201,151,58,0.08) 0%, transparent 65%);
    pointer-events: none;
  }
  .produksi-card {
    background: linear-gradient(145deg, #060e07 0%, #0d1a0f 40%, #0f2a17 100%);
    border-radius: 16px; padding: 18px 26px; margin-bottom: 14px;
    border: 1px solid rgba(201,151,58,0.22);
  }
  .rekom-item {
    background: linear-gradient(135deg, rgba(15,74,40,0.03), rgba(201,151,58,0.015));
    border-left: 3px solid var(--gold);
    border-top: 1px solid rgba(201,151,58,0.10);
    border-right: 1px solid rgba(15,74,40,0.06);
    border-bottom: 1px solid rgba(201,151,58,0.07);
    border-radius: 0 13px 13px 0; padding: 13px 16px; margin-bottom: 9px;
    transition: transform 0.18s ease, border-left-color 0.18s ease;
  }
  .rekom-item:hover { transform: translateX(4px); border-left-color: var(--leaf-mid); }
  .feature-card {
    background: var(--white); border-radius: 20px; padding: 26px;
    border: 1.5px solid rgba(15,74,40,0.13); border-bottom: 2px solid rgba(201,151,58,0.22);
    box-shadow: 0 3px 20px rgba(10,18,8,0.08); transition: all 0.28s cubic-bezier(.25,.8,.25,1);
    position: relative; overflow: hidden; min-height: 280px;
  }
  .feature-card::before {
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 0;
    background: linear-gradient(90deg, var(--leaf) 0%, var(--gold) 100%);
    transition: height 0.28s ease; border-radius: 20px 20px 0 0;
  }
  .feature-card:hover { transform: translateY(-5px); box-shadow: 0 14px 40px rgba(10,18,8,0.11); }
  .feature-card:hover::before { height: 3px; }
  .feature-card .feat-num {
    font-family: 'Playfair Display', Georgia, serif; font-size: 3rem;
    color: rgba(15,74,40,0.055); position: absolute; top: 10px; right: 18px; line-height: 1;
  }
  .warning-box {
    background: #fff8e1; border-left: 4px solid #c9973a;
    border-radius: 0 14px 14px 0; padding: 18px 20px; margin-bottom: 12px;
  }

  /* Sidebar — layout fit vertikal tanpa scroll */
  [data-testid="stSidebar"] [data-testid="stSidebarContent"] {
    display: flex !important;
    flex-direction: column !important;
    height: 100vh !important;
    overflow: hidden !important;
  }

  /* Sidebar custom classes */
  .sb-header {
    padding: 20px 24px 14px;
    position: relative;
    overflow: hidden;
    flex-shrink: 0;
  }
  .sb-logo-wrap { display: flex; align-items: center; gap: 14px; margin-bottom: 8px; }
  .sb-logo-icon {
    width: 48px; height: 48px;
    background: linear-gradient(135deg, #1a6b3c 0%, #0f4a28 60%, #0a3520 100%);
    border-radius: 14px; display: flex; align-items: center; justify-content: center;
    font-size: 1.5rem; flex-shrink: 0;
    box-shadow: 0 4px 20px rgba(0,0,0,0.3), inset 0 1px 0 rgba(255,255,255,0.10);
    border: 1px solid rgba(201,151,58,0.20);
  }
  .sb-logo-text h2 {
    font-family: 'DM Sans', sans-serif !important; font-size: 1.35rem !important;
    font-weight: 800 !important; color: white !important;
    margin: 0 !important; line-height: 1.1 !important;
  }
  .sb-logo-text h2 em { font-style: italic !important; color: #e2b554 !important; }
  .sb-logo-text p {
    font-size: 0.65rem !important; color: rgba(255,255,255,0.38) !important;
    margin: 2px 0 0 !important; line-height: 1 !important; letter-spacing: 0.5px !important;
  }
  .sb-pill {
    display: inline-flex; align-items: center; gap: 5px;
    background: rgba(201,151,58,0.10); border: 1px solid rgba(201,151,58,0.20);
    border-radius: 100px; padding: 3px 10px;
    font-size: 0.62rem; font-weight: 700;
    color: rgba(201,151,84,0.80) !important; letter-spacing: 1px; text-transform: uppercase;
  }
  .sb-divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(201,151,58,0.18) 30%, rgba(201,151,58,0.18) 70%, transparent);
    margin: 0 16px 10px;
    flex-shrink: 0;
  }
  .sb-nav-label {
    text-align: center !important; width: 100% !important;
    font-size: 0.70rem; font-weight: 800; letter-spacing: 1.8px; text-transform: uppercase;
    color: rgba(255,255,255,0.4) !important;
    margin: 0 0 8px !important;
    padding: 0 !important;
    flex-shrink: 0;
  }
  /* Nav radio wrapper — ambil sisa ruang tengah */
  [data-testid="stSidebar"] [data-testid="stRadio"] {
    flex: 1 !important;
    width: 100% !important;
    padding: 0 !important;
    margin: 0 !important;
  }
  .sb-footer {
    padding: 14px 24px 18px;
    margin-top: auto;
    flex-shrink: 0;
  }
  .sb-footer-divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.06) 50%, transparent);
    margin-bottom: 12px;
  }

  ::-webkit-scrollbar { width: 5px; }
  ::-webkit-scrollbar-track { background: transparent; }
  ::-webkit-scrollbar-thumb {
    background: linear-gradient(180deg, rgba(15,74,40,0.25), rgba(201,151,58,0.25));
    border-radius: 100px;
  }
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
    try:
        df_historis = pd.read_excel(os.path.join(base, "rata_rata_historis_provinsi.xlsx"))
    except Exception:
        df_historis = None
    try:
        import shap
        with open(os.path.join(base, "shap_explainer.pkl"), "rb") as f:
            shap_exp = pickle.load(f)
    except Exception:
        shap_exp = None
    return model_xgb, le, df_forecast, df_historis, shap_exp

model_xgb, le, df_forecast, df_historis, shap_exp = load_models()

FITUR_IKLIM = ["GWETROOT", "PRECTOTCORR", "RH2M", "T2M", "WS2M"]
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
        return {"label": "Baik",        "warna": "#2d9e5f", "icon": "✅", "pct": round(pct, 1)}
    elif pct >= 85:
        return {"label": "Cukup",       "warna": "#c9973a", "icon": "⚠️", "pct": round(pct, 1)}
    else:
        return {"label": "Rendah",      "warna": "#e74c3c", "icon": "❌", "pct": round(pct, 1)}


def status_iklim(nilai_input, avg_prov):
    hasil = {}
    for f in FITUR_IKLIM:
        avg = avg_prov.get(f)
        if not avg or avg == 0:
            hasil[f] = {"status": "normal", "label": "Normal", "warna": "#2d9e5f", "selisih_pct": 0}
            continue
        selisih_pct = ((nilai_input[f] - avg) / avg) * 100
        if selisih_pct > 10:
            hasil[f] = {"status": "di_atas",  "label": "Di Atas Normal",  "warna": "#2196F3", "selisih_pct": round(selisih_pct, 1)}
        elif selisih_pct < -10:
            hasil[f] = {"status": "di_bawah", "label": "Di Bawah Normal", "warna": "#c9973a", "selisih_pct": round(selisih_pct, 1)}
        else:
            hasil[f] = {"status": "normal",   "label": "Normal",          "warna": "#2d9e5f", "selisih_pct": round(selisih_pct, 1)}
    return hasil


def rekomendasi(status_dict, kategori):
    rekoms = []
    gwet = status_dict.get("GWETROOT",    {}).get("status")
    prec = status_dict.get("PRECTOTCORR", {}).get("status")
    rh   = status_dict.get("RH2M",        {}).get("status")
    t2m  = status_dict.get("T2M",         {}).get("status")
    ws   = status_dict.get("WS2M",        {}).get("status")
    if gwet == "di_bawah" or prec == "di_bawah":
        rekoms.append(("💧", "Perhatikan Ketersediaan Air",
            "Kelembaban tanah atau curah hujan di bawah normal. "
            "Pertimbangkan optimalisasi irigasi dan varietas tahan kekeringan."))
    if gwet == "di_atas" and prec == "di_atas":
        rekoms.append(("🌊", "Waspadai Kelebihan Air",
            "Curah hujan dan kelembaban tanah di atas normal. "
            "Pastikan drainase lahan berfungsi baik."))
    if t2m == "di_atas":
        rekoms.append(("🌡️", "Suhu Tinggi",
            "Suhu di atas rata-rata historis. "
            "Pertimbangkan pengaturan waktu tanam atau varietas toleran suhu tinggi."))
    if rh == "di_atas":
        rekoms.append(("🍄", "Waspadai Risiko Penyakit",
            "Kelembaban udara tinggi meningkatkan risiko serangan jamur. "
            "Tingkatkan pengawasan hama penyakit."))
    if ws == "di_atas":
        rekoms.append(("💨", "Kecepatan Angin Tinggi",
            "Angin kencang dapat menyebabkan kerebahan tanaman. "
            "Pertimbangkan varietas batang kokoh."))
    if not rekoms:
        rekoms.append(("🌾", "Kondisi Optimal",
            "Kondisi iklim mendukung produktivitas yang baik. "
            "Pertahankan praktik budidaya yang sudah berjalan."))
    return rekoms


# ── SIDEBAR ───────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
        <div class='sb-header'>
            <div class='sb-logo-wrap'>
                <div class='sb-logo-icon'>🌾</div>
                <div class='sb-logo-text'>
                    <h2>Padi<em>Sight</em></h2>
                    <p>SISTEM PREDIKSI PADI</p>
                </div>
            </div>
            <div style="text-align:center;">
                <span class='sb-pill'>✦ Machine Learning</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("<div class='sb-divider'></div>", unsafe_allow_html=True)
    st.markdown("<div class='sb-nav-label'>Navigasi Utama</div>", unsafe_allow_html=True)

    menu = st.radio(
        "nav",
        ["🏠 Beranda", "🌾 Prediksi Produktivitas", "📈 Peramalan Tren"],
        label_visibility="collapsed"
    )

    st.markdown("""
        <div class='sb-footer'>
            <div class='sb-footer-divider'></div>
            <div style='color:#666666 !important; font-size:0.75rem; text-align:center;
                        line-height:1.9; font-family:"DM Sans",sans-serif;'>
                Data: NASA POWER · BPS<br>
                Model: XGBoost · Prophet<br>
                2013 – 2025
            </div>
        </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════
# BERANDA
# ══════════════════════════════════════════════════════════
if menu == "🏠 Beranda":
    st.markdown("""
    <style>
      [data-testid="stMainBlockContainer"], .block-container {
        padding-top: 1rem !important; padding-bottom: 2rem !important;
      }
      [data-testid="stVerticalBlock"] { gap: 1.2rem !important; }
      [data-testid="stElementContainer"] { margin-bottom: 0.2rem !important; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
        <div style='padding:36px 0 28px;'>
            <div class='badge'>✦ Sistem Berbasis Machine Learning</div>
            <h1 style='font-size:3.2rem; font-weight:700; letter-spacing:-1.5px;
                       margin:10px 0 16px; line-height:1.1;
                       font-family:"Playfair Display",Georgia,serif; color:#0a1208;'>
                Prediksi <em style='color:#1a6b3c; font-style:italic;'>Produktivitas</em><br>
                Padi Indonesia
            </h1>
            <p style='color:#2d4035; font-size:1.05rem; max-width:520px; line-height:1.80; margin:0;'>
                Memanfaatkan data iklim NASA POWER dan algoritma XGBoost untuk memprediksi
                dan meramalkan produktivitas padi di 34 provinsi dengan akurasi tinggi.
            </p>
        </div>
    """, unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        with st.container(border=True):
            st.metric("Provinsi", "34", "Seluruh Indonesia")
    with c2:
        with st.container(border=True):
            st.metric("Periode Data", "13 Tahun", "2013 – 2025")
    with c3:
        with st.container(border=True):
            st.metric("Akurasi Model", "0.81", "R² XGBoost")
    with c4:
        with st.container(border=True):
            st.metric("Proyeksi", "+5 Tahun", "ke Depan")

    st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)

    col1, col2 = st.columns(2, gap="medium")
    with col1:
        st.markdown("""
        <div class='feature-card'>
            <div class='feat-num'>01</div>
            <div style='font-size:2rem; margin-bottom:14px; line-height:1;'>🌾</div>
            <div style='font-size:0.66rem; font-weight:700; color:#1a6b3c;
                        letter-spacing:1.4px; margin-bottom:9px; text-transform:uppercase;'>Prediksi</div>
            <h3 style='margin:0 0 11px; font-size:1.2rem;
                       font-family:"Playfair Display",Georgia,serif;
                       font-weight:600; color:#0a1208;'>Prediksi Produktivitas</h3>
            <p style='color:#2d4035; font-size:0.87rem; line-height:1.80; margin:0;'>
                Input data iklim suatu provinsi, dapatkan prediksi produktivitas padi (kuintal/ha),
                analisis kondisi iklim, dan rekomendasi tindakan menggunakan model XGBoost.
            </p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class='feature-card'>
            <div class='feat-num'>02</div>
            <div style='font-size:2rem; margin-bottom:14px; line-height:1;'>📈</div>
            <div style='font-size:0.66rem; font-weight:700; color:#1a6b3c;
                        letter-spacing:1.4px; margin-bottom:9px; text-transform:uppercase;'>Peramalan</div>
            <h3 style='margin:0 0 11px; font-size:1.2rem;
                       font-family:"Playfair Display",Georgia,serif;
                       font-weight:600; color:#0a1208;'>Peramalan Tren</h3>
            <p style='color:#2d4035; font-size:0.87rem; line-height:1.80; margin:0;'>
                Lihat tren historis dan proyeksi produktivitas padi 5 tahun ke depan
                per provinsi menggunakan model Facebook Prophet yang andal.
            </p>
        </div>
        """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════
# PREDIKSI PRODUKTIVITAS
# ══════════════════════════════════════════════════════════
elif menu == "🌾 Prediksi Produktivitas":
    st.markdown("""
        <div style='padding:8px 0 10px;'>
            <div class='badge'>🌾 Fitur 01</div>
            <h1 style='font-size:1.9rem; font-weight:700; letter-spacing:-0.5px; margin:5px 0 5px;
                       font-family:"Playfair Display",Georgia,serif; color:#0a1208;'>
                Prediksi Produktivitas Padi
            </h1>
            <p style='color:#2d4035; margin-bottom:0; font-size:0.88rem;
                      max-width:520px; line-height:1.6;'>
                Masukkan data iklim suatu provinsi untuk mendapatkan prediksi produktivitas,
                analisis kondisi iklim, dan rekomendasi tindakan yang akurat.
            </p>
        </div>
    """, unsafe_allow_html=True)

    col_form, col_hasil = st.columns([1, 1.2], gap="large")

    # ── Form Input ─────────────────────────────────────────
    with col_form:
        with st.container(border=True):
            st.markdown("<div class='section-label'>📥 Input Data Iklim</div>",
                        unsafe_allow_html=True)

            provinsi_list    = sorted(list(le.classes_))
            provinsi_display = [p.capitalize() for p in provinsi_list]
            prov_idx = st.selectbox(
                "Provinsi", range(len(provinsi_list)),
                format_func=lambda i: provinsi_display[i]
            )
            provinsi = provinsi_list[prov_idx]

            tahun = st.number_input("Tahun", min_value=2013, max_value=2030, value=2025)

            c1, c2 = st.columns(2)
            with c1:
                gwetroot = st.number_input(
                    "Kel. Tanah (0–1)", min_value=0.0, max_value=1.0,
                    value=0.85, step=0.001, format="%.3f"
                )
                rh2m = st.number_input(
                    "Kel. Udara (%)", min_value=0.0, max_value=100.0,
                    value=85.0, step=0.01
                )
            with c2:
                prectotcorr = st.number_input(
                    "Curah Hujan (mm/hr)", min_value=0.0,
                    value=7.5, step=0.001, format="%.3f"
                )
                t2m = st.number_input("Suhu (°C)", value=26.0, step=0.01)

            ws2m = st.number_input("Kec. Angin (m/s)", min_value=0.0, value=1.4, step=0.01)

            st.markdown("""
            <hr style='border:none; border-top:1px solid rgba(201,151,58,0.18); margin:8px 0 14px;'>
            <div class='section-label'>📐 Hitung Produksi Total</div>
            """, unsafe_allow_html=True)

            luas_panen   = st.number_input("Luas Panen (ha)", min_value=0.0, value=0.0, step=1000.0)
            prediksi_btn = st.button("🌾 Prediksi Sekarang", use_container_width=True)

    # ── Kolom Hasil ────────────────────────────────────────
    with col_hasil:
        if prediksi_btn:

            # ── VALIDASI: luas panen wajib > 0 ─────────────
            if luas_panen <= 0:
                st.markdown("""
                <div class='warning-box'>
                    <div style='font-size:0.85rem; font-weight:700; color:#7a5c1e; margin-bottom:6px;
                                font-family:"DM Sans",sans-serif;'>
                        ⚠️ Data Belum Lengkap
                    </div>
                    <div style='font-size:0.82rem; color:#5c4a1a; line-height:1.75;
                                font-family:"DM Sans",sans-serif;'>
                        Kolom <strong>Luas Panen (ha)</strong> wajib diisi dengan nilai lebih dari
                        <strong>0</strong> agar estimasi total produksi dapat dihitung.<br><br>
                        Silakan isi kolom tersebut pada form sebelah kiri, lalu klik
                        <strong>🌾 Prediksi Sekarang</strong> kembali.
                    </div>
                </div>
                """, unsafe_allow_html=True)

            else:
                # ── Jalankan prediksi ───────────────────────
                nilai_input = {
                    "GWETROOT": gwetroot, "PRECTOTCORR": prectotcorr,
                    "RH2M": rh2m, "T2M": t2m, "WS2M": ws2m
                }
                prov_encoded  = int(le.transform([provinsi])[0])
                fitur         = [[gwetroot, prectotcorr, rh2m, t2m, ws2m, tahun, prov_encoded]]
                produktivitas = float(model_xgb.predict(fitur)[0])

                avg_prov     = {}
                avg_nasional = None
                if df_historis is not None:
                    row = df_historis[df_historis['Provinsi'] == provinsi]
                    if not row.empty:
                        avg_prov = {
                            fk: float(row.iloc[0].get(fk, 0))
                            for fk in FITUR_IKLIM + ['Produktivitas']
                        }
                    avg_nasional = float(df_historis['Produktivitas'].mean())

                kat      = kategori_produktivitas(produktivitas, avg_nasional or produktivitas)
                status   = status_iklim(nilai_input, avg_prov)
                rekoms   = rekomendasi(status, kat)
                produksi = (produktivitas * luas_panen) / 10  # ton

                # ── FIX: Card produktivitas (tanpa embed HTML dalam f-string) ──
                # Render card utama terpisah dari blok estimasi produksi
                # agar kurung kurawal CSS tidak dikira ekspresi Python.

                kat_badge = (
                    "<span style='"
                    "display:inline-block;"
                    "background:" + kat['warna'] + "22;"
                    "color:" + kat['warna'] + ";"
                    "padding:7px 18px;"
                    "border-radius:100px;"
                    "font-size:0.81rem;"
                    "font-weight:600;"
                    "border:1px solid " + kat['warna'] + "44;"
                    "font-family:\"DM Sans\",sans-serif;'>"
                    + kat['icon'] + " " + kat['label']
                    + " &nbsp;·&nbsp; " + str(kat['pct']) + "% dari rata-rata nasional"
                    + "</span>"
                )

                st.markdown(
                    "<div class='hasil-card'>"
                        "<div style='font-size:0.64rem; font-weight:700; color:#c9973a;"
                        " letter-spacing:1.8px; text-transform:uppercase; margin-bottom:10px;"
                        " font-family:\"DM Sans\",sans-serif; position:relative; z-index:1;'>"
                        "Produktivitas Prediksi"
                        "</div>"
                        "<div style='font-size:3.8rem; font-weight:600; color:white;"
                        " letter-spacing:-2px; line-height:1;"
                        " font-family:\"Playfair Display\",Georgia,serif;"
                        " position:relative; z-index:1;'>"
                        + f"{produktivitas:.2f}" +
                        "</div>"
                        "<div style='font-size:0.84rem; color:rgba(255,255,255,0.38);"
                        " margin-top:4px; font-family:\"DM Sans\",sans-serif;"
                        " position:relative; z-index:1;'>"
                        "kuintal / ha"
                        "</div>"
                        "<div style='margin-top:6px; font-size:0.76rem;"
                        " color:rgba(255,255,255,0.28); font-family:\"DM Sans\",sans-serif;"
                        " position:relative; z-index:1;'>"
                        + f"{provinsi.capitalize()} &nbsp;·&nbsp; {tahun}" +
                        "</div>"
                        "<div style='margin-top:18px; position:relative; z-index:1;'>"
                        + kat_badge +
                        "</div>"
                    "</div>",
                    unsafe_allow_html=True
                )

                # ── Estimasi Produksi — blok TERPISAH ──────
                st.markdown(
                    "<div class='produksi-card'>"
                        "<div style='font-size:0.64rem; color:rgba(255,255,255,0.30);"
                        " text-transform:uppercase; letter-spacing:1.2px;"
                        " font-family:\"DM Sans\",sans-serif;'>"
                        "Estimasi Total Produksi"
                        "</div>"
                        "<div style='font-size:2.1rem; font-weight:600; color:#e2b554;"
                        " font-family:\"Playfair Display\",Georgia,serif; margin-top:3px;'>"
                        + f"{produksi:,.0f}" +
                        "<span style='font-size:0.88rem; color:rgba(226,181,84,0.55);"
                        " font-family:\"DM Sans\",sans-serif;'>&nbsp;ton</span>"
                        "</div>"
                    "</div>",
                    unsafe_allow_html=True
                )

                # ── Perbandingan Historis & Status Iklim ───
                c1, c2 = st.columns(2)

                with c1:
                    with st.container(border=True):
                        st.markdown(
                            "<div class='section-label'>📊 Perbandingan Historis</div>",
                            unsafe_allow_html=True
                        )
                        if avg_prov.get('Produktivitas'):
                            selisih     = produktivitas - avg_prov['Produktivitas']
                            selisih_pct = (selisih / avg_prov['Produktivitas']) * 100
                            arah        = "↑" if selisih >= 0 else "↓"
                            warna_arah  = "#1a6b3c" if selisih >= 0 else "#e74c3c"

                            rows_html = (
                                "<tr>"
                                "<td style='color:#6b8878; padding:10px 12px 10px 4px;"
                                " border-bottom:1px solid rgba(201,151,58,0.12);"
                                " line-height:1.4;'>Prediksi saat ini</td>"
                                "<td style='text-align:right; font-weight:600; color:#0a1208;"
                                " padding:10px 4px 10px 8px;"
                                " border-bottom:1px solid rgba(201,151,58,0.12);"
                                " white-space:nowrap;'>"
                                + f"{produktivitas:.2f} kw/ha" +
                                "</td></tr>"

                                "<tr>"
                                "<td style='color:#6b8878; padding:10px 12px 10px 4px;"
                                " border-bottom:1px solid rgba(201,151,58,0.12);"
                                " line-height:1.4;'>Rata-rata historis</td>"
                                "<td style='text-align:right; font-weight:600; color:#0a1208;"
                                " padding:10px 4px 10px 8px;"
                                " border-bottom:1px solid rgba(201,151,58,0.12);"
                                " white-space:nowrap;'>"
                                + f"{avg_prov['Produktivitas']:.2f} kw/ha" +
                                "</td></tr>"

                                "<tr>"
                                "<td style='color:#6b8878; padding:10px 12px 10px 4px;"
                                " border-bottom:1px solid rgba(201,151,58,0.12);"
                                " line-height:1.4;'>Rata-rata nasional</td>"
                                "<td style='text-align:right; font-weight:600; color:#0a1208;"
                                " padding:10px 4px 10px 8px;"
                                " border-bottom:1px solid rgba(201,151,58,0.12);"
                                " white-space:nowrap;'>"
                                + f"{avg_nasional:.2f} kw/ha" +
                                "</td></tr>"

                                "<tr>"
                                "<td style='color:#6b8878; padding:10px 12px 10px 4px;"
                                " line-height:1.4;'>Selisih historis</td>"
                                "<td style='text-align:right; font-weight:700;"
                                " color:" + warna_arah + ";"
                                " font-size:0.85rem; padding:10px 4px 10px 8px;"
                                " white-space:nowrap;'>"
                                + f"{arah} {abs(selisih):.2f} ({abs(selisih_pct):.1f}%)" +
                                "</td></tr>"
                            )

                            st.markdown(
                                "<table style='width:100%; font-size:0.82rem;"
                                " border-collapse:collapse;"
                                " font-family:\"DM Sans\",sans-serif; table-layout:fixed;'>"
                                "<colgroup>"
                                "<col style='width:58%;'>"
                                "<col style='width:42%;'>"
                                "</colgroup>"
                                + rows_html +
                                "</table>",
                                unsafe_allow_html=True
                            )
                        else:
                            st.caption("Data historis belum tersedia.")

                with c2:
                    with st.container(border=True):
                        st.markdown(
                            "<div class='section-label'>🌡️ Status Kondisi Iklim</div>",
                            unsafe_allow_html=True
                        )
                        for f, v in status.items():
                            selisih_str = (
                                "+" + str(v['selisih_pct']) + "%"
                                if v['selisih_pct'] >= 0
                                else str(v['selisih_pct']) + "%"
                            )
                            dot_shadow = "0 0 0 3px " + v['warna'] + "22"
                            st.markdown(
                                "<div style='display:flex; align-items:center; gap:12px;"
                                " padding:9px 12px;"
                                " background:rgba(10,18,8,0.025);"
                                " border-radius:11px; margin-bottom:7px;"
                                " border:1px solid rgba(201,151,58,0.08);'>"
                                "<div style='width:8px; height:8px; border-radius:50%;"
                                " background:" + v['warna'] + ";"
                                " flex-shrink:0;"
                                " box-shadow:" + dot_shadow + ";'></div>"
                                "<div style='flex:1; font-size:0.81rem; color:#2d4035;"
                                " font-weight:500;"
                                " font-family:\"DM Sans\",sans-serif;'>"
                                + LABEL_IKLIM[f] +
                                "</div>"
                                "<div style='text-align:right;'>"
                                "<div style='font-size:0.75rem; font-weight:700;"
                                " color:" + v['warna'] + ";"
                                " font-family:\"DM Sans\",sans-serif;'>"
                                + v['label'] +
                                "</div>"
                                "<div style='font-size:0.69rem; color:#6b8878;"
                                " font-family:\"DM Sans\",sans-serif;'>"
                                + selisih_str + " dari historis"
                                "</div>"
                                "</div>"
                                "</div>",
                                unsafe_allow_html=True
                            )

                # ── Rekomendasi Tindakan ────────────────────
                with st.container(border=True):
                    st.markdown(
                        "<div class='section-label'>💡 Rekomendasi Tindakan</div>",
                        unsafe_allow_html=True
                    )
                    for icon, judul, detail in rekoms:
                        st.markdown(
                            "<div class='rekom-item'>"
                            "<div style='display:flex; align-items:flex-start; gap:10px;'>"
                            "<span style='font-size:1.2rem; flex-shrink:0; line-height:1.4;'>"
                            + icon +
                            "</span>"
                            "<div>"
                            "<div style='font-size:0.85rem; font-weight:700; color:#0a1208;"
                            " margin-bottom:4px; font-family:\"DM Sans\",sans-serif;'>"
                            + judul +
                            "</div>"
                            "<div style='font-size:0.80rem; color:#2d4035; line-height:1.70;"
                            " font-family:\"DM Sans\",sans-serif;'>"
                            + detail +
                            "</div>"
                            "</div></div></div>",
                            unsafe_allow_html=True
                        )

        else:
            # ── Placeholder sebelum prediksi ─────────────
            st.markdown("""
            <div style='background:#ffffff; border-radius:20px; padding:40px 20px;
                        box-shadow:0 4px 28px rgba(0,0,0,0.10), 0 1px 6px rgba(0,0,0,0.07);
                        text-align:center;'>
                <div style='width:76px; height:76px;
                            background:linear-gradient(135deg,rgba(15,74,40,0.07),rgba(201,151,58,0.05));
                            border-radius:22px; display:flex; align-items:center; justify-content:center;
                            font-size:2rem; margin:0 auto 16px;
                            border:1.5px solid rgba(201,151,58,0.15);'>🌾</div>
                <p style='font-size:0.94rem; line-height:1.75; color:#6b8878; margin:0;
                          font-family:"DM Sans",sans-serif;'>
                    Isi form di sebelah kiri dan klik<br>
                    <strong style='color:#1a6b3c; font-weight:700;'>"Prediksi Sekarang"</strong>
                </p>
            </div>
            """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════
# PERAMALAN TREN
# ══════════════════════════════════════════════════════════
elif menu == "📈 Peramalan Tren":
    st.markdown("""
        <div style='padding:8px 0 10px;'>
            <div class='badge'>📈 Fitur 02</div>
            <h1 style='font-size:1.9rem; font-weight:700; letter-spacing:-0.5px; margin:5px 0 5px;
                       font-family:"Playfair Display",Georgia,serif; color:#0a1208;'>
                Peramalan Tren Produktivitas
            </h1>
            <p style='color:#2d4035; margin-bottom:0; font-size:0.88rem;
                      max-width:560px; line-height:1.6;'>
                Lihat tren historis dan proyeksi produktivitas padi 5 tahun ke depan per provinsi
                menggunakan model Facebook Prophet yang teruji.
            </p>
        </div>
    """, unsafe_allow_html=True)

    provinsi_list    = sorted(df_forecast['Provinsi'].unique().tolist())
    provinsi_display = [p.capitalize() for p in provinsi_list]
    prov_idx         = st.selectbox(
        "Pilih Provinsi", range(len(provinsi_list)),
        format_func=lambda i: provinsi_display[i]
    )
    provinsi_sel = provinsi_list[prov_idx]

    df_prov = df_forecast[df_forecast['Provinsi'] == provinsi_sel].sort_values('Tahun')
    df_hist = df_prov[df_prov['Is_Forecast'] == False]
    df_proj = df_prov[df_prov['Is_Forecast'] == True]

    terakhir     = df_hist.iloc[-1] if not df_hist.empty else None
    proj_pertama = df_proj.iloc[0]  if not df_proj.empty else None
    proj_last    = df_proj.iloc[-1] if not df_proj.empty else None
    peak         = df_proj.loc[df_proj['Proyeksi'].idxmax()] if not df_proj.empty else None

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        with st.container(border=True):
            st.metric(
                "Produktivitas Terakhir",
                f"{terakhir['Aktual']:.2f} kw/ha" if terakhir is not None else "—",
                f"Tahun {int(terakhir['Tahun'])}" if terakhir is not None else ""
            )
    with c2:
        with st.container(border=True):
            st.metric(
                "Proyeksi Tahun Pertama",
                f"{proj_pertama['Proyeksi']:.2f} kw/ha" if proj_pertama is not None else "—",
                f"Tahun {int(proj_pertama['Tahun'])}" if proj_pertama is not None else ""
            )
    with c3:
        with st.container(border=True):
            if terakhir is not None and proj_last is not None:
                tren = ((proj_last['Proyeksi'] - terakhir['Aktual']) / terakhir['Aktual']) * 100
                st.metric("Tren 5 Tahun", f"{tren:+.1f}%", "dari tahun terakhir")
            else:
                st.metric("Tren 5 Tahun", "—")
    with c4:
        with st.container(border=True):
            st.metric(
                "Puncak Proyeksi",
                f"{peak['Proyeksi']:.2f} kw/ha" if peak is not None else "—",
                f"Tahun {int(peak['Tahun'])}" if peak is not None else ""
            )

    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown(
            "<div class='section-label'>📊 Grafik Tren — "
            + provinsi_sel.capitalize() +
            "</div>",
            unsafe_allow_html=True
        )

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df_hist['Tahun'], y=df_hist['Aktual'],
            mode='lines+markers', name='Aktual',
            line=dict(color='#1a6b3c', width=2.5),
            marker=dict(size=7, color='#1a6b3c', line=dict(color='white', width=1.5)),
        ))
        fig.add_trace(go.Scatter(
            x=pd.concat([df_proj['Tahun'], df_proj['Tahun'][::-1]]),
            y=pd.concat([df_proj['Upper_95'], df_proj['Lower_95'][::-1]]),
            fill='toself', fillcolor='rgba(201,151,58,0.10)',
            line=dict(color='rgba(255,255,255,0)'),
            name='Interval 95%', showlegend=True
        ))
        fig.add_trace(go.Scatter(
            x=df_proj['Tahun'], y=df_proj['Proyeksi'],
            mode='lines+markers', name='Proyeksi',
            line=dict(color='#c9973a', width=2.5, dash='dash'),
            marker=dict(size=7, color='#c9973a', line=dict(color='white', width=1.5)),
        ))
        tahun_akhir = int(df_hist['Tahun'].max()) if not df_hist.empty else 2025
        fig.add_vline(x=tahun_akhir, line_dash="dot", line_color="rgba(10,18,8,0.18)")
        fig.update_layout(
            xaxis=dict(
                title='Tahun', gridcolor='rgba(10,18,8,0.05)', tickmode='linear',
                title_font=dict(size=11, color='#6b8878', family='DM Sans'),
                tickfont=dict(size=11, color='#6b8878', family='DM Sans')
            ),
            yaxis=dict(
                title='Produktivitas (kuintal/ha)', gridcolor='rgba(10,18,8,0.05)',
                title_font=dict(size=11, color='#6b8878', family='DM Sans'),
                tickfont=dict(size=11, color='#6b8878', family='DM Sans')
            ),
            plot_bgcolor='white', paper_bgcolor='white',
            legend=dict(
                orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1,
                font=dict(family='DM Sans', size=11, color='#2d4035'),
                bgcolor='rgba(255,255,255,0.95)',
                bordercolor='rgba(201,151,58,0.18)', borderwidth=1
            ),
            height=400, margin=dict(l=8, r=8, t=40, b=8), hovermode='x unified',
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown(
        "<div class='section-label' style='margin-top:4px;'>📋 Data Historis & Proyeksi</div>",
        unsafe_allow_html=True
    )

    df_tabel = df_prov[['Tahun', 'Aktual', 'Proyeksi', 'Lower_95', 'Upper_95', 'Is_Forecast']].copy()
    df_tabel['Tipe']     = df_tabel['Is_Forecast'].apply(lambda x: '🔮 Proyeksi' if x else '📊 Historis')
    df_tabel['Aktual']   = df_tabel['Aktual'].apply(lambda x:   f"{x:.2f}" if pd.notna(x) else '—')
    df_tabel['Proyeksi'] = df_tabel['Proyeksi'].apply(lambda x: f"{x:.2f}" if pd.notna(x) else '—')
    df_tabel['Lower_95'] = df_tabel['Lower_95'].apply(lambda x: f"{x:.2f}" if pd.notna(x) else '—')
    df_tabel['Upper_95'] = df_tabel['Upper_95'].apply(lambda x: f"{x:.2f}" if pd.notna(x) else '—')
    df_tabel = df_tabel[['Tahun', 'Tipe', 'Aktual', 'Proyeksi', 'Lower_95', 'Upper_95']]
    df_tabel.columns = [
        'Tahun', 'Tipe', 'Aktual (kw/ha)',
        'Proyeksi (kw/ha)', 'Batas Bawah 95%', 'Batas Atas 95%'
    ]
    st.dataframe(
        df_tabel.sort_values('Tahun', ascending=False),
        use_container_width=True,
        hide_index=True
    )
