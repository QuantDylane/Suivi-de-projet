import sys
import os

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from utils.data_manager import (
    load_data,
    get_member_name,
    compute_progress,
    days_until,
    STATUS_LABELS,
    STATUS_COLORS,
    PRIORITY_LABELS,
    PRIORITY_COLORS,
)

st.set_page_config(
    page_title="Dashboard — Suivi de Projet",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .kpi-box {
        background: linear-gradient(135deg, #1e3a5f 0%, #2a5298 100%);
        border-radius: 12px;
        padding: 1.2rem 1rem;
        text-align: center;
        color: white;
    }
    .kpi-value { font-size: 2.2rem; font-weight: 700; margin: 0; }
    .kpi-label { font-size: 0.85rem; opacity: 0.85; margin: 0; }
    .section-title { font-size: 1.15rem; font-weight: 600; margin-bottom: 0.5rem; color: #1f3864; }
    </style>
    """,
    unsafe_allow_html=True,
)

data = load_data()
project = data["project"]
tasks = data["tasks"]
members = data["members"]

prog = compute_progress(tasks)
days = days_until(project["deadline"])

# ── Header ────────────────────────────────────────────────────────────────────
col_title, col_deadline = st.columns([3, 1])
with col_title:
    st.title(f"📊 {project['name']}")
    st.caption(project["description"])
with col_deadline:
    color = "#E53935" if days < 30 else "#FB8C00" if days < 90 else "#43A047"
    label = "dépassée !" if days < 0 else f"J-{days}"
    st.markdown(
        f"""<div style='background:{color};border-radius:10px;padding:0.8rem 1rem;
        text-align:center;color:white;margin-top:0.5rem'>
        <div style='font-size:1.5rem;font-weight:700'>{label}</div>
        <div style='font-size:0.8rem'>Deadline : {project['deadline']}</div>
        </div>""",
        unsafe_allow_html=True,
    )

st.divider()

# ── KPI cards ─────────────────────────────────────────────────────────────────
c1, c2, c3, c4, c5 = st.columns(5)
kpis = [
    (c1, prog["total"], "Tâches totales", "#1565C0"),
    (c2, prog["done"], "Terminées ✅", "#2E7D32"),
    (c3, prog["in_progress"], "En cours 🔄", "#E65100"),
    (c4, prog["todo"], "À faire 📋", "#424242"),
    (c5, f"{prog['pct']} %", "Avancement", "#6A1B9A"),
]
for col, val, label, color in kpis:
    with col:
        st.markdown(
            f"""<div class='kpi-box' style='background:{color}'>
            <p class='kpi-value'>{val}</p>
            <p class='kpi-label'>{label}</p>
            </div>""",
            unsafe_allow_html=True,
        )

st.markdown("<br>", unsafe_allow_html=True)

# ── Progress bar ──────────────────────────────────────────────────────────────
st.markdown(f"<p class='section-title'>Progression globale — {prog['pct']} %</p>", unsafe_allow_html=True)
st.progress(prog["pct"] / 100)

st.divider()

# ── Charts row ────────────────────────────────────────────────────────────────
left, right = st.columns(2)

with left:
    st.markdown("<p class='section-title'>Répartition des statuts</p>", unsafe_allow_html=True)
    status_counts = {
        STATUS_LABELS[s]: sum(1 for t in tasks if t["status"] == s)
        for s in ["done", "in_progress", "todo"]
    }
    fig_pie = go.Figure(
        go.Pie(
            labels=list(status_counts.keys()),
            values=list(status_counts.values()),
            hole=0.45,
            marker_colors=[STATUS_COLORS["done"], STATUS_COLORS["in_progress"], STATUS_COLORS["todo"]],
            textinfo="label+percent",
        )
    )
    fig_pie.update_layout(
        margin=dict(t=10, b=10, l=10, r=10),
        showlegend=False,
        height=300,
    )
    st.plotly_chart(fig_pie, use_container_width=True)

with right:
    st.markdown("<p class='section-title'>Tâches par membre</p>", unsafe_allow_html=True)
    rows = []
    for t in tasks:
        rows.append(
            {
                "Membre": get_member_name(data, t["assigned_to"]),
                "Statut": STATUS_LABELS.get(t["status"], t["status"]),
            }
        )
    df = pd.DataFrame(rows)
    if not df.empty:
        grouped = df.groupby(["Membre", "Statut"]).size().reset_index(name="Nombre")
        fig_bar = px.bar(
            grouped,
            x="Membre",
            y="Nombre",
            color="Statut",
            color_discrete_map={
                STATUS_LABELS["done"]: STATUS_COLORS["done"],
                STATUS_LABELS["in_progress"]: STATUS_COLORS["in_progress"],
                STATUS_LABELS["todo"]: STATUS_COLORS["todo"],
            },
            barmode="stack",
        )
        fig_bar.update_layout(
            margin=dict(t=10, b=10, l=10, r=10),
            legend=dict(orientation="h", y=-0.25),
            height=300,
            xaxis_title=None,
            yaxis_title="Tâches",
        )
        st.plotly_chart(fig_bar, use_container_width=True)

st.divider()

# ── Upcoming deadlines ────────────────────────────────────────────────────────
st.markdown("<p class='section-title'>Prochaines échéances</p>", unsafe_allow_html=True)
upcoming = sorted(
    [t for t in tasks if t["status"] != "done"],
    key=lambda t: t["deadline"],
)[:6]

if upcoming:
    table_rows = []
    for t in upcoming:
        d = days_until(t["deadline"])
        flag = "🔴" if d < 0 else "🟠" if d < 30 else "🟡" if d < 90 else "🟢"
        table_rows.append(
            {
                " ": flag,
                "Tâche": t["title"],
                "Responsable": get_member_name(data, t["assigned_to"]),
                "Échéance": t["deadline"],
                "Jours restants": d,
                "Priorité": PRIORITY_LABELS.get(t["priority"], t["priority"]),
            }
        )
    st.dataframe(
        pd.DataFrame(table_rows),
        use_container_width=True,
        hide_index=True,
    )
else:
    st.success("Toutes les tâches sont terminées 🎉")
