import streamlit as st
from openai import OpenAI

# 頁面配置
st.set_page_config(page_title="寓蟄 | 空間設計視覺提案工具", layout="wide")

# --- 1. OpenAI API 設定 (從 Streamlit Secrets 讀取) ---
# 部署至 GitHub 並連結 Streamlit Cloud 時，請在 Settings > Secrets 加入 OPENAI_API_KEY
api_key = st.secrets.get("OPENAI_API_KEY")

if not api_key:
    st.sidebar.warning("🔑 尚未設定 API Key。請在 Secrets 中設定 OPENAI_API_KEY 以啟用 AI 繪圖功能。")
    # 若為本地開發測試，可手動輸入
    api_key = st.sidebar.text_input("或手動輸入 API Key 用於測試", type="password")

client = OpenAI(api_key=api_key) if api_key else None

# --- 2. 自定義 CSS ---
st.markdown(f"""
    <style>
    .stApp {{ background-color: #9c9e88; }}
    div.stButton > button:first-child {{
        background-color: #FFBF00; color: white; border-radius: 5px;
        border: none; padding: 0.7rem 2.5rem; font-weight: bold;
        font-size: 18px; box-shadow: 0px 4px 10px rgba(0,0,0,0.1);
    }}
    [data-testid="stVerticalBlock"] > div {{
        background-color: rgba(255, 255, 255, 0.1); padding: 10px; border-radius: 10px;
    }}
    h1, h2, h3, p, label {{ color: #ffffff !important; }}
    .stTextInput input, .stSelectbox div, .stTextArea textarea {{ color: #333333 !important; }}
    .stCode {{ background-color: #ffffff !important; }}
    .stCode code {{ color: #000000 !important; font-size: 16px !important; line-height: 1.6; }}
    </style>
""", unsafe_allow_html=True)

st.title("🏛️ 寓蟄 | 空間設計視覺提案工具")

# --- 3. 第一階段：空間區域設定 ---
with st.container():
    col1, col2 = st.columns(2)
    with col1:
        space_type = st.radio("空間性質", ["住家", "店家"])
        if space_type == "店家":
            brand_name = st.text_input("品牌名稱", placeholder="寓蟄設計")
            shop_type = st.text_input("店家性質", placeholder="藝廊、咖啡廳、服飾店")
            target_areas = st.multiselect("渲染的空間區域", ["用餐區", "櫃檯區", "展示區", "更衣室", "戶外座位區", "大廳", "包廂"], default=["用餐區"])
        else:
            brand_name, shop_type = "私人住宅", "居家空間"
            home_areas = ["客廳", "餐廳", "廚房", "主臥室", "次臥室", "客房", "書房", "和室", "中島廚房", "陽台", "玄關", "更衣間", "浴室", "交誼廳", "兒童房", "儲藏室"]
            target_areas = st.multiselect("渲染的空間區域", home_areas, default=["客廳"])
            
    with col2:
        total_size = st.slider("總空間坪數", 1.0, 200.0, 30.0, step=0.5)
        area_size = st.slider(f"渲染區域的預估坪數", 0.1, 100.0, 8.0, step=0.1)

st.divider()

# --- 第二階段：風格與情緒 ---
col3, col4 = st.columns(2)
with col3:
    style_options = ["日系原木風", "北歐極簡風", "韓系奶油風", "現代中式", "新中式禪風", "工業復古風", "輕奢華風", "極簡主義", "侘寂風 (Wabi-sabi)", "美式現代風", "法式優雅風", "波希米亞風", "賽博未來風", "包浩斯風", "英式古典", "裝飾藝術風 (Art Deco)"]
    selected_styles = st.multiselect("核心設計風格 (可多選混搭)", style_options, default=["日系原木風"])
    style_extra = st.text_input("風格額外補充說明")

with col4:
    moods = ["未來感", "高級感", "溫暖舒適", "奢華大氣", "現代俐落", "樸實自然", "明亮通透", "沈穩靜謐", "復古懷舊"]
    selected_moods = st.multiselect("空間情緒 (多選)", moods)
    color_scheme = st.text_input("整體配色方案", value="淺灰色調與溫潤木質相間")

st.divider()

# --- 第三階段：硬裝結構 ---
st.subheader("🧱 空間硬裝細節")
wall_num = st.select_slider("顯示牆面數量", options=[1, 2, 3])
mat_list = ["水泥漆","藝術漆", "木飾面", "大理石", "清水模", "紅磚", "特殊壁紙", "金屬烤漆", "長虹玻璃", "木格柵", "司曼特塗料"]
floor_materials = ["超耐磨木地板", "人字拼木地板", "魚骨拼木地板", "地毯", "拋光石英磚", "霧面磁磚", "六角磚", "花磚", "大理石材", "盤多魔 (Pandomo)", "無縫水泥找平", "水磨石", "波龍地毯", "長毛地毯", "塑膠地板 (SPC)"]

wall_data = []
col_w, col_cf = st.columns(2)
with col_w:
    for i in range(wall_num):
        st.write(f"**牆面 {i+1} 設定**")
        m = st.multiselect(f"材質 {i+1}", mat_list, key=f"m_{i}")
        c = st.text_input(f"顏色/說明 {i+1}", key=f"c_{i}")
        d = st.multiselect(f"裝飾物件 {i+1} (預設無)", ["無", "藝術掛畫", "內嵌衣櫃", "開放層架", "設計感壁燈", "線性燈條", "隱藏門", "圓拱門", "全身鏡"], default=["無"], key=f"d_{i}")
        wall_data.append({"mat": m, "color": c, "deco": d})

