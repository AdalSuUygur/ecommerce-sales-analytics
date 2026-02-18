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