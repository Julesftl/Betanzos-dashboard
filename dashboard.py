import streamlit as st
import json
import os
import anthropic
from pathlib import Path

st.set_page_config(page_title="Betanzos HB — Order Monitor", page_icon="📦", layout="wide")

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
COMMANDES_FILE = "commandes.json"

TRANSLATIONS = {
    "es": {
        "title": "Betanzos HB — Monitor de Pedidos", "listening": "🟢 Escuchando · cada 60s",
        "total": "Pedidos detectados", "sent": "Confirmaciones enviadas",
        "pending": "Pendientes", "languages": "Idiomas detectados",
        "today": "hoy", "auto": "automáticamente",
        "filter_status": "Estado", "filter_lang": "Idioma", "filter_conf": "Confianza",
        "all": "Todos", "all_f": "Todas", "pending_f": "Pendiente", "sent_f": "Enviado",
        "orders": "Pedidos", "product": "producto(s)",
        "client": "Cliente", "delivery": "Entrega", "sender": "Remitente",
        "subject": "Asunto", "language": "Idioma original", "confidence": "Confianza",
        "payment": "Condiciones de pago",
        "products": "Productos", "ref": "Ref", "qty": "Cant", "dim": "Dim",
        "notes": "Notas", "actions": "Acciones",
        "validate": "✅ Validar y enviar", "edit": "✏️ Modo edición", "reject": "❌ Rechazar",
        "already_sent": "✓ Confirmación ya enviada",
        "save": "💾 Guardar cambios", "cancel": "Cancelar edición",
        "saved": "¡Cambios guardados!", "validated": "¡Confirmación enviada!", "rejected": "Pedido rechazado.",
        "footer": "Betanzos HB Order Monitor · Actualice la página para ver nuevos pedidos",
        "badge_sent": "✓ Enviado", "badge_pending": "⏳ Pendiente",
        "na": "N/D", "to_confirm": "A confirmar", "translating": "Traduciendo...",
        "editing": "Modo edición activo — modifique los campos y guarde",
        "exit_edit": "↩️ Salir edición",
    },
    "fr": {
        "title": "Betanzos HB — Suivi Commandes", "listening": "🟢 En écoute · toutes les 60s",
        "total": "Commandes détectées", "sent": "Confirmations envoyées",
        "pending": "En attente", "languages": "Langues détectées",
        "today": "aujourd'hui", "auto": "automatiquement",
        "filter_status": "Statut", "filter_lang": "Langue", "filter_conf": "Confiance",
        "all": "Tous", "all_f": "Toutes", "pending_f": "En attente", "sent_f": "Envoyée",
        "orders": "Commandes", "product": "produit(s)",
        "client": "Client", "delivery": "Livraison", "sender": "Expéditeur",
        "subject": "Sujet", "language": "Langue originale", "confidence": "Confiance",
        "payment": "Conditions de paiement",
        "products": "Produits", "ref": "Réf", "qty": "Qté", "dim": "Dim",
        "notes": "Notes", "actions": "Actions",
        "validate": "✅ Valider et envoyer", "edit": "✏️ Mode édition", "reject": "❌ Rejeter",
        "already_sent": "✓ Confirmation déjà envoyée",
        "save": "💾 Sauvegarder", "cancel": "Annuler",
        "saved": "Modifications sauvegardées!", "validated": "Confirmation envoyée!", "rejected": "Commande rejetée.",
        "footer": "Betanzos HB Order Monitor · Actualisez la page pour voir les nouvelles commandes",
        "badge_sent": "✓ Envoyée", "badge_pending": "⏳ En attente",
        "na": "N/A", "to_confirm": "À confirmer", "translating": "Traduction en cours...",
        "editing": "Mode édition actif — modifiez les champs et sauvegardez",
        "exit_edit": "↩️ Quitter édition",
    },
    "en": {
        "title": "Betanzos HB — Order Monitor", "listening": "🟢 Listening · every 60s",
        "total": "Orders detected", "sent": "Confirmations sent",
        "pending": "Pending", "languages": "Languages detected",
        "today": "today", "auto": "automatically",
        "filter_status": "Status", "filter_lang": "Language", "filter_conf": "Confidence",
        "all": "All", "all_f": "All", "pending_f": "Pending", "sent_f": "Sent",
        "orders": "Orders", "product": "product(s)",
        "client": "Client", "delivery": "Delivery", "sender": "Sender",
        "subject": "Subject", "language": "Original language", "confidence": "Confidence",
        "payment": "Payment terms",
        "products": "Products", "ref": "Ref", "qty": "Qty", "dim": "Dim",
        "notes": "Notes", "actions": "Actions",
        "validate": "✅ Validate & send", "edit": "✏️ Edit mode", "reject": "❌ Reject",
        "already_sent": "✓ Confirmation already sent",
        "save": "💾 Save changes", "cancel": "Cancel",
        "saved": "Changes saved!", "validated": "Confirmation sent!", "rejected": "Order rejected.",
        "footer": "Betanzos HB Order Monitor · Refresh page to see new orders",
        "badge_sent": "✓ Sent", "badge_pending": "⏳ Pending",
        "na": "N/A", "to_confirm": "To confirm", "translating": "Translating...",
        "editing": "Edit mode active — modify fields and save",
        "exit_edit": "↩️ Exit edit",
    }
}

