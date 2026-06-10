"""
AEGIS - Gerador de dataset sintetico para o modelo TinyML.

Gera leituras plausiveis de uma estacao de monitoramento de habitat
(base lunar/marciana) e rotula cada amostra em uma de 4 condicoes.

Entradas (features) na ordem usada pelo ESP32:
    temp_c     - temperatura interna (graus C)        -> DHT22
    umidade    - umidade relativa (%)                 -> DHT22
    pressao    - pressao interna (kPa)                -> potenciometro 1
    co2        - concentracao de CO2 (ppm)            -> potenciometro 2
    radiacao   - radiacao / exposicao (uSv/h)         -> LDR

Saida (label):
    0 = NOMINAL
    1 = SOBRECARGA_TERMICA
    2 = RISCO_DESPRESSURIZACAO
    3 = AR_CRITICO
"""

import numpy as np
import pandas as pd

RNG = np.random.default_rng(42)
N_POR_CLASSE = 600
FEATURES = ["temp_c", "umidade", "pressao", "co2", "radiacao"]
CLASSES = ["NOMINAL", "SOBRECARGA_TERMICA", "RISCO_DESPRESSURIZACAO", "AR_CRITICO"]


def _clip(v, lo, hi):
    return np.clip(v, lo, hi)


def gerar_classe(label, n):
    """Gera n amostras para uma classe. Cada classe tem 1-2 features
    'dominantes' deslocadas para a zona de perigo, as demais ficam
    proximas do nominal mas com ruido (e ocasionalmente quase no limite,
    para criar fronteiras nebulosas)."""

    # base nominal para todas as features
    temp = RNG.normal(22, 3.0, n)
    umid = RNG.normal(45, 9.0, n)
    pres = RNG.normal(101, 1.5, n)
    co2 = RNG.normal(700, 160, n)
    rad = RNG.normal(0.30, 0.10, n)

    if label == 1:  # SOBRECARGA_TERMICA -> temperatura alta
        temp = RNG.normal(40, 4.5, n)
        co2 = RNG.normal(950, 280, n)            # ventilacao comprometida
        umid = RNG.normal(38, 10, n)             # ar mais seco/quente
    elif label == 2:  # RISCO_DESPRESSURIZACAO -> pressao baixa
        pres = RNG.normal(87, 4.0, n)
        temp = RNG.normal(18, 4.0, n)            # gas expandindo esfria
        rad = RNG.normal(0.45, 0.18, n)          # menos blindagem atmosferica
    elif label == 3:  # AR_CRITICO -> CO2 alto
        co2 = RNG.normal(2600, 550, n)
        umid = RNG.normal(58, 11, n)             # ar viciado/umido
        temp = RNG.normal(25, 3.5, n)

    # ruido extra de fronteira: ~12% das amostras recebem um empurrao
    # leve em outra feature, deixando o caso mais ambiguo
    mask = RNG.random(n) < 0.12
    pres[mask] -= RNG.uniform(2, 6, mask.sum())
    co2[mask] += RNG.uniform(150, 500, mask.sum())

    temp = _clip(temp, 5, 55)
    umid = _clip(umid, 5, 95)
    pres = _clip(pres, 70, 108)
    co2 = _clip(co2, 350, 5000)
    rad = _clip(rad, 0.05, 2.0)

    df = pd.DataFrame({
        "temp_c": temp.round(2),
        "umidade": umid.round(1),
        "pressao": pres.round(2),
        "co2": co2.round(0).astype(int),
        "radiacao": rad.round(3),
        "label": label,
        "classe": CLASSES[label],
    })
    return df


def main():
    partes = [gerar_classe(i, N_POR_CLASSE) for i in range(len(CLASSES))]
    df = pd.concat(partes, ignore_index=True)
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)  # embaralha

    saida = "/mnt/user-data/outputs/aegis_dataset.csv"
    df.to_csv(saida, index=False)

    print(f"Dataset salvo em {saida}")
    print(f"Total de amostras: {len(df)}\n")
    print("Amostras por classe:")
    print(df["classe"].value_counts().to_string(), "\n")
    print("Resumo estatistico das features:")
    print(df[FEATURES].describe().round(2).to_string())
    print("\nPrimeiras linhas:")
    print(df.head(8).to_string(index=False))


if __name__ == "__main__":
    main()
