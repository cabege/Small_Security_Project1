import os
import google.generativeai as genai
from dotenv import load_dotenv

# .env 파일에서 환경 변수 불러오기
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

try:
    # Google AI API 키 설정
    genai.configure(api_key=GOOGLE_API_KEY)

    print("--- 현재 API 키로 사용 가능한 모델 목록 ---")

    for model in genai.list_models():
        # 'generateContent' 메소드를 지원하는 모델인지 확인
        if 'generateContent' in model.supported_generation_methods:
            print(f"✅ 모델 이름: {model.name}")

    print("------------------------------------------")
    print("위 목록에서 '✅' 표시된 모델 이름을 main.py에 사용하세요.")

except Exception as e:
    print(f"오류가 발생했습니다: {e}")