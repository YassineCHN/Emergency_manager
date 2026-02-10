"""
🎨 DASHBOARD COMPONENTS V2 - VERSION CORRIGÉE FINALE
====================================================
Toutes les fonctions HTML sur une ligne pour éviter les bugs Streamlit
"""

import streamlit as st
from datetime import datetime
from typing import Dict, Any, List, Optional


def render_hero_zone(
    critical_backlog: int, ai_managing: int, status: str = "SAFE", temps: int = 0
) -> None:
    """Hero Zone avec KPI géant - VERSION CORRIGÉE"""
    status_labels = {
        "SAFE": "🟢 SYSTEM SAFE",
        "TENSION": "🟡 UNDER TENSION",
        "CRITICAL": "🔴 NEEDS ACTION",
    }

    # HTML sur une ligne
    html = f'<div class="hero-zone"><div class="hero-title">🤖 AI-POWERED EMERGENCY INTELLIGENCE</div><div class="hero-subtitle">Real-time autonomous patient flow management</div><div class="hero-kpi"><div class="hero-kpi-label">CRITICAL BACKLOG</div><div class="hero-kpi-value">{critical_backlog}</div><div class="hero-kpi-status {status.lower()}">{status_labels[status]}</div></div><div class="hero-metrics"><div class="hero-metric"><span>⚡</span><span><strong>{ai_managing}</strong> patients under AI management</span></div><div class="hero-metric"><span>⏱️</span><span><strong>T+{temps:03d}</strong> minutes runtime</span></div></div></div>'

    st.markdown(html, unsafe_allow_html=True)


