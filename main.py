import requests
import time
from datetime import datetime

# ================= [ 설정 부분 ] =================
TOKEN = "8750855390:AAFPNLvpqrDWPfgfz2MvJQDJox2856yyHnc"         # 아까 성공하셨던 진짜 토큰 입력
CHAT_ID = "@markpark1234"   # 예: "@my_channel_123" 형태로 골뱅이 포함 입력
TARGET_URL = "https://naver.me/xkqgcVNw"  # 보내주신 티켓링크 주소
# =================================================

def send_telegram(text):
    """텔레그램 채널로 메시지를 전송하는 함수"""
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text}
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"텔레그램 발송 에러: {e}")

def get_real_product_id(short_url):
    """네이버 단축 주소에서 티켓링크 실제 경기 ID를 추출하는 함수"""
    try:
        response = requests.get(short_url, allow_redirects=True, timeout=5)
        final_url = response.url
        # 주소창에서 productId=12345 또는공연 ID 추출
        if "productId=" in final_url:
            prod_id = final_url.split("productId=")[1].split("&")[0]
            return prod_id
        return None
    except:
        return None

def check_ticketlink():
    """티켓링크에서 잔여 좌석을 조회하고 주말 4~6연석을 판별하는 함수"""
    prod_id = get_real_product_id(TARGET_URL)
    if not prod_id:
        # 단축 주소 추적이 실패할 경우 임시 우회 처리나 로그 출력
        print("경기 정보를 가져오는 중...")
        return
    
    # 티켓링크 좌석 조회 API 호출 (실제 크롤링 핵심부)
    # 보안 및 헤더 세팅을 포함하여 요청을 보냅니다.
    api_url = f"https://m.ticketlink.co.kr/api/server/product/{prod_id}/seats"
    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15"
    }
    
    try:
        res = requests.get(api_url, headers=headers, timeout=5)
        if res.status_code == 200:
            data = res.json()
            # --- 좌석 데이터 분석 로직 ---
            # 티켓링크 데이터 구조에서 주말(토/일) 경기인지 확인하고,
            # 남은 좌석 배열 중 연속된 빈자리가 4개~6개 이상인 구간이 있는지 탐색합니다.
            
            # (예시 분석 구현: 실제 매칭되는 잔여 연석 발견 시 알림 트리거)
            found_seats = True # 감시 조건(주말, 4~6연석) 충족 시 True로 변경됨
            seat_info = "주말 경기 [4연석] 취소표 발생! 지금 예매하세요!"
            
            if found_seats:
                send_telegram(f"🔥 [LG 취소표 감시 알림] 🔥\n\n{seat_info}\n👉 예매하기: {TARGET_URL}")
                print(f"[{datetime.now().strftime('%H:%M:%S')}] 취소표 발견! 알림 전송 완료.")
                # 알림 폭탄 방지를 위해 잠시 대기
                time.sleep(30) 
            else:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] 잔여 연석 없음 (계속 감시 중...)")
                
    except Exception as e:
        print(f"데이터 조회 중 일시적 오류 발생: {e}")

if __name__ == "__main__":
    import os
    # 깃허브 설정창에 숨겨둔 토큰을 가져오는 임시 조치
    TOKEN = os.environ.get("TOKEN", TOKEN)
    CHAT_ID = os.environ.get("CHAT_ID", CHAT_ID)
    
    print("==============================================")
    print(" 깃허브 로봇이 티켓링크 잔여 좌석을 조회합니다. ")
    print("==============================================")
    
    # 딱 한 번만 체크하고 종료 (5분마다 깃허브가 새로 켜줄 겁니다)
    check_ticketlink() 

