"""Confere a instalação do Gerente de Criativos (Mac ou Windows) e, com --teste, faz um vídeo curto de ponta a ponta.

    python3 work/pipeline/conferir_instalacao.py            # só confere e lista o que falta (roda até sem o venv)
    ./py work/pipeline/conferir_instalacao.py --teste       # + teste: voz sintética -> transcrição -> básico RL de ~6 s

Só usa a biblioteca padrão na conferência (dá pra rodar com o Python do sistema antes de criar o venv).
Não instala nada: diz o que falta e o comando de cada coisa. Quem instala é a skill `instalar` (com o OK do usuário).
"""
import importlib
import json
import os
import platform
import re
import shutil
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
MAC, WIN = sys.platform == 'darwin', os.name == 'nt'
FALTA = []


def ok(item, txt):
    print(f'  [ok] {item}: {txt}')


def falta(item, txt, comando=''):
    print(f'  [FALTA] {item}: {txt}' + (f'\n          -> {comando}' if comando else ''))
    FALTA.append(item)


def rodar(cmd, **kw):
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=kw.pop('timeout', 120), **kw)
    except (OSError, subprocess.TimeoutExpired) as e:
        return subprocess.CompletedProcess(cmd, 1, '', str(e))


def venv_python():
    for p in (RAIZ / 'ferramentas' / 'venv' / 'bin' / 'python', RAIZ / 'ferramentas' / 'venv' / 'Scripts' / 'python.exe'):
        if p.exists():
            return p
    return None