with col_cf:
    has_ceil = st.checkbox("包含天花板設計", value=True)
    ceil_detail = st.text_input("天花板造型說明") if has_ceil else "無"
    has_flr = st.checkbox("包含地面設計", value=True)
    f_selected_mats = st.multiselect("地板材質選擇", floor_materials) if has_flr else []
    f_desc = st.text_input("地面顏色/額外說明") if has_flr else ""

st.divider()

# --- 第四階段：攝影與窗戶系統 ---
st.subheader("📸 攝影與窗戶系統")
col5, col6 = st.columns(2)
with col5:
    lens_type = st.selectbox("鏡頭視角", ["16mm 超廣角渲染", "24mm 空間全景", "35mm 人眼視覺", "50mm 局部氛圍", "85mm 特寫細節"])
with col6:
    indoor_on = st.toggle("開啟人工光源", value=True)
    if indoor_on:
        k_temp = st.select_slider("燈光色溫 (K)", options=[2500, 3000, 3500, 4000, 5000, 6000])
        main_l = st.selectbox("主要燈具", ["崁燈", "磁吸軌道燈", "裝飾吊燈", "吸頂燈", "落地燈", "間照", "LED燈條"])
    sun_on = st.toggle("開啟自然採光")
    win_final_desc = "無窗戶"
    if sun_on:
        has_win = st.checkbox("是否配置窗戶", value=False)
        if has_win:
            win_style = st.selectbox("窗戶形式", ["落地大窗", "格子窗", "百葉窗帶來的光影", "圓窗", "氣密窗"])
            win_loc = st.multiselect("開窗牆面", [f"牆面 {i+1}" for i in range(wall_num)])
            win_final_desc = f"透過{win_style}射入，位於{'、'.join(win_loc)}"
        else:
            win_final_desc = "無窗戶，僅模擬自然環境擴散光"

st.divider()

# --- 第五階段：軟裝家具 ---
st.subheader("🛋️ 家具配置")
f_options = ["三人沙發", "雙人沙發", "單人扶手椅", "電視櫃", "圓形茶几", "長型餐桌", "中島吧台", "單人床", "雙人床", "床頭櫃", "鞋櫃", "梳妝台", "全身鏡", "衣桿", "開放式書架", "落地燈", "大型植栽"]
f_items = st.multiselect("選擇家具 (可多選)", f_options)
f_mat = st.text_input("家具主要材質描述", value="木質、棉麻、消光金屬")
other_note = st.text_area("其他特殊要求", value="無其他要求")

# --- 生成按鈕邏輯 ---
if st.button("🚀 生成寓蟄視覺提案提詞"):
    areas_str = "、".join(target_areas)
    styles_str = "、".join(selected_styles)
    floor_str = "、".join(f_selected_mats) if f_selected_mats else "未指定"
    wall_desc_list = []
    for idx, w in enumerate(wall_data):
        m_str = "、".join(w['mat'])
        d_str = "、".join([item for item in w['deco'] if item != "裝飾" and item != "無"])
        wall_desc_list.append(f"牆面{idx+1}(材質：{m_str}，顏色：{w['color']}，裝飾：{d_str if d_str else '簡潔'})")
    wall_final = "；".join(wall_desc_list)
    mood_str = "、".join(selected_moods)

    full_prompt = f"""你是一名空間設計師，根據以下內容生成一張空間設計配置圖
畫面為16:9橫式照片，並生產出超高擬真品質，具8K畫質的專業3D渲染圖。。
【空間描述】核心風格：{styles_str}。渲染區域：{areas_str}。
【空間性質】此處為{space_type}（{brand_name if space_type == '店家' else ''}），類型為{shop_type}。
【坪數構圖】總坪數{total_size}坪，渲染目標區域為{area_size}坪，展現精準的空間深度與透視比例。
【硬裝細節】
- 牆面設計：{wall_final}
- 天花板：{ceil_detail}
- 地面材質：{floor_str}。{f_desc}
【風格氛圍】營造出{mood_str}的情緒。整體色調：{color_scheme}。
【軟裝家具】包含：{', '.join(f_items)}。家具材質：{f_mat}。
【攝影光學】
- 鏡頭：{lens_type}，保持建築垂直線校正。
- 光源：{'室內人工光源（' + str(k_temp) + 'K，' + main_l + '照明）' if indoor_on else '關閉人工光源'}；自然光（{win_final_desc if sun_on else '關閉'}）。
【技術規範】高品質渲染、8K解析度、室內設計雜誌質感、極致細節、寫實陰影。
【備註】{other_note}"""

    st.markdown("### 生成結果 (請點擊右上方複製按鈕)")
    st.code(full_prompt, language=None)

    # AI 繪圖功能
    if client:
        with st.spinner("寓蟄 AI 正在根據提案繪製 3D 渲染圖..."):
            try:
                response = client.images.generate(
                    model="dall-e-3",
                    prompt=f"Professional interior design rendering, architectural photography style: {full_prompt}",
                    size="1024x1024",
                    quality="hd",
                    n=1,
                )
                image_url = response.data[0].url
                st.image(image_url, caption="寓蟄 AI 生成視覺提案圖")
            except Exception as e:
                st.error(f"圖片生成失敗：{e}")
    else:
        st.info("💡 若要直接在畫面上生成圖片，請於 Secrets 中設定 API Key。")