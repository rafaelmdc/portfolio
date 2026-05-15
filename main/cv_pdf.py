"""
CV PDF generation via XeLaTeX + Jinja2.
"""
import os
import re
import subprocess
import tempfile
import mimetypes

import jinja2


_TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "templates")

_env = None


def _get_env():
    global _env
    if _env is None:
        _env = jinja2.Environment(
            variable_start_string="<<",
            variable_end_string=">>",
            block_start_string="<%",
            block_end_string="%>",
            comment_start_string="<#",
            comment_end_string="#>",
            trim_blocks=True,
            lstrip_blocks=True,
            autoescape=False,
            keep_trailing_newline=True,
            loader=jinja2.FileSystemLoader(_TEMPLATE_DIR),
        )
        _env.filters["e"] = _latex_escape
        _env.filters["authors_latex"] = _authors_to_latex
    return _env


def _latex_escape(value):
    if value is None:
        return ""
    s = str(value)
    s = s.replace("\\", r"\textbackslash{}")
    s = s.replace("&",  r"\&")
    s = s.replace("%",  r"\%")
    s = s.replace("$",  r"\$")
    s = s.replace("#",  r"\#")
    s = s.replace("_",  r"\_")
    s = s.replace("{",  r"\{")
    s = s.replace("}",  r"\}")
    s = s.replace("~",  r"\textasciitilde{}")
    s = s.replace("^",  r"\^{}")
    return s


def _authors_to_latex(html):
    """Convert authors_display HTML (<strong>) to LaTeX \textbf{}."""
    if not html:
        return ""
    parts = re.split(r"<strong>(.*?)</strong>", html)
    out = ""
    for i, part in enumerate(parts):
        if i % 2 == 1:
            out += r"\textbf{" + _latex_escape(part) + "}"
        else:
            out += _latex_escape(part)
    return out


def render_cv_pdf(context, profile_image_bytes=None, profile_image_mime=None):
    """
    Render the CV as a PDF and return raw bytes.

    context: dict with CV data (skills, experiences, educations, etc.)
    profile_image_bytes: raw image bytes or None
    profile_image_mime: MIME type string or None
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        # Write profile image to disk so XeLaTeX can include it
        photo_path = ""
        if profile_image_bytes:
            ext = mimetypes.guess_extension(profile_image_mime or "image/jpeg") or ".jpg"
            # guess_extension returns .jpeg on some systems; normalise
            if ext == ".jpeg":
                ext = ".jpg"
            photo_path = os.path.join(tmpdir, f"photo{ext}")
            with open(photo_path, "wb") as fh:
                fh.write(profile_image_bytes)

        ctx = dict(context)
        ctx["profile_image"] = photo_path

        tex = _get_env().get_template("resume.tex.j2").render(**ctx)

        tex_path = os.path.join(tmpdir, "cv.tex")
        with open(tex_path, "w", encoding="utf-8") as fh:
            fh.write(tex)

        cmd = [
            "xelatex",
            "-interaction=nonstopmode",
            "-halt-on-error",
            f"-output-directory={tmpdir}",
            tex_path,
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        # Run twice so \pageref{LastPage} resolves
        if result.returncode == 0:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

        pdf_path = os.path.join(tmpdir, "cv.pdf")
        if not os.path.exists(pdf_path):
            log = result.stdout + "\n" + result.stderr
            raise RuntimeError(f"XeLaTeX failed:\n{log}")

        with open(pdf_path, "rb") as fh:
            return fh.read()