def conferir():
    print(f'Sistema: {platform.system()} {platform.release()} ({platform.machine()}) — Python atual {sys.version.split()[0]}')
    print('Ferramentas do sistema:')
    if MAC:
        if shutil.which('brew'):
            ok('Homebrew', rodar(['brew', '--version']).stdout.split('\n')[0])
        else:
            falta('Homebrew', 'não instalado (é o instalador de programas do Mac)',
                  '/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"')
    # Python 3.12 (as versões fixadas no requirements.txt têm pacote pronto pra ele no Mac e no Windows)
    py312 = shutil.which('python3.12') or (shutil.which('py') and 'py -3.12')
    if py312 or sys.version_info[:2] == (3, 12):
        ok('Python 3.12', py312 or sys.executable)
    else:
        falta('Python 3.12', 'não achei', 'brew install python@3.12' if MAC else 'winget install Python.Python.3.12')
    ff = shutil.which('ffmpeg')
    if ff:
        v = rodar([ff, '-hide_banner', '-version']).stdout.split('\n')[0]
        filtros = rodar([ff, '-hide_banner', '-filters']).stdout
        ok('ffmpeg', v[:60] + (' (com zscale: converte vídeo HDR do iPhone)' if ' zscale ' in filtros else
                               ' — SEM zscale: vídeo HDR do iPhone pode sair com a cor lavada'))
        if not shutil.which('ffprobe'):
            falta('ffprobe', 'não está no PATH (vem junto com o ffmpeg)')
    else:
        falta('ffmpeg', 'não instalado', 'brew install ffmpeg' if MAC else 'winget install Gyan.FFmpeg')
    node = shutil.which('node')
    if node:
        v = rodar([node, '--version']).stdout.strip()
        maior = int(re.sub(r'\D', '', v.split('.')[0]) or 0)
        (ok if maior >= 20 else falta)('Node.js', v + ('' if maior >= 20 else ' (precisa 20 ou mais)'),
                                       *(['brew install node' if MAC else 'winget install OpenJS.NodeJS.LTS'] if maior < 20 else []))
    else:
        falta('Node.js', 'não instalado', 'brew install node' if MAC else 'winget install OpenJS.NodeJS.LTS')
    if not shutil.which('git'):
        falta('git', 'não instalado', 'brew install git' if MAC else 'winget install Git.Git')
    else:
        ok('git', rodar(['git', '--version']).stdout.strip())
    if MAC and not Path('/Applications/Google Chrome.app').exists():
        print('  [aviso] Google Chrome não está em /Applications — o HyperFrames baixa o Chrome dele; se o doctor reclamar: brew install --cask google-chrome')

    print('Projeto:')
    vp = venv_python()
    if not vp:
        falta('venv', 'ferramentas/venv não existe',
              ('python3.12' if MAC else 'py -3.12') + ' -m venv ferramentas/venv && ./py -m pip install -r requirements.txt')
    else:
        ok('venv', str(vp.relative_to(RAIZ)))
        reqs = [l.strip() for l in (RAIZ / 'requirements.txt').read_text().splitlines() if l.strip() and not l.startswith('#')]
        freeze = rodar([str(vp), '-m', 'pip', 'freeze']).stdout.lower()
        instalados = dict(l.split('==', 1) for l in freeze.splitlines() if '==' in l)
        for r in reqs:
            nome, ver = r.split('==')
            tem = instalados.get(nome.lower()) or instalados.get(nome.lower().replace('-', '_'))
            if tem == ver.lower():
                ok(nome, ver)
            elif tem:
                print(f'  [aviso] {nome}: {tem} instalado, {ver} pedido (normalmente funciona; o testado é o {ver})')
            else:
                falta(nome, f'não instalado ({ver})', './py -m pip install -r requirements.txt')
    m = RAIZ / 'models'
    if m.exists() and any(m.rglob('model.bin')):
        ok('modelo de transcrição', 'faster-whisper small em models/')
    else:
        falta('modelo de transcrição', 'faster-whisper small (~480 MB) não baixado',
              './py -c "from faster_whisper import WhisperModel; WhisperModel(\'small\', device=\'cpu\', compute_type=\'int8\', download_root=\'models\')"')
    if (RAIZ / 'remotion/node_modules/remotion').exists():
        ok('Remotion', 'remotion/node_modules')
    else:
        falta('Remotion', 'pacotes do Node não instalados', 'cd remotion && npm ci')
    fontes = ['Inter-Bold.ttf', 'Montserrat-Light.ttf', 'TikTokSans-Variable.ttf', 'EBGaramond-400.woff2']
    sem = [f for f in fontes if not (RAIZ / 'ferramentas/fontes' / f).exists()]
    (falta('fontes', 'faltando: ' + ', '.join(sem)) if sem else ok('fontes', 'ferramentas/fontes (OFL)'))
    if MAC and Path('/System/Library/Fonts/Apple Color Emoji.ttc').exists():
        ok('emoji do título', 'Apple Color Emoji do sistema')
    elif (RAIZ / 'ferramentas/emoji').exists():
        ok('emoji do título', 'PNGs em ferramentas/emoji')
    elif WIN and Path('C:/Windows/Fonts/seguiemj.ttf').exists():
        ok('emoji do título', 'Segoe UI Emoji do Windows')
    else:
        print('  [aviso] emoji do título: sem fonte de emoji colorida — título sai sem emoji')
    pj = json.loads((RAIZ / 'projeto.json').read_text(encoding='utf-8'))
    if not pj.get('nome_pessoa'):
        print('  [aviso] projeto.json: nome_pessoa vazio (perguntar ao usuário quem aparece nos vídeos)')
    hf = rodar(['npx', '-y', 'hyperframes@0.8.76', 'doctor'], timeout=300, shell=WIN,
               env={**os.environ, 'DO_NOT_TRACK': '1', 'HYPERFRAMES_NO_TELEMETRY': '1'}) if shutil.which('npx') else None
    if hf is not None:
        txt = re.sub(r'\x1b\[[0-9;]*m', '', hf.stdout + hf.stderr)
        print('  hyperframes doctor:\n' + '\n'.join('    ' + l for l in txt.strip().splitlines()[-14:]))
    print()
    print('TUDO CERTO' if not FALTA else 'FALTA: ' + ', '.join(FALTA))
    return not FALTA


