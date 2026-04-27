import sys
import os

import streamlit as st
import plotly.graph_objects as go
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
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
    page_title="Progression Individuelle — Suivi de Projet",
    page_icon="👤",
    layout="wide",
)

st.markdown(
    """
    <style>
    .member-card {
        border-radius: 12px;
        padding: 1rem;
        color: white;
        margin-bottom: 0.5rem;
    }
    .section-title { font-size: 1.15rem; font-weight: 600; color: #1f3864; }
    </style>
    """,
    unsafe_allow_html=True,
)

data = load_data()
tasks_all = data["tasks"]
members = data["members"]

st.title("👤 Progression Individuelle")
st.caption("Consultez l'avancement de chaque membre de l'équipe.")
st.divider()

if not members:
    st.warning("Aucun membre enregistré. Ajoutez des membres dans la page **Métadonnées**.")
    st.stop()

# ── Global summary cards ───────────────────────────────────────────────────────
st.markdown("<p class='section-title'>Vue d'ensemble de l'équipe</p>", unsafe_allow_html=True)

CARD_COLORS = ["#1565C0", "#2E7D32", "#E65100", "#6A1B9A", "#00838F", "#AD1457"]

cols = st.columns(len(members))
for idx, member in enumerate(members):
    member_tasks = [t for t in tasks_all if t["assigned_to"] == member["id"]]
    prog = compute_progress(member_tasks)
    color = CARD_COLORS[idx % len(CARD_COLORS)]
    with cols[idx]:
        st.markdown(
            f"""<div class='member-card' style='background:{color}'>
            <div style='font-size:1.1rem;font-weight:700'>{member['name']}</div>
            <div style='font-size:0.8rem;opacity:0.85'>{member['role']}</div>
            <hr style='border-color:rgba(255,255,255,0.3);margin:0.5rem 0'>
            <div style='font-size:1.6rem;font-weight:700'>{prog['pct']} %</div>
            <div style='font-size:0.75rem;opacity:0.85'>{prog['done']}/{prog['total']} tâches terminées</div>
            </div>""",
            unsafe_allow_html=True,
        )
        st.progress(prog["pct"] / 100)

st.divider()

# ── Radar / bar chart ──────────────────────────────────────────────────────────
st.markdown("<p class='section-title'>Comparaison par statut</p>", unsafe_allow_html=True)

chart_data = []
for member in members:
    member_tasks = [t for t in tasks_all if t["assigned_to"] == member["id"]]
    prog = compute_progress(member_tasks)
    chart_data.append(
        {
            "Membre": member["name"],
            STATUS_LABELS["done"]: prog["done"],
            STATUS_LABELS["in_progress"]: prog["in_progress"],
            STATUS_LABELS["todo"]: prog["todo"],
        }
    )

df_chart = pd.DataFrame(chart_data)
fig = go.Figure()
for status_key, label in STATUS_LABELS.items():
    fig.add_trace(
        go.Bar(
            name=label,
            x=df_chart["Membre"],
            y=df_chart[label],
            marker_color=STATUS_COLORS[status_key],
        )
    )
fig.update_layout(
    barmode="group",
    legend=dict(orientation="h", y=-0.2),
    margin=dict(t=10, b=10, l=10, r=10),
    height=320,
    xaxis_title=None,
    yaxis_title="Nombre de tâches",
)
st.plotly_chart(fig, use_container_width=True)

st.divider()

# ── Detail panel ──────────────────────────────────────────────────────────────
st.markdown("<p class='section-title'>Détail par membre</p>", unsafe_allow_html=True)

member_names = [m["name"] for m in members]
selected_name = st.selectbox("Sélectionner un membre", member_names)
selected_member = next(m for m in members if m["name"] == selected_name)

member_tasks = [t for t in tasks_all if t["assigned_to"] == selected_member["id"]]
prog = compute_progress(member_tasks)

st.markdown(f"**Rôle :** {selected_member['role']}")

mc1, mc2, mc3, mc4 = st.columns(4)
mc1.metric("Total", prog["total"])
mc2.metric("Terminées ✅", prog["done"])
mc3.metric("En cours 🔄", prog["in_progress"])
mc4.metric("À faire 📋", prog["todo"])

st.progress(prog["pct"] / 100, text=f"Avancement : {prog['pct']} %")

if member_tasks:
    rows = []
    for t in member_tasks:
        d = days_until(t["deadline"])
        flag = "🔴" if d < 0 and t["status"] != "done" else ""
        rows.append(
            {
                "": flag,
                "Tâche": t["title"],
                "Statut": STATUS_LABELS.get(t["status"], t["status"]),
                "Priorité": PRIORITY_LABELS.get(t["priority"], t["priority"]),
                "Échéance": t["deadline"],
                "Jours restants": d if t["status"] != "done" else "—",
            }
        )
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
else:
    st.info("Aucune tâche assignée à ce membre.")
