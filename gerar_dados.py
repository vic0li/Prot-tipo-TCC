import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import random
import os

np.random.seed(42)

# -------------------------
# CONFIGURAÇÃO
# -------------------------
N_PACIENTES = 15
HORAS = 48

motivos = ["sepse", "pos_operatorio", "trauma", "insuficiencia_respiratoria"]

# -------------------------
# COMORBIDADES REALISTAS
# -------------------------

def gerar_comorbidades():
    opcoes = ["obesidade", "dm", "irc", "dpoc", "has"]

    if np.random.rand() < 0.2:
        return "nenhuma"

    n = np.random.randint(1, 4)
    escolhidas = random.sample(opcoes, n)

    return ", ".join(escolhidas)

def peso_comorbidade(comorb_str):
    pesos = {
        "obesidade": 1,
        "dm": 2,
        "has": 1,
        "dpoc": 3,
        "irc": 3
    }

    if comorb_str == "nenhuma":
        return 0

    total = 0
    for c in comorb_str.split(", "):
        total += pesos.get(c, 0)

    return total

# -------------------------
# CLASSIFICAÇÕES CLÍNICAS
# -------------------------

def classificar_fc(fc):
    if fc < 60: return "bradicardia"
    elif fc <= 100: return "normal"
    elif fc <= 130: return "taquicardia"
    else: return "critico"

def classificar_spo2(spo2):
    if spo2 >= 95: return "normal"
    elif spo2 >= 90: return "alerta"
    else: return "critico"

def classificar_temp(temp):
    if temp < 35: return "hipotermia"
    elif temp <= 37.5: return "normal"
    elif temp <= 38.5: return "febre"
    else: return "critico"

def classificar_pa(ps):
    if ps < 90: return "hipotensao_grave"
    elif ps < 100: return "alerta"
    else: return "normal"

def alerta(valor, tipo):
    if tipo == "fc": return 1 if valor > 110 else 0
    if tipo == "spo2": return 1 if valor < 94 else 0
    if tipo == "temp": return 1 if valor > 37.8 else 0
    if tipo == "lactato": return 1 if valor > 2 else 0

# -------------------------
# SIMULAÇÃO FISIOLÓGICA
# -------------------------

def simular_sinais(motivo, t, peso_comorb):

    fc = np.random.normal(80, 10)
    ps = np.random.normal(120, 15)
    pdia = np.random.normal(80, 10)
    spo2 = np.random.normal(98, 2)
    temp = np.random.normal(36.8, 0.4)
    lactato = np.random.normal(1.2, 0.5)
    leuc = np.random.normal(8000, 2000)
    creat = np.random.normal(1.0, 0.3)

    # -------------------------
    # IMPACTO DAS COMORBIDADES
    # -------------------------
    fc += peso_comorb * 2
    spo2 -= peso_comorb * 1.5
    lactato += peso_comorb * 0.5
    creat += peso_comorb * 0.2

    # -------------------------
    # CONDIÇÃO CLÍNICA
    # -------------------------
    if motivo == "sepse":
        fc += 30
        ps -= 30
        temp += 1.5
        lactato += 3
        leuc += 4000

    elif motivo == "insuficiencia_respiratoria":
        spo2 -= 8
        fc += 15

    elif motivo == "trauma":
        ps -= 20
        fc += 20

    elif motivo == "pos_operatorio":
        temp += 0.5

    # -------------------------
    # DETERIORAÇÃO TEMPORAL
    # -------------------------
    fator = t / HORAS
    fc += fator * (10 + peso_comorb)
    spo2 -= fator * (3 + peso_comorb * 0.5)
    lactato += fator * (1 + peso_comorb * 0.3)

    return fc, ps, pdia, spo2, temp, lactato, leuc, creat

# -------------------------
# SIMULAÇÃO PRINCIPAL
# -------------------------

dados = []
inicio = datetime.now()