st.markdown("""
<style>
    .badge-high{background:#d4edda;color:#155724;padding:2px 10px;border-radius:12px;font-size:12px;font-weight:500}
    .badge-medium{background:#fff3cd;color:#856404;padding:2px 10px;border-radius:12px;font-size:12px;font-weight:500}
    .badge-low{background:#f8d7da;color:#721c24;padding:2px 10px;border-radius:12px;font-size:12px;font-weight:500}
    .badge-lang{background:#cce5ff;color:#004085;padding:2px 10px;border-radius:12px;font-size:12px}
    .badge-sent{background:#d4edda;color:#155724;padding:2px 10px;border-radius:12px;font-size:12px}
    .badge-pending{background:#fff3cd;color:#856404;padding:2px 10px;border-radius:12px;font-size:12px}
    .info-label{color:#6c757d;font-size:12px;margin-bottom:2px}
    .info-value{font-weight:500;font-size:14px;margin-bottom:12px}
    .produit-box{background:#f8f9fa;border-radius:8px;padding:10px 14px;margin-bottom:8px;font-size:13px;line-height:1.8;border-left:3px solid #dee2e6}
    .section-title{font-size:12px;font-weight:600;color:#495057;margin:14px 0 6px 0;text-transform:uppercase;letter-spacing:0.05em}
    .edit-banner{background:#fff3cd;border-radius:8px;padding:8px 14px;font-size:13px;color:#856404;margin-bottom:12px;border-left:3px solid #ffc107}
</style>
""", unsafe_allow_html=True)


