"""
🏥 EMERGENCY DASHBOARD V3 - STRUCTURE 3 ONGLETS
================================================
✨ NOUVEAU : Navigation verticale + Panneau latéral + Monitoring intégré
"""

import os

os.environ["HF_HUB_DOWNLOAD_TIMEOUT"] = "120"

import sys
from pathlib import Path

current_dir = Path(__file__).parent.absolute()
sys.path.insert(0, str(current_dir))
sys.path.insert(0, str(current_dir / "mcp"))

import streamlit as st
from datetime import datetime, timedelta
from typing import Optional
import time
import random

# Imports MCP
from mcp.state import (
    EmergencyState,
    Patient,
    Gravite,
    UniteCible,
    StatutPatient,
    TypeStaff,
)
from mcp.controllers.emergency_controller import EmergencyController
from rag.engine import HospitalRAGEngine

# Imports composants V2 (réutilisés)
from premium_styles import get_premium_css
from dashboard_components import (
    render_hero_zone,
    render_critical_situation_zone,
    render_kpi_secondary,
    render_staff_section_with_tension,
    render_room_with_risk,
    render_operational_timeline,
    render_queue_item_simple,
    render_spacer,
    render_divider,
    render_section_header,
)

# Imports composants chatbot
from chatbot_component import render_chatbot_premium, initialize_chatbot
from chatbot_panel_minimal import render_chat_panel_minimal

import json as json_module

# Imports monitoring
try:
    from monitoring.monitoring import monitor

    MONITORING_AVAILABLE = True
except ImportError as e:
    MONITORING_AVAILABLE = False

    # Créer un mock pour éviter les erreurs
    class MockMonitor:
        total_dollar_cost = 0.0
        total_energy_kwh = 0.0
        total_co2_kg = 0.0
        by_source = {}

        def get_average_latency(self):
            return 0.0

        def get_summary(self):
            return {
                "global": {
                    "total_requests": 0,
                    "total_cost": 0.0,
                    "total_energy_kwh": 0.0,
                    "total_co2_kg": 0.0,
                    "avg_latency_ms": 0.0,
                },
                "by_source": {},
            }

        def get_recent_history(self, n):
            return []

        def reset(self):
            pass

        def log_metrics_simple(self, **kwargs):
            pass

    monitor = MockMonitor()
    print(f"⚠️ Module monitoring non disponible : {e}")

# Vérifier chatbot
try:
    from chatbot.chatbot_engine import ChatbotEngine

    CHATBOT_AVAILABLE = True
except ImportError:
    CHATBOT_AVAILABLE = False

