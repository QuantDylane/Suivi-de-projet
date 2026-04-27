import sys
import os

import streamlit as st
from datetime import datetime, date

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.data_manager import (
    load_data,
    save_data,
    get_member_name,
    get_next_id,
    STATUS_LABELS,
    PRIORITY_LABELS,
)

st.set_page_config(
    page_title="Métadonnées — Suivi de Projet",
    page_icon="⚙️",
    layout="wide",
)

st.title("⚙️ Métadonnées")
st.caption("Gérez les informations du projet, les membres et les tâches.")
st.divider()

data = load_data()

tab_project, tab_members, tab_tasks = st.tabs(["📁 Projet", "👥 Membres", "📋 Tâches"])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — PROJECT
# ══════════════════════════════════════════════════════════════════════════════
with tab_project:
    st.subheader("Informations du projet")
    project = data["project"]

    with st.form("form_project"):
        proj_name = st.text_input("Nom du projet", value=project.get("name", ""))
        proj_desc = st.text_area("Description", value=project.get("description", ""), height=100)
        proj_deadline = st.date_input(
            "Deadline",
            value=datetime.strptime(project["deadline"], "%Y-%m-%d").date(),
            min_value=date(2020, 1, 1),
        )
        submitted = st.form_submit_button("💾 Enregistrer", use_container_width=True)

    if submitted:
        if not proj_name.strip():
            st.error("Le nom du projet ne peut pas être vide.")
        else:
            data["project"]["name"] = proj_name.strip()
            data["project"]["description"] = proj_desc.strip()
            data["project"]["deadline"] = proj_deadline.strftime("%Y-%m-%d")
            save_data(data)
            st.success("✅ Informations du projet mises à jour !")
            st.rerun()

    st.divider()
    st.markdown("**Valeurs actuelles**")
    st.json(
        {
            "Nom": data["project"].get("name"),
            "Description": data["project"].get("description"),
            "Deadline": data["project"].get("deadline"),
            "Créé le": data["project"].get("created_at"),
        }
    )

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — MEMBERS
# ══════════════════════════════════════════════════════════════════════════════
with tab_members:
    members = data["members"]

    add_col, edit_col, del_col = st.columns([1, 1, 1])

    # ── Add member ──────────────────────────────────────────────────────────
    with add_col:
        st.subheader("➕ Ajouter un membre")
        with st.form("form_add_member"):
            new_name = st.text_input("Nom complet")
            new_role = st.text_input("Rôle")
            add_submitted = st.form_submit_button("Ajouter", use_container_width=True)

        if add_submitted:
            if not new_name.strip():
                st.error("Le nom est obligatoire.")
            else:
                data["members"].append(
                    {
                        "id": get_next_id(data["members"]),
                        "name": new_name.strip(),
                        "role": new_role.strip(),
                    }
                )
                save_data(data)
                st.success(f"✅ Membre « {new_name.strip()} » ajouté !")
                st.rerun()

    # ── Edit member ─────────────────────────────────────────────────────────
    with edit_col:
        st.subheader("✏️ Modifier un membre")
        if members:
            member_options = {m["name"]: m for m in members}
            selected_member_name = st.selectbox(
                "Sélectionner", list(member_options.keys()), key="edit_member_select"
            )
            sel_member = member_options[selected_member_name]
            with st.form("form_edit_member"):
                edit_name = st.text_input("Nom complet", value=sel_member["name"])
                edit_role = st.text_input("Rôle", value=sel_member["role"])
                edit_submitted = st.form_submit_button("Modifier", use_container_width=True)

            if edit_submitted:
                if not edit_name.strip():
                    st.error("Le nom est obligatoire.")
                else:
                    for m in data["members"]:
                        if m["id"] == sel_member["id"]:
                            m["name"] = edit_name.strip()
                            m["role"] = edit_role.strip()
                    save_data(data)
                    st.success("✅ Membre mis à jour !")
                    st.rerun()
        else:
            st.info("Aucun membre à modifier.")

    # ── Delete member ───────────────────────────────────────────────────────
    with del_col:
        st.subheader("🗑️ Supprimer un membre")
        if members:
            del_member_options = {m["name"]: m for m in members}
            del_member_name = st.selectbox(
                "Sélectionner", list(del_member_options.keys()), key="del_member_select"
            )
            del_member = del_member_options[del_member_name]
            assigned_count = sum(1 for t in data["tasks"] if t["assigned_to"] == del_member["id"])
            if assigned_count:
                st.warning(f"⚠️ Ce membre a {assigned_count} tâche(s) assignée(s).")
            if st.button("Supprimer", type="primary", use_container_width=True, key="del_member_btn"):
                data["members"] = [m for m in data["members"] if m["id"] != del_member["id"]]
                save_data(data)
                st.success(f"✅ Membre « {del_member_name} » supprimé !")
                st.rerun()
        else:
            st.info("Aucun membre à supprimer.")

    st.divider()
    st.subheader("Liste des membres")
    if members:
        import pandas as pd

        st.dataframe(
            pd.DataFrame(members).rename(columns={"id": "ID", "name": "Nom", "role": "Rôle"}),
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("Aucun membre enregistré.")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — TASKS
# ══════════════════════════════════════════════════════════════════════════════
with tab_tasks:
    tasks = data["tasks"]
    members = data["members"]

    member_map = {m["id"]: m["name"] for m in members}
    member_name_to_id = {m["name"]: m["id"] for m in members}
    status_options = list(STATUS_LABELS.keys())
    priority_options = list(PRIORITY_LABELS.keys())

    add_task_col, right_task_col = st.columns([1, 1])

    # ── Add task ─────────────────────────────────────────────────────────────
    with add_task_col:
        st.subheader("➕ Ajouter une tâche")
        if not members:
            st.warning("Ajoutez d'abord des membres pour pouvoir assigner des tâches.")
        else:
            with st.form("form_add_task"):
                t_title = st.text_input("Titre")
                t_desc = st.text_area("Description", height=80)
                t_assigned = st.selectbox("Assigné à", list(member_name_to_id.keys()))
                t_status = st.selectbox(
                    "Statut",
                    status_options,
                    format_func=lambda s: STATUS_LABELS[s],
                )
                t_priority = st.selectbox(
                    "Priorité",
                    priority_options,
                    format_func=lambda p: PRIORITY_LABELS[p],
                )
                t_deadline = st.date_input("Échéance", min_value=date(2020, 1, 1))
                add_task_submitted = st.form_submit_button("Ajouter", use_container_width=True)

            if add_task_submitted:
                if not t_title.strip():
                    st.error("Le titre est obligatoire.")
                else:
                    data["tasks"].append(
                        {
                            "id": get_next_id(data["tasks"]),
                            "title": t_title.strip(),
                            "description": t_desc.strip(),
                            "assigned_to": member_name_to_id[t_assigned],
                            "status": t_status,
                            "priority": t_priority,
                            "deadline": t_deadline.strftime("%Y-%m-%d"),
                            "created_at": date.today().strftime("%Y-%m-%d"),
                        }
                    )
                    save_data(data)
                    st.success(f"✅ Tâche « {t_title.strip()} » ajoutée !")
                    st.rerun()

    # ── Edit / Delete task ────────────────────────────────────────────────────
    with right_task_col:
        st.subheader("✏️ Modifier / 🗑️ Supprimer une tâche")
        if tasks:
            task_options = {f"#{t['id']} — {t['title']}": t for t in tasks}
            selected_task_label = st.selectbox("Sélectionner une tâche", list(task_options.keys()))
            sel_task = task_options[selected_task_label]

            with st.form("form_edit_task"):
                et_title = st.text_input("Titre", value=sel_task["title"])
                et_desc = st.text_area("Description", value=sel_task.get("description", ""), height=80)

                current_assignee = member_map.get(sel_task["assigned_to"], list(member_name_to_id.keys())[0] if member_name_to_id else None)
                assignee_list = list(member_name_to_id.keys())
                default_idx = assignee_list.index(current_assignee) if current_assignee in assignee_list else 0
                et_assigned = st.selectbox("Assigné à", assignee_list, index=default_idx) if assignee_list else None

                et_status = st.selectbox(
                    "Statut",
                    status_options,
                    index=status_options.index(sel_task["status"]) if sel_task["status"] in status_options else 0,
                    format_func=lambda s: STATUS_LABELS[s],
                )
                et_priority = st.selectbox(
                    "Priorité",
                    priority_options,
                    index=priority_options.index(sel_task["priority"]) if sel_task["priority"] in priority_options else 0,
                    format_func=lambda p: PRIORITY_LABELS[p],
                )
                et_deadline = st.date_input(
                    "Échéance",
                    value=datetime.strptime(sel_task["deadline"], "%Y-%m-%d").date(),
                    min_value=date(2020, 1, 1),
                )
                edit_task_col, del_task_col = st.columns(2)
                edit_task_btn = edit_task_col.form_submit_button("💾 Modifier", use_container_width=True)
                del_task_btn = del_task_col.form_submit_button("🗑️ Supprimer", use_container_width=True)

            if edit_task_btn:
                if not et_title.strip():
                    st.error("Le titre est obligatoire.")
                else:
                    for t in data["tasks"]:
                        if t["id"] == sel_task["id"]:
                            t["title"] = et_title.strip()
                            t["description"] = et_desc.strip()
                            t["assigned_to"] = member_name_to_id[et_assigned] if et_assigned else sel_task["assigned_to"]
                            t["status"] = et_status
                            t["priority"] = et_priority
                            t["deadline"] = et_deadline.strftime("%Y-%m-%d")
                    save_data(data)
                    st.success("✅ Tâche mise à jour !")
                    st.rerun()

            if del_task_btn:
                data["tasks"] = [t for t in data["tasks"] if t["id"] != sel_task["id"]]
                save_data(data)
                st.success(f"✅ Tâche « {sel_task['title']} » supprimée !")
                st.rerun()
        else:
            st.info("Aucune tâche enregistrée.")

    st.divider()
    st.subheader("Liste des tâches")
    if tasks:
        import pandas as pd

        rows = []
        for t in tasks:
            rows.append(
                {
                    "ID": t["id"],
                    "Titre": t["title"],
                    "Responsable": member_map.get(t["assigned_to"], "—"),
                    "Statut": STATUS_LABELS.get(t["status"], t["status"]),
                    "Priorité": PRIORITY_LABELS.get(t["priority"], t["priority"]),
                    "Échéance": t["deadline"],
                }
            )
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    else:
        st.info("Aucune tâche enregistrée.")
