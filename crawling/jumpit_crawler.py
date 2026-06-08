from curl_cffi import requests
import pandas as pd
import time
import random

def scrape_jumpit(max_pages, filename):
    JUMPIT_COOKIE = "PHPSESSID=485nup4a2a21hb6bd2jjpi1cl747ep06qg7borlq0adncan55q; PCID=17792772600612507013889; _gid=GA1.3.1760385686.1779277260; _gcl_au=1.1.1718258939.1779277260; airbridge_migration_metadata__saramin=%7B%22version%22%3A%221.11.9%22%7D; ab180ClientId=90c73190-e363-483b-b19e-c0d1f951f941; airbridge_migration_metadata__jumpit=%7B%22version%22%3A%221.11.9%22%7D; _fbp=fb.2.1779277270013.29857540650661936; _ga_58W0W855T7=GS2.1.s1779277260$o1$g0$t1779277283$j37$l0$h0; _ga_0PN5NFZW7P=GS2.1.s1779277286$o1$g0$t1779277286$j60$l0$h0; _ga_E0LMXXGRZK=GS2.1.s1779277283$o1$g0$t1779277485$j59$l0$h0; _ga_X6JZ0HCBFC=GS2.1.s1779277260$o1$g1$t1779277511$j34$l0$h0; airbridge_session__saramin=%7B%22id%22%3A%22d0c4cc6b-6b71-4801-9d13-2dda49f0451c%22%2C%22timeout%22%3A1800000%2C%22start%22%3A1779277261032%2C%22end%22%3A1779277511464%7D; _ga_GR2XRGQ0FK=GS2.1.s1779277260$o1$g1$t1779277527$j17$l0$h0; _ga_L2PN791WR5=GS2.1.s1779277286$o1$g1$t1779277527$j19$l0$h0; _ga=GA1.3.2063060709.1779277260; cto_bundle=HpMX8l9xVVhvbWRJVXFrMnZ1bzVDU2FWQmI0UGxueFBnRFhKdUhSUGtQcENWOHdxNVdHQ3UxM0dSMWNZYjdLJTJCaWYlMkZNa0FUVXFhQXRQSiUyRmJhOFlPdmVDUnA2M1ZBZSUyRjVleXREJTJGWE5La2lCbjFQVG15Z1VzdyUyQml3RW9xWVJUbjF4YUJYbWd4RetbWw==; _gat_UA-188833836-1=1; airbridge_session__jumpit=%7B%22id%22%3A%222a46e510-5a90-48a4-8ab6-940b270a44e6%22%2C%22timeout%22%3A1800000%2C%22start%22%3A1779277270116%2C%22end%22%3A1779278015300%7D; _ga_HLK7K0XF15=GS2.1.s1779277269$o1$g1$t1779278022$j39$l0$h0"

    # 점핏의 WAF(보안벽) 통과 및 한국어 인코딩 보장을 위한 헤더셋
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
        'Referer': 'https://www.jumpit.co.kr/positions',
        'Origin': 'https://www.jumpit.co.kr',
        'Cookie': JUMPIT_COOKIE, 
        'X-Requested-With': 'XMLHttpRequest'
    }
    
    data_list = []
    
    print(f"🚀 [점핏] 총 {max_pages}회 요청(최대 {max_pages * 16}건) 수집을 시작합니다.")

    for step in range(1, max_pages + 1):
        print(f"⏳ [점핏] {step}/{max_pages} 회차 요청 중... (누적: {len(data_list)}건)")
        
        # 점핏 포지션 목록 API 엔드포인트 (page 번호 기반 호출)
        url = f"https://api.jumpit.co.kr/api/positions?page={step}&sort=rsp_chg&deviceType=pc"
        
        try:
            response = requests.get(url, headers=headers, timeout=12)
            
            if response.status_code != 200:
                print(f"❌ 점핏 API 접속 실패 (코드: {response.status_code})")
                break
                
            json_data = response.json()
            # 점핏의 결과 데이터 핵심 루트 진입
            result_body = json_data.get('result', {})
            jobs = result_body.get('positions', []) if isinstance(result_body, dict) else []
            
            if not jobs:
                print("📢 더 이상 가져올 공고가 없습니다.")
                break
                
            for j in jobs:
                try:
                    # 기본 컬럼 구조 및 딕셔너리 포맷 100% 동기화
                    job_id = str(j.get('id', ''))
                    company = j.get('companyName', '').strip()
                    title = j.get('title', '').strip()
                    
                    # 지역 정보 처리 (점핏은 보통 '서울 강남구' 형태로 내려줌)
                    location = j.get('workingPlace', '').strip()
                    
                    # 기술 스택 리스트 추출 후 문자열 변환
                    tech_list = j.get('techStacks', [])
                    if isinstance(tech_list, list):
                        tech_stack = ", ".join([str(t).strip() for t in tech_list if t])
                    else:
                        tech_stack = "정보 없음"
                        
                    # 마감일 처리
                    due_date = j.get('closedAt', '') # 점핏은 년-월-일 형식 혹은 특정 문구 표기
                    if due_date is None or due_date == "null" or not due_date or "상시" in str(due_date):
                        end_date = "상시채용"
                    else:
                        end_date = str(due_date).strip()
                    
                    # ⚠️ 저장 형식 일관성 유지
                    data_list.append({
                        '공고번호': job_id, '지역': location, '회사명': company,
                        '공고제목': title, '기술스택/분야': tech_stack, '마감일': end_date
                    })
                except Exception:
                    continue
            
            # 매 회차 실시간 CSV 파일 백업
            if data_list:
                pd.DataFrame(data_list).to_csv(filename, index=False, encoding='utf-8-sig')
                
            # 디도스 차단 방지 매너 타임
            time.sleep(random.uniform(2.0, 3.5))
            
        except Exception as e:
            print(f"네트워크 에러: {e}")
            time.sleep(5)
            
    print(f"✨ [점핏] 수집 완료! 총 {len(data_list)}건 저장.")