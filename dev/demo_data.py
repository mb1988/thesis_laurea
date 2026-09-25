# -*- coding: utf-8 -*-
"""Create a small demo dataset through the real admin endpoints.

Everything goes through the same HTTP POSTs a browser would send, so a green
run means the write path (Mongo documents + reference fields) works too.

Usage:  python dev/demo_data.py
"""

import json
import re
from pathlib import Path

import bootstrap  # noqa: F401  (env defaults + shims)

from app import app

ADMIN = {"login": "admin", "password": "password"}

CENTRO = {"citta": "Milano", "provincia": "MI", "indirizzo": "Via Torino 1"}
MEDICO = {"cognome": "Rossi", "nome": "Giulia"}
PAZIENTE = {"cognome": "Bianchi", "nome": "Marco", "nascita": "1980-05-06 00:00:00"}

REPO_ROOT = Path(__file__).resolve().parent.parent

# Sample answers for the free-text fields of each questionnaire.
WINDOW = "Paziente inviato dal SERT di zona."


def build_payload(json_name, extra=None):
    """Answer every field defined in a questionnaire JSON file.

    A browser submits a value for every <select>, and WTForms validates
    selects against the available choices, so a realistic POST needs all of
    them.  Picks are deterministic: first option for selects, "1" for numbers,
    a date for date fields, otherwise sample text.
    """
    with open(REPO_ROOT / json_name, encoding="utf-8") as handle:
        definitions = json.load(handle)

    payload = dict(extra or {})
    for dom in definitions:
        field_type = dom["type"]
        if field_type == "SelectField":
            choices = list(dom["choices"])
            payload[dom["name"]] = choices[0] if choices else ""
        elif field_type == "IntegerField":
            payload[dom["name"]] = "1"
        elif field_type == "DateField":
            payload[dom["name"]] = "2026-09-25"
        elif field_type == "TimeField":
            payload[dom["name"]] = "10:00"
        elif field_type == "BooleanField":
            payload.setdefault(dom["name"], "y")
        else:
            payload.setdefault(dom["name"], WINDOW)
    return payload


def option_values(html, field_name):
    match = re.search(
        r'<select[^>]*name="%s"[^>]*>(.*?)</select>' % re.escape(field_name),
        html,
        re.S,
    )
    if not match:
        return []
    return re.findall(r'<option[^>]*value="([^"]+)"', match.group(1))


def create(client, path, data, label, verbose=True):
    response = client.post(path, data=data, follow_redirects=False)
    ok = response.status_code in (301, 302)
    if verbose:
        print("%-28s -> %s%s" % (label, response.status_code, "" if ok else "  <-- FAILED"))
    if not ok:
        body = response.get_data(as_text=True)
        errors = re.findall(r'<li>(.*?)</li>', body, re.S)
        if verbose:
            for error in errors[:5]:
                print("    error: %s" % " ".join(error.split()))
    return ok


def seed(client, verbose=True):
    """Populate a fresh database through the admin's own forms."""
    failures = 0
    client.post("/", data=ADMIN)

    if not create(client, "/admin/centro/new/", CENTRO, "create centro", verbose):
        failures += 1

    html = client.get("/admin/medico/new/").get_data(as_text=True)
    centro_id = (option_values(html, "centro") or [None])[0]
    if centro_id:
        if not create(
            client, "/admin/medico/new/", dict(MEDICO, centro=centro_id), "create medico", verbose
        ):
            failures += 1

    html = client.get("/admin/paziente/new/").get_data(as_text=True)
    options = {name: (option_values(html, name) or [None])[0]
               for name in ("medico", "centro")}
    if not create(
        client,
        "/admin/paziente/new/",
        dict(PAZIENTE, **{k: v for k, v in options.items() if v}),
        "create paziente",
        verbose,
    ):
        failures += 1

    for path, json_name, label in (
        ("/admin/doc1/new/", "questionario_ingresso.json", "create questionario"),
        ("/admin/doc2/new/", "questionario_followup.json", "create follow-up"),
        ("/admin/doc3/new/", "modulo.json", "create modulo CDP"),
    ):
        html = client.get(path).get_data(as_text=True)
        paziente_id = (option_values(html, "paziente") or [None])[0]
        if not paziente_id:
            continue
        payload = build_payload(json_name, {"paziente": paziente_id})
        if not create(
            client,
            path,
            payload,
            label,
            verbose,
        ):
            failures += 1

    return failures


def main():
    failures = 0
    with app.test_client() as client:
        failures += seed(client, verbose=True)

        for path in (
            "/admin/centro/",
            "/admin/medico/",
            "/admin/paziente/",
            "/admin/doc1/",
            "/admin/doc2/",
            "/admin/doc3/",
            "/centri.pdf",
            "/medici.pdf",
            "/pazienti.pdf",
        ):
            response = client.get(path)
            flag = "" if response.status_code < 400 else "  <-- FAILED"
            if flag:
                failures += 1
            print("%-28s -> %s%s" % ("GET " + path, response.status_code, flag))

        # The document PDF endpoints need a document id from the list page.
        for list_path, pdf_path in (
            ("/admin/doc1/", "questionario_ingresso.pdf"),
            ("/admin/doc2/", "questionario_followup.pdf"),
            ("/admin/doc3/", "modulo_CDP.pdf"),
        ):
            body = client.get(list_path).get_data(as_text=True)
            match = re.search(r"\.pdf\?id=([0-9a-f]+)", body)
            if not match:
                print("note: no PDF link found on %s" % list_path)
                continue
            response = client.get("%s%s?id=%s" % (list_path, pdf_path, match.group(1)))
            flag = "" if response.status_code < 400 else "  <-- FAILED"
            if flag:
                failures += 1
            print("%-28s -> %s%s" % ("GET  " + pdf_path, response.status_code, flag))

    print()
    print("demo data: FAILURES=%d" % failures)
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
