"""
🤖 CHATBOT PREMIUM COMPONENT
=============================
Chatbot IA intégré avec design premium pour le dashboard V2
"""

import streamlit as st
from typing import Optional, Dict, Any, List
from chatbot_styles_v2 import get_chatbot_styles_v2


def render_chatbot_premium(
    chatbot_available: bool, chatbot_instance, chat_history: list, on_message_callback
):
    """
    Rendu du chatbot complet avec nouveau design V2
    """

    # ========== STYLES ==========
    st.markdown(get_chatbot_styles_v2(), unsafe_allow_html=True)

    # ✨ CSS COMPLET pour enlever le fond noir
    st.markdown(
        """
        <style>
        /* Forcer TOUT le container à fond blanc */
        [data-testid="stChatInput"] {
            background-color: transparent !important;
        }
        
        /* Container interne */
        [data-testid="stChatInput"] > div {
            background-color: white !important;
            border: 2px solid #0066CC !important;
            border-radius: 12px !important;
        }
        
        /* Zone de texte */
        [data-testid="stChatInput"] textarea {
            background-color: white !important;
            color: #1f2937 !important;
            border: none !important;
        }
        
        /* Placeholder */
        [data-testid="stChatInput"] textarea::placeholder {
            color: #9ca3af !important;
        }
        
        /* Bouton d'envoi */
        [data-testid="stChatInput"] button {
            background-color: #0066CC !important;
            color: white !important;
        }
        
        /* ✨ CRUCIAL : Enlever le fond noir du parent */
        .stChatInput {
            background-color: transparent !important;
        }
        
        /* Si Streamlit ajoute un container noir */
        [data-testid="stChatInputContainer"] {
            background-color: transparent !important;
        }
        
        /* Forcer le body autour du chat input */
        div:has(> [data-testid="stChatInput"]) {
            background-color: transparent !important;
        }
        </style>
    """,
        unsafe_allow_html=True,
    )

    # ========== CONTAINER PRINCIPAL ==========
    st.markdown('<div class="chatbot-container">', unsafe_allow_html=True)

    # ========== HEADER CARD BLEUE ==========
    st.markdown(
        """
                
        <div class="chatbot-header">
            <div class="chatbot-header-content">
                <div class="chatbot-header-left">
                    <div class="chatbot-icon">💬</div>
                    <div>
                        <div class="chatbot-title">AI Assistant</div>
                        <div class="chatbot-subtitle">Interface complète avec toutes les fonctionnalités</div>
                    </div>
                </div>
                <div class="chatbot-status">
                    <div class="chatbot-status-dot"></div>
                    ONLINE
                </div>
            </div>
        </div>
    """,
        unsafe_allow_html=True,
    )

    # ========== SUMMARY PANEL ==========
    if chatbot_instance:
        try:
            summary = chatbot_instance.get_system_summary()
            st.markdown(
                f"""
                <div class="summary-panel">
                    <div class="summary-text">📊 {summary}</div>
                </div>
            """,
                unsafe_allow_html=True,
            )
        except Exception as e:
            print(f"Erreur summary: {e}")

    # ========== ACTIONS RAPIDES ==========
    st.markdown('<div class="spacer-md"></div>', unsafe_allow_html=True)
    st.markdown("### ⚡ Actions rapides :")

    col2, col3, col4 = st.columns(3)

    # with col1:
    #     if st.button("📊 État système", use_container_width=True, key="action_status"):
    #         on_message_callback("Donne-moi l'état du système")

    with col2:
        if st.button("👥 Liste patients", use_container_width=True, key="action_list"):
            on_message_callback("Liste tous les patients")

    with col3:
        if st.button("➕ Ajouter patient", use_container_width=True, key="action_add"):
            on_message_callback("Ajoute un patient")

    with col4:
        if st.button(
            "🔄 Dernière décision", use_container_width=True, key="action_decision"
        ):
            on_message_callback("Quelle est ta dernière décision ?")

    # ========== HISTORIQUE MESSAGES ==========
    st.markdown('<div class="spacer-lg"></div>', unsafe_allow_html=True)

    if not chat_history:
        st.info(
            "💬 Aucun message pour le moment. Utilisez les actions rapides ou tapez votre question."
        )
    else:
        for idx, msg in enumerate(chat_history):
            role = msg["role"]
            content = msg["content"]

            if role == "user":
                st.markdown(
                    f"""
                    <div class="chatbot-message user">
                        <div class="message-header">👤 VOUS</div>
                        <div class="message-content">{content}</div>
                    </div>
                """,
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f"""
                    <div class="chatbot-message assistant">
                        <div class="message-header">🤖 ASSISTANT IA</div>
                        <div class="message-content">{content}</div>
                    </div>
                """,
                    unsafe_allow_html=True,
                )

                # Metadata badges
                metadata = msg.get("metadata", {})
                actions = metadata.get("actions_executed", [])

                if actions:
                    badges = []
                    for action in actions:
                        tool = action.get("tool", "Action")
                        if action.get("success"):
                            badges.append(
                                f'<span class="metadata-badge success">✅ {tool}</span>'
                            )
                        else:
                            badges.append(
                                f'<span class="metadata-badge error">❌ {tool}</span>'
                            )

                    if badges:
                        st.markdown(
                            f'<div style="margin-top: 0.75rem;">{"".join(badges)}</div>',
                            unsafe_allow_html=True,
                        )

    # ========== ZONE INPUT ==========
    st.markdown('<div class="spacer-lg"></div>', unsafe_allow_html=True)

    # # Input Streamlit
    # ✨ Container blanc forcé
    st.markdown(
        """
        <div style="
            background: white;
            background-color: white;
            padding: 1rem;
            border-radius: 12px;
            margin: -1rem;
        ">
        </div>
    """,
        unsafe_allow_html=True,
    )

    # Input Streamlit
    user_input = st.chat_input("Tapez votre message ici...", key="chatbot_input_main")
    # user_input = st.chat_input(
    #     "Tapez votre message ici...",
    #     key="chatbot_input_main"
    # )

    if user_input:
        on_message_callback(user_input)

    # ========== BOUTON EFFACER ==========
    st.markdown('<div class="spacer-md"></div>', unsafe_allow_html=True)

    if st.button(
        "🗑️ Effacer conversation",
        use_container_width=True,
        type="secondary",
        key="clear_chat_btn",
    ):
        chat_history.clear()
        st.rerun()

    # ========== FIN CONTAINER ==========
    st.markdown("</div>", unsafe_allow_html=True)


def initialize_chatbot(controller, state, decision_history):
    """
    Initialise le chatbot (fonction existante à conserver)
    """
    try:
        from chatbot.chatbot_engine import ChatbotEngine

        print("✅ ChatbotEngine importé")

        chatbot = ChatbotEngine(
            controller=controller, state=state, decision_history_ref=decision_history
        )

        print("✅ ChatbotEngine initialisé")
        return chatbot

    except ImportError as e:
        print(f"❌ Erreur import ChatbotEngine: {e}")
        return None
    except Exception as e:
        print(f"❌ Erreur initialisation ChatbotEngine: {e}")
        return None
