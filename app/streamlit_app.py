"""ScholAR - Autonomous Research Agent Frontend (Streamlit)."""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import json
import networkx as nx
import hashlib
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import agent
from storage import ResearchStorage
from export import export_to_bibtex, export_to_markdown, export_to_csv, export_to_json, export_to_ris, export_to_html
from analysis import (
    calculate_paper_quality_score,
    identify_research_gaps,
    extract_author_network,
    build_reading_roadmap,
    extract_timeline_data,
    find_related_topics
)
from comparison import compare_topics, find_related_topics_by_keywords
import warnings
warnings.filterwarnings('ignore')

try:
    from pdf_generator import generate_report_bytes
    PDF_AVAILABLE = True
except Exception as e:
    print(f"PDF import error: {e}")
    PDF_AVAILABLE = False
    generate_report_bytes = None

storage = ResearchStorage(storage_dir="scholarpython_research")

if "research_complete" not in st.session_state:
    st.session_state.research_complete = False
if "research_data" not in st.session_state:
    st.session_state.research_data = None
if "research_topic_current" not in st.session_state:
    st.session_state.research_topic_current = None
if "from_cache" not in st.session_state:
    st.session_state.from_cache = False
if "bookmarked_papers" not in st.session_state:
    st.session_state.bookmarked_papers = []
if "force_new_search" not in st.session_state:
    st.session_state.force_new_search = False
if "show_comparison" not in st.session_state:
    st.session_state.show_comparison = False
if "comparison_data" not in st.session_state:
    st.session_state.comparison_data = None