# Configuration Streamlit
st.set_page_config(
    page_title="🤖 UrgenceAI - Emergency Intelligence",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Injection CSS V3
st.markdown(get_premium_css(), unsafe_allow_html=True)

# ========== SESSION STATE ==========

# État de base
if "state" not in st.session_state:
    st.session_state.state = EmergencyState()
    st.session_state.temps = 0
    st.session_state.running = False
    st.session_state.events = []
    st.session_state.agent_enabled = True
    st.session_state.agent_speed = 1.0
    st.session_state.agent = None
    st.session_state.actions_count = 0

    if "controller" not in st.session_state:
        st.session_state.controller = EmergencyController(st.session_state.state)

# Onglet actif
if "current_tab" not in st.session_state:
    st.session_state.current_tab = "dashboard"

# Panneau chatbot
if "show_chat_panel" not in st.session_state:
    st.session_state.show_chat_panel = False

# Agent
if "agent_loaded" not in st.session_state:
    st.session_state.agent_loaded = False

# Historique décisions
if "decision_history" not in st.session_state:
    st.session_state.decision_history = []

# Chatbot
if "chatbot" not in st.session_state and CHATBOT_AVAILABLE:
    st.session_state.chatbot = initialize_chatbot(
        controller=st.session_state.controller,
        state=st.session_state.state,
        decision_history=st.session_state.decision_history,
    )

# Historique chat
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ========== FONCTIONS UTILITAIRES ==========


def add_event(msg, emoji="ℹ️"):
    """Ajoute un événement au log"""
    st.session_state.events.append(
        {
            "time": st.session_state.temps,
            "msg": msg,
            "emoji": emoji,
        }
    )
    if len(st.session_state.events) > 50:
        st.session_state.events = st.session_state.events[-50:]


def ajouter_patient_complet(gravite: Gravite = None) -> Patient:
    """Ajoute un patient ET l'assigne automatiquement à une salle."""
    if gravite is None:
        gravites = [Gravite.ROUGE, Gravite.JAUNE, Gravite.VERT, Gravite.GRIS]
        weights = [0.2, 0.3, 0.3, 0.2]
        gravite = random.choices(gravites, weights=weights)[0]

    # 80 PRÉNOMS
    prenoms = [
        "Jean",
        "Marie",
        "Pierre",
        "Sophie",
        "Luc",
        "Emma",
        "Thomas",
        "Julie",
        "Lucas",
        "Hugo",
        "Léa",
        "Chloé",
        "Nathan",
        "Camille",
        "Antoine",
        "Nicolas",
        "Sarah",
        "Alexandre",
        "Charlotte",
        "Maxime",
        "Laura",
        "Julien",
        "Océane",
        "Mathieu",
        "Pauline",
        "Raphaël",
        "Manon",
        "Benjamin",
        "Clara",
        "Romain",
        "Louise",
        "Théo",
        "Zoé",
        "Louis",
        "Alice",
        "Gabriel",
        "Inès",
        "Arthur",
        "Jade",
        "Tom",
        "Lola",
        "Paul",
        "Lily",
        "Enzo",
        "Anna",
        "Adam",
        "Rose",
        "Victor",
        "Eva",
        "Jules",
        "Mia",
        "Ethan",
        "Nina",
        "Mathis",
        "Lucie",
        "Noah",
        "Amélie",
        "Clément",
        "Anaïs",
        "Simon",
        "Margaux",
        "Baptiste",
        "Justine",
        "Valentin",
        "Emilie",
        "Adrien",
        "Melissa",
        "Bastien",
        "Aurore",
        "Damien",
        "Fanny",
        "Kevin",
        "Coralie",
        "Anthony",
        "Elise",
        "David",
        "Céline",
        "Florian",
        "Audrey",
        "Quentin",
    ]

    # 80 NOMS
    noms = [
        "Martin",
        "Bernard",
        "Dubois",
        "Thomas",
        "Robert",
        "Richard",
        "Petit",
        "Durand",
        "Leroy",
        "Moreau",
        "Simon",
        "Laurent",
        "Lefebvre",
        "Michel",
        "Garcia",
        "David",
        "Bertrand",
        "Roux",
        "Vincent",
        "Fournier",
        "Morel",
        "Girard",
        "Andre",
        "Mercier",
        "Dupont",
        "Lambert",
        "Bonnet",
        "Francois",
        "Martinez",
        "Legrand",
        "Garnier",
        "Faure",
        "Rousseau",
        "Blanc",
        "Guerin",
        "Muller",
        "Henry",
        "Roussel",
        "Nicolas",
        "Perrin",
        "Morin",
        "Mathieu",
        "Clement",
        "Gauthier",
        "Dumont",
        "Lopez",
        "Fontaine",
        "Chevalier",
        "Robin",
        "Masson",
        "Sanchez",
        "Gerard",
        "Nguyen",
        "Boyer",
        "Denis",
        "Lemaire",
        "Duval",
        "Joly",
        "Gautier",
        "Roger",
        "Roche",
        "Roy",
        "Noel",
        "Meyer",
        "Lucas",
        "Meunier",
        "Jean",
        "Perez",
        "Marchand",
        "Dufour",
        "Blanchard",
        "Marie",
        "Barbier",
        "Brun",
        "Dumas",
        "Brunet",
        "Schmitt",
        "Leroux",
        "Colin",
        "Fernandez",
    ]

    symptomes_map = {
        Gravite.ROUGE: [
            "Douleur thoracique intense",
            "Difficulté respiratoire sévère",
            "Perte de conscience",
            "Hémorragie importante",
        ],
        Gravite.JAUNE: [
            "Fracture suspectée",
            "Douleurs abdominales",
            "Fièvre élevée persistante",
            "Vertiges importants",
        ],
        Gravite.VERT: [
            "Entorse cheville",
            "Plaie superficielle",
            "Fièvre modérée",
            "Mal de dos",
        ],
        Gravite.GRIS: [
            "Consultation routine",
            "Renouvellement ordonnance",
            "Certificat médical",
            "Contrôle de suivi",
        ],
    }

    patient_id = f"P{int(time.time()*1000) % 100000}-{random.randint(0, 999):03d}"

    patient = Patient(
        id=patient_id,
        prenom=random.choice(prenoms),
        nom=random.choice(noms),
        gravite=gravite,
        symptomes=random.choice(symptomes_map[gravite]),
        age=random.randint(18, 85),
        antecedents=[],
    )

    result = st.session_state.controller.ajouter_patient(patient)

    if result["success"]:
        assign_result = st.session_state.controller.assigner_salle_attente(patient.id)

        if assign_result["success"]:
            salle_id = assign_result["salle_id"]
            add_event(
                f"Patient {patient.prenom} {patient.nom} assigné à {salle_id}", "🏥"
            )
        else:
            add_event(f"⚠️ {patient.prenom} {patient.nom} - Échec assignation", "❌")
    else:
        add_event(f"❌ {patient.prenom} {patient.nom} - Échec création", "❌")

    return patient


def handle_message(user_input):
    """Callback pour traiter un message utilisateur"""
    # Ajouter message utilisateur
    st.session_state.chat_history.append({"role": "user", "content": user_input})

    # Traiter avec chatbot
    if st.session_state.get("chatbot"):
        try:
            response = st.session_state.chatbot.process_message(user_input)

            # Ajouter réponse
            st.session_state.chat_history.append(
                {
                    "role": "assistant",
                    "content": response.message,
                    "metadata": {
                        "guardrail_status": response.guardrail_status,
                        "guardrail_details": response.guardrail_details,
                        "rag_context": response.rag_context,
                        "actions_executed": response.actions_executed,
                        "latency_ms": response.latency_ms,
                    },
                }
            )
        except Exception as e:
            st.session_state.chat_history.append(
                {
                    "role": "assistant",
                    "content": f"❌ Erreur : {str(e)}",
                    "metadata": {},
                }
            )
    else:
        st.session_state.chat_history.append(
            {
                "role": "assistant",
                "content": "❌ Chatbot non initialisé.",
                "metadata": {},
            }
        )

    st.rerun()


# ========== AGENT ==========


class EmergencyAgent:
    """Agent IA orchestrant les flux."""

    def __init__(self, state: EmergencyState, controller):
        self.state = state
        self.controller = controller
        self.rag_engine = HospitalRAGEngine(mode="simulation")

        # ✨ Initialisation du client Mistral
        self.mistral_client = None
        api_key = os.environ.get("MISTRAL_API_KEY")
        if api_key:
            try:
                from mistralai import Mistral

                self.mistral_client = Mistral(api_key=api_key)
                print("✅ Client Mistral initialisé pour V3")
            except ImportError:
                print("⚠️ mistralai package non installé")

        # Compteur pour limiter les appels LLM
        self.iteration_count = 0
        self.llm_frequency = 5

    def cycle_orchestration(self) -> list[str]:
        """Exécute le cycle complet des opérations urgences."""
        actions = []
        self.iteration_count += 1

        # 1. FINALISATION des transports (toujours exécuté)
        actions.extend(self._finaliser_transports())

        # 2. ✨ Appel LLM toutes les N itérations
        if self.mistral_client and self.iteration_count % self.llm_frequency == 0:
            llm_actions = self._decide_with_llm()
            actions.extend(llm_actions)
        else:
            # Mode règles simples entre les appels LLM
            actions.extend(self._gerer_surveillance())

            action_sortie = self._gerer_sortie_consultation()
            if action_sortie:
                actions.append(action_sortie)

            action_trans_unite = self._gerer_transport_unite()
            if action_trans_unite:
                actions.append(action_trans_unite)

            action_entree = self._gerer_consultation()
            if action_entree:
                actions.append(action_entree)

        return [a for a in actions if a is not None]

    def _decide_with_llm(self) -> list[str]:
        """✨ Utilise Mistral pour décider des actions à entreprendre."""
        actions = []

        # Construire le contexte
        etat = self.state.to_dict()
        patients = etat.get("patients", {})
        patients_actifs = [p for p in patients.values() if p.get("statut") != "sorti"]

        # Résumé de l'état
        nb_attente = len(
            [p for p in patients_actifs if p.get("statut") == "salle_attente"]
        )
        nb_rouge = len([p for p in patients_actifs if p.get("gravite") == "ROUGE"])
        nb_jaune = len([p for p in patients_actifs if p.get("gravite") == "JAUNE"])
        consultation_libre = etat.get("consultation", {}).get("patient_id") is None
        patient_en_consultation = etat.get("consultation", {}).get("patient_id")

        staff_data = etat.get("staff", [])
        staff_dispo = len(
            [s for s in staff_data if s.get("disponible") and not s.get("en_transport")]
        )

        queue_consultation = etat.get("queue_consultation", [])
        queue_transport = etat.get("queue_transport", [])

        prompt = f"""Tu es un agent IA gérant un service d'urgences hospitalières.

    ÉTAT ACTUEL:
    - Patients en attente: {nb_attente} (Rouge: {nb_rouge}, Jaune: {nb_jaune})
    - Consultation: {"LIBRE" if consultation_libre else f"OCCUPÉE par {patient_en_consultation}"}
    - Personnel disponible: {staff_dispo}
    - File consultation: {len(queue_consultation)} patients
    - File transport: {len(queue_transport)} patients

    RÈGLES:
    1. Priorité ROUGE > JAUNE > VERT
    2. Surveillance obligatoire toutes les 15 min
    3. Garder au moins 2 soignants pour la surveillance
    4. Orienter les patients VERT/GRIS vers MAISON après consultation
    5. Orienter les ROUGE/JAUNE vers l'unité appropriée (CARDIO, CHIRURGIE, etc.)

    Quelle action prioritaire dois-tu faire? Réponds en JSON:
    {{"action": "TRANSPORT_CONSULTATION|TRANSPORT_UNITE|SURVEILLANCE|TERMINER_CONSULTATION|ATTENDRE", "patient_id": "Pxxxx ou null", "destination": "MAISON|CARDIO|CHIRURGIE|null", "justification": "raison courte"}}"""

        try:
            start_time = time.perf_counter()

            response = self.mistral_client.chat.complete(
                model="ministral-3b-2512",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200,
                temperature=0.3,
            )

            latency_ms = (time.perf_counter() - start_time) * 1000

            # ✨ CRUCIAL : Enregistrer les métriques
            if hasattr(response, "usage") and response.usage and MONITORING_AVAILABLE:
                try:
                    monitor.log_metrics_simple(
                        input_tokens=response.usage.prompt_tokens,
                        output_tokens=response.usage.completion_tokens,
                        latency_ms=latency_ms,
                        model_name="ministral-3b-2512",
                        source="agent",
                    )
                except Exception as e:
                    print(f"Erreur log métriques: {e}")

            # Parser la réponse
            response_text = response.choices[0].message.content.strip()

            # Nettoyer le JSON
            if "```json" in response_text:
                response_text = (
                    response_text.split("```json")[1].split("```")[0].strip()
                )
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()

            decision = json_module.loads(response_text)
            action_type = decision.get("action", "ATTENDRE")
            patient_id = decision.get("patient_id")
            destination = decision.get("destination")
            justification = decision.get("justification", "")

            # Exécuter l'action décidée
            if action_type == "TRANSPORT_CONSULTATION" and patient_id:
                staff_dispo_list = [
                    s
                    for s in self.state.staff
                    if s.disponible
                    and not s.en_transport
                    and s.type.value in ["infirmier(ere)_mobile", "aide_soignant"]
                ]
                if staff_dispo_list and self.state.consultation.est_libre():
                    res = self.controller.demarrer_transport_consultation(
                        patient_id, staff_dispo_list[0].id
                    )
                    if res.get("success"):
                        st.session_state.actions_count += 1
                        actions.append(
                            f"🤖 LLM: {patient_id} → consultation ({justification})"
                        )

            elif action_type == "TERMINER_CONSULTATION" and patient_id:
                dest_map = {
                    "MAISON": UniteCible.MAISON,
                    "CARDIO": UniteCible.CARDIO,
                    "CHIRURGIE": UniteCible.CHIRURGIE,
                    "REA": UniteCible.REA,
                }
                dest = dest_map.get(destination, UniteCible.MAISON)
                res = self.controller.terminer_consultation(patient_id, dest)
                if res.get("success"):
                    st.session_state.actions_count += 1
                    actions.append(
                        f"🤖 LLM: Consultation terminée → {destination} ({justification})"
                    )

            elif action_type == "TRANSPORT_UNITE" and patient_id:
                staff_dispo_list = [
                    s
                    for s in self.state.staff
                    if s.disponible
                    and not s.en_transport
                    and s.type == TypeStaff.AIDE_SOIGNANT
                ]
                if staff_dispo_list:
                    res = self.controller.demarrer_transport_unite(
                        patient_id, staff_dispo_list[0].id
                    )
                    if res.get("success"):
                        st.session_state.actions_count += 1
                        actions.append(
                            f"🤖 LLM: {patient_id} → unité ({justification})"
                        )

            elif action_type == "SURVEILLANCE":
                actions.extend(self._gerer_surveillance())
                if actions:
                    actions[-1] = f"🤖 LLM: Surveillance ({justification})"

            else:
                actions.append(f"🤖 LLM: Attente ({justification})")

            # Enregistrer la décision
            st.session_state.decision_history.append(
                {
                    "timestamp": datetime.now(),
                    "decision": decision,
                    "temps_simulation": st.session_state.temps,
                }
            )

        except Exception as e:
            print(f"Erreur LLM: {e}")
            actions.append(f"⚠️ Erreur LLM: {str(e)[:50]}")

        return actions

    def _finaliser_transports(self) -> list[str]:
        actions = []
        for staff in self.state.staff:
            if staff.en_transport and staff.fin_transport_prevue:
                if self.state.current_time >= staff.fin_transport_prevue:
                    pid = staff.patient_transporte_id
                    if staff.destination_transport == "consultation":
                        self.controller.finaliser_transport_consultation(pid)
                        actions.append(f"✅ Arrivée en consultation : {pid}")
                        st.session_state.actions_count += 1
                    else:
                        self.controller.finaliser_transport_unite(pid)
                        p = self.state.patients.get(pid)
                        actions.append(f"🏁 {p.prenom if p else pid} arrivé en unité")
                        st.session_state.actions_count += 1
        return actions

    def _gerer_transport_unite(self) -> Optional[str]:
        queue = self.state.get_queue_transport_sortie()
        if not queue:
            return None
        p = queue[0]
        staff_mobiles = [
            s
            for s in self.state.staff
            if s.type.value in ["infirmier(ere)_mobile", "aide_soignant"]
        ]
        staff_dispo = [s for s in staff_mobiles if s.disponible and not s.en_transport]
        as_dispo = [s for s in staff_dispo if s.type == TypeStaff.AIDE_SOIGNANT]

        if as_dispo and len(staff_dispo) >= 3:
            res = self.controller.demarrer_transport_unite(p.id, as_dispo[0].id)
            if res.get("success"):
                st.session_state.actions_count += 1
                return f"🚑 {p.prenom} -> {p.unite_cible} (AS, 45 min)"

        if staff_dispo:
            agent = staff_dispo[0]
            res = self.controller.retourner_patient_salle_attente(p.id, agent.id)
            if res.get("success"):
                st.session_state.actions_count += 1
                return f"🔄 {p.prenom} replacé en salle (Secours, 5 min)"
        return None

    def _gerer_consultation(self) -> Optional[str]:
        if not self.state.consultation.est_libre():
            return None
        staff_mobiles = [
            s
            for s in self.state.staff
            if s.type.value in ["infirmier(ere)_mobile", "aide_soignant"]
        ]
        staff_dispo = [s for s in staff_mobiles if s.disponible and not s.en_transport]
        if len(staff_dispo) < 2:
            return None
        queue = self.state.get_queue_consultation()
        if queue and staff_dispo:
            res = self.controller.demarrer_transport_consultation(
                queue[0].id, staff_dispo[0].id
            )
            if res.get("success"):
                st.session_state.actions_count += 1
                return f"🚑 {queue[0].prenom} vers consultation"
        return None

    def _gerer_surveillance(self) -> list[str]:
        actions = []
        staff_dispo = self.state.get_staff_disponible(
            TypeStaff.INFIRMIERE_MOBILE
        ) + self.state.get_staff_disponible(TypeStaff.AIDE_SOIGNANT)
        for salle in self.state.salles_attente:
            if (
                salle.temps_sans_surveillance(self.state.current_time) > 10
                and len(salle.patients) > 0
            ):
                en_poste = any(
                    s.salle_surveillee == salle.id and not s.en_transport
                    for s in self.state.staff
                )
                if not en_poste and staff_dispo:
                    agent = staff_dispo.pop(0)
                    res = self.controller.assigner_surveillance(agent.id, salle.id)
                    if res.get("success"):
                        st.session_state.actions_count += 1
                        actions.append(f"📋 {agent.id} affecté à {salle.id}")
        return actions

    def _gerer_sortie_consultation(self) -> Optional[str]:
        if self.state.consultation.est_libre():
            return None
        pid = self.state.consultation.patient_id
        patient = self.state.patients.get(pid)
        debut = self.state.consultation.debut_consultation
        if not debut:
            return None
        duree_ecoulee = (self.state.current_time - debut).total_seconds() / 60
        duree_min = 10 if patient.gravite == Gravite.VERT else 20
        if duree_ecoulee >= duree_min:
            destination = (
                UniteCible.MAISON
                if patient.gravite in [Gravite.VERT, Gravite.GRIS]
                else UniteCible.CARDIO
            )
            res = self.controller.terminer_consultation(pid, destination)
            if res.get("success"):
                st.session_state.actions_count += 1
                return f"✅ Consultation terminée : {patient.prenom} -> {destination.value}"
        return None


# ========== SIDEBAR NAVIGATION ==========

with st.sidebar:
    # Afficher le temps (toujours visible)
    st.markdown("### ⏱️ Temps")
    heures = st.session_state.temps // 60
    minutes = st.session_state.temps % 60
    # st.markdown(f"<h2 style='color: white; font-size: 2.5rem; margin: 0; text-shadow: 0 2px 10px rgba(0,0,0,0.3);'>{heures:02d}h{minutes:02d}</h2>", unsafe_allow_html=True)
    st.markdown(
        f"<h2 style='color: #667eea; font-size: 2.5rem; margin: 0;'>{heures:02d}h{minutes:02d}</h2>",
        unsafe_allow_html=True,
    )

    render_divider()

    # Navigation principale
    st.markdown("### 📍 Navigation")

    # Boutons de navigation
    if st.button(
        "📊 Dashboard",
        use_container_width=True,
        type="primary" if st.session_state.current_tab == "dashboard" else "secondary",
        key="nav_dashboard",
    ):
        st.session_state.current_tab = "dashboard"
        st.rerun()

    if st.button(
        "💬 Chatbot",
        use_container_width=True,
        type="primary" if st.session_state.current_tab == "chatbot" else "secondary",
        key="nav_chatbot",
    ):
        st.session_state.current_tab = "chatbot"
        st.rerun()

    if st.button(
        "📈 Monitoring",
        use_container_width=True,
        type="primary" if st.session_state.current_tab == "monitoring" else "secondary",
        key="nav_monitoring",
    ):
        st.session_state.current_tab = "monitoring"
        st.rerun()

    render_divider()

    # Contenu spécifique à l'onglet Dashboard
    if st.session_state.current_tab == "dashboard":
        # Bouton ouvrir assistant
        st.markdown("### 🤖 Assistant IA")
        if st.button(
            (
                "🤖 Ouvrir Assistant"
                if not st.session_state.show_chat_panel
                else "❌ Fermer Assistant"
            ),
            use_container_width=True,
            type="secondary",
            key="toggle_chat_panel",
        ):
            st.session_state.show_chat_panel = not st.session_state.show_chat_panel
            st.rerun()

        render_divider()

        # Simulation
        st.markdown("### 🎮 Simulation")

        if st.button(
            "▶️ Play" if not st.session_state.running else "⏸️ Pause",
            use_container_width=True,
            type="primary",
            key="play_pause_btn",
        ):
            st.session_state.running = not st.session_state.running
            st.rerun()

        if st.button(
            "🔄 Reset", use_container_width=True, type="secondary", key="reset_btn"
        ):
            st.session_state.state = EmergencyState()
            st.session_state.controller = EmergencyController(st.session_state.state)
            st.session_state.temps = 0
            st.session_state.events = []
            st.session_state.agent = None
            st.session_state.actions_count = 0
            st.session_state.decision_history = []
            st.rerun()

        render_divider()

        # Agent
        st.markdown("### 🤖 Agent")
        st.session_state.agent_enabled = st.checkbox(
            "Activer l'agent", value=st.session_state.agent_enabled
        )
        if st.session_state.agent_enabled:
            st.success("✅ Agent actif")
        else:
            st.warning("⏸️ Agent désactivé")
        st.markdown("**Vitesse agent**")
        st.session_state.agent_speed = st.slider(
            "Vitesse (s)",
            0.1,
            2.0,
            st.session_state.agent_speed,
            0.1,
            label_visibility="collapsed",
        )

        render_divider()

        # Actions
        st.markdown("### ➕ Actions")
        if st.button("👤 +1 Patient", use_container_width=True, type="primary"):
            patient = ajouter_patient_complet()
            st.success(
                f"✅ {patient.prenom} {patient.nom} ({patient.gravite}) ajouté !"
            )
            time.sleep(0.3)
            st.rerun()

        if st.button("👥 +5 Patients", use_container_width=True):
            patients_ajoutes = 0
            for _ in range(5):
                patient = ajouter_patient_complet()
                if patient.id in st.session_state.state.patients:
                    patients_ajoutes += 1
            st.success(f"✅ {patients_ajoutes} patients ajoutés !")
            time.sleep(0.3)
            st.rerun()

        if st.button("🚨 Afflux (15)", use_container_width=True):
            rouge_count = 0
            jaune_count = 0

            for _ in range(15):
                if random.random() < 0.7:
                    patient = ajouter_patient_complet(Gravite.ROUGE)
                    if patient.id in st.session_state.state.patients:
                        rouge_count += 1
                else:
                    patient = ajouter_patient_complet(Gravite.JAUNE)
                    if patient.id in st.session_state.state.patients:
                        jaune_count += 1

            add_event(f"🚨 Afflux : {rouge_count} ROUGE + {jaune_count} JAUNE", "🚨")
            st.error(f"🚨 AFFLUX : {rouge_count} ROUGE + {jaune_count} JAUNE !")
            time.sleep(0.5)
            st.rerun()

        render_divider()

        # Statistiques
        st.markdown("### 📊 Stats Agent")
        st.markdown(f"**Actions prises**")
        st.markdown(
            f"<h2 style='color: #00D084; font-size: 2rem; margin: 0;'>{st.session_state.actions_count}</h2>",
            unsafe_allow_html=True,
        )

# ========== CONTENU PRINCIPAL SELON ONGLET ==========

st.empty()
# if st.session_state.current_tab == "dashboard":
# ✨ FIX : Forcer le rerun pour nettoyer l'affichage entre onglets
if "last_tab" not in st.session_state:
    st.session_state.last_tab = "dashboard"

if st.session_state.last_tab != st.session_state.current_tab:
    st.session_state.last_tab = st.session_state.current_tab
    st.rerun()

# ========== CONTENU SELON ONGLET ==========
if st.session_state.current_tab == "dashboard":

    # Créer colonnes SI panneau actif
    if (
        st.session_state.show_chat_panel
        and CHATBOT_AVAILABLE
        and st.session_state.get("chatbot")
    ):
        col_main, col_panel = st.columns([65, 35], gap="small")
    else:
        col_main = st.container()
        col_panel = None

    # ========== CONTENU DASHBOARD ==========
    with col_main:
        render_spacer("md")
        # ========== ONGLET DASHBOARD ==========

        # Récupérer état système
        etat = st.session_state.controller.get_etat_systeme()
        patients = etat.get("patients", {})

        # Calculs KPI
        nb_total = len([p for p in patients.values() if p.get("statut") != "sorti"])
        nb_rouge_attente = len(
            [
                p
                for p in patients.values()
                if p.get("gravite") == "ROUGE" and p.get("statut") == "salle_attente"
            ]
        )
        nb_attente = len(
            [p for p in patients.values() if p.get("statut") == "salle_attente"]
        )
        nb_consultation = 1 if etat.get("consultation", {}).get("patient_id") else 0
        nb_en_transport = len(
            [p for p in patients.values() if "transport" in p.get("statut", "")]
        )

        # Statut système
        if nb_rouge_attente >= 3:
            system_status = "CRITICAL"
        elif nb_rouge_attente > 0:
            system_status = "TENSION"
        else:
            system_status = "SAFE"

        # Hero Zone
        render_hero_zone(
            critical_backlog=nb_rouge_attente,
            ai_managing=nb_total,
            status=system_status,
            temps=st.session_state.temps,
        )

        render_spacer("lg")

        # Critical Situation (si nécessaire)
        alertes = etat.get("alertes_surveillance", [])
        patients_critiques = [
            p
            for p in patients.values()
            if p.get("gravite") == "ROUGE"
            and p.get("statut") == "salle_attente"
            and p.get("temps_attente_minutes", 0) > 30
        ]

        if alertes or patients_critiques:
            render_critical_situation_zone(alertes, patients_critiques)
            render_spacer("lg")

        # KPI Secondaires
        col1, col2, col3 = st.columns(3)
        with col1:
            render_kpi_secondary("CAPACITY", f"{nb_attente}/{20}", "📊")
        with col2:
            avg_wait = 12
            render_kpi_secondary("AVG WAIT", f"{avg_wait} min", "⏱️")
        with col3:
            ai_status = "✅ ACTIVE" if st.session_state.agent_enabled else "⏸️ PAUSED"
            render_kpi_secondary("AI STATUS", ai_status, "🤖")

        render_spacer("xl")

        # ========== LAYOUT : CONSULTATION QUEUE (30%) + RESOURCES (70%) ==========

        col_left, col_right = st.columns([3, 7])

        with col_left:
            # Consultation Queue (style Priorité Automatique IA)
            render_section_header("Consultation Queue", "📋")

            queue = etat.get("queue_consultation", [])
            if queue:
                for i, pid in enumerate(queue[:5], 1):
                    p = patients.get(pid, {})
                    if p:
                        render_queue_item_simple(
                            i, p, st.session_state.state.current_time
                        )
                if len(queue) > 5:
                    st.caption(f"... et {len(queue) - 5} autres patients")
            else:
                st.success("✅ No patients waiting")

        with col_right:
            # Resources (style Flux des Urgences)
            render_section_header("Resources", "👥")

            staff_data = etat.get("staff", [])
            medecins = [s for s in staff_data if s.get("type") == "médecin"]
            inf_mobiles = [
                s for s in staff_data if s.get("type") == "infirmier(ere)_mobile"
            ]
            aides_soignants = [
                s for s in staff_data if s.get("type") == "aide_soignant"
            ]

            consultation_occupee = (
                etat.get("consultation", {}).get("patient_id") is not None
            )

            col1, col2, col3 = st.columns(3)
            with col1:
                render_staff_section_with_tension(
                    "Médecins",
                    "👨‍⚕️",
                    medecins,
                    1,
                    is_medecin=True,
                    consultation_occupee=consultation_occupee,
                )
            with col2:
                render_staff_section_with_tension("Inf. Mobiles", "🏃", inf_mobiles, 2)
            with col3:
                render_staff_section_with_tension(
                    "Aides-Soignants", "🤝", aides_soignants, 2
                )

        render_spacer("xl")

        # ========== OPERATIONS FLOW (SALLES) ==========

        render_section_header("Operations Flow", "🏥")

        salles = etat.get("salles_attente", [])
        for salle in salles:
            render_room_with_risk(salle, patients)

        render_spacer("md")

        # ========== OPERATIONAL TIMELINE ==========

        render_section_header("Operational Timeline", "📋")
        render_operational_timeline(st.session_state.events)

        # ========== PANNEAU LATÉRAL CHATBOT (SI OUVERT) ==========

        # ========== PANNEAU LATÉRAL À DROITE ==========
    if col_panel is not None:
        with col_panel:
            render_chat_panel_minimal(
                chatbot_instance=st.session_state.chatbot,
                chat_history=st.session_state.chat_history,
                on_message_callback=handle_message,
            )


elif st.session_state.current_tab == "chatbot":
    st.empty()
    # ========== ONGLET CHATBOT COMPLET ==========

    st.markdown("## 💬 Chatbot")
    st.caption("Interface complète avec toutes les fonctionnalités")

    render_spacer("md")

    render_chatbot_premium(
        chatbot_available=CHATBOT_AVAILABLE,
        chatbot_instance=st.session_state.get("chatbot"),
        chat_history=st.session_state.chat_history,
        on_message_callback=handle_message,
    )

elif st.session_state.current_tab == "monitoring":
    st.empty()
    # ========== ONGLET MONITORING ==========

    st.markdown("## 📈 Monitoring des Métriques IA")
    st.caption("Suivi en temps réel du coût, de la latence et de l'impact écologique")

    if not MONITORING_AVAILABLE:
        st.error(
            "❌ Module monitoring non disponible. Installez `monitoring/monitoring.py`"
        )
    else:
        render_spacer("md")

        # ========== MÉTRIQUES GLOBALES (CARDS HTML) ==========
        st.markdown("### 📋 Métriques Globales")
        render_spacer("sm")

        col1, col2, col3, col4 = st.columns(4)

        # Card 1 : Coût
        with col1:
            st.markdown(
                f"""
                <div style="
                    background: white;
                    border: 2px solid var(--gray-200);
                    border-left: 5px solid var(--medical-blue);
                    border-radius: var(--radius-lg);
                    padding: 1.5rem;
                    box-shadow: var(--shadow-md);
                ">
                    <div style="
                        font-size: 0.75rem;
                        font-weight: 700;
                        color: var(--text-secondary);
                        margin-bottom: 0.5rem;
                        text-transform: uppercase;
                        letter-spacing: 0.05em;
                    ">
                        💵 COÛT TOTAL
                    </div>
                    <div style="
                        font-size: 2rem;
                        font-weight: 700;
                        color: var(--medical-blue);
                        margin-bottom: 0.25rem;
                    ">
                        ${monitor.total_dollar_cost:.4f}
                    </div>
                    <div style="
                        font-size: 0.7rem;
                        color: var(--text-tertiary);
                    ">
                        Tarifs Mistral AI
                    </div>
                </div>
            """,
                unsafe_allow_html=True,
            )

        # Card 2 : Énergie
        with col2:
            st.markdown(
                f"""
                <div style="
                    background: white;
                    border: 2px solid var(--gray-200);
                    border-left: 5px solid var(--stable-green);
                    border-radius: var(--radius-lg);
                    padding: 1.5rem;
                    box-shadow: var(--shadow-md);
                ">
                    <div style="
                        font-size: 0.75rem;
                        font-weight: 700;
                        color: var(--text-secondary);
                        margin-bottom: 0.5rem;
                        text-transform: uppercase;
                        letter-spacing: 0.05em;
                    ">
                        ⚡ ÉNERGIE
                    </div>
                    <div style="
                        font-size: 2rem;
                        font-weight: 700;
                        color: var(--stable-green);
                        margin-bottom: 0.25rem;
                    ">
                        {monitor.total_energy_kwh:.6f}
                    </div>
                    <div style="
                        font-size: 0.7rem;
                        color: var(--text-tertiary);
                    ">
                        kWh consommés
                    </div>
                </div>
            """,
                unsafe_allow_html=True,
            )

        # Card 3 : CO2
        with col3:
            st.markdown(
                f"""
                <div style="
                    background: white;
                    border: 2px solid var(--gray-200);
                    border-left: 5px solid var(--urgent-orange);
                    border-radius: var(--radius-lg);
                    padding: 1.5rem;
                    box-shadow: var(--shadow-md);
                ">
                    <div style="
                        font-size: 0.75rem;
                        font-weight: 700;
                        color: var(--text-secondary);
                        margin-bottom: 0.5rem;
                        text-transform: uppercase;
                        letter-spacing: 0.05em;
                    ">
                        🌍 EMPREINTE CO2
                    </div>
                    <div style="
                        font-size: 2rem;
                        font-weight: 700;
                        color: var(--urgent-orange);
                        margin-bottom: 0.25rem;
                    ">
                        {monitor.total_co2_kg:.6f}
                    </div>
                    <div style="
                        font-size: 0.7rem;
                        color: var(--text-tertiary);
                    ">
                        kg CO2eq
                    </div>
                </div>
            """,
                unsafe_allow_html=True,
            )

        # Card 4 : Latence
        with col4:
            avg_latency = monitor.get_average_latency()
            st.markdown(
                f"""
                <div style="
                    background: white;
                    border: 2px solid var(--gray-200);
                    border-left: 5px solid var(--critical-red);
                    border-radius: var(--radius-lg);
                    padding: 1.5rem;
                    box-shadow: var(--shadow-md);
                ">
                    <div style="
                        font-size: 0.75rem;
                        font-weight: 700;
                        color: var(--text-secondary);
                        margin-bottom: 0.5rem;
                        text-transform: uppercase;
                        letter-spacing: 0.05em;
                    ">
                        ⏱️ LATENCE MOY
                    </div>
                    <div style="
                        font-size: 2rem;
                        font-weight: 700;
                        color: var(--critical-red);
                        margin-bottom: 0.25rem;
                    ">
                        {avg_latency:.0f}
                    </div>
                    <div style="
                        font-size: 0.7rem;
                        color: var(--text-tertiary);
                    ">
                        ms / requête
                    </div>
                </div>
            """,
                unsafe_allow_html=True,
            )

        st.divider()

        # ========== DÉTAIL PAR COMPOSANT ==========
        st.markdown("### 📊 Détail par Composant")
        render_spacer("sm")

        col_agent, col_chatbot = st.columns(2)

        # Agent
        with col_agent:
            agent_stats = monitor.by_source.get("agent", {})
            agent_count = agent_stats.get("count", 0)

            st.markdown(
                """
                <div style="
                    font-size: 1.1rem;
                    font-weight: 700;
                    color: var(--text-primary);
                    margin-bottom: 0.75rem;
                ">
                    🤖 Agent
                </div>
            """,
                unsafe_allow_html=True,
            )

            st.markdown(
                f"""
                <div style="
                    background: white;
                    border: 2px solid var(--gray-200);
                    border-radius: var(--radius-md);
                    padding: 1rem;
                ">
                    <div style="font-size: 1.5rem; font-weight: 700; color: var(--medical-blue); margin-bottom: 0.5rem;">
                        {agent_count} requêtes
                    </div>
            """,
                unsafe_allow_html=True,
            )

            if agent_count > 0:
                st.caption(f"💵 ${agent_stats.get('cost', 0):.4f}")
                st.caption(f"⚡ {agent_stats.get('energy', 0):.6f} kWh")
                st.caption(f"🌍 {agent_stats.get('co2', 0):.6f} kg CO2")
            else:
                st.caption("Aucune requête")

            st.markdown("</div>", unsafe_allow_html=True)

        # Chatbot
        with col_chatbot:
            chat_stats = monitor.by_source.get("chatbot", {})
            chat_count = chat_stats.get("count", 0)

            st.markdown(
                """
                <div style="
                    font-size: 1.1rem;
                    font-weight: 700;
                    color: var(--text-primary);
                    margin-bottom: 0.75rem;
                ">
                    💬 Chatbot
                </div>
            """,
                unsafe_allow_html=True,
            )

            st.markdown(
                f"""
                <div style="
                    background: white;
                    border: 2px solid var(--gray-200);
                    border-radius: var(--radius-md);
                    padding: 1rem;
                ">
                    <div style="font-size: 1.5rem; font-weight: 700; color: var(--stable-green); margin-bottom: 0.5rem;">
                        {chat_count} requêtes
                    </div>
            """,
                unsafe_allow_html=True,
            )

            if chat_count > 0:
                st.caption(f"💵 ${chat_stats.get('cost', 0):.4f}")
                st.caption(f"⚡ {chat_stats.get('energy', 0):.6f} kWh")
                st.caption(f"🌍 {chat_stats.get('co2', 0):.6f} kg CO2")
            else:
                st.caption("Aucune requête")

            st.markdown("</div>", unsafe_allow_html=True)

        st.divider()

        # ========== HISTORIQUE DES REQUÊTES ==========
        st.markdown("### 📜 Historique des Requêtes")
        render_spacer("sm")

        recent = monitor.get_recent_history(10)
        if recent:
            for req in reversed(recent):
                source_emoji = {"agent": "🤖", "chatbot": "💬"}.get(req.source, "❓")
                time_str = req.timestamp.strftime("%H:%M:%S")

                st.markdown(
                    f"""
                    <div style="
                        background: var(--gray-50);
                        border-left: 3px solid var(--medical-blue);
                        padding: 0.75rem 1rem;
                        margin-bottom: 0.5rem;
                        border-radius: var(--radius-sm);
                        font-size: 0.875rem;
                        color: var(--text-primary);
                    ">
                        <strong>{source_emoji} {req.source.upper()}</strong> | 
                        <code style="background: var(--gray-200); padding: 0.2rem 0.4rem; border-radius: 4px;">{time_str}</code> | 
                        💵 ${req.dollar_cost:.5f} | 
                        ⏱️ {req.latency_ms:.0f}ms | 
                        📝 {req.input_tokens}→{req.output_tokens} tokens
                    </div>
                """,
                    unsafe_allow_html=True,
                )
        else:
            st.info("Aucune requête enregistrée.")

        st.divider()

        # ========== ACTIONS ==========
        col_action1, col_action2 = st.columns(2)

        with col_action1:
            if st.button("🔄 Réinitialiser métriques", use_container_width=True):
                monitor.reset()
                st.success("✅ Métriques réinitialisées")
                time.sleep(0.5)
                st.rerun()

        with col_action2:
            summary = monitor.get_summary()
            st.download_button(
                label="📥 Exporter (JSON)",
                data=str(summary),
                file_name="monitoring_summary.json",
                mime="application/json",
                use_container_width=True,
            )

if (
    st.session_state.running
    and st.session_state.agent_enabled
    and st.session_state.current_tab == "dashboard"
):
    if st.session_state.agent is None:
        st.session_state.agent = EmergencyAgent(
            st.session_state.state, st.session_state.controller
        )
        st.session_state.agent_loaded = True

    st.session_state.temps += 1
    st.session_state.controller.tick(1)
    st.session_state.agent.state = st.session_state.state
    actions = st.session_state.agent.cycle_orchestration()

    # Enregistrer décisions
    if actions:
        decision_record = {
            "timestamp": datetime.now(),
            "actions": actions,
            "raisonnement": f"{len(actions)} action(s) exécutée(s)",
            "temps_simulation": st.session_state.temps,
        }
        st.session_state.decision_history.append(decision_record)

        if len(st.session_state.decision_history) > 50:
            st.session_state.decision_history = st.session_state.decision_history[-50:]

        if st.session_state.get("chatbot"):
            st.session_state.chatbot.set_decision_history(
                st.session_state.decision_history
            )

    for action in actions:
        if action:
            emoji = "🚑" if "transport" in action.lower() else "✅"
            if "📋" in action:
                emoji = "📋"
            add_event(action, emoji)

    time.sleep(st.session_state.agent_speed)
    st.rerun()
