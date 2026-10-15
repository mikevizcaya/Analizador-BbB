from io import BytesIO

import plotly.io as pio
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

from charts import build_chart


def _figure_png(fig, width=1200, height=650):
    fig.update_layout(
        width=width,
        height=height,
        margin=dict(l=45, r=25, t=65, b=35),
    )
    return pio.to_image(
        fig,
        format="png",
        width=width,
        height=height,
        scale=1.35,
        engine="kaleido",
    )


def _draw_chart(c, png_bytes, x, y, max_w, max_h):
    image = ImageReader(BytesIO(png_bytes))
    iw, ih = image.getSize()
    scale = min(max_w / iw, max_h / ih)
    w = iw * scale
    h = ih * scale
    c.drawImage(
        image,
        x + (max_w - w) / 2,
        y + (max_h - h) / 2,
        width=w,
        height=h,
        preserveAspectRatio=True,
        mask="auto",
    )


def create_event_pdf(
    analyzed,
    source_index: int,
    asset_label: str,
    timeframe_seconds: int,
    theme: str = "Blanco",
    mc_period: int = 7,
    mc_projection: int = 0,
):
    """
    Crea PDF carta vertical de 3 páginas:
      1) Todo (ADX estándar) + Antes (ADX estándar)
      2) Inicio (ADX estándar) + Fin (ADX estándar)
      3) Inicio (ADX-MC) + Fin (ADX-MC)

    La tercera página usa únicamente la familia MC en el panel ADX.
    """
    images = {}

    # Páginas 1 y 2: ADX estándar, sin superponer ADX-MC.
    for mode in ["Todo", "Antes", "Inicio", "Fin"]:
        fig = build_chart(
            analyzed=analyzed,
            source_index=source_index,
            mode=mode,
            asset_label=asset_label,
            theme=theme,
            show_adx_standard=True,
            show_adx_mc=False,
            mc_period=mc_period,
            mc_projection=mc_projection,
        )
        try:
            images[(mode, "std")] = _figure_png(fig)
        except Exception as exc:
            raise RuntimeError(
                "No fue posible convertir las gráficas a imagen. "
                "Verifica que Kaleido se haya instalado correctamente."
            ) from exc

    # Página 3: genera Inicio/Fin con ADX-MC visible. Después ocultamos las
    # curvas estándar del panel inferior para que no queden contrapuestas.
    for mode in ["Inicio", "Fin"]:
        fig = build_chart(
            analyzed=analyzed,
            source_index=source_index,
            mode=mode,
            asset_label=asset_label,
            theme=theme,
            show_adx_standard=False,
            show_adx_mc=True,
            mc_period=mc_period,
            mc_projection=mc_projection,
        )
        # En build_chart las trazas estándar se llaman DI+, DI- y ADX IQ-fit.
        # La página MC debe mostrar únicamente DI+ MC, DI- MC y ADX MC.
        for trace in fig.data:
            if getattr(trace, "name", "") in {"DI+", "DI-", "ADX IQ-fit (EMA2)"}:
                trace.visible = False
        fig.update_layout(title=f"{asset_label} — {mode} — ADX-MC")
        images[(mode, "mc")] = _figure_png(fig)

    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    page_w, page_h = letter

    margin_x = 24
    top = 24
    bottom = 22
    header_h = 34
    gap = 8
    usable_w = page_w - (2 * margin_x)
    usable_h = page_h - top - bottom - header_h
    chart_h = (usable_h - gap) / 2

    selected = analyzed.loc[source_index]
    event_time = str(selected.get("datetime_mexico", ""))
    frame_min = max(1, int(timeframe_seconds // 60))

    pages = [
        ("Página 1 - Estándar / Antes", ("Todo", "std"), ("Antes", "std")),
        ("Página 2 - Inicio / Fin - ADX estándar", ("Inicio", "std"), ("Fin", "std")),
        ("Página 3 - Inicio / Fin - ADX-MC", ("Inicio", "mc"), ("Fin", "mc")),
    ]

    for page_title, upper_key, lower_key in pages:
        c.setFont("Helvetica-Bold", 12)
        c.drawString(margin_x, page_h - top, f"Analizador Bar by Bar - {asset_label}")

        c.setFont("Helvetica", 8)
        c.drawRightString(
            page_w - margin_x,
            page_h - top,
            f"{event_time} | {frame_min} min | Fondo {theme}",
        )

        c.setFont("Helvetica-Bold", 9)
        c.drawString(margin_x, page_h - top - 14, page_title)

        _draw_chart(
            c,
            images[upper_key],
            margin_x,
            bottom + chart_h + gap,
            usable_w,
            chart_h,
        )
        _draw_chart(
            c,
            images[lower_key],
            margin_x,
            bottom,
            usable_w,
            chart_h,
        )
        c.showPage()

    c.save()
    buffer.seek(0)
    return buffer.getvalue()
