import pandas as pd
import datetime as dt

def calculate_kpis(df):
    """
    Dashboard'un en tepesindeki Özet Kartlar (KPIs) için hesaplama yapar.
    Döndürdüğü sözlük: Toplam Ciro, Sipariş Sayısı, Müşteri Sayısı, Sepet Ortalaması.
    """
    total_revenue = df['TotalAmount'].sum()
    total_orders = df['OrderID'].nunique()
    total_customers = df['CustomerID'].nunique()
    
    # Ortalama Sepet Tutarı (AOV)
    avg_order_value = total_revenue / total_orders if total_orders > 0 else 0

    return {
        'total_revenue': total_revenue,
        'total_orders': total_orders,
        'total_customers': total_customers,
        'avg_order_value': avg_order_value
    }

def get_monthly_sales(df):
    """
    Zaman serisi grafiği (Line Chart) için aylık ciroları hesaplar.
    Index: Tarih, Value: Ciro
    """
    df_trend = df.set_index('OrderDate')
    # 'ME' = Month End (Ay sonu). Eski pandas sürümlerinde hata verirse 'M' yapın.
    monthly_sales = df_trend['TotalAmount'].resample('ME').sum()
    
    return monthly_sales

def get_category_performance(df):
    """
    Pareto Analizi (Bar Chart) için kategorileri sıralar.
    En çok ciro getiren kategoriden en aza doğru sıralı döner.
    """
    cat_perf = df.groupby('CategoryName')['TotalAmount'].sum().reset_index()
    cat_perf = cat_perf.sort_values('TotalAmount', ascending=False)
    
    # Yüzdelik payı da hesaplayalım (Dashboard'da lazım olur)
    total_rev = cat_perf['TotalAmount'].sum()
    cat_perf['Share_Percent'] = (cat_perf['TotalAmount'] / total_rev) * 100
    
    return cat_perf

def get_top_products(df, n=10):
    """
    En çok satan 'n' ürünü getirir.
    Varsayılan olarak ilk 10 ürünü getirir.
    """
    prod_perf = df.groupby('ProductName')['TotalAmount'].sum().reset_index()
    prod_perf = prod_perf.sort_values('TotalAmount', ascending=False).head(n)
    
    return prod_perf


def get_daily_sales_performance(df):
    """
    Satışların haftanın günlerine göre dağılımını analiz eder.
    """
    temp_df = df.copy()
    
    # Gün isimlerini Türkçe olarak eşleyelim
    gun_esleme = {
        0: 'Pazartesi', 1: 'Salı', 2: 'Çarşamba', 
        3: 'Perşembe', 4: 'Cuma', 5: 'Cumartesi', 6: 'Pazar'
    }
    
    temp_df['Gun_Adi'] = temp_df['OrderDate'].dt.dayofweek.map(gun_esleme)
    
    # Günlük toplam ciroyu hesapla
    daily_analysis = temp_df.groupby(['Gun_Adi'])['TotalAmount'].sum().reset_index()
    
    # Günleri mantıklı bir sıraya dizelim (Pazartesi'den başlayarak)
    gun_sirasi = ['Pazartesi', 'Salı', 'Çarşamba', 'Perşembe', 'Cuma', 'Cumartesi', 'Pazar']
    daily_analysis['Gun_Adi'] = pd.Categorical(daily_analysis['Gun_Adi'], categories=gun_sirasi, ordered=True)
    daily_analysis = daily_analysis.sort_values('Gun_Adi')
    
    return daily_analysis

