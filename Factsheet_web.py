import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Instant Fund Finder", layout="wide")

# --- ฟังก์ชันโหลดข้อมูลแบบ Super Fast ---
@st.cache_data(show_spinner=False)
def load_data_fast():
    pq_file = 'data_cache.parquet'
    excel_file = 'Factsheet_for_web.xlsx'
    
    # ถ้ามีไฟล์ Parquet อยู่แล้ว จะโหลดใน 0.01 วินาที
    if os.path.exists(pq_file):
        return pd.read_parquet(pq_file)
    
    # ถ้าไม่มี ให้โหลด Excel แล้วเซฟเป็น Parquet ไว้ใช้ครั้งหน้า
    if os.path.exists(excel_file):
        df = pd.read_excel(excel_file, engine='openpyxl')
        df.columns = df.columns.str.strip()
        df.to_parquet(pq_file) # เซฟไว้เป็น Cache ความเร็วสูง
        return df
    else:
        st.error("ไม่พบไฟล์ Factsheet_for_web.xlsx")
        return pd.DataFrame()

# โหลดข้อมูลเข้า RAM ทันทีที่เปิดเว็บ
df = load_data_fast()

st.title("⚡ ค้นหากองทุน (ฉบับเสี้ยววินาที)")

if not df.empty:
    # ส่วนค้นหา (Search)
    query = st.text_input("🔍 พิมพ์ชื่อกองทุน:", placeholder="เช่น SCB, K-CASH, HIDIV...", key="search_input").strip()

    # กรองข้อมูลในหน่วยความจำ (RAM) - เร็วมาก
    if query:
        filtered_df = df[df['fund_name'].astype(str).str.contains(query, case=False, na=False)]
    else:
        # ถ้ายังไม่ search ให้โชว์แค่ 20 อันพอ เพื่อความเร็วตอนเปิดหน้าแรก
        filtered_df = df.head(20)

    # แสดงผลด้วย st.dataframe (จัดการ Rendering แบบความเร็วสูง)
    st.dataframe(
        filtered_df,
        column_config={
            "link_pdf_factsheet": st.column_config.LinkColumn(
                "Fact Sheet PDF",
                display_text="📄 เปิดดูเอกสาร"
            ),
            "fund_name": "ชื่อกองทุน",
            "as_of_date": "อัปเดตเมื่อ"
        },
        hide_index=True,
        use_container_width=True,
        height=500 # กำหนดความสูงเพื่อความลื่นไหล
    )
    
    if not query:
        st.caption("💡 แสดง 20 รายการล่าสุด พิมพ์ชื่อกองทุนเพื่อค้นหาทั้งหมด...")