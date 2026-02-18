import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="AVP Fund Finder", layout="wide")

@st.cache_data(show_spinner=False)
def load_data_fast():
    pq_file, excel_file = 'data_cache.parquet', 'Factsheet_for_web.xlsx'
    if os.path.exists(pq_file): return pd.read_parquet(pq_file)
    if os.path.exists(excel_file):
        df = pd.read_excel(excel_file, engine='openpyxl')
        df.columns = df.columns.str.strip()
        df.to_parquet(pq_file)
        return df
    return pd.DataFrame()

df = load_data_fast()
st.title("⚡ ค้นหา FFS กองทุน (ฉบับเสี้ยววินาที)")

if not df.empty:
    query = st.text_input("🔍 พิมพ์ชื่อกองทุน:", placeholder="เช่น SCB, K-CASH...").strip()
    filtered = df[df['fund_name'].astype(str).str.contains(query, case=False, na=False)] if query else df.head(20)

    st.write(f"พบข้อมูล {len(filtered)} รายการ")
    h1, h2, h3 = st.columns([3, 2, 1.5])
    h1.write("**ชื่อกองทุน**"); h2.write("**อัปเดตเมื่อ**"); h3.write("**เอกสาร**")
    st.divider()

    for i, row in filtered.iterrows():
        c1, c2, c3 = st.columns([3, 2, 1.5])
        c1.write(row['fund_name'])
        c2.write(str(row['as_of_date']))
        
        # ผมแก้ตัวแปรใหม่หมดแล้ว ถ้ามันยัง Error คำว่า pdf_url แปลว่าพี่เซฟผิดไฟล์ครับ 100%
        final_document_link = str(row.get('link_pdf_factsheet', '#'))
        
        btn = f'''<a href="{final_document_link}" target="_blank" style="text-decoration:none;"><div style="background-color:#ff4b4b;color:white;padding:8px;border-radius:6px;text-align:center;font-weight:bold;cursor:pointer;">📄 เปิด PDF</div></a>'''
        c3.markdown(btn, unsafe_allow_html=True)