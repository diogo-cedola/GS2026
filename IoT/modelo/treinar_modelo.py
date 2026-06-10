"""
AEGIS - Treino do modelo TinyML e exportacao para o ESP32.

>>> RODE ESTE SCRIPT NO GOOGLE COLAB <<<
(O Colab ja vem com TensorFlow. Basta subir o arquivo aegis_dataset.csv.)

O que ele faz:
  1. Carrega o dataset sintetico.
  2. Treina uma rede pequena com normalizacao EMBUTIDA no modelo
     (o ESP32 vai alimentar os valores crus dos sensores).
  3. Avalia (acuracia + matriz de confusao).
  4. Converte para TensorFlow Lite.
  5. Gera 'model.h' (array C) pronto para o firmware do ESP32.

Saidas: aegis_model.tflite  e  model.h
"""

import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, classification_report

FEATURES = ["temp_c", "umidade", "pressao", "co2", "radiacao"]
CLASSES = ["NOMINAL", "SOBRECARGA_TERMICA", "RISCO_DESPRESSURIZACAO", "AR_CRITICO"]
CSV_PATH = "aegis_dataset.csv"

# ------------------------------------------------------------------
# 1. Carregar dados (no Colab, sobe o CSV se ele ainda nao estiver la)
# ------------------------------------------------------------------
try:
    df = pd.read_csv(CSV_PATH)
except FileNotFoundError:
    from google.colab import files  # type: ignore
    print("Suba o arquivo aegis_dataset.csv:")
    files.upload()
    df = pd.read_csv(CSV_PATH)

X = df[FEATURES].values.astype("float32")
y = df["label"].values.astype("int32")

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# ------------------------------------------------------------------
# 2. Modelo com normalizacao embutida
# ------------------------------------------------------------------
normalizador = tf.keras.layers.Normalization(axis=-1)
normalizador.adapt(X_train)  # aprende media/desvio de cada feature

modelo = tf.keras.Sequential([
    tf.keras.layers.Input(shape=(len(FEATURES),), name="sensores"),
    normalizador,
    tf.keras.layers.Dense(16, activation="relu"),
    tf.keras.layers.Dense(12, activation="relu"),
    tf.keras.layers.Dense(len(CLASSES), activation="softmax", name="estado"),
])

modelo.compile(
    optimizer="adam",
    loss="sparse_categorical_crossentropy",
    metrics=["accuracy"],
)
modelo.summary()

modelo.fit(
    X_train, y_train,
    validation_split=0.15,
    epochs=80,
    batch_size=32,
    verbose=2,
)

# ------------------------------------------------------------------
# 3. Avaliacao
# ------------------------------------------------------------------
loss, acc = modelo.evaluate(X_test, y_test, verbose=0)
print(f"\nAcuracia no teste: {acc*100:.2f}%\n")

y_pred = modelo.predict(X_test, verbose=0).argmax(axis=1)
print("Matriz de confusao (linhas = real, colunas = previsto):")
print(confusion_matrix(y_test, y_pred))
print("\nRelatorio por classe:")
print(classification_report(y_test, y_pred, target_names=CLASSES))

# ------------------------------------------------------------------
# 4. Conversao para TensorFlow Lite (float32)
# ------------------------------------------------------------------
converter = tf.lite.TFLiteConverter.from_keras_model(modelo)
converter.optimizations = [tf.lite.Optimize.DEFAULT]
tflite_model = converter.convert()

with open("aegis_model.tflite", "wb") as f:
    f.write(tflite_model)
print(f"\nModelo TFLite: {len(tflite_model)} bytes")

# ------------------------------------------------------------------
# 5. Gerar model.h (array C para o firmware)
# ------------------------------------------------------------------
def to_c_array(data, var="aegis_model_tflite"):
    linhas = []
    for i in range(0, len(data), 12):
        bloco = ", ".join(f"0x{b:02x}" for b in data[i:i + 12])
        linhas.append("  " + bloco + ",")
    corpo = "\n".join(linhas)
    return (
        "// Gerado automaticamente por treinar_modelo.py\n"
        "// Ordem das entradas: temp_c, umidade, pressao, co2, radiacao\n"
        "// Ordem das saidas:   0=NOMINAL 1=SOBRECARGA_TERMICA "
        "2=RISCO_DESPRESSURIZACAO 3=AR_CRITICO\n\n"
        "#ifndef AEGIS_MODEL_H\n#define AEGIS_MODEL_H\n\n"
        f"const unsigned char {var}[] = {{\n{corpo}\n}};\n"
        f"const unsigned int {var}_len = {len(data)};\n\n"
        "#endif  // AEGIS_MODEL_H\n"
    )

with open("model.h", "w") as f:
    f.write(to_c_array(tflite_model))

# arena = tamanho do modelo + folga para tensores intermediarios
arena = max(8 * 1024, len(tflite_model) + 4 * 1024)
print("Arquivo 'model.h' gerado.")
print(f"Sugestao de kTensorArenaSize para o ESP32: {arena} bytes "
      f"(~{arena//1024} KB)")
print("\nNo Colab, baixe os arquivos com:")
print("  from google.colab import files")
print("  files.download('model.h')")
