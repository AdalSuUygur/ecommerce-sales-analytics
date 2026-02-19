# 🛒 E-Ticaret Satış Analizi ve Öneri Sistemi

Bu proje, 72 saatlik Ideathon kapsamında geliştirilmiş veri bilimi tabanlı bir e-ticaret analiz paneli ve ürün öneri sistemidir. Müşterilerin geçmiş alışveriş verilerini analiz ederek **Kosinüs Benzerliği (Cosine Similarity)** algoritmasıyla kişiselleştirilmiş ürün önerileri sunar.

## 🛠️ Kullanılan Teknolojiler
- **Backend & Makine Öğrenmesi:** Python, Scikit-learn, Pandas
- **Frontend & Arayüz:** Streamlit
- **Yaklaşım:** İşbirlikçi Filtreleme (Collaborative Filtering)

## 🚀 Kurulum ve Çalıştırma

Projeyi yerel makinenizde çalıştırmak için aşağıdaki adımları takip edin:

### 1. Sanal Ortamı Oluşturun ve Aktif Edin
```bash
# Sanal ortam oluşturma
python -m venv venv

# Aktif etme (Windows)
.\venv\Scripts\activate

```

### 2. Gerekli Kütüphaneleri Yükleyin

```bash
pip install -r requirements.txt

```

### 3. Uygulamayı Başlatın

```bash
streamlit run dashboard/app.py

```

## 👥 Ekip ve Roller

* **Dilara:** Veri Mühendisi (Veri Temizleme & Hazırlama)
* **Eren:** Veri Analisti (Keşifsel Veri Analizi & Matris Oluşturma)
* **Adal:** Algoritma Lideri (Öneri Motoru Mimarisi & Backend)
* **Batuhan:** Arayüz Geliştirici (Dashboard & Kullanıcı Deneyimi)

## 📂 Proje Mimarisi (Klasör Yapısı)

Düzenli çalışmak için aşağıdaki klasör yapısına sadık kalıyoruz:

* **`data/`**: Veri setleri burada durur.
    * `processed/`: Temizlenmiş ve analize hazır veriler.
* **`notebooks/`**: Deneme kodları ve analizler (Jupyter Notebook).
* **`src/`**: Projenin ana mantık kodları (Fonksiyonlar, recommender).
* **`dashboard/`**: Streamlit/Dash arayüz kodları.
* **`requirements.txt`**: Gerekli kütüphaneler.
