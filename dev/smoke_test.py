# -*- coding: utf-8 -*-
"""End-to-end smoke test: log in, GET every page, and check every asset link.

Usage:  python dev/smoke_test.py
"""

import re
import sys

import bootstrap  # noqa: F401  (env defaults + shims)

from app import app

ADMIN = {"login": "admin", "password": "password"}
GUEST = {"login": "guest", "password": "password"}

ASSET_RE = re.compile(r'(?:src|href)="([^"]+\.(?:js|css|png|gif|jpg|svg))"')

PAGES = [
    "/",
    "/admin/",
    "/admin/centro/",
    "/admin/centro/new/",
    "/admin/medico/",
    "/admin/medico/new/",
    "/admin/paziente/",
    "/admin/paziente/new/",
    "/admin/doc1/",
    "/admin/doc1/new/",
    "/admin/doc2/",
    "/admin/doc2/new/",
    "/admin/doc3/",
    "/admin/doc3/new/",
    "/admin/myfileadmin/",
    "/admin/user/",
    "/admin/logout/",
    "/centri.pdf",
    "/medici.pdf",
    "/pazienti.pdf",
]


def expect(client, path, status, label, failures):
    response = client.get(path)
    ok = response.status_code == status
    print("%-36s -> %s (expected %s)%s"
          % (label, response.status_code, status, "" if ok else "  <-- FAIL"))
    if not ok:
        failures.append((label, response.status_code))
    return response


def check_pages(client, failures):
    bodies = []
    for path in PAGES:
        response = client.get(path)
        is_html = response.headers.get("Content-Type", "").startswith("text/")
        if response.status_code < 400 and is_html:
            bodies.append(response.get_data(as_text=True))
        marker = ""
        if response.status_code >= 400:
            failures.append((path, response.status_code))
            marker = "  <-- FAIL"
        elif response.headers.get("X-Pdf-Backend") == "html-fallback":
            marker = "  (pdf backend missing, html served)"
        print("GET  %-28s -> %s%s" % (path, response.status_code, marker))
    return bodies


def check_assets(client, bodies, failures):
    urls = set()
    for body in bodies:
        urls.update(ASSET_RE.findall(body))

    missing = 0
    for url in sorted(urls):
        response = client.get(url)
        if response.status_code >= 400:
            missing += 1
            failures.append((url, response.status_code))
            print("ASSET %-26s -> %s  <-- FAIL" % (url, response.status_code))
    print("checked %d asset link(s), %d missing" % (len(urls), missing))


def main():
    failures = []
    with app.test_client() as client:
        # Anonymous visitors must be refused, not crash: the 2014 code calls
        # current_user.is_authenticated() everywhere (see compat/shim_login.py).
        expect(client, "/admin/", 403, "GET /admin/ (anonymous)", failures)
        expect(client, "/", 200, "GET /", failures)

        response = client.post("/", data=ADMIN, follow_redirects=False)
        print("%-36s -> %s %s" % ("POST / (login as admin)", response.status_code,
                                  response.headers.get("Location", "")))
        if response.status_code not in (301, 302):
            failures.append(("POST / (admin)", response.status_code))

        bodies = check_pages(client, failures)

        # guest may use the app, but not the admin-only Users screen.
        client.get("/logout/")
        client.post("/", data=GUEST)
        expect(client, "/admin/centro/", 200, "GET /admin/centro/ (guest)", failures)
        expect(client, "/admin/user/", 403, "GET /admin/user/ (guest)", failures)
        bodies.append(client.get("/admin/").get_data(as_text=True))

        check_assets(client, bodies, failures)

    print()
    if failures:
        print("FAILURES:")
        for path, status in failures:
            print("  %s -> %s" % (path, status))
        return 1
    print("all pages returned < 400 and all asset links resolve")
    return 0


if __name__ == "__main__":
    sys.exit(main())