def charger_commandes():
    if Path(COMMANDES_FILE).exists():
        with open(COMMANDES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def sauvegarder_commandes(commandes):
    with open(COMMANDES_FILE, 'w', encoding='utf-8') as f:
        json.dump(commandes, f, ensure_ascii=False, indent=2)

def charger_demo():
    return [
        {
            "id": "demo_001", "timestamp": "2026-06-04 16:24",
            "sujet": "Pedido de venta - BetanzosHB",
            "expediteur_email": "nformoso@betanzoshb.es", "expediteur_nom": "Nuria Formoso",
            "client": "TRASERAS RM S.L.", "langue": "inglés",
            "niveau_confiance": "high", "date_livraison": "02-07-2026",
            "condiciones_pago": "Transferencia 60 días F.F.",
            "produits": [{"description": "Tablero pintado HTP L424 LM", "reference": "BCSB004279", "quantite": "2.800 UNI", "dimensions": "2440x1220x3.0"}],
            "notes": "INCOTERMS: CIP · Transporte: Camión Julio · Nº pedido: 83254996",
            "statut": "envoyee"
        },
        {
            "id": "demo_002", "timestamp": "2026-06-04 16:34",
            "sujet": "RV: Pedido nº:4503169418",
            "expediteur_email": "comercial@betanzoshb.es", "expediteur_nom": "Comercial Betanzos",
            "client": "Fustes Est, S.A.U.", "langue": "español",
            "niveau_confiance": "high", "date_livraison": "A confirmar",
            "condiciones_pago": "60 días fecha factura",
            "produits": [
                {"description": "Tablex Crudo", "reference": "80680000", "quantite": "251 TAB", "dimensions": "2440X1220X2,5"},
                {"description": "Tablex Crudo", "reference": "80617000", "quantite": "200 TAB", "dimensions": "2440X1220X3"}
            ],
            "notes": "Confirmar hora de carga con almacén.",
            "statut": "en_attente"
        },
        {
            "id": "demo_003", "timestamp": "2026-06-04 09:12",
            "sujet": "Purchase order - OPTIMERA",
            "expediteur_email": "erik.lindgren@optimera.se", "expediteur_nom": "Erik Lindgren",
            "client": "Optimera Centrallager Varberg", "langue": "sueco",
            "niveau_confiance": "high", "date_livraison": "2026-06-30",
            "condiciones_pago": "30 días neto",
            "produits": [
                {"description": "Tablero de aceite endurecido LION OIL TEMPERED", "reference": "HCTH200001", "quantite": "2800 ST", "dimensions": "3X1220X2440"},
                {"description": "Certificado FSC MIX CREDIT", "reference": "FSC/901241", "quantite": "1 ST", "dimensions": ""}
            ],
            "notes": "Nº pedido: 9832426 · Ref: MÅRTEN LEIJMAN · Recepción: 07:00-15:00",
            "statut": "envoyee"
        }
    ]


def traduire_commande(commande, langue_cible):
    if not ANTHROPIC_API_KEY:
        return commande
    cache_key = f"tr_{commande['id']}_{langue_cible}"
    if cache_key in st.session_state:
        return st.session_state[cache_key]
    try:
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        prompt = f"""Translate to {langue_cible}. Return ONLY valid JSON with same keys.
DO NOT translate: references, dimensions, codes, numbers, company names, emails.
TRANSLATE: descriptions, notes, payment terms.
{{"notes":"{commande.get('notes','').replace('"',"'")}","condiciones_pago":"{commande.get('condiciones_pago','').replace('"',"'")}","produits_descriptions":{json.dumps([p.get('description','') for p in commande.get('produits',[])])}}}
Reply ONLY with JSON."""
        msg = client.messages.create(model="claude-sonnet-4-5", max_tokens=400, messages=[{"role":"user","content":prompt}])
        texte = msg.content[0].text.strip()
        if texte.startswith("```"):
            texte = texte.split("```")[1]
            if texte.startswith("json"): texte = texte[4:]
        traduit = json.loads(texte.strip())
        c = commande.copy()
        c['notes'] = traduit.get('notes', commande.get('notes',''))
        c['condiciones_pago'] = traduit.get('condiciones_pago', commande.get('condiciones_pago',''))
        prods = []
        for i, p in enumerate(commande.get('produits',[])):
            pt = p.copy()
            descs = traduit.get('produits_descriptions',[])
            if i < len(descs): pt['description'] = descs[i]
            prods.append(pt)
        c['produits'] = prods
        st.session_state[cache_key] = c
        return c
    except:
        return commande


if 'lang' not in st.session_state:
    st.session_state.lang = 'es'

col_title, col_lang, col_status = st.columns([3, 1, 1])
with col_title:
    t = TRANSLATIONS[st.session_state.lang]
    st.markdown(f"## 📦 {t['title']}")
with col_lang:
    st.markdown("<br>", unsafe_allow_html=True)
    lang_choice = st.selectbox("", ["🇪🇸 Español","🇫🇷 Français","🇬🇧 English"], label_visibility="collapsed")
    new_lang = 'es' if "Español" in lang_choice else ('fr' if "Français" in lang_choice else 'en')
    if new_lang != st.session_state.lang:
        st.session_state.lang = new_lang
        st.rerun()
    t = TRANSLATIONS[st.session_state.lang]
with col_status:
    st.markdown("<br>", unsafe_allow_html=True)
    st.success(t['listening'])

st.divider()

commandes_reelles = charger_commandes()
commandes = commandes_reelles if commandes_reelles else charger_demo()

total = len(commandes)
envoyees = len([c for c in commandes if c.get('statut') == 'envoyee'])
en_attente = len([c for c in commandes if c.get('statut') == 'en_attente'])
langues = list(set([c.get('langue','') for c in commandes]))

col1,col2,col3,col4 = st.columns(4)
with col1: st.metric(t['total'], total, delta=t['today'])
with col2: st.metric(t['sent'], envoyees, delta=t['auto'])
with col3: st.metric(t['pending'], en_attente, delta_color="inverse")
with col4: st.metric(t['languages'], len(langues))

st.divider()

col_f1,col_f2,col_f3 = st.columns(3)
with col_f1: filtre_statut = st.selectbox(t['filter_status'], [t['all'],t['pending_f'],t['sent_f']])
with col_f2: filtre_langue = st.selectbox(t['filter_lang'], [t['all_f']]+langues)
with col_f3: filtre_confiance = st.selectbox(t['filter_conf'], [t['all_f'],"HIGH","MEDIUM","LOW"])

commandes_filtrees = commandes[:]
if filtre_statut == t['pending_f']: commandes_filtrees = [c for c in commandes_filtrees if c.get('statut')=='en_attente']
elif filtre_statut == t['sent_f']: commandes_filtrees = [c for c in commandes_filtrees if c.get('statut')=='envoyee']
if filtre_langue != t['all_f']: commandes_filtrees = [c for c in commandes_filtrees if c.get('langue')==filtre_langue]
if filtre_confiance != t['all_f']: commandes_filtrees = [c for c in commandes_filtrees if c.get('niveau_confiance','').upper()==filtre_confiance]

st.markdown(f"### {t['orders']} ({len(commandes_filtrees)})")

for idx, commande in enumerate(commandes_filtrees):
    if st.session_state.lang != 'es':
        with st.spinner(t['translating']):
            ca = traduire_commande(commande, 'français' if st.session_state.lang=='fr' else 'English')
    else:
        ca = commande

    confiance = commande.get('niveau_confiance','high').upper()
    statut = commande.get('statut','en_attente')
    nb_produits = len(commande.get('produits',[]))
    badge_statut = t['badge_sent'] if statut=='envoyee' else t['badge_pending']
    expediteur_affiche = f"{commande.get('expediteur_nom','')} · {commande.get('expediteur_email','')}"
    edit_mode = st.session_state.get(f"edit_{idx}", False)

    with st.expander(f"**{commande.get('client','?')}** · {commande.get('timestamp','')} · {nb_produits} {t['product']}"):
        col_info, col_actions = st.columns([3, 1])

        with col_info:
            st.markdown(
                f'<span class="badge-{confiance.lower()}">{confiance}</span> '
                f'<span class="badge-lang">{commande.get("langue","").capitalize()}</span> '
                f'<span class="badge-{"sent" if statut=="envoyee" else "pending"}">{badge_statut}</span>',
                unsafe_allow_html=True
            )

            if edit_mode:
                st.markdown(f'<div class="edit-banner">✏️ {t["editing"]}</div>', unsafe_allow_html=True)

            st.markdown("")

            # === LIGNE 1 : Client + Livraison ===
            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown(f'<div class="info-label">{t["client"]}</div>', unsafe_allow_html=True)
                if edit_mode:
                    nouveau_client = st.text_input("", value=commande.get('client',''), key=f"c_{idx}", label_visibility="collapsed")
                else:
                    st.markdown(f'<div class="info-value">{ca.get("client",t["na"])}</div>', unsafe_allow_html=True)
            with col_b:
                st.markdown(f'<div class="info-label">{t["delivery"]}</div>', unsafe_allow_html=True)
                if edit_mode:
                    nouvelle_livraison = st.text_input("", value=commande.get('date_livraison',''), key=f"l_{idx}", label_visibility="collapsed")
                else:
                    st.markdown(f'<div class="info-value">{ca.get("date_livraison",t["to_confirm"])}</div>', unsafe_allow_html=True)

            # === LIGNE 2 : Paiement + Expéditeur ===
            col_c, col_d = st.columns(2)
            with col_c:
                st.markdown(f'<div class="info-label">{t["payment"]}</div>', unsafe_allow_html=True)
                if edit_mode:
                    nouveau_paiement = st.text_input("", value=commande.get('condiciones_pago',''), key=f"p_{idx}", label_visibility="collapsed")
                else:
                    st.markdown(f'<div class="info-value">{ca.get("condiciones_pago",t["na"])}</div>', unsafe_allow_html=True)
            with col_d:
                st.markdown(f'<div class="info-label">{t["sender"]}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="info-value">{expediteur_affiche}</div>', unsafe_allow_html=True)

            # === LIGNE 3 : Sujet ===
            st.markdown(f'<div class="info-label">{t["subject"]}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="info-value">{commande.get("sujet",t["na"])}</div>', unsafe_allow_html=True)

            # === PRODUITS ===
            st.markdown(f'<div class="section-title">{t["products"]}</div>', unsafe_allow_html=True)
            produits_modifies = [p.copy() for p in commande.get('produits',[])]
            for pi, p in enumerate(ca.get('produits',[])):
                if edit_mode:
                    col_d2, col_q2, col_dim2 = st.columns([3, 1, 2])
                    with col_d2:
                        produits_modifies[pi]['description'] = st.text_input(
                            f"Desc. {pi+1}", value=commande.get('produits',[])[pi].get('description',''), key=f"d_{idx}_{pi}")
                    with col_q2:
                        produits_modifies[pi]['quantite'] = st.text_input(
                            t['qty'], value=commande.get('produits',[])[pi].get('quantite',''), key=f"q_{idx}_{pi}")
                    with col_dim2:
                        produits_modifies[pi]['dimensions'] = st.text_input(
                            t['dim'], value=commande.get('produits',[])[pi].get('dimensions',''), key=f"dim_{idx}_{pi}")
                else:
                    dims = f" · {t['dim']}: {p.get('dimensions')}" if p.get('dimensions') else ""
                    st.markdown(f"""
                    <div class="produit-box">
                        <strong>{p.get('description',t['na'])}</strong><br>
                        {t['ref']}: {p.get('reference',t['na'])} · {t['qty']}: {p.get('quantite',t['na'])}{dims}
                    </div>
                    """, unsafe_allow_html=True)

            # === NOTES ===
            st.markdown(f'<div class="section-title">{t["notes"]}</div>', unsafe_allow_html=True)
            if edit_mode:
                nouvelles_notes = st.text_area("", value=commande.get('notes',''), key=f"n_{idx}", height=70, label_visibility="collapsed")
            else:
                if ca.get('notes'):
                    st.info(f"📋 {ca.get('notes')}")

            # === SAVE / CANCEL ===
            if edit_mode:
                col_s, col_cc = st.columns(2)
                with col_s:
                    if st.button(t['save'], key=f"s_{idx}", type="primary"):
                        idx_real = commandes.index(commande)
                        commandes[idx_real]['client'] = nouveau_client
                        commandes[idx_real]['date_livraison'] = nouvelle_livraison
                        commandes[idx_real]['condiciones_pago'] = nouveau_paiement
                        commandes[idx_real]['notes'] = nouvelles_notes
                        commandes[idx_real]['produits'] = produits_modifies
                        sauvegarder_commandes(commandes)
                        st.session_state[f"edit_{idx}"] = False
                        st.success(t['saved'])
                        st.rerun()
                with col_cc:
                    if st.button(t['cancel'], key=f"cc_{idx}"):
                        st.session_state[f"edit_{idx}"] = False
                        st.rerun()

        with col_actions:
            st.markdown(f"**{t['actions']}**")
            if statut == 'en_attente':
                if not edit_mode:
                    if st.button(t['validate'], key=f"v_{idx}", type="primary"):
                        idx_real = commandes.index(commande)
                        commandes[idx_real]['statut'] = 'envoyee'
                        sauvegarder_commandes(commandes)
                        st.success(t['validated'])
                        st.rerun()
                if st.button(t['edit'] if not edit_mode else t['exit_edit'], key=f"e_{idx}"):
                    st.session_state[f"edit_{idx}"] = not edit_mode
                    st.rerun()
                if not edit_mode:
                    if st.button(t['reject'], key=f"r_{idx}"):
                        idx_real = commandes.index(commande)
                        commandes[idx_real]['statut'] = 'rejete'
                        sauvegarder_commandes(commandes)
                        st.warning(t['rejected'])
                        st.rerun()
            else:
                st.success(t['already_sent'])
                st.markdown(f"*{commande.get('timestamp','')}*")

st.divider()
st.markdown(f"<p style='text-align:center;color:gray;font-size:12px;'>{t['footer']}</p>", unsafe_allow_html=True)
