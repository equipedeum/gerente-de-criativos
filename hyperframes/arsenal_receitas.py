# -*- coding: utf-8 -*-
"""Receitas do arsenal (07/11/2026): as ideias que se repetem de vídeo pra vídeo (o CTA e os meios do lote de estúdio),
cada uma com VÁRIAS cenas possíveis escolhidas por ar.escolhe (não repete no vídeo nem nos irmãos de gancho/meio/final).
Cada receita cria a cena (cena + an.cenario + monta) e devolve c. Tempos em s (float) ou índice (int).

    r = ar.receita('A:ia_rodando', cena(157, 172, '...'), '{64f}...|{120}*IA rodando', t_ia=ts(167))

Ideias prontas (opções entre parênteses; 'base' = a cena antiga do bo, que vai pro fim da fila):
  A:ia_rodando  (engrenagens, corte, aberto, fabrica, fluxo | base escritorio)      t_ia
  A:perguntas   (celular, transito, cafe, mao, parque | base onibus)                  tempos=[t1, t2, t3]
  A:acelerar    (foguete, linha, escada, semente, notebook, tempo | base tv)         t_tv, t_fim
  A:aguardando  (contraluz, cafe, janela, costas, balcao | base recepcao, videochamada)
  C:responde_hora (celular, rosto, janelas | base sofa)                                t_msg, t_ia
  C:campanha    (notebook, grade, linha, funil | base painel, quarto)                  t_ia, t_corta
  C:repetitivo_ia (fabrica, aberto, corte, antes_depois | base deposito)               t_ia
  C:time_manha  (cafe, caravana, parque | base recepcao)
  C:fechar      (balcao, carimbo, caixa | base contrato)                               t_assina
  C:lucro_parado (barco, balanca, iceberg, carteira | base pote)
  C:escalar     (foguete, mapa, escada, construcao, ima | base predio, loja)
"""
import animada as an
import bonecos as bo
import motor
from bonecos import _T
from pecas import monta


def _ar():
    import arsenal_animada as ar
    return ar


def _ts(lst, n, t0, passo):
    return [(_T(x)) for x in lst] if lst else [t0 + 0.4 + passo * k for k in range(n)]


def receita(ideia, c, spec, so=None, transicao=None, extra=(), **k):
    """Escolhe a opção da ideia (ar.escolhe), põe o ambiente, monta a cena e devolve c. so=[nomes] restringe as opções;
    transicao='auto'|'tinta'|... aplica na entrada; extra = peças a mais (rótulo, selo...)."""
    ar = _ar()
    t = c.t0 + 0.05
    t1 = bo._fim(c)
    R = RECEITAS[ideia]
    ops = {n: v for n, v in R['ops'].items() if not so or n in so}
    usadas = set(ar.pecas_usadas())
    livres = [n for n in ops if not (set(PECA.get((ideia, n), ())) & usadas)]   # peça já usada à mão no vídeo sai da escolha
    nome = ar.escolhe(ideia, livres or list(ops), base=R.get('base'), pecas={n: PECA.get((ideia, n), ()) for n in ops})
    tipo, op, fn = ops[nome]
    an.cenario(c, tipo, **op)
    if transicao:
        ar.transicao(c, transicao)
    pec = fn(ar, c, t, t1, k)
    pecs = pec if isinstance(pec, (list, tuple)) else [pec]
    monta(c, spec, *pecs, *extra)
    c.receita = (ideia, nome)
    return c


def _meio(t, t1, f=0.5):
    return t + (t1 - t) * f