def render_critical_situation_zone(
    alertes: List[str], patients_critiques: List[Dict]
) -> None:
    """Zone critique - VERSION CORRIGÉE"""
    if not alertes and not patients_critiques:
        return

    st.markdown(
        '<div class="section-header critical">🚨 CRITICAL SITUATION</div>',
        unsafe_allow_html=True,
    )
    st.markdown('<div class="critical-zone">', unsafe_allow_html=True)

    # Alertes
    for alerte in alertes:
        html = f'<div class="critical-alert"><div class="critical-alert-icon">⚠️</div><div>{alerte}</div></div>'
        st.markdown(html, unsafe_allow_html=True)

    # Patients critiques
    for p in patients_critiques:
        attente = p.get("temps_attente", 0)
        nom = f"{p.get('prenom', '')} {p.get('nom', '')}"
        html = f'<div class="critical-alert"><div class="critical-alert-icon">🔴</div><div><strong>{nom}</strong> en attente depuis <strong>{attente} min</strong></div></div>'
        st.markdown(html, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


def render_kpi_secondary(label: str, value: Any, icon: str = "📊") -> None:
    """KPI secondaire - VERSION CORRIGÉE"""
    html = f'<div class="kpi-secondary"><div class="kpi-secondary-label">{icon} {label}</div><div class="kpi-secondary-value">{value}</div></div>'
    st.markdown(html, unsafe_allow_html=True)


def render_staff_section_with_tension(
    title: str,
    icon: str,
    staff_list: List[Dict],
    total: int,
    is_medecin: bool = False,
    consultation_occupee: bool = False,
) -> None:
    """Section personnel avec tension - VERSION CORRIGÉE"""

    # Calculer disponibilité
    if is_medecin and consultation_occupee:
        disponibles = 0
    else:
        disponibles = sum(1 for s in staff_list if s.get("disponible", False))

    charge_pct = int((total - disponibles) / total * 100) if total > 0 else 0

    # Déterminer tension
    if charge_pct < 50:
        tension = "safe"
        tension_label = "🟢 SAFE"
    elif charge_pct < 80:
        tension = "tension"
        tension_label = "🟡 TENSION"
    else:
        tension = "critical"
        tension_label = "🔴 CRITICAL"

    # Header section
    html = f'<div class="staff-section"><div class="staff-header"><div class="staff-title">{icon} {title}</div><div class="staff-tension {tension}">{tension_label}</div></div><div class="staff-availability">{disponibles}/{total} disponibles</div><div class="staff-charge-bar"><div class="staff-charge-fill {"high" if charge_pct > 70 else ""}" style="width: {charge_pct}%;"></div></div>'
    st.markdown(html, unsafe_allow_html=True)

    # Cartes staff
    for staff in staff_list:
        staff_id = staff.get("id", "N/A")
        disponible = staff.get("disponible", False)
        en_transport = staff.get("en_transport", False)
        salle = staff.get("salle_surveillee")
        patient = staff.get("patient_transporte_id")

        if en_transport:
            status_text = f"🚑 Transport {patient}"
        elif salle:
            status_text = f"📋 Surveillance {salle}"
        elif disponible:
            status_text = "✅ Disponible"
        else:
            status_text = f"📍 {staff.get('localisation', 'Occupé')}"

        indicator = "🟢" if disponible else "🔴"

        card_html = f'<div class="staff-card"><div style="display: flex; justify-content: space-between; align-items: center;"><div><strong>{staff_id}</strong></div><div>{indicator}</div></div><div style="color: var(--text-secondary); font-size: 0.9rem; margin-top: 4px;">{status_text}</div></div>'
        st.markdown(card_html, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


def render_room_with_risk(salle: Dict[str, Any], patients: Dict[str, Any]) -> None:
    """Salle avec risque - VERSION CORRIGÉE"""

    salle_id = salle.get("id", "N/A")
    capacite = salle.get("capacite", 10)
    patients_ids = salle.get("patients", [])
    nb_patients = len(patients_ids)
    taux = int((nb_patients / capacite * 100)) if capacite > 0 else 0

    # Compter par gravité
    nb_rouge = sum(
        1 for pid in patients_ids if patients.get(pid, {}).get("gravite") == "ROUGE"
    )

    # Déterminer risque
    if taux < 60 and nb_rouge == 0:
        risk = "safe"
        risk_label = "🟢 SAFE"
    elif taux < 90 and nb_rouge < 2:
        risk = "tension"
        risk_label = "🟡 TENSION"
    else:
        risk = "critical"
        risk_label = "🔴 CRITICAL"

    # Créer dots
    dots_html = ""
    for pid in patients_ids:
        p = patients.get(pid, {})
        gravite = p.get("gravite", "GRIS").lower()
        emoji = {"rouge": "🔴", "jaune": "🟡", "vert": "🟢", "gris": "⚪"}.get(
            gravite, "❓"
        )
        dots_html += f'<div class="patient-dot {gravite}" title="{pid}">{emoji}</div>'

    # Emplacements vides
    for _ in range(capacite - nb_patients):
        dots_html += '<div class="patient-dot empty">◻️</div>'

    # Alerte si ROUGE
    alert_html = ""
    if nb_rouge > 0:
        alert_html = f'<div style="margin-top: 16px; padding: 10px 14px; background: rgba(255, 75, 75, 0.1); border: 1px solid var(--critical); border-radius: 8px; font-size: 0.9rem; color: var(--critical);">🚨 <strong>{nb_rouge} ROUGE</strong> en attente</div>'

    # HTML complet
    room_html = f'<div class="room-card {risk}"><div class="room-header"><div class="room-title">🏥 {salle_id.upper().replace("_", " ")}</div><div class="room-risk-label {risk}">{risk_label}</div></div><div style="color: var(--text-secondary); font-size: 0.9rem; margin-bottom: 12px;">{nb_patients}/{capacite} patients · {taux}% occupation</div><div class="patient-dots">{dots_html}</div>{alert_html}</div>'

    st.markdown(room_html, unsafe_allow_html=True)


def render_operational_timeline(events: List[Dict[str, Any]]) -> None:
    """Timeline opérationnelle - VERSION CORRIGÉE"""
    if not events:
        st.info("Aucun événement")
        return

    # Grouper par type
    ai_events = []
    success_events = []
    incident_events = []

    for evt in events:
        emoji = evt.get("emoji", "ℹ️")
        msg = evt.get("msg", "")

        if (
            "🚑" in emoji
            or "📋" in emoji
            or "transport" in msg.lower()
            or "surveillance" in msg.lower()
        ):
            ai_events.append(evt)
        elif (
            "✅" in emoji
            or "🏁" in emoji
            or "arrivé" in msg.lower()
            or "terminée" in msg.lower()
        ):
            success_events.append(evt)
        elif "⚠️" in emoji or "🚨" in emoji:
            incident_events.append(evt)
        else:
            ai_events.append(evt)

    st.markdown('<div class="timeline-container">', unsafe_allow_html=True)

    # Section AI
    if ai_events:
        st.markdown(
            '<div class="timeline-section"><div class="timeline-section-title">🤖 AI DECISIONS</div>',
            unsafe_allow_html=True,
        )
        for evt in reversed(ai_events[-5:]):
            time_val = evt.get("time", 0)
            emoji = evt.get("emoji", "ℹ️")
            msg = evt.get("msg", "")
            event_html = f'<div class="timeline-event ai"><span class="timeline-time">[T+{time_val:03d}]</span><span>{emoji} {msg}</span></div>'
            st.markdown(event_html, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # Section Successes
    if success_events:
        st.markdown(
            '<div class="timeline-section"><div class="timeline-section-title">✅ SUCCESSES</div>',
            unsafe_allow_html=True,
        )
        for evt in reversed(success_events[-5:]):
            time_val = evt.get("time", 0)
            emoji = evt.get("emoji", "ℹ️")
            msg = evt.get("msg", "")
            event_html = f'<div class="timeline-event success"><span class="timeline-time">[T+{time_val:03d}]</span><span>{emoji} {msg}</span></div>'
            st.markdown(event_html, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # Section Incidents
    if incident_events:
        st.markdown(
            '<div class="timeline-section"><div class="timeline-section-title">⚠️ INCIDENTS</div>',
            unsafe_allow_html=True,
        )
        for evt in reversed(incident_events[-5:]):
            time_val = evt.get("time", 0)
            emoji = evt.get("emoji", "ℹ️")
            msg = evt.get("msg", "")
            event_html = f'<div class="timeline-event incident"><span class="timeline-time">[T+{time_val:03d}]</span><span>{emoji} {msg}</span></div>'
            st.markdown(event_html, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


def render_queue_item_simple(
    position: int, patient: Dict, current_time: datetime
) -> None:
    """Item file d'attente - VERSION CORRIGÉE"""
    patient_id = patient.get("id", "N/A")
    prenom = patient.get("prenom", "")
    nom = patient.get("nom", "")
    gravite = patient.get("gravite", "GRIS")

    # Temps d'attente
    try:
        arrived_at = datetime.fromisoformat(patient.get("arrived_at", ""))
        temps_attente = int((current_time - arrived_at).total_seconds() / 60)
    except:
        temps_attente = 0

    # Icône gravité
    emoji_map = {"ROUGE": "🔴", "JAUNE": "🟡", "VERT": "🟢", "GRIS": "⚪"}
    emoji = emoji_map.get(gravite, "❓")

    # Warning si > 30min
    warning = " ⚠️" if (temps_attente > 30 and gravite == "ROUGE") else ""

    queue_html = f'<div class="queue-item"><div style="min-width: 40px; font-weight: 700; font-size: 1.2rem; color: var(--accent);">{position}</div><div style="flex: 1;"><div style="font-weight: 600; color: var(--text-primary);">{emoji} {prenom} {nom}{warning}</div><div style="font-size: 0.85rem; color: var(--text-secondary); margin-top: 4px;">{patient_id} · {temps_attente} min d\'attente</div></div></div>'

    st.markdown(queue_html, unsafe_allow_html=True)


def render_spacer(size: str = "md") -> None:
    """Espacement"""
    st.markdown(f'<div class="spacer-{size}"></div>', unsafe_allow_html=True)


def render_divider() -> None:
    """Séparateur"""
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)


def render_section_header(title: str, icon: str = "📊", critical: bool = False) -> None:
    """En-tête section - VERSION CORRIGÉE"""
    class_name = "section-header critical" if critical else "section-header"
    st.markdown(
        f'<div class="{class_name}">{icon} {title}</div>', unsafe_allow_html=True
    )
