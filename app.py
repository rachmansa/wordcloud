import streamlit as st
import pandas as pd
import numpy as np
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import re
from collections import Counter
import io

# Daftar kata penghubung bahasa Indonesia yang akan dihapus
STOPWORDS_INDONESIA = {
    'dan', 'yang', 'atau', 'di', 'ke', 'dari', 'untuk', 'dengan', 'pada',
    'dalam', 'oleh', 'sebagai', 'adalah', 'akan', 'telah', 'sudah', 'belum',
    'tidak', 'bukan', 'juga', 'dapat', 'bisa', 'harus', 'perlu', 'mungkin',
    'karena', 'sehingga', 'namun', 'tetapi', 'jika', 'kalau', 'apabila',
    'ketika', 'saat', 'waktu', 'setelah', 'sebelum', 'selama', 'hingga',
    'sampai', 'antara', 'atas', 'bawah', 'depan', 'belakang', 'kiri', 'kanan',
    'ini', 'itu', 'tersebut', 'mereka', 'kami', 'kita', 'saya', 'anda',
    'dia', 'ia', 'nya', 'mu', 'ku', 'kamu', 'kalian', 'beliau',
    'ada', 'ada', 'adanya', 'bahwa', 'hal', 'cara', 'bagaimana', 'mengapa',
    'kapan', 'dimana', 'kemana', 'darimana', 'siapa', 'apa', 'mana',
    'sangat', 'sekali', 'lebih', 'paling', 'agak', 'cukup', 'kurang',
    'hampir', 'kira', 'sekitar', 'rata', 'semua', 'setiap', 'masing',
    'beberapa', 'banyak', 'sedikit', 'seluruh', 'sebagian', 'lain',
    'lainnya', 'sendiri', 'bersama', 'sama', 'berbeda', 'beda'
}

def clean_text(text):
    """
    Membersihkan teks dengan menghapus karakter khusus, angka, 
    dan kata penghubung bahasa Indonesia
    """
    if pd.isna(text):
        return ""
    
    # Konversi ke string dan lowercase
    text = str(text).lower()
    
    # Hapus karakter khusus dan angka, hanya simpan huruf dan spasi
    text = re.sub(r'[^a-zA-Z\s]', ' ', text)
    
    # Hapus spasi berlebih
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Split menjadi kata-kata
    words = text.split()
    
    # Filter kata yang bukan stopwords dan panjangnya > 2
    filtered_words = [word for word in words 
                     if word not in STOPWORDS_INDONESIA and len(word) > 2]
    
    return ' '.join(filtered_words)

def generate_wordcloud(text, width=800, height=400):
    """
    Membuat wordcloud dari teks yang sudah dibersihkan
    """
    if not text.strip():
        return None
    
    wordcloud = WordCloud(
        width=width,
        height=height,
        background_color='white',
        max_words=100,
        colormap='viridis',
        relative_scaling=0.5,
        random_state=42
    ).generate(text)
    
    return wordcloud

