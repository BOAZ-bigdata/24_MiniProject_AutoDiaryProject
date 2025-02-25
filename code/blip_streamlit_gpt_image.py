import streamlit as st
import os
from PIL import Image
import base64
from io import BytesIO
from openai import OpenAI
import dotenv
import datetime


# 환경 변수 로드
dotenv.load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# 페이지 설정
st.set_page_config(page_title="사진 일기 생성기", layout="wide")
st.title("AI 사진 일기 생성기")

# OpenAI 클라이언트 초기화
client = OpenAI(api_key=OPENAI_API_KEY)

# 파일 업로드 섹션
st.header("사진 업로드")
uploaded_files = st.file_uploader("여러 장의 사진을 선택하세요", type=['jpg', 'jpeg', 'png'], accept_multiple_files=True)

def encode_uploaded_file(file_obj):
    # 파일 포인터를 처음으로 돌려놓고 bytes 추출
    file_obj.seek(0)
    return base64.b64encode(file_obj.read()).decode("utf-8")

if uploaded_files:
    images_info = []
    
    for uploaded_file in uploaded_files:
        st.subheader(f"사진: {uploaded_file.name}")
        
        # 이미지와 입력 필드를 나란히 배치
        col1, col2 = st.columns([1, 2])
        
        with col1:
            # 이미지 표시
            image = Image.open(uploaded_file)
            image = image.convert("RGB")
            st.image(image, caption=uploaded_file.name, width=200)
            # Base64 인코딩
            base64_image = encode_uploaded_file(uploaded_file)
        
        with col2:
            # 사용자 입력 받기
            person_name = st.text_input("사진 속 다른 인물들의 이름", key=f"person_{uploaded_file.name}")
            location = st.text_input("촬영 장소", key=f"location_{uploaded_file.name}")
            keywords = st.text_input("활동 키워드", key=f"keywords_{uploaded_file.name}")
        
        images_info.append({
            "file_name": uploaded_file.name,
            "base64_image": base64_image,
            "person": person_name if person_name else "친구들",
            "location": location if location else "어딘가",
            "keywords": keywords if keywords else ""
        })
        
        st.divider()
    
    # 일기 분위기 직접 입력
    mood = st.text_input('일기의 분위기를 입력해주세요 (입력하지 않으면 평범한 톤으로 작성됩니다)', '')

    # 일기 생성 버튼
    if st.button("일기 생성하기"):
        with st.spinner("AI가 일기를 작성하고 있습니다..."):
            diary_prompt = """오늘 찍은 사진들을 보고 일기를 작성해주세요.
각 사진과 함께 장소, 함께한 사람들, 활동 키워드가 제공됩니다.
이 정보들을 자연스럽게 활용하여 실제 있었던 일만을 서술해주세요.
"""
            diary_prompt += "**입력된 사진 정보** (순서대로 작성해주세요):\n"

            for info in images_info:
                diary_prompt += (
                    f"- 사진 파일: {info['file_name']}\n"
                    f"  장소: {info['location']}\n"
                    f"  함께한 사람: {info['person']}\n"
                    f"  키워드: {info['keywords']}\n\n"
                )
            base_guidelines = """
**일기 작성 가이드라인**:
1. **일기의 주체는 "나"**이며, 함께한 사람들을 적절히 언급해주세요.
2. **장소, 인물, 활동 키워드를 적극적으로 활용**하여 실제 경험을 기록하는 것처럼 자연스럽게 서술해주세요.
3. **감정 표현을 추가적으로 반영**하여 좀 더 몰입할 수 있는 글이 되도록 해주세요.
4. **사진이 업로드된 순서를 시간 순서로 간주하고**, 입력된 순서대로 일기를 작성해주세요. (밤에 찍은 사진 뒤에 낮에 찍은 사진이 오면, 다음 날로 간주해주세요)
5. **주어진 정보만을 활용**하여, 날짜 정보는 반영하지않고, 사실적으로 일기를 작성해주세요."""

            if mood.strip():  # mood가 비어있지 않은 경우
                diary_prompt += base_guidelines + f'\n6. **입력 받은 분위기에 맞게 일기를 작성**해주세요. 입력 받은 분위기: "{mood}"'
            else:  # mood가 비어있는 경우
                diary_prompt += base_guidelines

            # GPT API에 전달할 메시지 구성: 텍스트와 이미지 데이터를 함께 포함
            message_content = []
            # 텍스트 프롬프트 추가
            message_content.append({
                "type": "text",
                "text": diary_prompt
            })
            # 각 이미지별로 인코딩된 데이터 추가
            for info in images_info:
                message_content.append({
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{info['base64_image']}"}
                })

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "당신은 사진 속 상황을 객관적으로 서술하는 작가입니다."},
                    {"role": "user", "content": message_content}
                ],
                temperature=0.3,  # 창의성을 낮춰서 더 사실적인 응답 유도
                max_tokens=1000
            )
            
            # 결과 표시
            today = datetime.date.today()
            weekday = ["월요일", "화요일", "수요일", "목요일", "금요일", "토요일", "일요일"]
            formatted_date = f"{today.year}년 {today.month}월 {today.day}일, {weekday[today.weekday()]}"
            st.header(f"📅 {formatted_date}")
            st.write(response.choices[0].message.content)
else:
    st.info("위의 업로더를 통해 사진을 선택해주세요.") 