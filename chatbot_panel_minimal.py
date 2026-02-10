"""
🤖 CHATBOT PANEL MINIMAL - VERSION AVEC BORDURE BLEUE
======================================================
Panneau latéral avec bordure arrondie bleue comme Hero Zone
"""

import streamlit as st
from typing import Optional, Any, List, Dict, Callable


def render_chat_panel_minimal(
    chatbot_instance: Optional[Any],
    chat_history: List[Dict],
    on_message_callback: Callable,
) -> None:
    """
    Affiche le panneau latéral chatbot avec bordure bleue arrondie.

    ✨ VERSION AVEC BORDURE :
    - Bordure bleue épaisse (3px) arrondie
    - Fond blanc
    - Ombre portée
    - Style cohérent avec Hero Zone
    """

    # ========== CONTAINER AVEC BORDURE BLEUE ==========
    # st.markdown("""
    #     <div style="
    #         background: white;
    #         border: 3px solid var(--medical-blue);
    #         border-radius: 16px;
    #         padding: 0;
    #         box-shadow: 0 10px 25px rgba(0, 102, 204, 0.15);
    #         overflow: hidden;
    #         height: calc(100vh - 120px);
    #         display: flex;
    #         flex-direction: column;
    #     ">
    # """, unsafe_allow_html=True)

    # ========== HEADER DU PANNEAU ==========
    st.markdown(
        """
        <div style="
            background: linear-gradient(135deg, var(--medical-blue) 0%, var(--medical-blue-dark) 100%);
            color: white;
            padding: 1.5rem;
            margin: 0;
        ">
            <div style="
                display: flex;
                align-items: center;
                gap: 12px;
                margin-bottom: 0.5rem;
            ">
                <span style="font-size: 1.5rem;">🤖</span>
                <span style="
                    font-family: var(--font-heading);
                    font-size: 1.25rem;
                    font-weight: 700;
                ">
                    Assistant IA Médical
                </span>
            </div>
            <div style="
                font-size: 0.875rem;
                opacity: 0.9;
                font-weight: 500;
            ">
                Powered by RAG Medical Knowledge
            </div>
        </div>
    """,
        unsafe_allow_html=True,
    )

    # ========== RÉSUMÉ SYSTÈME ==========
    st.markdown('<div style="padding: 1rem;">', unsafe_allow_html=True)

    if chatbot_instance:
        try:
            summary = chatbot_instance.get_system_summary()
            st.markdown(
                f"""
                <div style="
                    background: var(--medical-blue-light);
                    border: 2px solid var(--medical-blue);
                    border-left: 5px solid var(--medical-blue);
                    border-radius: var(--radius-md);
                    padding: 0.75rem 1rem;
                    margin-bottom: 1rem;
                    font-size: 0.875rem;
                    color: var(--text-primary);
                    font-weight: 600;
                ">
                    📊 {summary}
                </div>
            """,
                unsafe_allow_html=True,
            )
        except:
            pass

    st.markdown("</div>", unsafe_allow_html=True)

    # ========== CORPS DU PANNEAU (MESSAGES) ==========
    st.markdown(
        """
        <div style="
            flex: 1;
            overflow-y: auto;
            padding: 0 1rem 1rem 1rem;
        ">
    """,
        unsafe_allow_html=True,
    )

    # Message d'accueil si vide
    if not chat_history:
        st.markdown(
            """
            <div style="
                text-align: center;
                padding: 2rem 1rem;
                color: var(--text-tertiary);
            ">
                <div style="font-size: 2.5rem; margin-bottom: 1rem;">💬</div>
                <div style="
                    font-size: 1rem;
                    font-weight: 600;
                    color: var(--text-primary);
                    margin-bottom: 0.5rem;
                ">
                    Bonjour ! Je peux vous aider
                </div>
                <div style="font-size: 0.8rem; color: var(--text-secondary); line-height: 1.4;">
                    Posez-moi des questions sur les protocoles médicaux,
                    l'analyse des symptômes et les recommandations de triage.
                </div>
            </div>
        """,
            unsafe_allow_html=True,
        )

    else:
        # Afficher les messages
        for idx, msg in enumerate(chat_history):
            role = msg["role"]
            content = msg["content"]

            # Message utilisateur
            if role == "user":
                st.markdown(
                    f"""
                    <div style="
                        background: var(--medical-blue-light);
                        color: var(--text-primary);
                        padding: 0.75rem 1rem;
                        border-radius: var(--radius-md);
                        margin-bottom: 0.75rem;
                        margin-left: 1.5rem;
                        border-left: 3px solid var(--medical-blue);
                        animation: fadeIn 0.3s ease;
                        font-size: 0.875rem;
                    ">
                        <div style="
                            font-weight: 700;
                            font-size: 0.65rem;
                            letter-spacing: 0.05em;
                            text-transform: uppercase;
                            color: var(--text-secondary);
                            margin-bottom: 0.5rem;
                        ">
                            👤 VOUS
                        </div>
                        <div style="line-height: 1.5;">
                            {content}
                        </div>
                    </div>
                """,
                    unsafe_allow_html=True,
                )

            # Message assistant
            else:
                st.markdown(
                    f"""
                    <div style="
                        background: var(--gray-100);
                        color: var(--text-primary);
                        padding: 0.75rem 1rem;
                        border-radius: var(--radius-md);
                        margin-bottom: 0.75rem;
                        margin-right: 1.5rem;
                        border-left: 4px solid var(--stable-green);
                        animation: fadeIn 0.3s ease;
                        font-size: 0.875rem;
                    ">
                        <div style="
                            font-weight: 700;
                            font-size: 0.65rem;
                            letter-spacing: 0.05em;
                            text-transform: uppercase;
                            color: var(--text-secondary);
                            margin-bottom: 0.5rem;
                        ">
                            🤖 ASSISTANT IA
                        </div>
                        <div style="line-height: 1.5;">
                            {content}
                        </div>
                    </div>
                """,
                    unsafe_allow_html=True,
                )

                # Métadonnées (badges actions)
                metadata = msg.get("metadata", {})
                actions_executed = metadata.get("actions_executed", [])

                if actions_executed:
                    badges_html = '<div style="display: flex; flex-wrap: wrap; gap: 0.4rem; margin-top: 0.5rem; margin-right: 1.5rem;">'
                    for action in actions_executed:
                        if action.get("success"):
                            badge_bg = "var(--stable-green-light)"
                            badge_color = "var(--stable-green)"
                            badge_border = "var(--stable-green)"
                            icon = "✅"
                        else:
                            badge_bg = "var(--critical-red-light)"
                            badge_color = "var(--critical-red)"
                            badge_border = "var(--critical-red)"
                            icon = "❌"

                        tool_name = action.get("tool", "Action")
                        badges_html += f"""
                            <span style="
                                display: inline-block;
                                padding: 0.2rem 0.5rem;
                                background: {badge_bg};
                                color: {badge_color};
                                border: 1px solid {badge_border};
                                border-radius: 6px;
                                font-size: 0.65rem;
                                font-weight: 600;
                                font-family: var(--font-mono);
                            ">
                                {icon} {tool_name}
                            </span>
                        """
                    badges_html += "</div>"
                    st.markdown(badges_html, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # ========== ZONE INPUT (EN BAS FIXE) ==========
    st.markdown(
        """
                
        <div style="
            background: var(--gray-50);
            border-top: 2px solid var(--gray-200);
            padding: 1rem;
            margin: 0;
        ">
        </div>
    """,
        unsafe_allow_html=True,
    )

    user_input = st.chat_input("💬 Posez votre question...", key="chat_panel_input_v3")

    if user_input:
        on_message_callback(user_input)

    # Fermer le container principal
    st.markdown("</div>", unsafe_allow_html=True)


def render_chat_panel_toggle_button() -> bool:
    """
    Affiche le bouton pour ouvrir/fermer le panneau latéral.
    """
    if "show_chat_panel" not in st.session_state:
        st.session_state.show_chat_panel = False

    if st.button(
        (
            "🤖 Ouvrir Assistant"
            if not st.session_state.show_chat_panel
            else "❌ Fermer Assistant"
        ),
        use_container_width=True,
        type="secondary",
        key="toggle_chat_panel_v3",
    ):
        st.session_state.show_chat_panel = not st.session_state.show_chat_panel
        st.rerun()

    return st.session_state.show_chat_panel


# """
# 🤖 CHATBOT PANEL MINIMAL - VERSION CORRIGÉE V3
# ===============================================
# Panneau latéral épuré pour assistant IA dans l'onglet Dashboard
# ✨ FIXED : Utilise les styles CSS de premium_styles_v3_FIXED.py
# """

# import streamlit as st
# from typing import Optional, Any, List, Dict, Callable


# def render_chat_panel_minimal(
#     chatbot_instance: Optional[Any],
#     chat_history: List[Dict],
#     on_message_callback: Callable
# ) -> None:
#     """
#     Affiche le panneau latéral chatbot minimaliste.

#     ✨ VERSION CORRIGÉE :
#     - Utilise les classes CSS existantes dans V3
#     - Fond blanc (pas bleu vide)
#     - Header avec dégradé bleu
#     - Messages stylés comme V2

#     Args:
#         chatbot_instance: Instance ChatbotEngine (vérifié avant appel)
#         chat_history: Historique messages
#         on_message_callback: Fonction appelée lors nouveau message
#     """

#     # ========== HEADER DU PANNEAU ==========
#     st.markdown("""
#         <div style="
#             background: linear-gradient(135deg, rgba(0, 102, 204, 0.95) 0%, rgba(0, 76, 153, 0.95) 100%);
#             color: white;
#             padding: 1.5rem;
#             border-radius: 12px 12px 0 0;
#             margin-bottom: 1rem;
#             box-shadow: 0 4px 12px rgba(0, 102, 204, 0.2);
#         ">
#             <div style="
#                 display: flex;
#                 align-items: center;
#                 gap: 12px;
#                 margin-bottom: 0.5rem;
#             ">
#                 <span style="font-size: 1.5rem;">🤖</span>
#                 <span style="
#                     font-family: var(--font-heading);
#                     font-size: 1.25rem;
#                     font-weight: 700;
#                 ">
#                     Assistant IA Médical
#                 </span>
#             </div>
#             <div style="
#                 font-size: 0.875rem;
#                 opacity: 0.9;
#                 font-weight: 500;
#             ">
#                 Powered by RAG Medical Knowledge
#             </div>
#         </div>
#     """, unsafe_allow_html=True)

#     # ========== RÉSUMÉ SYSTÈME ==========
#     if chatbot_instance:
#         try:
#             summary = chatbot_instance.get_system_summary()
#             st.markdown(f"""
#                 <div style="
#                     background: var(--medical-blue-light);
#                     border: 2px solid var(--medical-blue);
#                     border-left: 5px solid var(--medical-blue);
#                     border-radius: var(--radius-md);
#                     padding: 0.75rem 1rem;
#                     margin-bottom: 1rem;
#                     font-size: 0.875rem;
#                     color: var(--text-primary);
#                     font-weight: 600;
#                 ">
#                     📊 {summary}
#                 </div>
#             """, unsafe_allow_html=True)
#         except:
#             pass

#     # ========== CORPS DU PANNEAU (MESSAGES) ==========
#     st.markdown('<div style="padding: 0 0.5rem; margin-bottom: 1rem;">', unsafe_allow_html=True)

#     # Message d'accueil si vide
#     if not chat_history:
#         st.markdown("""
#             <div style="
#                 text-align: center;
#                 padding: 3rem 1rem;
#                 color: var(--text-tertiary);
#             ">
#                 <div style="font-size: 3rem; margin-bottom: 1rem;">💬</div>
#                 <div style="
#                     font-size: 1.125rem;
#                     font-weight: 600;
#                     color: var(--text-primary);
#                     margin-bottom: 0.5rem;
#                 ">
#                     Bonjour ! Je peux vous aider
#                 </div>
#                 <div style="font-size: 0.875rem; color: var(--text-secondary);">
#                     Posez-moi des questions sur les protocoles médicaux,<br>
#                     l'analyse des symptômes et les recommandations de triage.
#                 </div>
#             </div>
#         """, unsafe_allow_html=True)

#     else:
#         # Afficher les messages
#         for idx, msg in enumerate(chat_history):
#             role = msg["role"]
#             content = msg["content"]

#             # Message utilisateur
#             if role == "user":
#                 st.markdown(f"""
#                     <div style="
#                         background: var(--medical-blue-light);
#                         color: var(--text-primary);
#                         padding: 0.875rem 1rem;
#                         border-radius: var(--radius-md);
#                         margin-bottom: 0.75rem;
#                         margin-left: 2rem;
#                         border-left: 3px solid var(--medical-blue);
#                         animation: fadeIn 0.3s ease;
#                     ">
#                         <div style="
#                             font-weight: 700;
#                             font-size: 0.7rem;
#                             letter-spacing: 0.05em;
#                             text-transform: uppercase;
#                             color: var(--text-secondary);
#                             margin-bottom: 0.5rem;
#                         ">
#                             👤 VOUS
#                         </div>
#                         <div style="line-height: 1.5;">
#                             {content}
#                         </div>
#                     </div>
#                 """, unsafe_allow_html=True)

#             # Message assistant
#             else:
#                 st.markdown(f"""
#                     <div style="
#                         background: var(--gray-100);
#                         color: var(--text-primary);
#                         padding: 0.875rem 1rem;
#                         border-radius: var(--radius-md);
#                         margin-bottom: 0.75rem;
#                         margin-right: 2rem;
#                         border-left: 4px solid var(--stable-green);
#                         animation: fadeIn 0.3s ease;
#                     ">
#                         <div style="
#                             font-weight: 700;
#                             font-size: 0.7rem;
#                             letter-spacing: 0.05em;
#                             text-transform: uppercase;
#                             color: var(--text-secondary);
#                             margin-bottom: 0.5rem;
#                         ">
#                             🤖 ASSISTANT IA
#                         </div>
#                         <div style="line-height: 1.5;">
#                             {content}
#                         </div>
#                     </div>
#                 """, unsafe_allow_html=True)

#                 # Métadonnées (badges actions)
#                 metadata = msg.get("metadata", {})
#                 actions_executed = metadata.get("actions_executed", [])

#                 if actions_executed:
#                     badges_html = '<div style="display: flex; flex-wrap: wrap; gap: 0.5rem; margin-top: 0.5rem; padding-left: 0.5rem;">'
#                     for action in actions_executed:
#                         if action.get("success"):
#                             badge_bg = "var(--stable-green-light)"
#                             badge_color = "var(--stable-green)"
#                             badge_border = "var(--stable-green)"
#                             icon = "✅"
#                         else:
#                             badge_bg = "var(--critical-red-light)"
#                             badge_color = "var(--critical-red)"
#                             badge_border = "var(--critical-red)"
#                             icon = "❌"

#                         tool_name = action.get("tool", "Action")
#                         badges_html += f'''
#                             <span style="
#                                 display: inline-block;
#                                 padding: 0.25rem 0.625rem;
#                                 background: {badge_bg};
#                                 color: {badge_color};
#                                 border: 1px solid {badge_border};
#                                 border-radius: 6px;
#                                 font-size: 0.7rem;
#                                 font-weight: 600;
#                                 font-family: var(--font-mono);
#                             ">
#                                 {icon} {tool_name}
#                             </span>
#                         '''
#                     badges_html += '</div>'
#                     st.markdown(badges_html, unsafe_allow_html=True)

#                 # Latence (très discret)
#                 latency_ms = metadata.get("latency_ms")
#                 if latency_ms:
#                     st.markdown(f'''
#                         <div style="
#                             margin-top: 0.5rem;
#                             padding-left: 0.5rem;
#                             font-size: 0.7rem;
#                             color: var(--text-tertiary);
#                             opacity: 0.6;
#                             font-family: var(--font-mono);
#                         ">
#                             ⚡ {latency_ms:.0f}ms
#                         </div>
#                     ''', unsafe_allow_html=True)

#     st.markdown('</div>', unsafe_allow_html=True)

#     # ========== ZONE INPUT (EN BAS) ==========
#     st.markdown("""
#         <div style="
#             background: var(--gray-50);
#             border-top: 2px solid var(--gray-200);
#             padding: 1rem;
#             border-radius: 0 0 12px 12px;
#         ">
#         </div>
#     """, unsafe_allow_html=True)

#     user_input = st.chat_input(
#         "💬 Posez votre question ou donnez une commande...",
#         key="chat_panel_input_minimal"
#     )

#     if user_input:
#         on_message_callback(user_input)


# def render_chat_panel_toggle_button() -> bool:
#     """
#     Affiche le bouton pour ouvrir/fermer le panneau latéral.

#     Returns:
#         True si le panneau doit s'afficher
#     """
#     if 'show_chat_panel' not in st.session_state:
#         st.session_state.show_chat_panel = False

#     # Bouton dans la sidebar
#     if st.button(
#         "🤖 Ouvrir Assistant" if not st.session_state.show_chat_panel else "❌ Fermer Assistant",
#         use_container_width=True,
#         type="secondary",
#         key="toggle_chat_panel_btn"
#     ):
#         st.session_state.show_chat_panel = not st.session_state.show_chat_panel
#         st.rerun()

#     return st.session_state.show_chat_panel