RECEITAS = {
    'A:ia_rodando': {'base': 'escritorio', 'ops': {
        'engrenagens': ('escritorio2', {'topo': 'quadros'}, lambda ar, c, t, t1, k: ar.engrenagens(c, t, ('Marketing', 'Comercial', 'IA'), t_gira=k.get('t_ia', _meio(t, t1)))),
        'corte': ('corte', {}, lambda ar, c, t, t1, k: ar.predio_corte(c, t, (('Marketing', 'digita'), ('Comercial', 'telefone'), ('IA', 'headset')), ia=k.get('t_ia', _meio(t, t1)))),
        'aberto': ('escritorio_noite', {}, lambda ar, c, t, t1, k: ar.escritorio_aberto(c, t, ia=True, tempos=[k.get('t_ia', _meio(t, t1)) + 0.2 * j for j in range(7)])),
        'fabrica': ('fabrica', {}, lambda ar, c, t, t1, k: ar.fabrica_linha(c, t, ia=k.get('t_ia', _meio(t, t1)))),
        'fluxo': ('pergaminho', {}, lambda ar, c, t, t1, k: ar.fluxo(c, t, ['Marketing', 'Comercial', 'IA rodando'], tempos=[t + 0.3, _meio(t, t1, 0.35), k.get('t_ia', _meio(t, t1))])),
        'escritorio': ('escritorio2', {'topo': 'prateleira'}, lambda ar, c, t, t1, k: bo.escritorio(c, t, acoes=('digita', 'headset', 'pasta'), placas=('Marketing', 'Comercial'), ia=k.get('t_ia', _meio(t, t1)))),
    }},
    'A:perguntas': {'base': 'onibus', 'ops': {
        'celular': ('casa', {}, lambda ar, c, t, t1, k: ar.celular_mao(c, t, [('Pergunta', x, 'ok') for x in _ts(k.get('tempos'), 3, t, 0.6)])),
        'transito': ('transito', {'parado': True}, lambda ar, c, t, t1, k: ar.transito_preso(c, t, relogio=False, baloes=[('Pergunta', x, 'ok') for x in _ts(k.get('tempos'), 2, t, 0.8)[:2]])),
        'cafe': ('cafe', {}, lambda ar, c, t, t1, k: [ar.close_rosto(c, t, 'sorri', objeto='celular', t_reacao=_ts(k.get('tempos'), 1, t, 0.6)[-1]),
                                                       ar.balao(c, 700, 1020, 'Respondido', _ts(k.get('tempos'), 1, t, 0.6)[-1], 'ok')]),
        'mao': ('sala_dono', {}, lambda ar, c, t, t1, k: ar.mao_escreve(c, t, ('Pergunta', 'Pergunta', 'Pergunta'), vela=False)),
        'parque': ('parque', {}, lambda ar, c, t, t1, k: [ar.parque_passeio(c, t, crianca=False),
                                                          ar.balao(c, 640, 1050, 'Respondido', _ts(k.get('tempos'), 1, t, 0.6)[-1], 'ok')]),
        'onibus': ('rua', {}, lambda ar, c, t, t1, k: bo.ponto_onibus(c, t, tempos=_ts(k.get('tempos'), 3, t, 0.6))),
    }},
    'A:acelerar': {'base': 'tv', 'ops': {
        'foguete': ('campo', {}, lambda ar, c, t, t1, k: ar.foguete(c, t, t_lanca=k.get('t_tv', _meio(t, t1, 0.4)))),
        'linha': ('pergaminho', {}, lambda ar, c, t, t1, k: ar.grafico_linha(c, t, t_linha=k.get('t_tv', _meio(t, t1, 0.3)), marcar=(5, 'Crescimento', k.get('t_fim', t1 - 0.8)))),
        'escada': ('parque', {}, lambda ar, c, t, t1, k: ar.escada(c, t, ('Seu momento', 'Plano', 'Crescer'), tempos=[t + 0.3, _meio(t, t1, 0.45), k.get('t_fim', t1 - 0.8)])),
        'semente': ('campo_tarde', {}, lambda ar, c, t, t1, k: ar.semente(c, t, t_cresce=k.get('t_tv', _meio(t, t1, 0.3)))),
        'notebook': ('escritorio', {}, lambda ar, c, t, t1, k: ar.notebook_grafico(c, t, 'sobe', t_linha=k.get('t_tv', _meio(t, t1, 0.3)))),
        'tempo': ('pergaminho', {}, lambda ar, c, t, t1, k: ar.linha_tempo(c, t, 'Seu momento', 'Crescimento', t_anda=k.get('t_tv', _meio(t, t1, 0.3)))),
        'tv': ('reuniao', {}, lambda ar, c, t, t1, k: bo.sala_reuniao(c, t, tv='grafico', t_tv=k.get('t_tv', _meio(t, t1, 0.3)), poses=('aponta', 'celular'), itens=(None, 'tablet'),
                                                                  empurra=_meio(t, t1, 0.55), comemora=k.get('t_fim', t1 - 0.6))),
    }},
    'A:aguardando': {'base': ('videochamada', 'recepcao'), 'ops': {
        'contraluz': ('tunel', {}, lambda ar, c, t, t1, k: ar.contraluz(c, t, n=1, nomes=('Você',))),
        'cafe': ('cafe', {}, lambda ar, c, t, t1, k: ar.cafe_maquina(c, t)),
        'janelas': ('rua_noite', {}, lambda ar, c, t, t1, k: ar.janelas(c, t, n=6, apaga=[0, 1, 3, 4], acesa=5, t_muda=t + 0.3)),
        'costas': ('porto_tarde', {}, lambda ar, c, t, t1, k: ar.de_costas(c, t)),
        'balcao': ('loja', {}, lambda ar, c, t, t1, k: ar.balcao(c, t, sacola=False)),
        'recepcao': ('recepcao', {}, lambda ar, c, t, t1, k: bo.recepcao(c, t, 'espera')),
        'videochamada': ('escritorio2', {'topo': 'quadros'}, lambda ar, c, t, t1, k: bo.videochamada(c, t)),
    }},
    'C:responde_hora': {'base': 'sofa', 'ops': {
        'celular': ('sala_noite', {}, lambda ar, c, t, t1, k: ar.celular_mao(c, t, [('Vi o anúncio', k.get('t_msg', t + 0.1), 'ponto'), ('Já te ajudo', k.get('t_ia', _meio(t, t1)), 'ia')])),
        'rosto': ('quarto_noite', {}, lambda ar, c, t, t1, k: [ar.close_rosto(c, t, 'surpreso', objeto='celular', t_reacao=k.get('t_ia', _meio(t, t1))),
                                                               ar.balao(c, 700, 1020, 'Já te ajudo', k.get('t_ia', _meio(t, t1)), 'ia', '#F2B544')]),
        'janelas': ('rua_noite', {}, lambda ar, c, t, t1, k: [ar.janelas(c, t, n=6, apaga=[0, 2, 3], acesa=4, t_muda=k.get('t_msg', t + 0.2)),
                                                              ar.balao(c, 560, 1010, 'Já te ajudo', k.get('t_ia', _meio(t, t1)), 'ia', '#F2B544')]),
        'sofa': ('sala_noite', {}, lambda ar, c, t, t1, k: bo.sala_noite(c, t, t_notif=k.get('t_msg', t + 0.05), hora=(11, 0),
                                                                    baloes=[('Oi! Vi o anúncio', k.get('t_msg', t + 0.05) + 0.1, 'ponto'), ('Oi! Já te ajudo', k.get('t_ia', _meio(t, t1)), 'ia')])),
    }},
    'C:campanha': {'base': ('painel', 'quarto'), 'ops': {
        'notebook': ('escritorio_noite', {}, lambda ar, c, t, t1, k: ar.notebook_grafico(c, t, 'sobe', t_linha=k.get('t_ia', t + 0.3))),
        'grade': ('preto', {}, lambda ar, c, t, t1, k: ar.grade_objetos(c, t, n=12, destaque=('x', [1, 4, 6, 11]), t_destaque=k.get('t_corta', _meio(t, t1)))),
        'linha': ('pergaminho', {}, lambda ar, c, t, t1, k: ar.grafico_linha(c, t, t_linha=k.get('t_ia', t + 0.3))),
        'funil': ('escritorio_noite', {}, lambda ar, c, t, t1, k: ar.funil(c, t, 'Anúncios', 'Vendas', t_sai=k.get('t_corta', _meio(t, t1)))),
        'painel': ('escritorio_noite', {}, lambda ar, c, t, t1, k: bo.campanhas(c, t, t_ia=k.get('t_ia', t + 0.3), t_corta=k.get('t_corta', _meio(t, t1)))),
        'quarto': ('quarto_noite', {}, lambda ar, c, t, t1, k: bo.quarto_ia(c, t, t_ia=k.get('t_ia', t + 0.3), t_corta=k.get('t_corta', _meio(t, t1)))),
    }},
    'C:repetitivo_ia': {'base': 'deposito', 'ops': {
        'fabrica': ('fabrica', {}, lambda ar, c, t, t1, k: ar.fabrica_linha(c, t, ia=k.get('t_ia', _meio(t, t1)))),
        'aberto': ('escritorio', {}, lambda ar, c, t, t1, k: ar.escritorio_aberto(c, t, ia=True, tempos=[k.get('t_ia', _meio(t, t1)) + 0.18 * j for j in range(7)])),
        'corte': ('corte', {}, lambda ar, c, t, t1, k: ar.predio_corte(c, t, (('Time', 'digita'), ('Repetitivo', 'caixa'), ('IA', 'headset')), ia=k.get('t_ia', _meio(t, t1)))),
        'antes_depois': ('escritorio2', {'topo': 'relogio'}, lambda ar, c, t, t1, k: ar.antes_depois(c, t, 'Antes', 'Com IA', t_depois=k.get('t_ia', _meio(t, t1)))),
        'deposito': ('deposito', {}, lambda ar, c, t, t1, k: bo.deposito(c, t, ia=k.get('t_ia', _meio(t, t1)))),
    }},
    'C:time_manha': {'base': 'recepcao', 'ops': {
        'cafe': ('cafe', {}, lambda ar, c, t, t1, k: [ar.cafe_maquina(c, t), ar.selo_canto(c, 'Manhã', t + 0.3)]),
        'caravana': ('campo', {}, lambda ar, c, t, t1, k: [ar.caravana(c, t, n=6, silhueta=False, y=1700, esc=0.6), ar.selo_canto(c, 'Manhã', t + 0.3)]),
        'parque': ('parque', {}, lambda ar, c, t, t1, k: [ar.parque_passeio(c, t, cachorro=False, crianca=False), ar.selo_canto(c, 'Manhã', t + 0.3)]),
        'recepcao': ('recepcao', {}, lambda ar, c, t, t1, k: bo.recepcao(c, t, 'chegada', n=3)),
    }},
    'C:fechar': {'base': 'contrato', 'ops': {
        'balcao': ('loja', {}, lambda ar, c, t, t1, k: ar.balcao(c, t, t_paga=k.get('t_assina', _meio(t, t1)))),
        'carimbo': ('reuniao', {}, lambda ar, c, t, t1, k: [ar.reuniao_em_pe(c, t, t_move=_meio(t, t1, 0.3)), ar.carimbo(c, k.get('t_assina', _meio(t, t1, 0.7)), 'Fechado', y=1560)]),
        'caixa': ('loja', {}, lambda ar, c, t, t1, k: ar.caixa_registradora(c, t, t_abre=k.get('t_assina', _meio(t, t1)))),
        'contrato': ('reuniao', {}, lambda ar, c, t, t1, k: bo.sala_reuniao(c, t, tv='contrato', assina=k.get('t_assina', _meio(t, t1, 0.4)), aperto=_meio(t, t1, 0.75))),
    }},
    'C:lucro_parado': {'base': 'pote', 'ops': {
        'barco': ('porto', {}, lambda ar, c, t, t1, k: ar.barco_furado(c, t, k.get('saidas', ('Folha', 'Ferramentas')))),
        'balanca': ('pergaminho', {}, lambda ar, c, t, t1, k: ar.balanca(c, t, 'Custo', 'Lucro', 'esq', t_pende=_meio(t, t1, 0.4))),
        'iceberg': ('porto', {}, lambda ar, c, t, t1, k: ar.iceberg(c, t, k.get('topo', 'Lucro'), k.get('saidas', ('Folha', 'Ferramentas')))),
        'carteira': ('loja', {}, lambda ar, c, t, t1, k: ar.carteira(c, t, 'esvazia')),
        'pote': ('sala_dono', {}, lambda ar, c, t, t1, k: bo.pote(c, t, 'Lucro', 'Vendas', k.get('saidas', ('Folha', 'Ferramentas')))),
    }},
    'C:escalar': {'base': 'predio', 'ops': {
        'foguete': ('campo', {}, lambda ar, c, t, t1, k: ar.foguete(c, t, t_lanca=k.get('t_x', _meio(t, t1, 0.4)))),
        'mapa': ('pergaminho', {}, lambda ar, c, t, t1, k: ar.mapa_rotas(c, t, ('Sua empresa', 560, 1450), [('Tráfego', 280, 1180), ('Marketing', 800, 1230), ('Vendas', 330, 1720)])),
        'escada': ('escritorio2', {'topo': 'quadros'}, lambda ar, c, t, t1, k: ar.escada(c, t, k.get('degraus', ('Tráfego', 'Marketing', 'Escalar')))),
        'construcao': ('aereo', {}, lambda ar, c, t, t1, k: ar.construcao(c, t, rotulo='Sua empresa')),
        'ima': ('loja', {}, lambda ar, c, t, t1, k: ar.ima(c, t, rotulo='Clientes')),
        'predio': ('rua', {}, lambda ar, c, t, t1, k: bo.crescimento_predio(c, t, 'Sua empresa', andares=3)),
    }},
}


