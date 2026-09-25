# -*- coding: utf-8 -*-
"""Stand-in for Flask-WeasyPrint.

The original app turns questionnaire templates into PDFs with
``render_pdf(HTML(string=html))``.  WeasyPrint itself needs GTK/Pango, which is
not present on a plain Windows box, so this module keeps the same API but
degrades gracefully:

1. real WeasyPrint, if it happens to be importable;
2. xhtml2pdf, if installed (pure Python PDF renderer);
3. otherwise the rendered HTML is returned as-is, so the page still opens.
"""

from flask import Response

__version__ = "0.6"
__all__ = ["HTML", "CSS", "render_pdf"]


class HTML(object):
    def __init__(self, string=None, filename=None, url=None, base_url=None,
                 encoding="utf-8"):
        self.string = string
        self.filename = filename
        self.url = url
        self.base_url = base_url
        self.encoding = encoding

    def render(self):
        if self.string is not None:
            return self.string
        if self.filename is not None:
            with open(self.filename, encoding=self.encoding) as handle:
                return handle.read()
        raise NotImplementedError("remote URLs are not supported by this shim")


class CSS(object):
    def __init__(self, string=None, filename=None, url=None, encoding="utf-8"):
        self.string = string
        self.filename = filename
        self.url = url
        self.encoding = encoding


def _weasyprint_pdf(source):
    try:
        from weasyprint import HTML as WeasyHTML
    except Exception:
        return None
    return WeasyHTML(string=source).write_pdf()


def _xhtml2pdf(source):
    try:
        from xhtml2pdf import pisa
    except Exception:
        return None
    from io import BytesIO
    buffer = BytesIO()
    pisa.CreatePDF(src=source, dest=buffer, encoding="utf-8")
    return buffer.getvalue()


def render_pdf(html, stylesheets=None, download_filename=None, **kwargs):
    source = html.render() if isinstance(html, HTML) else html
    pdf = _weasyprint_pdf(source) or _xhtml2pdf(source)

    if pdf:
        response = Response(pdf, mimetype="application/pdf")
    else:
        # No PDF backend available: show the document instead of a 500.
        response = Response(source, mimetype="text/html")
        response.headers["X-Pdf-Backend"] = "html-fallback"

    if download_filename:
        response.headers["Content-Disposition"] = (
            'attachment; filename="%s"' % download_filename
        )
    return response
