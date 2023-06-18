import streamlit as st
import plotly.graph_objects as go
import yfinance as yf
from prophet import Prophet
from datetime import datetime

# pilih daftar saham
choice={
    "Bank Rakyat Indonesia":"BBRI.JK",
    "Bank Mandiri":"BMRI.JK",
    "PT Astra International Tbk":"ASII.JK",
    "PT GoTo Gojek Tokopedia Tbk ":"GOTO.JK",
    "Adaro Energy Indonesia":"ADRO.JK",
    "Bank Central Asia":"BBCA.JK",
    "PT Telekomunikasi Indonesia Tbk":"TLKM.JK",
    "PT Bank Negara Indonesia (Persero) Tbk":"BBNI.JK"
}

# dapat data
st.markdown("""
<style>
h1 {
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

st.markdown("<h1>DashBroad Harga Saham</h1>", unsafe_allow_html=True)
selected_title = st.selectbox("Pilih Saham", list(choice.keys()))
# ini untuk input data
start_date = st.date_input("Tanggal Mulai")
# ini untuk convert format tanggal ke dalam string di terima oleh yfinance
start_date_str = start_date.strftime("%Y-%m-%d")
# ini untuk input data akhir
end_date = datetime.now().date()
# Mengubah format tanggal ke string yang diterima oleh yfinance
end_date_str = end_date.strftime("%Y-%m-%d")
if st.button("Klik Me"):
    data=yf.download(choice[selected_title],start=start_date_str,end=end_date_str)
    data = data.reset_index()  # Menghapus indeks tanggal
    lates_data= data.iloc[-1]
    # Format angka dengan tanda baca ribuan dan dua desimal
    open_price = "{:,.2f}".format(lates_data['Open'])
    close_price = "{:,.2f}".format(lates_data['Close'])
    change_price = "{:,.2f}".format(lates_data['Close'] - lates_data['Open'])
    percentage_change = "{:.2f}".format((lates_data['Close'] - lates_data['Open']) / lates_data['Open'] * 100)

    # Membuat teks status harga saham
    status_harga = f"{close_price}-{change_price} ({percentage_change}%)"

    # Menentukan warna teks berdasarkan perubahan harga
    if lates_data['Close'] > lates_data['Open']:
        color = 'green'
    else:
        color = 'red'

    # Menggunakan fitur-formatting teks dan CSS di Streamlit untuk menampilkan status harga saham dengan warna yang sesuai
    st.markdown(
        f'<p style="font-size:24px;color:{color};font-weight:bold;">{status_harga}</p>',
        unsafe_allow_html=True
    )
    fig = go.Figure(data=go.Scatter(x=data['Date'], y=data['Close'], mode='lines', name='Harga Saham'))
    fig.update_layout(xaxis_title="Waktu", yaxis_title="Harga Saham dalam Rupiah (IDR)")
    st.plotly_chart(fig)
    # Menghitung interval kepercayaan
    data["Daily Return"] = data['Adj Close'].pct_change()
    confidence_interval = data["Daily Return"].quantile([0.025, 0.975])

    fig_interval = go.Figure()
    fig_interval.add_trace(go.Scatter(x=data['Date'], y=data['Adj Close'], name='Stock Price'))
    fig_interval.add_trace(go.Scatter(x=data['Date'], y=[confidence_interval.iloc[0]]*len(data), fill=None, mode='lines', line_color='gray', name='Confidence Interval'))
    fig_interval.add_trace(go.Scatter(x=data['Date'], y=[confidence_interval.iloc[1]]*len(data), fill='tonexty', mode='lines', line_color='gray', name='Confidence Interval'))

    fig_interval.update_layout(
        xaxis_title='Date',
        yaxis_title='Adjusted Close Price',
        title='Stock Price with 5% Confidence Interval',
        legend=dict(
            x=1,
            y=0,
            bgcolor='rgba(255, 255, 255, 0.5)',
            bordercolor='rgba(0, 0, 0, 0.5)'
        )
    )

    st.plotly_chart(fig_interval)
    
    # Menyusun ulang kolom sesuai format yang diperlukan oleh Prophet
    df_model = data[['Date', 'Close']].copy()
    df_model.columns = ['ds', 'y']
    model=Prophet()
    model.fit(df_model)
    # Membuat dataframe dengan tanggal untuk prediksi di masa depan
    periode=[7,15,30]
    #choice_periode=st.selectbox("Pilih Periode",periode)
    future = model.make_future_dataframe(periods=21)  # Prediksi untuk 7 hari ke depan

    # Melakukan prediksi
    forecast = model.predict(future)

    # Menampilkan plot prediksi
    fig = model.plot(forecast)
    st.pyplot(fig)
