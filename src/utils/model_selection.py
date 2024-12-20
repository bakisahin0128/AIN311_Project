# compare_models.py

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Scikit-learn kütüphanesinden gerekli modüller
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score

# Sınıflandırma modelleri
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.svm import SVC
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier

# Model kaydetmek için joblib
import joblib

# Sınıf dengesizliği için SMOTE
from imblearn.over_sampling import SMOTE

import warnings

warnings.filterwarnings("ignore")  # Uyarıları gizlemek için


def main():
    """
    Futbol Maç Sonucu Tahmin Modellerini Eğitme ve Karşılaştırma
    """

    # ============================
    # 1. Veri Yükleme ve Ön İşleme
    # ============================

    # İşlenmiş CSV dosyanızın yolunu belirtin
    processed_csv_path = r"C:\Users\mbaki\Desktop\Proje\data\processed\processed_model.csv"  # Dosya yolunuza göre güncelleyin

    try:
        # CSV dosyasını yükleme
        df = pd.read_csv(processed_csv_path)
        print("İşlenmiş DataFrame'in ilk 5 satırı:")
        print(df.head())
    except FileNotFoundError:
        print(f"Hata: '{processed_csv_path}' dosyası bulunamadı. Dosya yolunu kontrol edin.")
        return

    # 2. Hedef Değişkeni Yeniden Kodlama
    # -----------------------------------
    # -1: Away Win (Deplasman Galibiyeti) -> 0
    #  0: Draw (Beraberlik)               -> 1
    #  1: Home Win (Ev Sahibi Galibiyeti) -> 2

    df['Match_Result'] = df['Match_Result'].map({-1: 0, 0: 1, 1: 2})

    # Yeniden kodlamanın doğru yapıldığını kontrol etme
    print("\nYeniden kodlanmış 'Match_Result' değerleri:")
    print(df['Match_Result'].value_counts())

    # 3. Özellikleri Düşürme
    # ------------------------
    # Eğitim sürecinde kullanmak istemediğiniz özellikleri düşürün
    features_to_drop = ['Performance_Diff', 'Away Goals', 'Home Goals']
    X = df.drop(['Match_Result'] + features_to_drop, axis=1)
    y = df['Match_Result']

    print(f"\nDüşürülen Özellikler: {features_to_drop}")
    print("Kalan Özelliklerin boyutu:", X.shape)
    print("Hedef değişkenin boyutu:", y.shape)

    # ============================
    # 4. Eğitim ve Test Setlerine Bölme
    # ============================

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    print(f"\nEğitim seti boyutu: {X_train.shape}")
    print(f"Test seti boyutu: {X_test.shape}")

    # ============================
    # 5. Veri Ölçeklendirme
    # ============================

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # ============================
    # 6. Sınıf Dengesizliği Kontrolü ve SMOTE (Opsiyonel)
    # ============================

    print("\nHedef Değişken Dağılımı (Eğitim Seti):")
    print(y_train.value_counts())

    class_counts = y_train.value_counts()
    imbalance_ratio = class_counts.min() / class_counts.max()

    if imbalance_ratio < 0.5:
        print("Sınıf dengesizliği tespit edildi. SMOTE uygulanıyor...")
        smote = SMOTE(random_state=42)
        X_train_res, y_train_res = smote.fit_resample(X_train_scaled, y_train)
        print("SMOTE sonrası hedef değişken dağılımı:")
        print(pd.Series(y_train_res).value_counts())
    else:
        X_train_res, y_train_res = X_train_scaled, y_train

    print("\nEğitim Seti Sonrası Hedef Dağılımı:")
    print(pd.Series(y_train_res).value_counts())

    # ============================
    # 7. Modelleri Tanımlama
    # ============================

    models = {
        'Logistic Regression': LogisticRegression(random_state=42, max_iter=1000),
        'Decision Tree': DecisionTreeClassifier(random_state=42),
        'Random Forest': RandomForestClassifier(random_state=42),
        'Support Vector Machine': SVC(random_state=42, probability=True),
        'Gradient Boosting': GradientBoostingClassifier(random_state=42),
        'XGBoost': XGBClassifier(random_state=42, use_label_encoder=False, eval_metric='mlogloss'),
        'LightGBM': LGBMClassifier(random_state=42)
    }

    # ============================
    # 8. Modelleri Eğitme ve Değerlendirme
    # ============================

    model_performances = []

    for model_name, model in models.items():
        print(f"\n{model_name} Modeli Eğitiliyor...")

        # Modeli eğitme
        if model_name in ['Random Forest', 'XGBoost', 'LightGBM']:
            model.fit(X_train_res, y_train_res)
        else:
            model.fit(X_train_scaled, y_train)

        # Tahmin yapma
        y_pred = model.predict(X_test_scaled)

        # Performans ölçümleri
        accuracy = accuracy_score(y_test, y_pred)
        report = classification_report(y_test, y_pred, output_dict=True)
        cm = confusion_matrix(y_test, y_pred)

        # Performansı kaydetme
        model_performances.append({
            'Model': model_name,
            'Accuracy': accuracy,
            'Report': report,
            'Confusion Matrix': cm
        })

        # Performans raporunu yazdırma
        print(f"{model_name} Doğruluk Oranı: {accuracy:.4f}")
        print(f"{model_name} Sınıflandırma Raporu:\n", classification_report(y_test, y_pred))

    # ============================
    # 9. Sonuçları Karşılaştırma
    # ============================

    performance_df = pd.DataFrame({
        'Model': [perf['Model'] for perf in model_performances],
        'Accuracy': [perf['Accuracy'] for perf in model_performances]
    })

    print("\nModellerin Doğruluk Oranları:")
    print(performance_df)

    # Doğruluk oranlarını görselleştirme
    plt.figure(figsize=(10, 6))
    sns.barplot(x='Accuracy', y='Model', data=performance_df.sort_values('Accuracy', ascending=False))
    plt.title('Modellerin Doğruluk Oranları Karşılaştırması')
    plt.xlabel('Doğruluk Oranı')
    plt.ylabel('Modeller')
    plt.xlim(0, 1)
    plt.show()

    print("\nModel karşılaştırması tamamlandı.")


if __name__ == "__main__":
    main()
