# Monitoramento Inteligente de Áreas de Preservação e Supressão Vegetal com Visão Computacional

**Global Solution — Visão Computacional | FIAP**

Classificação de imagens de satélite (350×350) em `wildfire` (risco/ocorrência de incêndio) vs `nowildfire`, usando *transfer learning* com **MobileNetV2**, para apoiar o monitoramento ambiental.


---

## Conteúdo do pacote

```
projeto_wildfire_visao_computacional/
├── notebook/
│   └── Wildfire_Visao_Computacional.ipynb   # notebook executado, com saídas e gráficos
├── roteiro_video.md                          # roteiro do vídeo (até 3 min), com os números reais
└── README.md
```

## Resultados obtidos (conjunto de teste)

| Métrica | Valor |
|---|---|
| Acurácia | 97,60% |
| ROC AUC | 0,9983 |
| Precisão `wildfire` | 0,9929 |
| Recall `wildfire` | 0,9635 |
| F1 `wildfire` | 0,9780 |
| Falsos negativos | 127 (de 3.479 áreas de risco) |
| Falsos positivos | 24 |

## Etapas cobertas (enunciado)

1. Compreensão do problema ambiental + sensoriamento remoto.
2. Análise inicial da base (estrutura, contagem por classe/split, dimensões, exemplos e diferenças visuais).
3. Pré-processamento: limpeza de imagens corrompidas, redimensionamento (224×224), normalização, *data augmentation* só no treino, splits separados (sem vazamento de dados).
4. Modelagem: CNN do zero (baseline) + MobileNetV2 (transfer learning + fine-tuning), com justificativa.
5. Avaliação no teste: acurácia, precisão, recall, F1, matriz de confusão e ROC AUC, com foco em falsos negativos.
6. Proposta de aplicação real ("VigIA Florestal"): mapa de risco, alertas automáticos, acompanhamento temporal + função de inferência.

## Como reproduzir (Google Colab)

1. Abra `notebook/Wildfire_Visao_Computacional.ipynb` no Colab.
2. Ative a GPU: **Ambiente de execução → Alterar o tipo de ambiente de execução → GPU (T4)**.
3. Conecte ao Kaggle (token em Settings → API). O `kagglehub` pede usuário/key na 1ª execução.
4. **Ambiente de execução → Executar tudo.** (`QUICK_RUN = False` para métricas finais.)

## Dataset

[Wildfire Prediction Dataset — Kaggle](https://www.kaggle.com/datasets/abdelghaniaaba/wildfire-prediction-dataset) — ~42.850 imagens, divididas em treino/validação/teste (~70/15/15).

## Stack

Python · TensorFlow/Keras · scikit-learn · Matplotlib · kagglehub · Google Colab (GPU)
