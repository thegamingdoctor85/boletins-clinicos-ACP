"""Prepara a atualização do site ACP a partir do JPEG final de um boletim."""

import argparse
from datetime import date
from pathlib import Path
import re
from shutil import copytree

from PIL import Image

MONTHS = (
    "janeiro", "fevereiro", "março", "abril", "maio", "junho",
    "julho", "agosto", "setembro", "outubro", "novembro", "dezembro",
)
FILE = re.compile(r"BC_(\d{4}-\d{2}-\d{2})_Boletim_Clinico_ACP_WhatsApp\.jpg")


def long_date(day):
    return f"{day.day} de {MONTHS[day.month - 1]} de {day.year}"


ARCHIVE = re.compile(r"(<!-- arquivo:inicio -->).*?(<!-- arquivo:fim -->)", re.DOTALL)


def replace_outside_archive(html, before, after):
    region = ARCHIVE.search(html)
    if not region:
        raise ValueError("A página não contém o marcador para o arquivo.")
    start, end = region.span()
    return html[:start].replace(before, after) + html[start:end] + html[end:].replace(before, after)


def render_archive(html, directory, latest):
    entries = []
    for file in directory.iterdir():
        match = FILE.fullmatch(file.name)
        if not match or not file.is_file():
            continue
        day = date.fromisoformat(match[1])
        if day < latest:
            entries.append((day, file.name))
    cards = []
    for day, name in sorted(entries, reverse=True):
        label = long_date(day)
        path = f"boletins/{name}"
        cards.append(f"""          <li>
            <time datetime="{day.isoformat()}">{label}</time>
            <div class="archive-links">
              <a href="{path}" target="_blank" rel="noopener noreferrer" aria-label="Ver boletim de {label}">Ver boletim</a>
              <a href="{path}" download aria-label="Descarregar boletim de {label}">Descarregar JPEG</a>
            </div>
          </li>""")
    content = '<p class="archive-empty">As próximas edições ficam disponíveis aqui.</p>'
    if cards:
        content = '<ul class="archive-list">\n' + "\n".join(cards) + '\n        </ul>'
    updated, count = ARCHIVE.subn(lambda m: f"{m[1]}\n        {content}\n        {m[2]}", html)
    if count != 1:
        raise ValueError("A página deve ter um único arquivo.")
    return updated


def update(site, jpeg, output):
    match = FILE.fullmatch(jpeg.name)
    if not match:
        raise ValueError("Use o JPEG final com a data no nome, no formato BC_AAAA-MM-DD.")
    day = date.fromisoformat(match[1])
    image_bytes = jpeg.read_bytes()
    with Image.open(jpeg) as image:
        if image.format != "JPEG":
            raise ValueError("O boletim deve ser um JPEG.")
        image.load()
        width, height = image.size

    html = (site / "index.html").read_text(encoding="utf-8")
    page = ARCHIVE.sub("", html)
    refs = set(re.findall(r'"boletins/(BC_[^"/]+\.jpg)"', page))
    if len(refs) != 1:
        raise ValueError("O site de partida deve ter uma edição apresentada.")
    current = next(iter(refs))
    previous_match = FILE.fullmatch(current)
    if not previous_match:
        raise ValueError("Não foi possível confirmar a data da edição apresentada.")
    previous_day = date.fromisoformat(previous_match[1])
    if day < previous_day:
        raise ValueError("O novo boletim é anterior à edição apresentada.")
    if not (site / "boletins" / current).is_file():
        raise ValueError("O JPEG da edição apresentada não está na pasta do site.")

    def document_size(match):
        return f'{match[1]} width="{width}" height="{height}"'

    html, count = re.subn(
        rf'(<img src="boletins/{re.escape(current)}") width="\d+" height="\d+"',
        document_size,
        html,
    )
    if count != 1:
        raise ValueError("Não foi possível identificar a imagem principal do boletim.")
    html = replace_outside_archive(html, f"boletins/{current}", f"boletins/{jpeg.name}")
    html = replace_outside_archive(html, f'datetime="{previous_day.isoformat()}"', f'datetime="{day.isoformat()}"')
    html = replace_outside_archive(html, previous_day.strftime("%d/%m/%Y"), day.strftime("%d/%m/%Y"))
    html = replace_outside_archive(html, long_date(previous_day), long_date(day))

    if output.resolve().is_relative_to(site.resolve()):
        raise ValueError("Escolha uma pasta de saída fora da pasta do site.")
    copytree(site, output, ignore=lambda _path, names: {".git", ".openai"}.intersection(names))
    (output / "boletins" / jpeg.name).write_bytes(image_bytes)
    html = render_archive(html, output / "boletins", day)
    (output / "index.html").write_text(html, encoding="utf-8")
    print(f"Site pronto para revisão: {output / 'index.html'}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("site", type=Path, help="Pasta do site atual")
    parser.add_argument("jpeg", type=Path, help="Boletim final")
    parser.add_argument("output", type=Path, help="Nova pasta com o site atualizado")
    options = parser.parse_args()
    update(options.site, options.jpeg, options.output)
