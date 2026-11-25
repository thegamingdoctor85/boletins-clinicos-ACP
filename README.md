# Boletins clínicos ACP

Site público do Departamento Médico do Atlético Clube de Portugal. Apresenta a edição mais recente e o arquivo dos boletins já publicados.

## Atualizar a edição

1. Preparar o JPEG final e confirmar a data e o conteúdo para divulgação.
2. Gerar a página atualizada com `ferramentas/atualizar_site_acp.py` (Python com Pillow). O programa recebe a pasta atual do site, o JPEG e uma pasta de saída nova.
3. Colocar a página e o novo JPEG em `boletins/` no mesmo commit à branch `main`. Conservar os JPEG das edições anteriores para manter o arquivo.
4. Confirmar que o Netlify publicou o commit e que a página abre a edição correta.

O site é estático. O `netlify.toml` indica a raiz do repositório como pasta de publicação e o site não precisa de um comando de compilação. Para pré-visualizar no computador, abrir `index.html` no navegador.

Fotografia do Estádio da Tapadinha por [Hmf Costa](https://commons.wikimedia.org/wiki/File:Estadio-da-tapadinha_001.jpg), [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/). Enquadramento adaptado no site.
