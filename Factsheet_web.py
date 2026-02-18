import streamlit as st
import pandas as pd
import os

# 1. ตั้งค่าหน้าเว็บให้เหมาะสมกับทั้งคอมและมือถือ
st.set_page_config(page_title="AVP Fund Finder", layout="wide")

# 2. ฟังก์ชันโหลดข้อมูลแบบรวดเร็วพิเศษ (Parquet Cache)
@st.cache_data(show_spinner=False)
def load_data_fast():
    pq_file, excel_file = 'data_cache.parquet', 'Factsheet_for_web.xlsx'
    # โหลดจาก Cache ถ้ามีไฟล์อยู่แล้ว
    if os.path.exists(pq_file):
        return pd.read_parquet(pq_file)
    # ถ้าไม่มี ให้โหลดจาก Excel แล้วสร้าง Cache ไว้
    if os.path.exists(excel_file):
        df = pd.read_excel(excel_file, engine='openpyxl')
        df.columns = df.columns.str.strip() # ตัดช่องว่างหัวตารางป้องกัน Error
        df.to_parquet(pq_file)
        return df
    return pd.DataFrame()

df = load_data_fast()

# 3. หัวข้อเว็บแบบใหม่ (FFS) และขึ้นบรรทัดใหม่อัตโนมัติ
st.title("⚡ ค้นหา FFS \nกองทุน (ฉบับเสี้ยววินาที)")

if not df.empty:
    # ส่วนช่องค้นหา (Search Box)
    query = st.text_input("🔍 พิมพ์ชื่อกองทุน:", placeholder="เช่น SCB, K-CASH...").strip()

    # กรองข้อมูลใน RAM (ความเร็วสูง)
    if query:
        filtered_df = df[df['fund_name'].astype(str).str.contains(query, case=False, na=False)]
    else:
        filtered_df = df.head(20)

    st.write(f"พบข้อมูล {len(filtered_df)} รายการ")
    
    # 4. ส่วนหัวตารางแสดงผล
    c1, c2, c3 = st.columns([3, 2, 1.5])
    c1.write("**ชื่อกองทุน**")
    c2.write("**อัปเดตเมื่อ**")
    c3.write("**เอกสาร (เปิดดูทันที)**")
    st.divider()

    # 5. วนลูปแสดงผล และใช้ Google Docs Viewer เพื่อแก้ปัญหาเปิดในมือถือไม่ได้
    for index, row in filtered_df.iterrows():
        col1, col2, col3 = st.columns([3, 2, 1.5])
        
        col1.write(row['fund_name'])
        col2.write(str(row['as_of_date']))
        
        # ดึง URL จากคอลัมน์ link_pdf_factsheet
        raw_link = str(row.get('link_pdf_factsheet', '#'))
        
        # ใช้ Google Docs Viewer ช่วยเรนเดอร์ PDF ป้องกันการดาวน์โหลดลงเครื่องบนมือถือ
        view_link = f"https://docs.google.com/viewer?url={raw_link}&embedded=true"
        
        # สร้างปุ่ม HTML แบบเปิดแท็บใหม่ (target="_blank")
        btn_html = f'''
            <a href="{view_link}" target="_blank" style="text-decoration: none;">
                <div style="
                    background-color: #ff4b4b;
                    color: white;
                    padding: 8px 12px;
                    border-radius: 6px;
                    text-align: center;
                    font-size: 14px;
                    font-weight: bold;
                    cursor: pointer;
                    transition: 0.3s;
                " onmouseover="this.style.backgroundColor='#d32f2f'" onmouseout="this.style.backgroundColor='#ff4b4b'">
                    📄 เปิดดู PDF
                </div>
            </a>
        '''
        col3.markdown(btn_html, unsafe_allow_html=True)
    
    if not query:
        st.caption("💡 แสดง 20 รายการล่าสุด พิมพ์ชื่อกองทุนเพื่อค้นหาทั้งหมด...")