def main():
    st.set_page_config(
        page_title="CSV WordCloud Generator",
        page_icon="☁️",
        layout="wide"
    )
    
    st.title("☁️ CSV WordCloud Generator")
    st.markdown("**Buat wordcloud dari data teks dalam file CSV Anda**")
    
    # Sidebar untuk upload file
    st.sidebar.header("📁 Upload File CSV")
    uploaded_file = st.sidebar.file_uploader(
        "Pilih file CSV",
        type=['csv'],
        help="Upload file CSV yang berisi kolom teks untuk dianalisis"
    )
    
    if uploaded_file is not None:
        try:
            # Baca file CSV
            df = pd.read_csv(uploaded_file)
            
            st.sidebar.success(f"✅ File berhasil dimuat!")
            st.sidebar.info(f"📊 Jumlah baris: {len(df)}")
            st.sidebar.info(f"📋 Jumlah kolom: {len(df.columns)}")
            
            # Tampilkan preview data
            st.subheader("📋 Preview Data")
            st.dataframe(df.head(), use_container_width=True)
            
            # Pilih kolom teks
            text_columns = df.select_dtypes(include=['object']).columns.tolist()
            
            if not text_columns:
                st.error("❌ Tidak ada kolom teks yang ditemukan dalam file CSV!")
                return
            
            st.subheader("⚙️ Pengaturan")
            col1, col2 = st.columns(2)
            
            with col1:
                selected_column = st.selectbox(
                    "Pilih kolom teks untuk wordcloud:",
                    text_columns,
                    help="Pilih kolom yang berisi teks untuk dianalisis"
                )
            
            with col2:
                max_words = st.slider(
                    "Maksimal kata dalam wordcloud:",
                    min_value=20,
                    max_value=200,
                    value=100,
                    step=10
                )
            
            if st.button("🚀 Generate WordCloud", type="primary"):
                with st.spinner("Memproses data dan membuat wordcloud..."):
                    # Gabungkan semua teks dari kolom yang dipilih
                    all_text = ' '.join(df[selected_column].astype(str))
                    
                    # Bersihkan teks
                    cleaned_text = clean_text(all_text)
                    
                    if not cleaned_text.strip():
                        st.error("❌ Tidak ada teks yang tersisa setelah pembersihan!")
                        return
                    
                    # Generate wordcloud
                    wordcloud = WordCloud(
                        width=1200,
                        height=600,
                        background_color='white',
                        max_words=max_words,
                        colormap='viridis',
                        relative_scaling=0.5,
                        random_state=42
                    ).generate(cleaned_text)
                    
                    # Tampilkan wordcloud
                    st.subheader("☁️ WordCloud")
                    fig, ax = plt.subplots(figsize=(15, 8))
                    ax.imshow(wordcloud, interpolation='bilinear')
                    ax.axis('off')
                    st.pyplot(fig)
                    
                    # Statistik kata
                    st.subheader("📊 Statistik Kata")
                    words = cleaned_text.split()
                    word_freq = Counter(words)
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Total Kata Unik", len(word_freq))
                    with col2:
                        st.metric("Total Kata", len(words))
                    with col3:
                        st.metric("Rata-rata Panjang Kata (Huruf)", f"{np.mean([len(w) for w in words]):.1f}")
                    
                    # Top 20 kata paling sering
                    st.subheader(" Kata Yang Muncul")
                    top_words = word_freq.most_common(200)
                    
                    if top_words:
                        # Buat dataframe untuk ditampilkan
                        top_df = pd.DataFrame(top_words, columns=['Kata', 'Frekuensi'])
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.dataframe(top_df, use_container_width=True)
                        
                        with col2:
                            # Buat pie chart
                            fig, ax = plt.subplots(figsize=(8, 8))
                            words_list = [item[0] for item in top_words[:10]]
                            freq_list = [item[1] for item in top_words[:10]]
                            
                            ax.pie(freq_list, labels=words_list, autopct='%1.1f%%', startangle=140)
                            ax.set_title("Top 10 Kata Paling Sering (Pie Chart)")
                            ax.axis('equal')  # Supaya bentuknya bulat sempurna
                            
                            st.pyplot(fig)
                    
                    # Download wordcloud
                    st.subheader("💾 Download")
                    
                    # Simpan wordcloud sebagai image
                    img_buffer = io.BytesIO()
                    wordcloud.to_image().save(img_buffer, format='PNG')
                    img_buffer.seek(0)
                    
                    st.download_button(
                        label="📥 Download WordCloud (PNG)",
                        data=img_buffer.getvalue(),
                        file_name=f"wordcloud_{selected_column}.png",
                        mime="image/png"
                    )
                    
                    # Download data kata yang sudah dibersihkan
                    cleaned_words_df = pd.DataFrame(list(word_freq.items()), 
                                                  columns=['Kata', 'Frekuensi'])
                    cleaned_words_df = cleaned_words_df.sort_values('Frekuensi', ascending=False)
                    
                    csv_buffer = io.StringIO()
                    cleaned_words_df.to_csv(csv_buffer, index=False)
                    
                    st.download_button(
                        label="📥 Download Data Kata (CSV)",
                        data=csv_buffer.getvalue(),
                        file_name=f"word_frequency_{selected_column}.csv",
                        mime="text/csv"
                    )
        
        except Exception as e:
            st.error(f"❌ Error saat memproses file: {str(e)}")
            st.info("💡 Pastikan file CSV Anda memiliki format yang benar dan berisi data teks.")
    
    else:
        # Tampilkan instruksi jika belum ada file yang diupload
        st.info("👆 Silakan upload file CSV di sidebar untuk memulai")
        
        
        
        st.markdown("""
        **Fitur Aplikasi:**
        - 📁 Upload file CSV dengan mudah
        - 🔍 Pilih kolom teks yang ingin dianalisis
        - 🧹 Pembersihan otomatis kata penghubung bahasa Indonesia
        - ☁️ Generate wordcloud yang menarik
        - 📊 Statistik dan analisis frekuensi kata
        - 💾 Download hasil wordcloud dan data
        """)

if __name__ == "__main__":
    main()