for p in range(N_PACIENTES):

    idade = np.random.randint(18, 90)
    comorb = gerar_comorbidades()
    peso = peso_comorbidade(comorb)
    motivo = random.choice(motivos)

    historico = []

    for t in range(HORAS):
        dt = inicio + timedelta(hours=t)

        fc, ps, pdia, spo2, temp, lactato, leuc, creat = simular_sinais(motivo, t, peso)

        # sensores
        ang = np.random.uniform(20, 60)
        mud = np.random.randint(0, 5)
        tempo_pos = np.random.uniform(10, 180)
        pressao_col = np.random.uniform(20, 80)

        # -------------------------
        # RISCOS COM CORRELAÇÃO
        # -------------------------
        risco_escorregamento = ang * 0.3 + (1/(mud+1)) * 10 + peso * 2

        pam = (ps + 2 * pdia) / 3

        indice_mov = mud / 24
        risco_imob = (tempo_pos / (mud + 1)) + peso * 5
        risco_bronco = 1 if ang < 30 else 0
        risco_pressao = (tempo_pos * pressao_col) + peso * 10

        # histórico
        historico.append({
            "fc": fc,
            "spo2": spo2,
            "lactato": lactato,
            "ps": ps,
            "pdia": pdia,
            "temp": temp
        })

        df_hist = pd.DataFrame(historico).tail(3)

        def tendencia(col):
            if len(df_hist) < 3:
                return "estavel"
            return "subindo" if df_hist[col].iloc[-1] > df_hist[col].mean() else "descendo"

        dados.append({
            "id_paciente": p,
            "Data": dt.date(),
            "Hora": dt.hour,
            "timestamp": dt,

            "frequencia_cardiaca": round(fc,1),
            "pressao_sistolica": round(ps,1),
            "pressao_diastolica": round(pdia,1),
            "pressao_media": round(pam,1),
            "saturacao_O2": round(spo2,1),
            "temperatura": round(temp,1),
            "lactato": round(lactato,2),
            "leucocitos": int(leuc),
            "creatinina": round(creat,2),

            "idade": idade,
            "comorbidades": comorb,
            "motivo_internacao": motivo,

            "angulacao_dorso": round(ang,1),
            "mudancas_posicao_24h": mud,
            "tempo_posicao_atual_min": round(tempo_pos,1),
            "pressao_media_colchao": round(pressao_col,1),
            "risco_escorregamento": round(risco_escorregamento,1),

            "alerta_fc": alerta(fc, "fc"),
            "alerta_spo2": alerta(spo2, "spo2"),
            "alerta_temp": alerta(temp, "temp"),
            "alerta_lactato": alerta(lactato, "lactato"),

            "class_pa": classificar_pa(ps),
            "faixa_fc": classificar_fc(fc),
            "faixa_spo2": classificar_spo2(spo2),

            "indice_movimento": round(indice_mov,2),
            "risco_imobilidade": round(risco_imob,2),
            "risco_broncoaspiracao": risco_bronco,
            "risco_pressao": round(risco_pressao,1),

            "frequencia_cardiaca_media_3": round(df_hist["fc"].mean(),1),
            "frequencia_cardiaca_tendencia": tendencia("fc"),

            "saturacao_O2_media_3": round(df_hist["spo2"].mean(),1),
            "saturacao_O2_tendencia": tendencia("spo2"),

            "lactato_media_3": round(df_hist["lactato"].mean(),2),
            "lactato_tendencia": tendencia("lactato"),

            "pressao_sistolica_media_3": round(df_hist["ps"].mean(),1),
            "pressao_sistolica_tendencia": tendencia("ps"),

            "pressao_diastolica_media_3": round(df_hist["pdia"].mean(),1),
            "pressao_diastolica_tendencia": tendencia("pdia"),

            "temperatura_media_3": round(df_hist["temp"].mean(),1),
            "temperatura_tendencia": tendencia("temp")
        })

# -------------------------
# DATAFRAME FINAL
# -------------------------

df = pd.DataFrame(dados)

os.makedirs("data", exist_ok=True)

df.to_csv(
    "data/raw/UTI_simulada_avancada2.csv",
    index=False
)

print("Dataset gerado com sucesso!")
print(df.head())
