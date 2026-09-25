# -*- coding: utf-8 -*-
"""Dati per la dashboard iniziale dell'area di amministrazione.

La pagina iniziale di flask-admin era vuota: qui si raccolgono i numeri che
servono a un operatore del servizio (quanti centri, medici e pazienti, quali
pazienti hanno gia' i questionari compilati, quali sono gli ultimi inseriti).
"""

from app.admin.centro.models import Centro
from app.admin.documenti.models import (Modulo_CDP, Questionario_followup,
                                        Questionario_ingresso)
from app.admin.medico.models import Medico
from app.admin.paziente.models import Paziente


def _distinct_pazienti(model):
    """Id dei pazienti referenziati da un documento (senza dereferenziare)."""
    ids = set()
    for ref in model.objects.distinct("paziente"):
        ids.add(getattr(ref, "id", ref))
    return ids


def _percent(part, total):
    return round(100.0 * part / total) if total else 0


def build_context():
    pazienti = list(Paziente.objects)
    centri = list(Centro.objects.order_by("citta"))
    medici = list(Medico.objects.order_by("cognome"))

    # Pazienti per centro (grafico a barre).
    per_centro = []
    for centro in centri:
        per_centro.append(
            {
                "centro": centro,
                "pazienti": Paziente.objects(centro=centro).count(),
            }
        )
    max_centro = max([row["pazienti"] for row in per_centro], default=0)
    for row in per_centro:
        row["percent"] = _percent(row["pazienti"], max_centro)

    # Copertura documentale: quanti pazienti hanno compilato cosa.
    id_ingresso = _distinct_pazienti(Questionario_ingresso)
    id_followup = _distinct_pazienti(Questionario_followup)
    id_modulo = _distinct_pazienti(Modulo_CDP)
    totale_pazienti = len(pazienti)
    copertura = [
        {
            "label": "Questionario di ingresso",
            "fatti": sum(1 for p in pazienti if p.pk in id_ingresso),
            "endpoint": "doc1.index_view",
            "icon": "fa-file-text-o",
        },
        {
            "label": "Questionario di follow-up",
            "fatti": sum(1 for p in pazienti if p.pk in id_followup),
            "endpoint": "doc2.index_view",
            "icon": "fa-repeat",
        },
        {
            "label": "Modulo CDP",
            "fatti": sum(1 for p in pazienti if p.pk in id_modulo),
            "endpoint": "doc3.index_view",
            "icon": "fa-list-alt",
        },
    ]
    for row in copertura:
        row["percent"] = _percent(row["fatti"], totale_pazienti)

    senza_questionario = [
        p for p in pazienti if p.pk not in id_ingresso
    ]

    # Carico per medico (primi 6).
    per_medico = []
    for medico in medici:
        per_medico.append(
            {"medico": medico, "pazienti": Paziente.objects(medico=medico).count()}
        )
    per_medico.sort(key=lambda row: row["pazienti"], reverse=True)

    ultimi_pazienti = sorted(pazienti, key=lambda p: p.pk, reverse=True)[:6]
    ultimi_ingressi = list(Questionario_ingresso.objects.order_by("-id").limit(5))

    return {
        "stats": {
            "centri": len(centri),
            "medici": len(medici),
            "pazienti": totale_pazienti,
            "ingressi": Questionario_ingresso.objects.count(),
            "followup": Questionario_followup.objects.count(),
            "moduli": Modulo_CDP.objects.count(),
            "documenti": (
                Questionario_ingresso.objects.count()
                + Questionario_followup.objects.count()
                + Modulo_CDP.objects.count()
            ),
            "senza_questionario": len(senza_questionario),
        },
        "per_centro": per_centro,
        "per_medico": per_medico[:6],
        "copertura": copertura,
        "ultimi_pazienti": ultimi_pazienti,
        "ultimi_ingressi": ultimi_ingressi,
    }
