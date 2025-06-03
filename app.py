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

def create_analysis_section(df, text_column, category_column=None, category_value=None, max_words=100):
    """
    Membuat section analisis untuk data tertentu
    """
    # Filter data berdasarkan kategori jika ada
    if category_column is not None and category_value is not None:
        filtered_df = df[df[category_column] == category_value]
        title_suffix = f" - {category_value}"
        file_suffix = f"_{category_value.replace(' ', '_')}"
    else:
        filtered_df = df
        title_suffix = ""
        file_suffix = ""
    
    if len(filtered_df) == 0:
        st.warning(f"Tidak ada data untuk kategori: {category_value}")
        return
    
    # Gabungkan semua teks dari kolom yang dipilih
    all_text = ' '.join(filtered_df[text_column].astype(str))
    
    # Bersihkan teks
    cleaned_text = clean_text(all_text)
    
    if not cleaned_text.strip():
        st.error(f"❌ Tidak ada teks yang tersisa setelah pembersihan{title_suffix}!")
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
    st.subheader(f"☁️ WordCloud{title_suffix}")
    fig, ax = plt.subplots(figsize=(15, 8))
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis('off')
    st.pyplot(fig)
    
    # Statistik kata
    st.subheader(f"📊 Statistik Kata{title_suffix}")
    words = cleaned_text.split()
    word_freq = Counter(words)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Kata Unik", len(word_freq))
    with col2:
        st.metric("Total Kata", len(words))
    with col3:
        st.metric("Rata-rata Panjang Kata (Huruf)", f"{np.mean([len(w) for w in words]):.1f}")
    
    # Top kata paling sering
    st.subheader(f"📝 Kata Yang Muncul{title_suffix}")
    top_words = word_freq.most_common(200)
    
    if top_words:
        # Buat dataframe untuk ditampilkan
        top_df = pd.DataFrame(top_words, columns=['Kata', 'Frekuensi'])
        
        col1, col2 = st.columns(2)
        with col1:
            st.dataframe(top_df, use_container_width=True)
        
        with col2:
            # Buat pie chart untuk top 10 kata
            fig, ax = plt.subplots(figsize=(10, 8))
            words_list = [item[0] for item in top_words[:10]]
            freq_list = [item[1] for item in top_words[:10]]
            
            # Buat warna yang menarik
            colors = plt.cm.Set3(np.linspace(0, 1, len(words_list)))
            
            wedges, texts, autotexts = ax.pie(
                freq_list, 
                labels=words_list, 
                autopct='%1.1f%%', 
                startangle=140,
                colors=colors,
                explode=[0.05] * len(words_list)  # Sedikit pisahkan setiap slice
            )
            
            # Styling untuk text
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
                autotext.set_fontsize(9)
            
            for text in texts:
                text.set_fontsize(10)
                text.set_fontweight('bold')
            
            ax.set_title(f"Top 10 Kata Paling Sering{title_suffix} (Pie Chart)", 
                        fontsize=14, fontweight='bold', pad=20)
            ax.axis('equal')  # Supaya bentuknya bulat sempurna
            
            st.pyplot(fig)
    
    # Download section
    st.subheader(f"💾 Download{title_suffix}")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Simpan wordcloud sebagai image
        img_buffer = io.BytesIO()
        wordcloud.to_image().save(img_buffer, format='PNG')
        img_buffer.seek(0)
        
        st.download_button(
            label=f"📥 Download WordCloud{title_suffix} (PNG)",
            data=img_buffer.getvalue(),
            file_name=f"wordcloud_{text_column}{file_suffix}.png",
            mime="image/png"
        )
    
    with col2:
        # Download data kata yang sudah dibersihkan
        cleaned_words_df = pd.DataFrame(list(word_freq.items()), 
                                      columns=['Kata', 'Frekuensi'])
        cleaned_words_df = cleaned_words_df.sort_values('Frekuensi', ascending=False)
        
        csv_buffer = io.StringIO()
        cleaned_words_df.to_csv(csv_buffer, index=False)
        
        st.download_button(
            label=f"📥 Download Data Kata{title_suffix} (CSV)",
            data=csv_buffer.getvalue(),
            file_name=f"word_frequency_{text_column}{file_suffix}.csv",
            mime="text/csv"
        )

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
            col1, col2, col3 = st.columns(3)
            
            with col1:
                selected_column = st.selectbox(
                    "Pilih kolom teks untuk wordcloud:",
                    text_columns,
                    help="Pilih kolom yang berisi teks untuk dianalisis"
                )
            
            with col2:
                # Pilih kolom kategori
                category_column = st.selectbox(
                    "Pilih kolom kategori (opsional):",
                    ["Tidak ada"] + text_columns,
                    help="Pilih kolom yang berisi kategori untuk analisis terpisah"
                )
            
            with col3:
                max_words = st.slider(
                    "Maksimal kata dalam wordcloud:",
                    min_value=20,
                    max_value=200,
                    value=100,
                    step=10
                )
            
            # Jika kolom kategori dipilih, tampilkan informasi kategori
            if category_column != "Tidak ada":
                st.sidebar.subheader("📊 Informasi Kategori")
                unique_categories = df[category_column].unique()
                for cat in unique_categories:
                    count = len(df[df[category_column] == cat])
                    percentage = (count / len(df)) * 100
                    st.sidebar.info(f"**{cat}**: {count} data ({percentage:.1f}%)")
            
            if st.button("🚀 Generate WordCloud", type="primary"):
                with st.spinner("Memproses data dan membuat wordcloud..."):
                    
                    # Jika kategori dipilih, buat analisis terpisah
                    if category_column != "Tidak ada":
                        unique_categories = df[category_column].unique()
                        
                        # Buat tabs untuk setiap kategori + tab untuk semua data
                        tab_names = ["📊 Semua Data"] + [f"📋 {cat}" for cat in unique_categories]
                        tabs = st.tabs(tab_names)
                        
                        # Tab untuk semua data
                        with tabs[0]:
                            create_analysis_section(df, selected_column, max_words=max_words)
                        
                        # Tab untuk setiap kategori
                        for i, category_value in enumerate(unique_categories, 1):
                            with tabs[i]:
                                create_analysis_section(
                                    df, 
                                    selected_column, 
                                    category_column=category_column,
                                    category_value=category_value,
                                    max_words=max_words
                                )
                    else:
                        # Jika tidak ada kategori, tampilkan analisis untuk semua data
                        create_analysis_section(df, selected_column, max_words=max_words)
        
        except Exception as e:
            st.error(f"❌ Error saat memproses file: {str(e)}")
            st.info("💡 Pastikan file CSV Anda memiliki format yang benar dan berisi data teks.")
    
    else:
        # Tampilkan instruksi jika belum ada file yang diupload
        st.info("👆 Silakan upload file CSV di sidebar untuk memulai")
        
        # Contoh format CSV dengan kategori
        st.subheader("📝 Contoh Format CSV")
        sample_data = {
            'nama_produk': ['Laptop Gaming', 'Mouse Wireless', 'Keyboard Mechanical', 'Monitor 4K'],
            'deskripsi': [
                'Laptop gaming dengan performa tinggi untuk bermain game',
                'Mouse wireless yang nyaman digunakan untuk kerja sehari-hari',
                'Keyboard mechanical dengan switch yang responsif dan tahan lama',
                'Monitor 4K dengan kualitas gambar yang sangat jernih'
            ],
            'kategori': ['ASN', 'selain ASN', 'ASN', 'selain ASN']
        }
        sample_df = pd.DataFrame(sample_data)
        st.dataframe(sample_df, use_container_width=True)
        
        st.markdown("""
        **Fitur Aplikasi:**
        - 📁 Upload file CSV dengan mudah
        - 🔍 Pilih kolom teks yang ingin dianalisis
        - 🧹 Pembersihan otomatis kata penghubung bahasa Indonesia
        - 🔄 Analisis berdasarkan kategori (ASN/selain ASN atau kategori lainnya)
        - ☁️ Generate wordcloud yang menarik
        - 📊 Statistik dan analisis frekuensi kata
        - 🥧 Visualisasi pie chart untuk top 10 kata
        - 💾 Download hasil wordcloud dan data
        """)

if __name__ == "__main__":
    main()
