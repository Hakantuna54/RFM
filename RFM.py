#########2.VEriyi Tanımlama#####
import datetime as dt
import pandas as pd

pd.set_option("display.max_columns", None)
pd.set_option("display.max_rows", None)
pd.set_option("display.float_format", lambda x: "%.3f" % x)
df_ = pd.read_excel(r"C:\Users\hakan\PycharmProjects\CRM_Tekrar\online_retail_II.xlsx", sheet_name="Year 2009-2010")
df = df_.copy()
df.head()
df["TotalPrice"] = df["Price"] * df["Quantity"]  # Toplam ne kadar kazanç sağlandığını buluyoruz.
df["TotalPrice"].head()
df.shape  # Veri setimizin boyutuna baktık
df.isnull().sum()  # hangi değerden kaç tane eksik değer var onu tespit ettik. Descriptionda eksik var
# eşsiz ürün sayısı nedir?
df["Description"].nunique()

df["Description"].value_counts().head()  # Hangi üründen kaçar tane satıldığına bakıyoruz

df.groupby("Description").agg(
    {"Quantity": "sum"}).head()  # hangi üründen kaç tane satılmış baktık ama hata var quantity - çıkamaz.

df.groupby("Description").agg({"Quantity": "sum"}).sort_values("Quantity",
                                                               ascending=False).head()  # descriptiona göre groupbya aldık ve quantitye göre sort ettik

df["Invoice"].nunique()  # eşsiz invoice sayısını getirdik. Kaç eşsiz ınvoice var buna baktık.
# Fatura başına ortalama kazanç ne kadardır
df["TotalPrice"] = df["Price"] * df["Quantity"]  # Toplam ne kadar kazanç sağlandığını buluyoruz.

df.groupby("Invoice").agg({"TotalPrice": "sum"}).head()

###########3.Veriyi Hazırlama##########
df.isnull().sum()
df.dropna(inplace=True)
df.describe().T  # -ler var bu da C yani iadelerden kaynaklanıyordu.

df = df[~df["Invoice"].str.contains("C", na=False)]
df.head()

#############4.RFM Metriklerinin Hesaplanması ############
# recency, frequency, monetary değerlerini hesaplayacağız.
# recency = müşteririnin yeniliği, sıcaklığı == analizin yapıldığı tarih - ilgili müşterinin satın alma yaptığı son tarih
# frequency = müşterinin ypatığı toplam satın alma
# müşterinin toplam satın almalar karşılığında bırkatığı parasal değer.

df["InvoiceDate"].max()
today_date = dt.datetime(2010, 12, 11)
type(today_date)

rfm = df.groupby("Customer ID").agg({"InvoiceDate": lambda date: (today_date - date.max()).days,
                                     # Fatura tarihlerine göre yaptık. analiz yapılan gğnden son alışverişi çıkardık
                                     "Invoice": lambda num: num.nunique(),  # kaç tane eşsiz fatura var ona baktık
                                     "TotalPrice": lambda
                                         TotalPrice: TotalPrice.sum()})  # Tüm total priceleri toplayarak toplam parasal değerin ne old.baktık(monetary)

rfm.head()
rfm.columns = ["recency", "frequency", "monetary"]  # isimlerini de biizm istediğimiz şekilde atadık.
rfm.describe().T  # şimdi ne durumdayız diye bir kontrol ediyoruz. Min monetary değeri 0 bu bizim istemediğimzi bir durum
rfm = rfm[rfm[
              "monetary"] > 0]  # o zaman rfm içerisinden monetaryi seçiyoruz ve 0 dan büyük olmasını istediğimizi söylüyoruz. Terkar rfme atadık

#########5.RFM skorlarının hesaplanması:##############
# recency frequenct ve monetarynin değerlerini skoarlara çevireceğiz. Recency ters monetary ve frequnecy düz bir büyüklük algısı vardır. Yani recencyde küçük
# olan iyidir diğerlerinde büyük olan iyidir.
rfm["recency_score"] = pd.qcut(rfm["recency"], 5, labels=[5, 4, 3, 2, 1])

rfm["monetary_score"] = pd.qcut(rfm["monetary"], 5, labels=[1, 2, 3, 4, 5])

rfm["frequency_score"] = pd.qcut(rfm["frequency"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5])

rfm.head()

# ŞİMDİ R-F-M skoarlarını bir araya getirmeliyiz.

rfm["RFM_SCORE"] = (rfm["recency_score"].astype(str) +
                    rfm["frequency_score"].astype(str))
# ve RFM skorlarım geldi.
rfm.describe().T  # Yeni oluşturduğumuz skorlar gelmedi çünkü onları str olarka vermiştik. burada sadece sayısalllar geliyor.

rfm[rfm["RFM_SCORE"] == "55"]  # şampiyon olan kullanıcılarımız getirmiş olduk.

rfm[rfm["RFM_SCORE"] == "11"]  # Görece önemi daha az olan kullanıcılar.

#########6.RFM segmentlerinin oluşturulması ve analiz edilmesi #############
# Elimizdeki tabloya göre bir segment işlemi yapyıoruz.

# rfm isimlendirilmesi:
seg_map = {r"[1-2][1-2]": "hibernating",
           r"[1-2][3-4]": "at_Risk",
           r"[1-2]5": "cant_loose",
           r"3[1-2]": "about_to_sleep",
           r"33": "need_attention",
           r"[3-4][4-5]": "loyal_customers",
           r"41": "promissing",
           r"51": "new_customers",
           r"[4-5][2-3]": "potantial_loyalist",
           r"5[4-5]": "champions"}

rfm["segment"] = rfm["RFM_SCORE"].replace(seg_map,
                                          regex=True)  # RFm skorlarını replace et ne ile ben sana bir map verdim(seg_map)

rfm[["segment", "recency", "frequency", "monetary"]].groupby("segment").agg(
    ["mean", "count"])  # segmente göre group by a aldık ve toplam ve ortalamsına baktık
# her kesimde nasıl sonuçlar var onları incledik.
rfm[rfm["segment"] == "cant_loose"].head()
rfm[rfm["segment"] == "cant_loose"].index

new_df = pd.DataFrame()

new_df["new_customer_id"] = rfm[rfm["segment"] == "new_customers"].index

new_df["new_customer_id"] == new_df["new_customer_id"].astype(int)  # ondalıklardan kurtulmak için yaptık.

new_df.to_csv("new_customers.csv") #new_customers.csv adıyla kaydettik dosyamızı ilgili departmana iletebiliriz.

rfm.to_csv("rfm.csv")
















