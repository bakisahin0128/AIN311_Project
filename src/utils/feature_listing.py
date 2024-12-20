# football_prediction.py

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


def main():
    """
    Futbol Maç Sonucu Tahmin Modeli Oluşturma
    """

    # ============================
    # 1. Veri Yükleme ve Yeniden Kodlama
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

    # ============================
    # 3. Özellikler ve Hedef Değişkeni Ayırma
    # ============================

    X = df.drop('Match_Result', axis=1)
    y = df['Match_Result']

    print("\nÖzelliklerin boyutu:", X.shape)
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

    # ============================
    # 10. En İyi Modeli Seçme ve Kaydetme
    # ============================

    best_model_info = max(model_performances, key=lambda x: x['Accuracy'])
    best_model_name = best_model_info['Model']
    best_model_accuracy = best_model_info['Accuracy']

    print(f"\nEn İyi Model: {best_model_name} - Doğruluk Oranı: {best_model_accuracy:.4f}")

    # En iyi modeli yeniden eğitme (isteğe bağlı)
    best_model = models[best_model_name]
    if best_model_name in ['Random Forest', 'XGBoost', 'LightGBM']:
        best_model.fit(X_train_res, y_train_res)
    else:
        best_model.fit(X_train_scaled, y_train)

    # Modeli kaydetme
    model_save_path = f'best_model_{best_model_name.replace(" ", "_").lower()}.joblib'
    joblib.dump(best_model, model_save_path)
    print(f"En iyi model '{model_save_path}' olarak kaydedildi.")

    # ============================
    # 11. Özellik Önemini Görselleştirme
    # ============================

    if best_model_name in ['Random Forest', 'Gradient Boosting', 'XGBoost', 'LightGBM']:
        feature_importances = pd.Series(best_model.feature_importances_, index=X.columns)
        feature_importances = feature_importances.sort_values(ascending=False)
        print("\nEn Önemli Özellikler:")
        print(feature_importances.head(20))

        # Özellik önemlerini görselleştirme
        plt.figure(figsize=(12, 8))
        sns.barplot(x=feature_importances[:20], y=feature_importances.index[:20])
        plt.title(f'{best_model_name} - En Önemli 20 Özellik')
        plt.xlabel('Özellik Önemi')
        plt.ylabel('Özellikler')
        plt.show()

    # ============================
    # 12. Cross-Validation ile Performans Değerlendirmesi
    # ============================

    print("\nCross-Validation ile Modellerin Performansını Değerlendiriyoruz:")

    for model_name, model in models.items():
        print(f"\n{model_name} için Cross-Validation Yapılıyor...")
        if model_name in ['Random Forest', 'XGBoost', 'LightGBM']:
            scores = cross_val_score(model, X_train_res, y_train_res, cv=5, scoring='accuracy', n_jobs=-1)
        else:
            scores = cross_val_score(model, X_train_scaled, y_train, cv=5, scoring='accuracy', n_jobs=-1)
        print(f"{model_name} Cross-Validation Doğruluk Oranları: {scores}")
        print(f"Ortalama Doğruluk Oranı: {scores.mean():.4f} ± {scores.std():.4f}")

    # ============================
    # 13. Özellik Önem Tablosunu Kaydetme (Opsiyonel)
    # ============================

    if best_model_name in ['Random Forest', 'Gradient Boosting', 'XGBoost', 'LightGBM']:
        # En iyi modelin özellik önemlerini DataFrame'e dönüştürme
        feature_importance_df = feature_importances.reset_index()
        feature_importance_df.columns = ['Feature', 'Importance']

        # CSV dosyasına kaydetme
        feature_importance_df.to_csv('feature_importance.csv', index=False)
        print("\nÖzellik önem tablosu 'feature_importance.csv' olarak kaydedildi.")

    print("\nModelleme süreci tamamlandı.")


if __name__ == "__main__":
    main()