def teste():
    """Voz sintética (say no Mac / SAPI no Windows) + vídeo de cor -> preparar.py -> básico RL -> confere o MP4."""
    import tempfile
    print('\nTeste de ponta a ponta (vídeo de demonstração, ~1–3 min):')
    tmp = Path(tempfile.mkdtemp(prefix='gerente-teste-'))
    frase = 'Este é um teste do Gerente de Criativos. Se você está ouvindo, está tudo funcionando.'
    voz = tmp / 'voz.wav'
    if MAC:
        aiff = tmp / 'voz.aiff'
        r = rodar(['say', '-v', 'Luciana', '-o', str(aiff), frase])
        if r.returncode:
            r = rodar(['say', '-o', str(aiff), frase])
        rodar(['ffmpeg', '-v', 'error', '-y', '-i', str(aiff), '-ar', '48000', '-ac', '1', str(voz)])
    elif WIN:
        ps = ("Add-Type -AssemblyName System.Speech; $s=New-Object System.Speech.Synthesis.SpeechSynthesizer; "
              "try{$s.SelectVoice('Microsoft Maria Desktop')}catch{}; $s.SetOutputToWaveFile($env:SAIDA); $s.Speak($env:FRASE); $s.Dispose()")
        rodar(['powershell', '-NoProfile', '-Command', ps], env={**os.environ, 'SAIDA': str(voz), 'FRASE': frase})
    if not voz.exists():
        print('  [FALTA] não consegui gerar a voz de teste neste sistema')
        return False
    video = tmp / 'teste.mp4'
    rodar(['ffmpeg', '-v', 'error', '-y', '-f', 'lavfi', '-i', 'testsrc2=size=1080x1920:rate=30', '-i', str(voz),
           '-shortest', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-c:a', 'aac', str(video)])
    py = [str(RAIZ / 'py')] if not WIN else ['bash', str(RAIZ / 'py')]
    r = rodar(py + ['work/pipeline/preparar.py', 'teste-instalacao', str(video), '--sem-corte'], cwd=RAIZ, timeout=900)
    print('  preparar.py:', (r.stdout.strip().splitlines() or [r.stderr[-300:]])[-2:])
    palavras = RAIZ / 'work/teste-instalacao/words_cut.json'
    if r.returncode or not palavras.exists() or not json.loads(palavras.read_text(encoding='utf-8')):
        print('  [FALHOU] preparo/transcrição:', r.stderr[-500:])
        return False
    W = json.loads(palavras.read_text(encoding='utf-8'))
    blocos, atual = [], []
    for w in W:
        atual.append(w['w'])
        if len(atual) == 3 or w['w'][-1:] in '.,':
            blocos.append(' '.join(atual))
            atual = []
    if atual:
        blocos.append(' '.join(atual))
    cfg = RAIZ / 'work/basico/cfg/teste-instalacao.py'
    cfg.write_text('CFG = dict(id="teste-instalacao", pasta="Teste de instalacao", sem_titulo=True, repl={}, '
                   f'frases={" | ".join(blocos)!r}, leg_estilo=None, enquadro=lambda t: (1.0, 0.33))\n', encoding='utf-8')
    r = rodar(py + ['work/basico/render.py', 'teste-instalacao'], cwd=RAIZ, timeout=900)
    saida = RAIZ / 'saidas/basico/Teste de instalacao/RL Teste de instalacao.mp4'
    if r.returncode or not saida.exists():
        print('  [FALHOU] render do básico:', (r.stdout + r.stderr)[-600:])
        return False
    info = rodar(['ffprobe', '-v', 'error', '-show_entries', 'stream=codec_type,width,height:format=duration', '-of', 'json',
                  str(saida)]).stdout
    print(f'  [ok] transcreveu {len(W)} palavras: {" ".join(w["w"] for w in W)}')
    print(f'  [ok] básico RL renderizado: {saida.relative_to(RAIZ)} {info.replace(chr(10), "")[:160]}')
    print(f'  (arquivos de teste: work/teste-instalacao, {cfg.relative_to(RAIZ)}, {saida.parent.relative_to(RAIZ)} — '
          'podem ir pra Lixeira depois de olhar)')
    return True


if __name__ == '__main__':
    tudo = conferir()
    if '--teste' in sys.argv:
        tudo = teste() and tudo
    sys.exit(0 if tudo else 1)
