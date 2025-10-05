import os
import json
import requests
import google.generativeai as genai
from dotenv import load_dotenv

# .env 파일에서 환경 변수 불러오기
load_dotenv()

# .env 파일에 저장한 Google API 키와 GitHub 토큰을 불러옵니다.
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

# --- ⚠️ 중요: 아래 2개의 변수를 여러분의 환경에 맞게 수정하세요! ---
# 예: "my-github-id/ai-security-bot"
REPO_NAME = "cabege/Small_Security_Project1" 
# 아래 2단계에서 생성할 테스트 PR의 번호 (보통 1)
PR_NUMBER = 1 
# --------------------------------------------------------------------

def read_scan_result(file_path="result.json"):
    """Checkov 스캔 결과(result.json) 파일을 읽어 내용을 반환합니다."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"오류: {file_path}을(를) 찾을 수 없습니다.")
        return None
    except json.JSONDecodeError:
        print(f"오류: {file_path} 파일이 올바른 JSON 형식이 아닙니다.")
        return None

def get_ai_analysis(scan_result):
    """스캔 결과를 Google AI (Gemini)에 보내 분석을 요청하고, 결과를 받습니다."""
    if not scan_result:
        return "스캔 결과가 없습니다."

    failed_checks = scan_result.get("results", {}).get("failed_checks", [])
    if not failed_checks:
        return "✅ 분석 결과, 발견된 보안 취약점이 없습니다."

    # Google AI API 키 설정
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel('gemini-pro')

    # AI에게 보낼 프롬프트 구성
    prompt = f"""
    당신은 코드 보안 전문가입니다. 주어진 Terraform 코드의 보안 스캔 결과를 분석하고,
    마치 코드 리뷰를 하듯 개발자가 이해하기 쉽게 설명해주세요.
    각 취약점에 대해 다음 내용을 포함하여 한국어로 설명해주세요.

    1.  **취약점 요약**: 어떤 문제인지 간결하게 설명
    2.  **영향**: 이 취약점이 방치될 경우 발생할 수 있는 잠재적 위험
    3.  **수정 제안**: 문제를 해결하기 위한 구체적인 코드 수정 방안

    결과는 Markdown 형식을 사용하여 가독성 좋게 작성해주세요.

    ---
    ### 보안 스캔 결과:
    {json.dumps(failed_checks, indent=2, ensure_ascii=False)}
    ---
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"AI 분석 중 오류가 발생했습니다: {e}"

def post_github_comment(repo_name, pr_number, comment_body):
    """GitHub PR에 분석 결과를 댓글로 남깁니다."""
    url = f"https://api.github.com/repos/{repo_name}/issues/{pr_number}/comments"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    data = {"body": comment_body}

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 201:
        print(f"✅ 성공: PR #{pr_number}에 AI 분석 댓글을 남겼습니다.")
    else:
        print(f"❌ 실패: GitHub 댓글 작성 중 오류 발생 (상태 코드: {response.status_code})")
        print(response.text)

if __name__ == "__main__":
    scan_results = read_scan_result()
    if scan_results:
        ai_comment = get_ai_analysis(scan_results)
        post_github_comment(REPO_NAME, PR_NUMBER, ai_comment)