# peças que cada opção usa (pra não repetir no vídeo uma peça já usada fora da receita)
PECA = {
    ('A:ia_rodando', 'engrenagens'): ('engrenagens',), ('A:ia_rodando', 'corte'): ('predio_corte',), ('A:ia_rodando', 'aberto'): ('escritorio_aberto',),
    ('A:ia_rodando', 'fabrica'): ('fabrica_linha',), ('A:ia_rodando', 'fluxo'): ('fluxo',), ('A:ia_rodando', 'escritorio'): ('escritorio',),
    ('A:perguntas', 'celular'): ('celular_mao',), ('A:perguntas', 'transito'): ('transito_preso',), ('A:perguntas', 'cafe'): ('close_rosto',),
    ('A:perguntas', 'mao'): ('mao_escreve',), ('A:perguntas', 'parque'): ('parque_passeio',), ('A:perguntas', 'onibus'): ('ponto_onibus',),
    ('A:acelerar', 'foguete'): ('foguete',), ('A:acelerar', 'linha'): ('grafico_linha',), ('A:acelerar', 'escada'): ('escada',),
    ('A:acelerar', 'semente'): ('semente',), ('A:acelerar', 'notebook'): ('notebook_grafico',), ('A:acelerar', 'tempo'): ('linha_tempo',),
    ('A:acelerar', 'tv'): ('sala_reuniao',),
    ('A:aguardando', 'contraluz'): ('contraluz',), ('A:aguardando', 'cafe'): ('cafe_maquina',), ('A:aguardando', 'janelas'): ('janelas',),
    ('A:aguardando', 'costas'): ('de_costas',), ('A:aguardando', 'balcao'): ('balcao',), ('A:aguardando', 'recepcao'): ('recepcao',),
    ('A:aguardando', 'videochamada'): ('videochamada',),
    ('C:responde_hora', 'celular'): ('celular_mao',), ('C:responde_hora', 'rosto'): ('close_rosto',), ('C:responde_hora', 'janelas'): ('janelas',),
    ('C:responde_hora', 'sofa'): ('sala_noite',),
    ('C:campanha', 'notebook'): ('notebook_grafico',), ('C:campanha', 'grade'): ('grade_objetos',), ('C:campanha', 'linha'): ('grafico_linha',),
    ('C:campanha', 'funil'): ('funil',), ('C:campanha', 'painel'): ('campanhas',), ('C:campanha', 'quarto'): ('quarto_ia',),
    ('C:repetitivo_ia', 'fabrica'): ('fabrica_linha',), ('C:repetitivo_ia', 'aberto'): ('escritorio_aberto',), ('C:repetitivo_ia', 'corte'): ('predio_corte',),
    ('C:repetitivo_ia', 'antes_depois'): ('antes_depois',), ('C:repetitivo_ia', 'deposito'): ('deposito',),
    ('C:time_manha', 'cafe'): ('cafe_maquina',), ('C:time_manha', 'caravana'): ('caravana',), ('C:time_manha', 'parque'): ('parque_passeio',),
    ('C:time_manha', 'recepcao'): ('recepcao',),
    ('C:fechar', 'balcao'): ('balcao',), ('C:fechar', 'carimbo'): ('reuniao_em_pe', 'carimbo'), ('C:fechar', 'caixa'): ('caixa_registradora',),
    ('C:fechar', 'contrato'): ('sala_reuniao',),
    ('C:lucro_parado', 'barco'): ('barco_furado',), ('C:lucro_parado', 'balanca'): ('balanca',), ('C:lucro_parado', 'iceberg'): ('iceberg',),
    ('C:lucro_parado', 'carteira'): ('carteira',), ('C:lucro_parado', 'pote'): ('pote',),
    ('C:escalar', 'foguete'): ('foguete',), ('C:escalar', 'mapa'): ('mapa_rotas',), ('C:escalar', 'escada'): ('escada',),
    ('C:escalar', 'construcao'): ('construcao',), ('C:escalar', 'ima'): ('ima',), ('C:escalar', 'predio'): ('crescimento_predio',),
}
