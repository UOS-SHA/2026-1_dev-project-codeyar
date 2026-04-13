import requests
import json
import time

url_post = "http://127.0.0.1:8000/api/v1/submissions/"

# 1. 대상 파이썬 코드
python_code = """
import sys
input_data = sys.stdin.read().split()
if len(input_data) == 2:
    a, b = map(int, input_data)
    print(a + b)
"""

# 2. 전송 Payload
payload = {
    "code": python_code,
    "language_id": 71,
    "time_limit": 2.0,
    "memory_limit": 128,
    "test_cases": [
        {"stdin": "1 2\n", "expected_output": "3\n"},
        {"stdin": "100 200\n", "expected_output": "300\n"},
        {"stdin": "-5 5\n", "expected_output": "0\n"}
    ]
}

def run_test():
    print("🚀 서버에 채점 스케쥴을 던집니다 (Post)")
    
    try:
        response = requests.post(url_post, json=payload, headers={"Content-Type": "application/json"})
        
        if response.status_code == 202:
            data = response.json()
            submission_id = data["submission_id"]
            print(f"✅ 채점 등록 즉시 응답 성공! (할당 ID: {submission_id})\n")
            
            # --- 여기서부터는 프론트엔드라고 가정하고 GET 폴링을 치는 로직 ---
            url_get = f"{url_post}{submission_id}"
            
            while True:
                time.sleep(1.5)
                res_get = requests.get(url_get)
                
                if res_get.status_code != 200:
                    print("❌ 조회 실패:", res_get.status_code)
                    break
                    
                get_data = res_get.json()
                status = get_data["status"]
                
                if status == "Pending":
                    print("⏳ 현황 확인 중... (백엔드 뒤에서 열심히 채점중입니다)")
                    continue
                elif status == "Completed":
                    print("\n🎉 채점 완료!")
                    results = get_data["results"]
                    for i, res in enumerate(results, start=1):
                        print(f"--- 📝 테스트 케이스 {i} 결과 ---")
                        print(f"상태: {res['status_desc']} (ID: {res['status_id']})")
                        print(f"퍼포먼스: {res['time']}초 소요, {res['memory']}KB 메모리 사용")
                        print(f"출력 내용: {repr(res['stdout'])}")
                        if res['stderr']:
                            print(f"에러 로그: {res['stderr']}")
                        print("")
                    break
                else:
                    print(f"\n❌ 채점 중 에러 발생: {status}")
                    break
                    
        else:
            print("❌ POST 요청 실패:", response.text)
            
    except requests.exceptions.ConnectionError:
        print("❌ 서버 연결 에러. uvicorn이 켜져있나요?")

if __name__ == "__main__":
    run_test()