def calculate_rfm(df):
    """
    Müşteri Segmentasyonu (RFM Analizi) yapar.
    Müşterileri 'Champions', 'At Risk' gibi sınıflara ayırır.
    """
    # 1. Analiz Tarihi (Son tarihten 2 gün sonrası)
    last_date = df['OrderDate'].max()
    analysis_date = last_date + pd.Timedelta(days=2)

    # 2. Metrikler
    rfm = df.groupby('CustomerID').agg({
        'OrderDate': lambda date: (analysis_date - date.max()).days,
        'OrderID': 'nunique',
        'TotalAmount': 'sum'
    })

    rfm.columns = ['Recency', 'Frequency', 'Monetary']
    rfm = rfm[rfm['Monetary'] > 0] # Negatifleri temizle

    # 3. Skorlama (1-5 Puan)
    rfm["RecencyScore"] = pd.qcut(rfm['Recency'], 5, labels=[5, 4, 3, 2, 1])
    rfm["FrequencyScore"] = pd.qcut(rfm['Frequency'].rank(method="first"), 5, labels=[1, 2, 3, 4, 5])
    
    # Skor Birleştirme
    rfm["RFM_SCORE"] = (rfm['RecencyScore'].astype(str) + 
                        rfm['FrequencyScore'].astype(str))

    # 4. Segment İsimlendirme (Regex Map)
    seg_map = {
        r'[1-2][1-2]': 'Hibernating',
        r'[1-2][3-4]': 'At Risk',
        r'[1-2]5': 'Can\'t Loose',
        r'3[1-2]': 'About to Sleep',
        r'33': 'Need Attention',
        r'[3-4][4-5]': 'Loyal Customers',
        r'41': 'Promising',
        r'51': 'New Customers',
        r'[4-5][2-3]': 'Potential Loyalists',
        r'5[4-5]': 'Champions'
    }

    rfm['Segment'] = rfm['RFM_SCORE'].replace(seg_map, regex=True)

    return rfm


def calculate_monthly_growth(df):
    """
    Aylık ciro büyüme oranlarını (Month-over-Month Growth) hesaplar.
    Dashboard'da 'Geçen aya göre %X büyüdük' demek için kullanılır.
    """
    df_trend = df.set_index('OrderDate')
    monthly_sales = df_trend['TotalAmount'].resample('ME').sum()
    
    # Yüzdelik Değişim (PCT Change)
    growth_df = pd.DataFrame(monthly_sales)
    growth_df['Growth_Rate'] = growth_df['TotalAmount'].pct_change() * 100
    
    return growth_df


def calculate_cohort_matrix(df):
    """
    Meşhur Cohort Analizi (Retention Heatmap) için veri hazırlar.
    Müşterilerin ilk geldiği aydan sonraki aylarda ne kadarının kaldığını gösterir.
    """
    # 1. Veriyi kopyalayalım
    cohort_data = df[['CustomerID', 'OrderDate']].copy()
    
    # 2. Sipariş ayını bul (Order Month)
    cohort_data['OrderMonth'] = cohort_data['OrderDate'].dt.to_period('M')
    
    # 3. Müşterinin İLK sipariş tarihini bul (Cohort Month)
    cohort_data['CohortMonth'] = cohort_data.groupby('CustomerID')['OrderDate'] \
                                            .transform('min').dt.to_period('M')
    
    # 4. Cohort Index (Müşteri kaç aydır bizle?)
    # Formül: (Sipariş Yılı - Cohort Yılı) * 12 + (Sipariş Ayı - Cohort Ayı) + 1
    def get_date_int(df, column):
        year = df[column].dt.year
        month = df[column].dt.month
        return year, month

    order_year, order_month = get_date_int(cohort_data, 'OrderMonth')
    cohort_year, cohort_month = get_date_int(cohort_data, 'CohortMonth')

    years_diff = order_year - cohort_year
    months_diff = order_month - cohort_month

    cohort_data['CohortIndex'] = years_diff * 12 + months_diff + 1
    
    # 5. Pivot Table (Satırlar: Cohort Ayı, Sütunlar: Geçen Ay Sayısı, Değer: Müşteri Sayısı)
    cohort_counts = cohort_data.groupby(['CohortMonth', 'CohortIndex'])['CustomerID'].nunique().reset_index()
    cohort_matrix = cohort_counts.pivot(index='CohortMonth', columns='CohortIndex', values='CustomerID')
    
    # 6. Retention Oranına Çevirme (İlk aydaki sayıya bölme)
    cohort_size = cohort_matrix.iloc[:, 0]
    retention = cohort_matrix.divide(cohort_size, axis=0)
    
    return retention