st.set_page_config(
    page_title="ScholAR - Autonomous Research Agent",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ══════════════════════════════════════════════════════════════════════════════
#  GLOBAL STYLES  —  Deep Aurora / Purple Nebula Theme
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=Space+Grotesk:wght@400;500;600;700;800&display=swap');

/* ── variables ── */
:root {
  --void:       #03010a;
  --deep:       #07040f;
  --ink:        #0d0720;
  --glass:      rgba(255,255,255,0.04);
  --glass-border: rgba(255,255,255,0.09);
  --purple-core: #7b2fff;
  --purple-mid:  #9d4edd;
  --purple-soft: #c77dff;
  --indigo:      #4361ee;
  --violet:      #b721ff;
  --white:       #ffffff;
  --off-white:   rgba(255,255,255,0.85);
  --muted:       rgba(255,255,255,0.45);
  --glow-purple: rgba(123,47,255,0.55);
  --glow-violet: rgba(183,33,255,0.4);
}

/* ── base ── */
html, body, [class*="css"] {
  font-family: 'Inter', sans-serif !important;
  color: rgba(255,255,255,0.75) !important;
}

/* ── input placeholder ── */
input::placeholder {
  color: rgba(255,255,255,0.4) !important;
  opacity: 1 !important;
}

input {
  color: rgba(255,255,255,0.8) !important;
}

/* ── text elements ── */
p, span, div, label {
  color: rgba(255,255,255,0.75) !important;
}

/* ── headers ── */
h1, h2, h3, h4, h5, h6 {
  color: rgba(255,255,255,0.9) !important;
}

/* ── app background — deep black with subtle purple tint ── */
.stApp {
  background: #03010a !important;
  min-height: 100vh;
  overflow-x: hidden;
}

/* ── large ambient aurora behind everything ── */
.stApp::before {
  content: '';
  position: fixed;
  top: -20%; left: 50%;
  width: 900px; height: 900px;
  transform: translateX(-50%);
  background: radial-gradient(ellipse at center,
    rgba(123,47,255,0.28) 0%,
    rgba(157,78,221,0.14) 30%,
    rgba(67,97,238,0.06) 60%,
    transparent 75%);
  border-radius: 50%;
  pointer-events: none;
  z-index: 0;
  animation: ambientPulse 8s ease-in-out infinite;
}

.stApp::after {
  content: '';
  position: fixed;
  bottom: -10%; left: -10%;
  width: 600px; height: 600px;
  background: radial-gradient(ellipse at center,
    rgba(183,33,255,0.18) 0%,
    rgba(123,47,255,0.08) 50%,
    transparent 70%);
  border-radius: 50%;
  pointer-events: none;
  z-index: 0;
  animation: ambientPulse 11s ease-in-out infinite reverse;
}

@keyframes ambientPulse {
  0%,100% { transform: translateX(-50%) scale(1);   opacity: 1; }
  50%      { transform: translateX(-50%) scale(1.12); opacity: 0.75; }
}

/* ── sidebar ── */
[data-testid="stSidebar"] {
  background: linear-gradient(180deg, #06030f 0%, #0a061a 100%) !important;
  border-right: 1px solid rgba(123,47,255,0.2) !important;
  box-shadow: 4px 0 60px rgba(123,47,255,0.1) !important;
}
[data-testid="stSidebar"] * { color: #e8e8ff !important; }

[data-testid="stSidebar"] .stTextInput input {
  background: rgba(123,47,255,0.08) !important;
  border: 1px solid rgba(123,47,255,0.3) !important;
  border-radius: 12px !important;
  color: rgba(255,255,255,0.8) !important;
  padding: 12px 16px !important;
  font-size: 14px !important;
  transition: all 0.35s ease !important;
}
[data-testid="stSidebar"] .stTextInput input::placeholder {
  color: rgba(255,255,255,0.4) !important;
  opacity: 1 !important;
}
[data-testid="stSidebar"] .stTextInput input:focus {
  border-color: var(--purple-soft) !important;
  box-shadow: 0 0 0 3px rgba(123,47,255,0.2), 0 0 24px rgba(123,47,255,0.3) !important;
  outline: none !important;
}

/* ── primary button ── */
.stButton > button[kind="primary"] {
  background: linear-gradient(135deg, #7b2fff 0%, #b721ff 100%) !important;
  border: none !important;
  border-radius: 50px !important;
  color: #fff !important;
  font-weight: 700 !important;
  font-size: 14px !important;
  letter-spacing: 0.6px !important;
  padding: 12px 28px !important;
  box-shadow: 0 0 30px rgba(123,47,255,0.5), 0 4px 20px rgba(183,33,255,0.3) !important;
  transition: all 0.3s cubic-bezier(0.23,1,0.32,1) !important;
  position: relative !important;
  overflow: hidden !important;
}
.stButton > button[kind="primary"]:hover {
  transform: translateY(-3px) scale(1.04) !important;
  box-shadow: 0 0 50px rgba(123,47,255,0.7), 0 8px 30px rgba(183,33,255,0.4) !important;
}
.stButton > button[kind="primary"]::after {
  content: '';
  position: absolute; top:0; left:-100%;
  width:60%; height:100%;
  background: linear-gradient(90deg,transparent,rgba(255,255,255,0.3),transparent);
  animation: btnShimmer 2.5s infinite;
}
@keyframes btnShimmer { 0%{left:-100%} 100%{left:220%} }

/* ── secondary button ── */
.stButton > button:not([kind="primary"]) {
  background: rgba(123,47,255,0.1) !important;
  border: 1px solid rgba(123,47,255,0.35) !important;
  border-radius: 50px !important;
  color: var(--purple-soft) !important;
  font-weight: 600 !important;
  transition: all 0.3s ease !important;
}
.stButton > button:not([kind="primary"]):hover {
  background: rgba(123,47,255,0.2) !important;
  box-shadow: 0 0 24px rgba(123,47,255,0.35) !important;
  transform: translateY(-2px) !important;
}

/* ── sidebar button override ── */
[data-testid="stSidebar"] .stButton:last-child > button,
[data-testid="stSidebar"] .stButton:nth-child(2) > button {
  background: rgba(100, 100, 120, 0.25) !important;
  border: 1px solid rgba(150, 150, 170, 0.4) !important;
  color: rgba(255, 255, 255, 0.7) !important;
  border-radius: 50px !important;
  font-weight: 600 !important;
}
[data-testid="stSidebar"] .stButton:last-child > button:hover,
[data-testid="stSidebar"] .stButton:nth-child(2) > button:hover {
  background: rgba(100, 100, 120, 0.4) !important;
  color: rgba(255, 255, 255, 0.9) !important;
  box-shadow: 0 0 15px rgba(100, 100, 120, 0.3) !important;
}

/* ── tabs ── */
.stTabs [data-baseweb="tab-list"] {
  background: rgba(255,255,255,0.04) !important;
  backdrop-filter: blur(20px) !important;
  -webkit-backdrop-filter: blur(20px) !important;
  border-radius: 16px !important;
  padding: 5px !important;
  border: 1px solid var(--glass-border) !important;
  gap: 3px !important;
}
.stTabs [data-baseweb="tab-list"] button {
  font-size: 13px !important;
  font-weight: 600 !important;
  border-radius: 11px !important;
  color: rgba(255,255,255,0.45) !important;
  padding: 10px 22px !important;
  transition: all 0.3s ease !important;
  letter-spacing: 0.3px !important;
}
.stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
  background: linear-gradient(135deg, rgba(123,47,255,0.35), rgba(183,33,255,0.25)) !important;
  color: rgba(255,255,255,0.9) !important;
  border: 1px solid rgba(123,47,255,0.4) !important;
  box-shadow: 0 0 20px rgba(123,47,255,0.25), inset 0 1px 0 rgba(255,255,255,0.1) !important;
}

/* ── metric cards ── */
[data-testid="stMetric"] {
  background: rgba(255,255,255,0.035) !important;
  border: 1px solid var(--glass-border) !important;
  border-radius: 20px !important;
  padding: 22px !important;
  backdrop-filter: blur(20px) !important;
  transition: all 0.35s cubic-bezier(0.23,1,0.32,1) !important;
  position: relative;
  overflow: hidden;
}
[data-testid="stMetric"]::before {
  content:'';
  position:absolute; inset:0;
  background: linear-gradient(135deg,rgba(123,47,255,0.08),transparent);
  border-radius:20px;
  pointer-events:none;
}
[data-testid="stMetric"]:hover {
  border-color: rgba(123,47,255,0.45) !important;
  box-shadow: 0 0 40px rgba(123,47,255,0.18), 0 12px 40px rgba(0,0,0,0.5) !important;
  transform: translateY(-5px) !important;
}
[data-testid="stMetricValue"] {
  color: rgba(255,255,255,0.9) !important;
  font-family: 'Space Grotesk', sans-serif !important;
  font-size: 2.2rem !important;
  font-weight: 800 !important;
}
[data-testid="stMetricLabel"] {
  color: rgba(255,255,255,0.45) !important;
  font-size: 11px !important;
  font-weight: 600 !important;
  text-transform: uppercase !important;
  letter-spacing: 1.5px !important;
}

/* ── expanders ── */
.streamlit-expanderHeader {
  background: rgba(255,255,255,0.03) !important;
  border: 1px solid var(--glass-border) !important;
  border-radius: 14px !important;
  color: rgba(255,255,255,0.75) !important;
  font-weight: 600 !important;
  transition: all 0.3s ease !important;
  backdrop-filter: blur(12px) !important;
}
.streamlit-expanderHeader:hover {
  border-color: rgba(123,47,255,0.4) !important;
  background: rgba(123,47,255,0.08) !important;
}
.streamlit-expanderContent {
  background: rgba(7,4,15,0.8) !important;
  border: 1px solid var(--glass-border) !important;
  border-top: none !important;
  border-radius: 0 0 14px 14px !important;
}

/* ── dataframe ── */
.stDataFrame {
  border: 1px solid var(--glass-border) !important;
  border-radius: 16px !important;
  overflow: hidden !important;
  backdrop-filter: blur(10px) !important;
}

/* ── alerts ── */
.stAlert { border-radius: 14px !important; backdrop-filter: blur(10px) !important; }

/* ── select ── */
.stSelectbox > div > div {
  background: rgba(123,47,255,0.07) !important;
  border: 1px solid rgba(123,47,255,0.25) !important;
  border-radius: 12px !important;
}

/* ── download button ── */
.stDownloadButton > button {
  background: linear-gradient(135deg,rgba(123,47,255,0.2),rgba(183,33,255,0.15)) !important;
  border: 1px solid rgba(123,47,255,0.4) !important;
  border-radius: 50px !important;
  color: var(--purple-soft) !important;
  font-weight: 700 !important;
  font-size: 15px !important;
  padding: 14px 32px !important;
  transition: all 0.3s ease !important;
}
.stDownloadButton > button:hover {
  background: linear-gradient(135deg,rgba(123,47,255,0.35),rgba(183,33,255,0.28)) !important;
  box-shadow: 0 0 40px rgba(123,47,255,0.4) !important;
  transform: translateY(-2px) !important;
}

/* ── code / pre ── */
pre, code {
  background: rgba(0,0,0,0.5) !important;
  border: 1px solid rgba(123,47,255,0.2) !important;
  border-radius: 12px !important;
  color: var(--purple-soft) !important;
  font-size: 13px !important;
}

/* ── markdown ── */
.stMarkdown p, .stMarkdown li { color: rgba(255,255,255,0.75) !important; }
.stMarkdown h1,.stMarkdown h2,.stMarkdown h3 {
  color: rgba(255,255,255,0.9) !important;
  font-family: 'Space Grotesk',sans-serif !important;
}
.stMarkdown strong { color: var(--purple-soft) !important; }
.stMarkdown a { color: var(--purple-mid) !important; }

/* ── scrollbar ── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: var(--void); }
::-webkit-scrollbar-thumb {
  background: linear-gradient(180deg,#7b2fff,#b721ff);
  border-radius: 3px;
}

/* ── divider ── */
hr {
  border: none !important;
  border-top: 1px solid rgba(255,255,255,0.07) !important;
  margin: 28px 0 !important;
}

/* ── headings ── */
h1,h2,h3,h4 { font-family:'Space Grotesk',sans-serif !important; color:#fff !important; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  HERO  —  Full-width aurora sphere + bold headline
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
/* ───── keyframes ───── */
@keyframes sphereRotate {
  0%   { transform: translate(-50%,-60%) rotate(0deg)   scale(1); }
  50%  { transform: translate(-50%,-60%) rotate(180deg) scale(1.06); }
  100% { transform: translate(-50%,-60%) rotate(360deg) scale(1); }
}
@keyframes sphere2Drift {
  0%,100% { transform: translate(-30%,-30%) scale(1);    opacity:0.7; }
  33%      { transform: translate(-25%,-35%) scale(1.08); opacity:0.9; }
  66%      { transform: translate(-35%,-28%) scale(0.95); opacity:0.6; }
}
@keyframes sphere3Drift {
  0%,100% { transform: translate(10%, 20%) scale(1);    opacity:0.5; }
  50%      { transform: translate(15%, 15%) scale(1.1);  opacity:0.8; }
}
@keyframes ringRotate {
  from { transform: translate(-50%,-50%) rotateX(75deg) rotateZ(0deg); }
  to   { transform: translate(-50%,-50%) rotateX(75deg) rotateZ(360deg); }
}
@keyframes ring2Rotate {
  from { transform: translate(-50%,-50%) rotateX(70deg) rotateZ(360deg); }
  to   { transform: translate(-50%,-50%) rotateX(70deg) rotateZ(0deg); }
}
@keyframes heroFadeUp {
  from { opacity:0; transform:translateY(28px); }
  to   { opacity:1; transform:translateY(0); }
}
@keyframes badgePop {
  0%  { transform:scale(0.85); opacity:0; }
  70% { transform:scale(1.04); }
  100%{ transform:scale(1);    opacity:1; }
}
@keyframes glowPulse {
  0%,100% { box-shadow: 0 0 0 0 rgba(123,47,255,0.35); }
  50%      { box-shadow: 0 0 0 10px rgba(123,47,255,0); }
}
@keyframes scanMove {
  0%   { top:-2px; }
  100% { top:100%; }
}
@keyframes particleFloat {
  0%   { transform:translateY(0) rotate(0deg); opacity:0.8; }
  100% { transform:translateY(-180px) rotate(720deg); opacity:0; }
}
@keyframes textShine {
  0%   { background-position: 200% center; }
  100% { background-position: -200% center; }
}
@keyframes tiltCard {
  0%,100% { transform: perspective(1200px) rotateX(0deg) rotateY(0deg); }
  25%      { transform: perspective(1200px) rotateX(2deg) rotateY(4deg); }
  75%      { transform: perspective(1200px) rotateX(-2deg) rotateY(-4deg); }
}

/* ───── hero wrapper ───── */
.hero {
  position: relative;
  width: 100%;
  min-height: 420px;
  border-radius: 28px;
  overflow: hidden;
  margin-bottom: 40px;
  background: radial-gradient(ellipse at 50% 0%,
    #1a0533 0%,
    #0d0720 40%,
    #06030f 70%,
    #03010a 100%);
  border: 1px solid rgba(123,47,255,0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  animation: tiltCard 14s ease-in-out infinite;
  box-shadow:
    0 0 0 1px rgba(255,255,255,0.04),
    0 40px 120px rgba(123,47,255,0.15),
    0 2px 0 rgba(255,255,255,0.05) inset;
}

/* ───── aurora spheres ───── */
.aurora-sphere-1 {
  position: absolute;
  top: -60%; left: 50%;
  width: 800px; height: 800px;
  border-radius: 50%;
  background: conic-gradient(
    from 0deg,
    rgba(123,47,255,0) 0deg,
    rgba(123,47,255,0.55) 60deg,
    rgba(183,33,255,0.7) 120deg,
    rgba(157,78,221,0.6) 180deg,
    rgba(67,97,238,0.5) 240deg,
    rgba(123,47,255,0.3) 300deg,
    rgba(123,47,255,0) 360deg
  );
  filter: blur(60px);
  animation: sphereRotate 18s linear infinite;
  pointer-events: none;
  z-index: 1;
}
.aurora-sphere-2 {
  position: absolute;
  top: -20%; left: -10%;
  width: 520px; height: 520px;
  border-radius: 50%;
  background: radial-gradient(circle,
    rgba(123,47,255,0.5) 0%,
    rgba(67,97,238,0.3) 45%,
    transparent 70%);
  filter: blur(70px);
  animation: sphere2Drift 12s ease-in-out infinite;
  pointer-events: none;
  z-index: 1;
}
.aurora-sphere-3 {
  position: absolute;
  bottom: -20%; right: -5%;
  width: 480px; height: 480px;
  border-radius: 50%;
  background: radial-gradient(circle,
    rgba(183,33,255,0.45) 0%,
    rgba(123,47,255,0.2) 50%,
    transparent 70%);
  filter: blur(65px);
  animation: sphere3Drift 15s ease-in-out infinite;
  pointer-events: none;
  z-index: 1;
}

/* ───── 3-D rings ───── */
.ring-container {
  position: absolute;
  top: 50%; left: 50%;
  pointer-events: none;
  z-index: 2;
}
.ring {
  position: absolute;
  border-radius: 50%;
  border: 1.5px solid transparent;
  top: 50%; left: 50%;
}
.ring-1 {
  width: 700px; height: 700px;
  background: transparent;
  border: 1.5px solid rgba(123,47,255,0.25);
  box-shadow: 0 0 30px rgba(123,47,255,0.15), inset 0 0 30px rgba(123,47,255,0.05);
  animation: ringRotate 20s linear infinite;
}
.ring-2 {
  width: 550px; height: 550px;
  border: 1px solid rgba(183,33,255,0.2);
  box-shadow: 0 0 20px rgba(183,33,255,0.1);
  animation: ring2Rotate 15s linear infinite;
}
.ring-3 {
  width: 380px; height: 380px;
  border: 1px dashed rgba(157,78,221,0.2);
  animation: ringRotate 10s linear infinite reverse;
}

/* ───── floating dot particles ───── */
.hero-particle {
  position: absolute;
  border-radius: 50%;
  pointer-events: none;
  z-index: 3;
  animation: particleFloat linear infinite;
}

/* ───── hero content ───── */
.hero-content {
  position: relative;
  z-index: 10;
  text-align: center;
  padding: 60px 40px;
  max-width: 800px;
}

.hero-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: rgba(123,47,255,0.15);
  border: 1px solid rgba(123,47,255,0.4);
  border-radius: 100px;
  padding: 7px 20px;
  font-size: 11px;
  font-weight: 700;
  color: rgba(199,125,255,0.95);
  text-transform: uppercase;
  letter-spacing: 2.5px;
  margin-bottom: 28px;
  animation: badgePop 0.7s cubic-bezier(0.34,1.56,0.64,1) forwards, glowPulse 2.5s ease-in-out infinite;
  backdrop-filter: blur(8px);
}
.hero-badge .live-dot {
  width:7px; height:7px; border-radius:50%;
  background:#c77dff;
  box-shadow:0 0 10px #c77dff, 0 0 20px rgba(199,125,255,0.5);
  animation: glowPulse 1.5s ease-in-out infinite;
}

.hero-title {
  font-family: 'Space Grotesk', sans-serif;
  font-size: clamp(42px,7vw,80px);
  font-weight: 900;
  line-height: 1.0;
  margin: 0 0 20px 0;
  color: #fff;
  letter-spacing: -2px;
  text-shadow: 0 0 60px rgba(123,47,255,0.5), 0 0 120px rgba(183,33,255,0.25);
  animation: heroFadeUp 1s ease 0.1s both;
}
.hero-title span {
  background: linear-gradient(90deg, #c77dff, #9d4edd, #7b2fff, #b721ff, #c77dff);
  background-size: 300% auto;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  animation: textShine 5s linear infinite;
}

.hero-sub {
  font-size: 17px;
  color: rgba(255,255,255,0.55);
  line-height: 1.7;
  max-width: 560px;
  margin: 0 auto 36px auto;
  animation: heroFadeUp 1s ease 0.25s both;
  font-weight: 400;
}

.feature-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  justify-content: center;
  animation: heroFadeUp 1s ease 0.4s both;
}
.feat-chip {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  padding: 8px 18px;
  border-radius: 100px;
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.3px;
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.1);
  color: rgba(255,255,255,0.75);
  backdrop-filter: blur(8px);
  transition: all 0.3s ease;
  cursor: default;
}
.feat-chip:hover {
  background: rgba(123,47,255,0.2);
  border-color: rgba(123,47,255,0.5);
  color: #fff;
  transform: translateY(-3px);
  box-shadow: 0 8px 24px rgba(123,47,255,0.25);
}
</style>

<!-- ══ HERO ══ -->
<div class="hero">
  <!-- Aurora spheres -->
  <div class="aurora-sphere-1"></div>
  <div class="aurora-sphere-2"></div>
  <div class="aurora-sphere-3"></div>

  <!-- 3D Rings -->
  <div class="ring-container">
    <div class="ring ring-1"></div>
    <div class="ring ring-2"></div>
    <div class="ring ring-3"></div>
  </div>

  <!-- Particles -->
  <div class="hero-particle" style="width:5px;height:5px;background:#c77dff;left:12%;bottom:5%;animation-duration:5s;animation-delay:0s;box-shadow:0 0 8px #c77dff;"></div>
  <div class="hero-particle" style="width:3px;height:3px;background:#7b2fff;left:28%;bottom:8%;animation-duration:7s;animation-delay:1.2s;box-shadow:0 0 6px #7b2fff;"></div>
  <div class="hero-particle" style="width:4px;height:4px;background:#b721ff;left:50%;bottom:3%;animation-duration:6s;animation-delay:0.6s;box-shadow:0 0 8px #b721ff;"></div>
  <div class="hero-particle" style="width:3px;height:3px;background:#9d4edd;left:70%;bottom:10%;animation-duration:8s;animation-delay:2s;box-shadow:0 0 6px #9d4edd;"></div>
  <div class="hero-particle" style="width:5px;height:5px;background:#c77dff;left:85%;bottom:6%;animation-duration:5.5s;animation-delay:0.3s;box-shadow:0 0 10px #c77dff;"></div>
  <div class="hero-particle" style="width:2px;height:2px;background:#fff;left:92%;bottom:15%;animation-duration:4s;animation-delay:1.8s;"></div>
  <div class="hero-particle" style="width:3px;height:3px;background:#7b2fff;left:6%;bottom:20%;animation-duration:9s;animation-delay:0.9s;box-shadow:0 0 6px #7b2fff;"></div>

  <!-- Content -->
  <div class="hero-content">
    <div class="hero-badge"><span class="live-dot"></span> AI-Powered Research Intelligence</div>
    <h1 class="hero-title">Schol<span>AR</span></h1>
    <p class="hero-sub">
      Autonomous research agent that searches, analyzes, and synthesizes
      academic literature — uncovering contradictions, gaps, and trends at scale.
    </p>
    <div class="feature-grid">
      <span class="feat-chip">🤖 Autonomous Search</span>
      <span class="feat-chip">🔍 Deep-Dive Recursion</span>
      <span class="feat-chip">📊 Saturation Detection</span>
      <span class="feat-chip">🎯 Gap Analysis</span>
      <span class="feat-chip">🤔 Devil's Advocate</span>
      <span class="feat-chip">📈 Trend Tracking</span>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
st.sidebar.markdown("""
<style>
@keyframes logoGlow {
  0%,100%{ filter:drop-shadow(0 0 12px rgba(123,47,255,0.7)); }
  50%    { filter:drop-shadow(0 0 28px rgba(183,33,255,0.95)); }
}
.sb-logo {
  text-align:center;
  padding:28px 0 32px;
  border-bottom:1px solid rgba(123,47,255,0.15);
  margin-bottom:28px;
}
.sb-logo .icon {
  font-size:52px;
  display:block;
  margin-bottom:10px;
  animation: logoGlow 3s ease-in-out infinite;
}
.sb-logo .name {
  font-family:'Space Grotesk',sans-serif;
  font-size:24px; font-weight:800; color:#fff;
  letter-spacing:1px;
}
.sb-logo .name span {
  background:linear-gradient(90deg,#7b2fff,#c77dff);
  -webkit-background-clip:text;
  -webkit-text-fill-color:transparent;
  background-clip:text;
}
.sb-logo .tagline {
  font-size:11px; color:rgba(255,255,255,0.35);
  text-transform:uppercase; letter-spacing:2.5px; margin-top:6px;
}
.sb-label {
  font-size:10px; font-weight:700;
  color:rgba(123,47,255,0.65);
  text-transform:uppercase; letter-spacing:2.5px;
  padding-left:4px; margin-bottom:10px;
}
.sb-info {
  margin-top:36px;
  padding:18px 16px;
  background:rgba(123,47,255,0.07);
  border:1px solid rgba(123,47,255,0.15);
  border-radius:16px;
  font-size:12px;
  color:rgba(255,255,255,0.45);
  line-height:1.9;
}
.sb-info strong { color:rgba(199,125,255,0.8); }
</style>
<div class="sb-logo">
  <span class="icon">🎓</span>
  <div class="name">Schol<span>AR</span></div>
  <div class="tagline">Research Intelligence</div>
</div>
<div class="sb-label">⚙ Configuration</div>
""", unsafe_allow_html=True)

research_topic = st.sidebar.text_input(
    "Research Topic",
    placeholder="e.g., 'Federated Learning in Healthcare'",
    help="The main topic you want to research",
    key="research_input",
    label_visibility="collapsed"
)
st.sidebar.caption("Enter any academic research topic above")
st.sidebar.divider()

col1, col2 = st.sidebar.columns(2)
with col1:
    start_button = st.sidebar.button("🚀 Start Research", type="primary", use_container_width=True)
with col2:
    force_new = st.sidebar.button("🔄 Force New", use_container_width=True, help="Ignore cache and search fresh")

if force_new:
    st.session_state.force_new_search = True

st.sidebar.markdown("""
<div class="sb-info">
  <strong>How it works</strong><br>
  ScholAR queries Semantic Scholar autonomously, builds a citation knowledge graph,
  detects contradictions via LLM, and generates a full literature review report.
</div>
""", unsafe_allow_html=True)

st.sidebar.divider()
st.sidebar.markdown("<strong style='font-size:13px;color:#9d4edd;'>🔄 Compare Topics</strong>", unsafe_allow_html=True)

compare_mode = st.sidebar.checkbox("Enable Topic Comparison", key="compare_mode")
if compare_mode:
    st.sidebar.info("Load two saved research topics to compare findings, keywords, and contradictions.")

    history = storage.get_history(limit=100)
    topic_names = [h['topic'] for h in history]

    if len(topic_names) >= 2:
        col1, col2 = st.sidebar.columns(2)
        with col1:
            topic1_name = st.sidebar.selectbox("Topic 1", topic_names, key="comp_topic1")
        with col2:
            topic2_name = st.sidebar.selectbox("Topic 2", topic_names, index=1 if len(topic_names) > 1 else 0, key="comp_topic2")

        if st.sidebar.button("Compare Topics", use_container_width=True):
            # Load both topics
            topic1_data = None
            topic2_data = None

            for h in history:
                if h['topic'] == topic1_name:
                    topic1_data = storage.load_research(h['file_path'])
                    topic1_data['topic'] = topic1_name
                if h['topic'] == topic2_name:
                    topic2_data = storage.load_research(h['file_path'])
                    topic2_data['topic'] = topic2_name

            if topic1_data and topic2_data:
                st.session_state.comparison_data = {
                    'topic1_data': topic1_data,
                    'topic2_data': topic2_data,
                    'comparison': compare_topics(topic1_data, topic2_data)
                }
                st.session_state.show_comparison = True
    else:
        st.sidebar.warning("Need at least 2 saved topics to compare.")

# ══════════════════════════════════════════════════════════════════════════════
#  COMPARISON VIEW
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.get('show_comparison') and st.session_state.get('comparison_data'):
    st.divider()
    comp_data = st.session_state.comparison_data
    comparison = comp_data['comparison']

    st.markdown("""
    <div style="font-family:'Space Grotesk',sans-serif;font-size:26px;font-weight:800;color:#fff;margin:8px 0 24px;">
      <span style="background:linear-gradient(90deg,#c77dff,#7b2fff);
        -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;">
        🔄 Topic Comparison
      </span>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(f"📖 {comparison['topic1'][:20]}", f"{comparison['papers1_count']} papers")
    with col2:
        st.metric(f"📖 {comparison['topic2'][:20]}", f"{comparison['papers2_count']} papers")
    with col3:
        st.metric("Common Keywords", len(comparison['common_keywords']))
    with col4:
        st.metric("Overlap", f"{comparison['overlap_percentage']:.1f}%")

    st.divider()

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("**🔗 Shared Keywords**")
        for kw in comparison['common_keywords']:
            st.caption(f"• {kw}")

    with col2:
        st.markdown(f"**🎯 Unique to {comparison['topic1'][:20]}**")
        for kw in comparison['unique_to_topic1']:
            st.caption(f"• {kw}")

    with col3:
        st.markdown(f"**🎯 Unique to {comparison['topic2'][:20]}**")
        for kw in comparison['unique_to_topic2']:
            st.caption(f"• {kw}")

    if st.button("Close Comparison", key="close_comp"):
        st.session_state.show_comparison = False
        st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
#  CACHE / SEARCH TRIGGER  (workflow unchanged)
# ══════════════════════════════════════════════════════════════════════════════
if start_button:
    if not research_topic:
        st.error("❌ Please enter a research topic")
    else:
        if not st.session_state.force_new_search:
            history = storage.get_history(limit=1000)
            cached_result = None
            for item in history:
                if item['topic'].lower() == research_topic.lower():
                    cached_result = item
                    break
            if cached_result:
                try:
                    st.session_state.research_data = storage.load_research(cached_result['file_path'])
                    st.session_state.research_complete = True
                    st.session_state.from_cache = True
                    st.session_state.research_topic_current = research_topic
                    st.success(f"✅ Loaded from cache! (Searched on {cached_result['timestamp']})")
                    st.rerun()
                except Exception as e:
                    st.warning(f"Cache load failed: {e}. Starting new search...")
                    st.session_state.research_topic_current = research_topic
                    st.session_state.research_complete = False
                    st.session_state.research_data = None
                    st.session_state.from_cache = False
                    st.session_state.force_new_search = False
            else:
                st.session_state.research_topic_current = research_topic
                st.session_state.research_complete = False
                st.session_state.research_data = None
                st.session_state.from_cache = False
                st.session_state.force_new_search = False
        else:
            st.session_state.research_topic_current = research_topic
            st.session_state.research_complete = False
            st.session_state.research_data = None
            st.session_state.from_cache = False
            st.session_state.force_new_search = False

# ══════════════════════════════════════════════════════════════════════════════
#  THOUGHT LOG
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.research_topic_current and not st.session_state.research_complete:
    st.markdown("""
    <style>
    @keyframes scanMove { 0%{top:0} 100%{top:100%} }
    @keyframes blink    { 0%,100%{opacity:1} 50%{opacity:0} }
    .thought-shell {
      position:relative;
      background:linear-gradient(135deg,rgba(7,4,15,0.97) 0%,rgba(13,7,32,0.97) 100%);
      border:1px solid rgba(123,47,255,0.3);
      border-radius:22px;
      padding:30px 36px;
      margin:28px 0;
      overflow:hidden;
      box-shadow: 0 0 60px rgba(123,47,255,0.1), inset 0 0 80px rgba(0,0,0,0.5);
    }
    .thought-shell::after {
      content:'';
      position:absolute; left:0; right:0; height:1.5px;
      background:linear-gradient(90deg,transparent,rgba(123,47,255,0.7),transparent);
      animation: scanMove 2.5s linear infinite;
      pointer-events:none;
    }
    .thought-hdr {
      display:flex; align-items:center; gap:12px;
      font-family:'Space Grotesk',sans-serif;
      font-size:16px; font-weight:700; color:#c77dff;
      margin-bottom:14px;
    }
    .blink-dot {
      width:10px; height:10px; border-radius:50%;
      background:#7b2fff;
      box-shadow:0 0 14px #7b2fff, 0 0 28px rgba(123,47,255,0.5);
      animation: blink 1s infinite;
    }
    </style>
    <div class="thought-shell">
      <div class="thought-hdr"><div class="blink-dot"></div> 🧠 Agent Thought Log — Processing</div>
    </div>
    """, unsafe_allow_html=True)

    thought_container = st.container()
    with thought_container:
        thought_log_placeholder = st.empty()
        log_entries = []

    try:
        for update in agent.run_research_agent(st.session_state.research_topic_current):
            if update["type"] == "log":
                log_entries.append(f"➜ {update['message']}")
                log_text = "\n".join(log_entries[-20:])
                thought_log_placeholder.markdown(f"```\n{log_text}\n```")
            elif update["type"] == "complete":
                st.session_state.research_data = update
                # Add metadata for PDF generation
                st.session_state.research_data['topic'] = st.session_state.research_topic_current
                st.session_state.research_data['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                st.session_state.research_complete = True
                try:
                    storage.save_research(st.session_state.research_topic_current, update)
                    st.session_state.saved_successfully = True
                except Exception as e:
                    print(f"Storage save error: {e}")
                st.session_state.force_new_search = False
                st.rerun()
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")

# ══════════════════════════════════════════════════════════════════════════════
#  RESULTS
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.research_complete and st.session_state.research_data:
    final_data = st.session_state.research_data

    if st.session_state.from_cache:
        st.info("📦 Results loaded from cache! Click 'Force New' to search again.")

    paper_count = len(final_data.get('papers', []))
    st.markdown(f"""
    <style>
    @keyframes bannerIn {{
      from {{ transform:translateY(14px) scale(0.98); opacity:0; }}
      to   {{ transform:translateY(0) scale(1); opacity:1; }}
    }}
    .done-banner {{
      display:flex; align-items:center; gap:18px;
      background:linear-gradient(135deg,rgba(123,47,255,0.15),rgba(183,33,255,0.08));
      border:1px solid rgba(123,47,255,0.35);
      border-radius:20px;
      padding:22px 32px;
      margin-bottom:32px;
      animation: bannerIn 0.5s cubic-bezier(0.34,1.56,0.64,1) forwards;
      box-shadow: 0 0 40px rgba(123,47,255,0.12);
      backdrop-filter:blur(12px);
    }}
    .done-icon {{ font-size:32px; filter:drop-shadow(0 0 10px rgba(199,125,255,0.7)); }}
    .done-title {{ font-family:'Space Grotesk',sans-serif; font-size:18px; font-weight:800; color:#fff; }}
    .done-sub   {{ font-size:13px; color:rgba(255,255,255,0.45); margin-top:3px; }}
    </style>
    <div class="done-banner">
      <div class="done-icon">✦</div>
      <div>
        <div class="done-title">Analysis Complete — {paper_count} papers processed</div>
        <div class="done-sub">Knowledge graph built · Contradictions identified · Report generated</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── TABS ──────────────────────────────────────────────────────────────────
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10, tab11 = st.tabs([
        "📊 Dashboard",
        "🕸️ Knowledge Graph",
        "🤝 Contradictions",
        "📑 Full Report",
        "📚 Sources",
        "🔍 Research Gaps",
        "📈 Timeline",
        "👥 Authors",
        "🛣️ Reading Path",
        "📤 Export",
        "💾 Saved Research"
    ])

    # ─────────────────── TAB 1: DASHBOARD ────────────────────────────────────
    with tab1:
        st.markdown("""
        <div style="font-family:'Space Grotesk',sans-serif;font-size:26px;font-weight:800;
             color:#fff;margin:8px 0 28px;">
          <span style="background:linear-gradient(90deg,#c77dff,#7b2fff);
            -webkit-background-clip:text;-webkit-text-fill-color:transparent;
            background-clip:text;">Research Dashboard</span>
        </div>
        """, unsafe_allow_html=True)

        c1,c2,c3,c4 = st.columns(4)
        with c1: st.metric("Papers", len(final_data['papers']))
        with c2: st.metric("Concepts", len(final_data.get('concepts',[])))
        with c3: st.metric("Contradictions", len(final_data.get('contradictions',[])))
        with c4: st.metric("Status","Complete")

        st.markdown('<div style="height:24px"></div>', unsafe_allow_html=True)

        st.markdown("### 📋 Top Papers")
        papers_sorted = sorted(final_data['papers'], key=lambda p: int(p.get('year', 0)), reverse=True)

        for idx, paper in enumerate(papers_sorted[:10], 1):
            # Get authors string - handle both list and string formats
            authors = paper.get('authors', [])
            try:
                if isinstance(authors, list):
                    if authors:
                        authors_list = []
                        for a in authors[:2]:
                            if isinstance(a, dict):
                                author_name = a.get('name', str(a))
                            else:
                                author_name = str(a)
                            authors_list.append(author_name)
                        authors_str = ", ".join(authors_list)
                    else:
                        authors_str = "N/A"
                else:
                    authors_str = str(authors)[:60]
            except:
                authors_str = "N/A"

            col1, col2, col3, col4 = st.columns([4, 1, 1, 1])
            with col1:
                st.write(f"**{idx}. {paper.get('title', 'Unknown')[:60]}...**")
                st.caption(f"By: {authors_str}")
            with col2:
                st.write("")
            with col3:
                st.write(f"📍 {paper.get('year', 'N/A')}")
            with col4:
                st.write(f"📊 {paper.get('citationCount', 0)}")

        st.divider()
        years = {}
        for p in final_data['papers']:
            y = p.get('year', 0)
            if y: years[y] = years.get(y, 0) + 1

        if years:
            sy = sorted(years.keys())
            vals = [years[y] for y in sy]

            fig = go.Figure()

            # Area fill
            fig.add_trace(go.Scatter(
                x=sy, y=vals,
                mode='none',
                fill='tozeroy',
                fillcolor='rgba(123,47,255,0.12)',
                showlegend=False,
                hoverinfo='none',
            ))

            # Line + markers
            fig.add_trace(go.Scatter(
                x=sy, y=vals,
                mode='lines+markers',
                line=dict(color='#9d4edd', width=3),
                marker=dict(
                    size=9, color=vals,
                    colorscale=[[0,'#4361ee'],[0.4,'#7b2fff'],[0.7,'#9d4edd'],[1,'#c77dff']],
                    showscale=False,
                    line=dict(width=2, color='rgba(255,255,255,0.3)')
                ),
                hovertemplate='<b>%{x}</b><br>Papers: %{y}<extra></extra>',
                showlegend=False,
            ))

            fig.update_layout(
                title=dict(
                    text='Publication Volume Over Time',
                    font=dict(family='Space Grotesk', size=18, color='rgba(255,255,255,0.85)'),
                    x=0.02
                ),
                xaxis=dict(
                    title='Year',
                    title_font=dict(color='rgba(255,255,255,0.4)', size=12),
                    tickfont=dict(color='rgba(255,255,255,0.5)', size=11),
                    gridcolor='rgba(255,255,255,0.04)',
                    showline=False, zeroline=False,
                ),
                yaxis=dict(
                    title='Papers',
                    title_font=dict(color='rgba(255,255,255,0.4)', size=12),
                    tickfont=dict(color='rgba(255,255,255,0.5)', size=11),
                    gridcolor='rgba(255,255,255,0.04)',
                    showline=False, zeroline=False,
                ),
                plot_bgcolor='rgba(7,4,15,0.97)',
                paper_bgcolor='rgba(7,4,15,0)',
                height=420,
                margin=dict(l=20,r=20,t=60,b=20),
                hoverlabel=dict(
                    bgcolor='rgba(13,7,32,0.98)',
                    bordercolor='rgba(123,47,255,0.5)',
                    font=dict(color='#c77dff', size=13, family='Inter')
                ),
            )
            st.plotly_chart(fig, use_container_width=True)

    # ─────────────────── TAB 2: KNOWLEDGE GRAPH ──────────────────────────────
    with tab2:
        st.markdown("""
        <div style="font-family:'Space Grotesk',sans-serif;font-size:26px;font-weight:800;color:#fff;margin:8px 0 6px;">
          <span style="background:linear-gradient(90deg,#c77dff,#7b2fff);
            -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;">
            Interactive Knowledge Graph
          </span>
        </div>
        <p style="color:rgba(255,255,255,0.4);font-size:13px;margin-bottom:24px;">
          Hover over nodes to see paper details including venue, abstract, and direct links. Node size reflects citation count. Color intensity indicates citation frequency.
        </p>
        """, unsafe_allow_html=True)

        papers = final_data.get('papers', [])
        contradictions = final_data.get('contradictions', [])

        if papers:
            G = nx.DiGraph()
            paper_map = {}
            for i, p in enumerate(papers[:30]):
                paper_map[i] = p
                G.add_node(i, title=p['title'][:30], citations=p.get('citationCount', 0))
            for i, p1 in enumerate(papers[:30]):
                for j, p2 in enumerate(papers[:30]):
                    if i != j and i in paper_map and j in paper_map:
                        if p1.get('citationCount', 0) > 5 or p2.get('citationCount', 0) > 5:
                            if (i + j) % 3 == 0:
                                G.add_edge(i, j)

            pos = nx.spring_layout(G, k=2, iterations=50, seed=42)

            edge_x, edge_y = [], []
            for edge in G.edges():
                x0,y0 = pos[edge[0]]
                x1,y1 = pos[edge[1]]
                edge_x += [x0,x1,None]
                edge_y += [y0,y1,None]

            node_x = [pos[n][0] for n in G.nodes()]
            node_y = [pos[n][1] for n in G.nodes()]
            node_text, node_colors, node_sizes = [], [], []

            for node in G.nodes():
                if node in paper_map:
                    p = paper_map[node]
                    citations = p.get('citationCount', 0)
                    year = p.get('year', 'N/A')
                    authors = p.get('author_str', 'N/A')
                    abstract = p.get('abstract', 'N/A')[:120] + "..." if p.get('abstract') else 'N/A'
                    venue = p.get('venue', 'N/A')
                    url = p.get('url', '')

                    # Build rich hover text with more details
                    node_text.append(
                        f"<b style='font-size:13px; color:#c77dff;'>{p['title']}</b><br>"
                        f"<b>Year:</b> {year}<br>"
                        f"<b>Citations:</b> {citations}<br>"
                        f"<b>Venue:</b> {venue}<br>"
                        f"<b>Authors:</b> {authors[:50]}...<br>"
                        f"<b>Abstract:</b> {abstract}<br>"
                        f"{'<b>Link:</b> <a href=\"' + url + '\" target=\"_blank\">View Paper</a>' if url else ''}"
                    )
                    node_colors.append(citations)
                    node_sizes.append(max(15, min(52, citations / 2 + 12)))

            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=edge_x, y=edge_y, mode='lines',
                line=dict(width=1, color='rgba(123,47,255,0.18)'),
                hoverinfo='none', showlegend=False, name='edges'
            ))
            fig.add_trace(go.Scatter(
                x=node_x, y=node_y,
                mode='markers+text',
                marker=dict(
                    size=node_sizes,
                    color=node_colors,
                    colorscale=[[0,'#0d0720'],[0.2,'#4361ee'],[0.5,'#7b2fff'],[0.75,'#9d4edd'],[1,'#c77dff']],
                    showscale=True,
                    colorbar=dict(
                        title=dict(text="Citations", font=dict(color='rgba(255,255,255,0.5)',size=11)),
                        tickfont=dict(color='rgba(255,255,255,0.5)'),
                        thickness=10, len=0.55,
                        bgcolor='rgba(7,4,15,0.8)',
                        bordercolor='rgba(123,47,255,0.2)',
                    ),
                    line=dict(width=1.5, color='rgba(199,125,255,0.4)'),
                    opacity=0.95,
                ),
                text=[f"P{i}" for i in range(len(G))],
                textposition="middle center",
                textfont=dict(color='white', size=9, family='Space Grotesk'),
                hovertext=node_text,
                hoverinfo='text',
                showlegend=False, name='Papers'
            ))
            fig.update_layout(
                title=dict(
                    text='Research Paper Network — Citation Topology',
                    font=dict(family='Space Grotesk', size=16, color='rgba(255,255,255,0.8)'),
                    x=0.02
                ),
                showlegend=False, hovermode='closest',
                margin=dict(b=20,l=5,r=5,t=50),
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                height=640,
                plot_bgcolor='rgba(3,1,10,0.98)',
                paper_bgcolor='rgba(3,1,10,0)',
                hoverlabel=dict(
                    bgcolor='rgba(13,7,32,0.98)',
                    bordercolor='rgba(123,47,255,0.55)',
                    font=dict(color='#c77dff', size=13, family='Inter')
                ),
            )
            st.plotly_chart(fig, use_container_width=True)

            st.divider()
            st.markdown('<div style="font-family:Space Grotesk,sans-serif;font-size:18px;font-weight:700;color:#c77dff;margin-bottom:14px;">Paper Details & Contradictions</div>', unsafe_allow_html=True)

            selected_paper = st.selectbox(
                "Select a paper:",
                options=range(len(papers[:30])),
                format_func=lambda i: f"P{i}: {papers[i]['title'][:60]}..."
            )

            if selected_paper is not None and selected_paper in paper_map:
                paper = paper_map[selected_paper]
                c1,c2,c3,c4 = st.columns(4)
                with c1: st.metric("Year", paper.get('year','N/A'))
                with c2: st.metric("Citations", paper.get('citationCount',0))
                with c3:
                    authors = paper.get('authors',[])
                    author_count = len(authors) if isinstance(authors, list) else 1
                    st.metric("Authors", f"{author_count} author(s)")
                with c4: st.metric("ID", paper.get('paperId','N/A')[:15])

                st.markdown('<div style="color:#c77dff;font-weight:700;margin-top:16px;margin-bottom:4px;">Title</div>', unsafe_allow_html=True)
                st.write(paper['title'])
                st.markdown('<div style="color:#c77dff;font-weight:700;margin-top:12px;margin-bottom:4px;">Authors</div>', unsafe_allow_html=True)
                st.write(paper.get('author_str','N/A') or "N/A")
                if paper.get('abstract'):
                    st.markdown('<div style="color:#c77dff;font-weight:700;margin-top:12px;margin-bottom:4px;">Abstract</div>', unsafe_allow_html=True)
                    st.write(paper['abstract'])
                if paper.get('url'):
                    st.markdown(f'<a href="{paper["url"]}" target="_blank" style="color:#9d4edd;font-weight:600;">🔗 View on Semantic Scholar →</a>', unsafe_allow_html=True)

                st.divider()
                st.markdown('<div style="font-family:Space Grotesk,sans-serif;font-size:15px;font-weight:700;color:#9d4edd;margin-bottom:12px;">Contradictions Involving This Paper</div>', unsafe_allow_html=True)

                paper_title_lower = paper['title'].lower()
                related_contradictions = []
                for contra in contradictions:
                    contra_text = f"{contra.get('paper_a','')} {contra.get('paper_b','')}".lower()
                    if any(w in paper_title_lower for w in contra_text.split()) or \
                       any(w in contra_text for w in paper_title_lower.split()):
                        related_contradictions.append(contra)

                if related_contradictions:
                    for idx, contra in enumerate(related_contradictions, 1):
                        with st.expander(f"⚡ Contradiction {idx}: {contra.get('theme','N/A')}"):
                            c1,c2 = st.columns(2)
                            with c1:
                                st.markdown(f"**Paper A:** {contra.get('paper_a','N/A')[:80]}")
                                st.markdown(f"**Claim A:** {contra.get('claim_a','N/A')}")
                            with c2:
                                st.markdown(f"**Paper B:** {contra.get('paper_b','N/A')[:80]}")
                                st.markdown(f"**Claim B:** {contra.get('claim_b','N/A')}")
                else:
                    st.info("No contradictions found for this paper")

    # ─────────────────── TAB 3: CONTRADICTIONS ───────────────────────────────
    with tab3:
        st.markdown("""
        <div style="font-family:'Space Grotesk',sans-serif;font-size:26px;font-weight:800;color:#fff;margin:8px 0 24px;">
          <span style="background:linear-gradient(90deg,#c77dff,#7b2fff);
            -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;">
            Contradictions & Debates Matrix
          </span>
        </div>
        """, unsafe_allow_html=True)

        contradictions = final_data.get('contradictions', [])
        if contradictions:
            st.markdown(f"""
            <div style="display:inline-flex;align-items:center;gap:10px;
              background:rgba(123,47,255,0.12);border:1px solid rgba(123,47,255,0.3);
              border-radius:100px;padding:9px 22px;margin-bottom:20px;
              font-size:13px;font-weight:600;color:#c77dff;">
              ⚡ {len(contradictions)} contradictions detected in the literature
            </div>
            """, unsafe_allow_html=True)

            st.divider()
            st.markdown('<div style="font-family:Space Grotesk,sans-serif;font-size:18px;font-weight:700;color:#c77dff;margin-bottom:16px;">Analysis by Theme</div>', unsafe_allow_html=True)

            themes = {}
            for contra in contradictions:
                t = contra.get('theme','Other')
                themes.setdefault(t,[]).append(contra)
            for theme, items in themes.items():
                with st.expander(f"🏷️ {theme} — {len(items)} contradiction(s)"):
                    for item in items:
                        st.write(f"- **{item.get('paper_a','N/A')}**: {item.get('claim_a','N/A')}")
                        st.write("  **vs**")
                        st.write(f"- **{item.get('paper_b','N/A')}**: {item.get('claim_b','N/A')}")
                        st.divider()
        else:
            st.info("No contradictions found in the analyzed papers")

    # ─────────────────── TAB 4: FULL REPORT ──────────────────────────────────
    with tab4:
        st.markdown("""
        <div style="font-family:'Space Grotesk',sans-serif;font-size:26px;font-weight:800;color:#fff;margin:8px 0 24px;">
          <span style="background:linear-gradient(90deg,#c77dff,#7b2fff);
            -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;">
            Literature Review Report
          </span>
        </div>
        """, unsafe_allow_html=True)

        report = final_data.get('report','No report generated')
        st.markdown("""
        <div style="background:rgba(7,4,15,0.92);border:1px solid rgba(123,47,255,0.18);
          border-radius:20px;padding:36px 40px;line-height:1.85;
          color:rgba(255,255,255,0.82);box-shadow:inset 0 0 60px rgba(0,0,0,0.4);">
        """, unsafe_allow_html=True)
        st.markdown(report)
        st.markdown("</div>", unsafe_allow_html=True)

        st.divider()
        st.markdown('<div style="font-family:Space Grotesk,sans-serif;font-size:18px;font-weight:700;color:#c77dff;margin-bottom:16px;">📥 Download Report</div>', unsafe_allow_html=True)

        if PDF_AVAILABLE and generate_report_bytes:
            try:
                # Pass complete research data for comprehensive PDF
                pdf_data, ext, mime = generate_report_bytes(report, "pdf", research_data=final_data)
                st.download_button(
                    "📥 Download PDF Report",
                    data=pdf_data,
                    file_name=f"literature_review_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                    mime=mime,
                    use_container_width=True,
                    key="download_pdf"
                )
                st.success("✅ PDF Ready — Click to Download")
            except Exception as e:
                st.error(f"PDF generation error: {str(e)}")
                st.info("Please try again")
        else:
            st.warning("⚠️ PDF generation not available. Install reportlab: pip install reportlab")

    # ─────────────────── TAB 5: SOURCES ──────────────────────────────────────
    with tab5:
        st.markdown("""
        <div style="font-family:'Space Grotesk',sans-serif;font-size:26px;font-weight:800;color:#fff;margin:8px 0 24px;">
          <span style="background:linear-gradient(90deg,#c77dff,#7b2fff);
            -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;">
            Source Papers
          </span>
        </div>
        """, unsafe_allow_html=True)

        # Filtering options
        st.markdown("### 🔍 Filter & Sort")
        col1, col2, col3 = st.columns(3)

        with col1:
            # Year range filter
            years = [int(p.get('year', 0)) for p in final_data['papers'] if p.get('year')]
            if years:
                min_year, max_year = min(years), max(years)
                year_range = st.slider("Year Range", min_year, max_year, (min_year, max_year), key="year_filter")
            else:
                year_range = None

        with col2:
            # Sort option
            sort_by = st.selectbox("Sort by", ["Title (A-Z)", "Year (Newest)", "Year (Oldest)", "Citations (Most)"], key="paper_sort")

        with col3:
            # Show only bookmarked
            show_bookmarked = st.checkbox("✨ Show Only Bookmarked", value=False, key="show_bookmarked")

        st.divider()

        # Filter and sort papers
        filtered_papers = final_data['papers'].copy()

        # Year filter
        if year_range:
            filtered_papers = [p for p in filtered_papers if int(p.get('year', 0)) >= year_range[0] and int(p.get('year', 0)) <= year_range[1]]

        # Sort
        if sort_by == "Title (A-Z)":
            filtered_papers.sort(key=lambda p: p.get('title', ''))
        elif sort_by == "Year (Newest)":
            filtered_papers.sort(key=lambda p: int(p.get('year', 0)), reverse=True)
        elif sort_by == "Year (Oldest)":
            filtered_papers.sort(key=lambda p: int(p.get('year', 0)))
        elif sort_by == "Citations (Most)":
            filtered_papers.sort(key=lambda p: int(p.get('citationCount', 0)), reverse=True)

        # Show bookmarked only
        if show_bookmarked:
            filtered_papers = [p for p in filtered_papers if p.get('title', '') in st.session_state.bookmarked_papers]

        st.markdown(f"**Showing {len(filtered_papers)} of {len(final_data['papers'])} papers**")

        for i, p in enumerate(filtered_papers, 1):
            is_bookmarked = p.get('title', '') in st.session_state.bookmarked_papers
            bookmark_icon = "⭐" if is_bookmarked else "☆"

            # Calculate paper quality score
            quality_score = calculate_paper_quality_score(p)

            with st.expander(f"{i}. {p['title'][:70]} {bookmark_icon}"):
                c1, c2, c3, c4, c5 = st.columns(5)
                with c1:
                    st.metric("Year", p.get('year', 'N/A'))
                with c2:
                    st.metric("Citations", p.get('citationCount', 0))
                with c3:
                    authors = p.get('authors', [])
                    author_count = len(authors) if isinstance(authors, list) else 1
                    st.metric("Authors", author_count)
                with c4:
                    # Quality score visual
                    score = quality_score['score']
                    score_color = "🟢" if score >= 70 else "🟡" if score >= 40 else "🔴"
                    st.metric("Quality", f"{score_color} {score}/100")
                with c5:
                    if st.button("Toggle Bookmark", key=f"bookmark_{i}_{p.get('title', '')[:20]}"):
                        if is_bookmarked:
                            st.session_state.bookmarked_papers.remove(p.get('title', ''))
                            st.success("Removed from bookmarks")
                        else:
                            st.session_state.bookmarked_papers.append(p.get('title', ''))
                            st.success("Added to bookmarks ⭐")

                # Show quality details
                if quality_score['details']:
                    st.caption("**Quality Indicators:** " + " • ".join(quality_score['details']))

                # Display authors
                authors = p.get('authors', [])
                try:
                    if isinstance(authors, list):
                        if authors:
                            # Convert each author to string (in case they're dicts)
                            authors_list = [str(a) for a in authors]
                            authors_str = ", ".join(authors_list)
                        else:
                            authors_str = "N/A"
                    else:
                        authors_str = str(p.get("author_str", str(authors)))[:200]
                except:
                    authors_str = "N/A"

                st.markdown(f'<div style="color:rgba(199,125,255,0.8);font-size:13px;margin-top:8px;"><b>Authors:</b> {authors_str}</div>', unsafe_allow_html=True)

                if p.get('abstract'):
                    st.markdown(f'<div style="color:rgba(255,255,255,0.72);font-size:14px;margin-top:10px;line-height:1.7;">{p["abstract"][:300]}...</div>', unsafe_allow_html=True)
                if p.get('url'):
                    st.markdown(f'<a href="{p["url"]}" target="_blank" style="color:#9d4edd;font-weight:600;font-size:13px;">🔗 View Paper →</a>', unsafe_allow_html=True)

    # ─────────────────── TAB 6: RESEARCH GAPS ──────────────────────────────────
    with tab6:
        st.markdown("""
        <div style="font-family:'Space Grotesk',sans-serif;font-size:26px;font-weight:800;color:#fff;margin:8px 0 24px;">
          <span style="background:linear-gradient(90deg,#c77dff,#7b2fff);
            -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;">
            Research Gaps & Opportunities
          </span>
        </div>
        """, unsafe_allow_html=True)

        gaps = identify_research_gaps(final_data.get('papers', []), final_data.get('report', ''))

        for idx, gap in enumerate(gaps, 1):
            priority_color = "🔴" if gap['priority'] == "High" else "🟡" if gap['priority'] == "Medium" else "🟢"
            with st.expander(f"{priority_color} {gap['gap']} [{gap['priority']} Priority]"):
                st.write(gap['description'])

    # ─────────────────── TAB 8: TIMELINE ────────────────────────────────────────
    with tab7:
        st.markdown("""
        <div style="font-family:'Space Grotesk',sans-serif;font-size:26px;font-weight:800;color:#fff;margin:8px 0 24px;">
          <span style="background:linear-gradient(90deg,#c77dff,#7b2fff);
            -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;">
            Research Timeline
          </span>
        </div>
        """, unsafe_allow_html=True)

        timeline = extract_timeline_data(final_data.get('papers', []))

        if timeline['timeline']:
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Earliest Paper", timeline['earliest'])
            col2.metric("Latest Paper", timeline['latest'])
            col3.metric("Peak Year", timeline['peak_year'])
            col4.metric("Years Covered", timeline['total_years'])

            st.divider()

            import plotly.graph_objects as go
            years, counts = zip(*timeline['timeline'])

            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=list(years),
                y=list(counts),
                marker_color='rgba(123,47,255,0.7)',
                name='Papers per Year'
            ))
            fig.update_layout(
                title="Publication Timeline",
                xaxis_title="Year",
                yaxis_title="Number of Papers",
                template="plotly_dark",
                hovermode='x unified'
            )
            st.plotly_chart(fig, use_container_width=True)

    # ─────────────────── TAB 8: AUTHOR NETWORK ──────────────────────────────────
    with tab8:
        st.markdown("""
        <div style="font-family:'Space Grotesk',sans-serif;font-size:26px;font-weight:800;color:#fff;margin:8px 0 24px;">
          <span style="background:linear-gradient(90deg,#c77dff,#7b2fff);
            -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;">
            Author Network & Impact
          </span>
        </div>
        """, unsafe_allow_html=True)

        author_data = extract_author_network(final_data.get('papers', []))

        col1, col2 = st.columns(2)
        col1.metric("Total Authors", author_data['total_authors'])
        col2.metric("Top Authors", len(author_data['top_authors']))

        st.divider()
        st.markdown("### 🌟 Top Authors")

        for idx, author in enumerate(author_data['top_authors'], 1):
            with st.expander(f"{idx}. {author['name']}"):
                col1, col2, col3 = st.columns(3)
                col1.metric("Papers", author['papers'])
                col2.metric("Collaborators", author['collaborators'])
                col3.metric("Influence", f"{min(100, author['papers']*10)}%")

    # ─────────────────── TAB 9: READING ROADMAP ──────────────────────────────
    with tab9:
        st.markdown("""
        <div style="font-family:'Space Grotesk',sans-serif;font-size:26px;font-weight:800;color:#fff;margin:8px 0 24px;">
          <span style="background:linear-gradient(90deg,#c77dff,#7b2fff);
            -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;">
            Suggested Reading Path
          </span>
        </div>
        """, unsafe_allow_html=True)

        roadmap = build_reading_roadmap(final_data.get('papers', []))

        categories = {}
        for item in roadmap:
            cat = item['category']
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(item)

        for category in ['Foundational', 'Intermediate', 'Advanced']:
            if category in categories:
                st.markdown(f"### 📚 {category} Papers")
                for idx, paper in enumerate(categories[category], 1):
                    title = paper['paper']
                    display_title = f"{title[:80]}..." if len(title) > 80 else title
                    if paper.get('url'):
                        st.markdown(f"{idx}. [{display_title}]({paper['url']}) ({paper.get('year', 'N/A')})")
                    else:
                        st.write(f"{idx}. **{display_title}** ({paper.get('year', 'N/A')})")
                    st.caption(paper['recommendation'])

    # ─────────────────── TAB 10: EXPORT CENTER ──────────────────────────────────
    with tab10:
        st.markdown("""
        <div style="font-family:'Space Grotesk',sans-serif;font-size:26px;font-weight:800;color:#fff;margin:8px 0 24px;">
          <span style="background:linear-gradient(90deg,#c77dff,#7b2fff);
            -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;">
            Export Research
          </span>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("### 📤 Available Formats")

        col1, col2 = st.columns(2)

        # BibTeX
        with col1:
            if st.button("📖 BibTeX Format", use_container_width=True):
                bibtex_data = export_to_bibtex(final_data.get('papers', []))
                st.download_button(
                    label="Download BibTeX",
                    data=bibtex_data,
                    file_name=f"references_{datetime.now().strftime('%Y%m%d_%H%M%S')}.bib",
                    mime="text/plain",
                    use_container_width=True
                )

        # Markdown
        with col2:
            if st.button("📝 Markdown Format", use_container_width=True):
                md_data = export_to_markdown(
                    final_data.get('topic', 'Research'),
                    final_data.get('papers', []),
                    final_data.get('contradictions', []),
                    final_data.get('report', '')
                )
                st.download_button(
                    label="Download Markdown",
                    data=md_data,
                    file_name=f"research_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                    mime="text/markdown",
                    use_container_width=True
                )

        col1, col2 = st.columns(2)

        # CSV
        with col1:
            if st.button("📊 CSV Format", use_container_width=True):
                csv_data = export_to_csv(final_data.get('papers', []))
                st.download_button(
                    label="Download CSV",
                    data=csv_data,
                    file_name=f"papers_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )

        # JSON
        with col2:
            if st.button("📋 JSON Format", use_container_width=True):
                json_data = export_to_json(
                    final_data.get('topic', 'Research'),
                    final_data.get('papers', []),
                    final_data.get('contradictions', []),
                    final_data.get('report', '')
                )
                st.download_button(
                    label="Download JSON",
                    data=json_data,
                    file_name=f"research_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json",
                    use_container_width=True
                )

        col1, col2 = st.columns(2)

        # RIS
        with col1:
            if st.button("📚 RIS Format (Mendeley/Zotero)", use_container_width=True):
                ris_data = export_to_ris(final_data.get('papers', []))
                st.download_button(
                    label="Download RIS",
                    data=ris_data,
                    file_name=f"references_{datetime.now().strftime('%Y%m%d_%H%M%S')}.ris",
                    mime="text/plain",
                    use_container_width=True
                )

        # HTML
        with col2:
            if st.button("🌐 HTML Report", use_container_width=True):
                html_data = export_to_html(
                    final_data.get('topic', 'Research'),
                    final_data.get('papers', []),
                    final_data.get('contradictions', []),
                    final_data.get('report', '')
                )
                st.download_button(
                    label="Download HTML",
                    data=html_data,
                    file_name=f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
                    mime="text/html",
                    use_container_width=True
                )

    # ─────────────────── TAB 11 (last): SAVED RESEARCH ────────────────
    with tab11:
        st.markdown("""
        <div style="font-family:'Space Grotesk',sans-serif;font-size:26px;font-weight:800;color:#fff;margin:8px 0 24px;">
          <span style="background:linear-gradient(90deg,#c77dff,#7b2fff);
            -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;">
            Saved Research History
          </span>
        </div>
        """, unsafe_allow_html=True)

        if st.session_state.get("saved_successfully"):
            st.success("✅ Research saved locally!")

        c1,c2,c3 = st.columns(3)
        with c1:
            history = storage.get_history()
            st.metric("Total Searches", len(history))
        with c2:
            st.metric("Storage Used", storage.get_storage_size())
        with c3:
            st.metric("Location", "scholarpython_research/")

        st.divider()
        st.markdown('<div style="font-family:Space Grotesk,sans-serif;font-size:18px;font-weight:700;color:#c77dff;margin-bottom:16px;">Recent Research</div>', unsafe_allow_html=True)

        history = storage.get_history(limit=20)
        if history:
            for research in history:
                with st.expander(f"📅 {research['topic']} — {research['timestamp']}"):
                    c1,c2,c3,c4 = st.columns(4)
                    with c1: st.metric("Papers", research['papers_count'])
                    with c2: st.metric("Contradictions", research['contradictions_count'])
                    with c3: st.write("**Status**: Completed")
                    with c4:
                        if st.button("Load", key=f"load_{research['id']}"):
                            try:
                                loaded_data = storage.load_research(research['file_path'])
                                st.session_state.research_data = loaded_data
                                st.session_state.research_complete = True
                                st.success("Loaded! Refresh to view.")
                            except Exception as e:
                                st.error(f"Error loading: {e}")

                    st.markdown("**Files in this research:**")
                    research_path = research['file_path']
                    if os.path.exists(research_path):
                        for file in os.listdir(research_path):
                            st.markdown(f'<span style="color:rgba(157,78,221,0.8);font-size:13px;">📄 {file}</span>', unsafe_allow_html=True)

                    c1,c2 = st.columns(2)
                    with c1:
                        if st.button("Export as ZIP", key=f"export_{research['id']}"):
                            try:
                                zip_path = storage.export_research(research['file_path'])
                                st.success(f"Exported to: {zip_path}")
                            except Exception as e:
                                st.error(f"Export error: {e}")
                    with c2:
                        if st.button("Delete", key=f"delete_{research['id']}"):
                            storage.delete_research(research['file_path'])
                            st.success("Deleted!")
                            st.rerun()
        else:
            st.info("No saved research yet. Complete a search to save it!")

        st.divider()

# ══════════════════════════════════════════════════════════════════════════════
#  FOOTER
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@keyframes ftGlow { 0%,100%{opacity:0.6} 50%{opacity:1} }
.footer {
  position:relative;
  margin-top:70px;
  padding:34px 44px;
  background:linear-gradient(135deg,rgba(7,4,15,0.98) 0%,rgba(13,7,32,0.98) 100%);
  border:1px solid rgba(123,47,255,0.15);
  border-radius:24px;
  display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:16px;
  overflow:hidden;
  animation: ftGlow 5s ease-in-out infinite;
}
.footer::before {
  content:'';
  position:absolute; bottom:-60%; left:50%;
  width:500px; height:200px;
  transform:translateX(-50%);
  background:radial-gradient(ellipse,rgba(123,47,255,0.12) 0%,transparent 70%);
  pointer-events:none;
}
.ft-brand {
  font-family:'Space Grotesk',sans-serif;
  font-size:20px; font-weight:900; color:#fff;
}
.ft-brand span {
  background:linear-gradient(90deg,#7b2fff,#c77dff);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;
}
.ft-tag  { font-size:12px; color:rgba(255,255,255,0.3); margin-top:4px; }
.ft-right{ font-size:12px; color:rgba(255,255,255,0.3); text-align:right; line-height:2; }
</style>
<div class="footer">
  <div>
    <div class="ft-brand">🎓 Schol<span>AR</span></div>
    <div class="ft-tag">Intelligent Literature Review System</div>
  </div>
  <div class="ft-right">
    Making research discovery autonomous and accessible.<br>
    Powered by Semantic Scholar · OpenRouter · Python
  </div>
</div>
""", unsafe_allow_html=True)