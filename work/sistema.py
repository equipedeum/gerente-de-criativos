"""O que muda entre Mac e Windows, num lugar só, e as configurações do projeto (projeto.json).

    import sistema
    sistema.FF, sistema.FFPROBE            caminhos do ffmpeg/ffprobe
    sistema.lixeira(caminho)               manda pra Lixeira (nunca apaga de vez)
    sistema.projeto()                      dict do projeto.json (com os padrões)
    sistema.pasta_entrega()                Path da pasta PARA REVISAR
"""
import json
import os
import shutil
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
MAC = sys.platform == 'darwin'
WIN = os.name == 'nt'

PADRAO = {
    'nome_pessoa': '', 'genero_pessoa': 'a', 'marca': '', 'termos_transcricao': '', 'prefixo_codigo': 'CR',
    'pasta_entrega': '~/Desktop/CRIATIVOS/PARA REVISAR', 'cor_destaque': '#059669',
}


def projeto():
    p = RAIZ / 'projeto.json'
    d = dict(PADRAO)
    if p.exists():
        d.update({k: v for k, v in json.loads(p.read_text(encoding='utf-8')).items() if v not in (None, '')})
    return d


def _ffmpeg():
    if os.environ.get('FFMPEG'):
        return os.environ['FFMPEG']
    txt = RAIZ / 'ferramentas/ffmpeg_path.txt'
    if txt.exists():
        c = txt.read_text().strip()
        if c and Path(c).exists():
            return c
    c = shutil.which('ffmpeg')
    if c:
        return c
    raise SystemExit('ffmpeg não encontrado — peça ao Claude: "instala"')


FF = _ffmpeg()
FFPROBE = next((str(Path(FF).with_name(n)) for n in ('ffprobe.exe', 'ffprobe') if Path(FF).with_name(n).exists()),
               shutil.which('ffprobe') or 'ffprobe')


def lixeira(caminho):
    """Manda arquivo ou pasta pra Lixeira (Mac e Windows) — nunca apaga de vez. Devolve True se saiu do lugar.
    Usa o send2trash (requirements.txt); sem ele, cai no jeito nativo do sistema (Finder no Mac, Shell no Windows)."""
    import subprocess
    caminho = Path(caminho).resolve()
    if not caminho.exists():
        return True
    try:
        from send2trash import send2trash
        send2trash(str(caminho))
    except ImportError:
        if MAC:
            alvo = str(caminho).replace('"', '')   # nome com aspas não entra no AppleScript
            subprocess.run(['osascript', '-e', f'tell application "Finder" to delete POSIX file "{alvo}"'],
                           capture_output=True, check=False)
        elif WIN:
            metodo = 'DeleteDirectory' if caminho.is_dir() else 'DeleteFile'
            subprocess.run(['powershell', '-NoProfile', '-Command', 'Add-Type -AssemblyName Microsoft.VisualBasic; '
                            f"[Microsoft.VisualBasic.FileIO.FileSystem]::{metodo}($env:ALVO, 'OnlyErrorDialogs', 'SendToRecycleBin')"],
                           env={**os.environ, 'ALVO': str(caminho)}, capture_output=True, check=False)
        else:
            subprocess.run(['gio', 'trash', str(caminho)], capture_output=True, check=False)
    except OSError as e:
        print(f'Lixeira falhou para {caminho}: {e}')
    return not caminho.exists()


def pasta_entrega():
    return Path(os.path.expanduser(os.environ.get('PASTA_ENTREGA') or projeto()['pasta_entrega']))


def codigo(n):
    return f"#{projeto()['prefixo_codigo']}{n:02d}" if isinstance(n, int) else n
