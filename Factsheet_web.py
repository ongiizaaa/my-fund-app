import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Instant Fund Finder", layout="wide")

# --- ฟังก์ชันโหลดข้อมูลแบบ Super Fast ---
@st.cache_data(show_spinner=False)
def load_data_fast():
    pq_file = 'data_cache.parquet'
    excel_file = 'Factsheet_for_web.xlsx'
    
    if os.path.exists(pq_file):
        return pd.read_parquet(pq_file)
    
    if os.path.exists(excel_file):
        df = pd.read_excel(excel_file, engine='openpyxl')
        df.columns = df.columns.str.strip()
        df.to_parquet(pq_file) 
        return df
    else:
        st.error("ไม่พบไฟล์ Factsheet_for_web.xlsx")
        return pd.DataFrame()

df = load_data_fast()

st.title("⚡ ค้นหากองทุน (ฉบับเสี้ยววินาที)")

if not df.empty:
    query = st.text_input("🔍 พิมพ์ชื่อกองทุน:", placeholder="เช่น SCB, K-CASH, HIDIV...", key="search_input").strip()

    if query:
        filtered_df = df[df['fund_name'].astype(str).str.contains(query, case=False, na=False)]
    else:
        filtered_df = df.head(20)

    # --- ส่วนการแสดงผลแบบใหม่ เพื่อให้เปิดแท็บใหม่ได้ ---
    st.write(f"พบข้อมูล {len(filtered_df)} รายการ")
    
    # สร้าง Header ของตารางแบบง่าย
    cols = st.columns([3, 2, 2])
    cols[0].write("**ชื่อกองทุน**")
    cols[1].write("**อัปเดตเมื่อ**")
    cols[2].write("**เอกสาร (เปิดหน้าใหม่)**")
    st.divider()

    # วนลูปแสดงผลรายรายการ
    for index, row in filtered_df.iterrows():
        c1, c2, c3 = st.columns([3, 2, 2])
        
        c1.write(row['fund_name'])
        c2.write(str(row['as_of_date']))
        
        # สูตรเด็ด: สร้างปุ่ม HTML ที่บังคับเปิดแท็บใหม่
        pdf_url = row['link_pdf