import streamlit as st
st.image("logo.jpg")
import pandas as pd

# Cấu hình trang
st.set_page_config(page_title="Tính Lãi Tiết Kiệm", page_icon="💰", layout="centered")

st.title("💰 Ứng Dụng Tính Lãi Gửi Tiết Kiệm")
st.markdown("Nhập các thông tin bên dưới để tính toán số tiền lãi bạn sẽ nhận được.")

# Tạo các cột nhập liệu
col1, col2 = st.columns(2)

with col1:
    so_tien_goc = st.number_input("Số tiền gửi (VNĐ)", min_value=0.0, value=100000000.0, step=1000000.0)
    ky_han = st.number_input("Kỳ hạn (tháng)", min_value=1, value=12, step=1)

with col2:
    lai_suat_nam = st.number_input("Lãi suất (%/năm)", min_value=0.0, value=6.0, step=0.1)
    hinh_thuc_nhan_lai = st.selectbox(
        "Hình thức nhận lãi", 
        options=["Cuối kỳ", "Hàng tháng", "Hàng quý"]
    )

loai_lai = st.radio("Loại lãi suất", options=["Lãi đơn", "Lãi kép"], horizontal=True)

# Xử lý Logic tính toán
if st.button("Tính Toán", type="primary", use_container_width=True):
    
    # Xác định số tháng trong một kỳ trả lãi
    if hinh_thuc_nhan_lai == "Hàng tháng":
        thang_mot_ky = 1
    elif hinh_thuc_nhan_lai == "Hàng quý":
        thang_mot_ky = 3
    else: # Cuối kỳ
        thang_mot_ky = ky_han
        
    # Cảnh báo nếu kỳ hạn không chia hết cho kỳ trả lãi (đối với hàng quý)
    if ky_han % thang_mot_ky != 0:
        st.warning(f"Lưu ý: Kỳ hạn {ky_han} tháng không chia tròn cho kỳ trả lãi {hinh_thuc_nhan_lai.lower()} ({thang_mot_ky} tháng/kỳ). Tiền lãi của các tháng lẻ cuối cùng sẽ được tính theo số ngày thực tế, nhưng app sẽ tạm tính tròn theo số kỳ.")

    so_ky = ky_han // thang_mot_ky
    lai_suat_thang = (lai_suat_nam / 100) / 12
    lai_suat_ky = lai_suat_thang * thang_mot_ky
    
    tong_tien_lai = 0
    tong_tien_nhan = 0
    tien_lai_dinh_ky = 0
    
    # Danh sách lưu lịch sử nếu là lãi kép
    lich_su = []
    so_du_hien_tai = so_tien_goc

    if loai_lai == "Lãi đơn":
        # Tính lãi đơn
        tong_tien_lai = so_tien_goc * lai_suat_thang * ky_han
        tong_tien_nhan = so_tien_goc + tong_tien_lai
        if so_ky > 0:
            tien_lai_dinh_ky = tong_tien_lai / (ky_han / thang_mot_ky)
            
    else:
        # Tính lãi kép
        for i in range(1, so_ky + 1):
            lai_ky_nay = so_du_hien_tai * lai_suat_ky
            so_du_hien_tai += lai_ky_nay
            lich_su.append({
                "Kỳ": f"Kỳ {i}",
                "Số dư đầu kỳ (VNĐ)": round(so_du_hien_tai - lai_ky_nay),
                "Tiền lãi sinh ra (VNĐ)": round(lai_ky_nay),
                "Số dư cuối kỳ (VNĐ)": round(so_du_hien_tai)
            })
            
        tong_tien_nhan = so_du_hien_tai
        tong_tien_lai = tong_tien_nhan - so_tien_goc
        tien_lai_dinh_ky = lich_su[0]["Tiền lãi sinh ra (VNĐ)"] if lich_su else 0

    # Hiển thị kết quả
    st.markdown("---")
    st.subheader("📊 Kết Quả Ước Tính")
    
    m1, m2, m3 = st.columns(3)
    with m1:
        st.metric(label="Tổng số tiền gốc", value=f"{so_tien_goc:,.0f} đ")
    with m2:
        st.metric(label="Tổng tiền lãi", value=f"{tong_tien_lai:,.0f} đ")
    with m3:
        st.metric(label="Tổng gốc + lãi", value=f"{tong_tien_nhan:,.0f} đ")
        
    st.info(f"💡 **Tiền lãi định kỳ ({hinh_thuc_nhan_lai.lower()}):** " + 
            (f"{tien_lai_dinh_ky:,.0f} đ" if loai_lai == "Lãi đơn" 
             else f"Bắt đầu từ {tien_lai_dinh_ky:,.0f} đ (Tăng dần theo mỗi kỳ do cộng gộp gốc)"))

    # Hiển thị bảng chi tiết cho Lãi Kép
    if loai_lai == "Lãi kép" and so_ky > 1:
        st.write("### 📈 Chi tiết diễn biến lãi kép từng kỳ")
        df_lich_su = pd.DataFrame(lich_su)
        
        # Format lại bảng cho đẹp
        st.dataframe(
            df_lich_su.style.format({
                "Số dư đầu kỳ (VNĐ)": "{:,.0f}",
                "Tiền lãi sinh ra (VNĐ)": "{:,.0f}",
                "Số dư cuối kỳ (VNĐ)": "{:,.0f}"
            }),
            use_container_width=True
        )
