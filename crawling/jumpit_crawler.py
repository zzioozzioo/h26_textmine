import os
import requests
import pandas as pd
import time
import random

def scrape_jumpit(max_pages, filename):
    # API 요청에 맞는 헤더 설정 (JSON 데이터를 받기 위함)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Referer': 'https://www.jumpit.co.kr/'
    }
    
    collected_ids = set()
    
    if os.path.exists(filename):
        try:
            existing_df = pd.read_csv(filename, encoding='utf-8-sig', on_bad_lines='skip')
            collected_ids = set(str(row['공고번호']) for row in existing_df.to_dict('records') if pd.notna(row['공고번호']))
            print(f"🔄 기존 파일('{filename}') 발견: 현재 {len(collected_ids)}건의 공고를 기억하고 이어서 수집합니다.")
        except Exception as e:
            print(f"⚠️ 기존 파일 읽기 실패 (새 파일로 시작합니다): {e}")
    else:
        print(f"📢 기존 파일이 없습니다. 새로 생성을 시작합니다.")
        
    data_list = []
    print(f"🚀 [점핏 API] 총 {max_pages}페이지 대량 수집을 시작합니다.")

    start_page = 1
    for page in range(start_page, max_pages + 1):
        print(f"⏳ [점핏] {page}/{max_pages} 페이지 훑는 중... (기록된 총 유니크 건수: {len(collected_ids)}건)")
        
        # 1. HTML 주소가 아닌, 점핏의 실제 데이터가 오가는 '내부 API 주소'를 타겟팅합니다.
        url = f"https://api.jumpit.co.kr/api/positions?keyword=IT&page={page}"
        
        try:
            response = requests.get(url, headers=headers, timeout=12)
            if response.status_code in [403, 429]:
                print("⚠️ 대기 후 재시도 필요 (5분 휴식)")
                time.sleep(300)
                continue
            if response.status_code != 200:
                break
                
            # 2. BeautifulSoup 대신 response.json()을 통해 딕셔너리 형태로 바로 변환합니다.
            json_data = response.json()
            recruits = json_data.get('result', {}).get('positions', [])
            
            if not recruits:
                print(f"ℹ️ {page}페이지에 더 이상 공고가 없습니다. 수집을 종료합니다.")
                break
                
            page_new_items = 0
            for r in recruits:
                try:
                    # 3. 깨끗하게 정돈된 JSON 데이터에서 필요한 값만 쏙쏙 추출합니다.
                    job_id = r.get('id', '')
                    
                    if not job_id or str(job_id) in collected_ids:
                        continue
                    
                    # 회사명
                    company_text = str(r.get('companyName', '')).strip().replace('"', '')

                    # 공고제목
                    title_text = str(r.get('title', '')).strip().replace('"', '')

                    # 지역
                    location_text = r.get('location') or r.get('workingArea') or "미지정"
                    location_text = str(location_text).strip().replace(',', ' ')
                    
                    # 경력
                    experience_text = r.get('career') or ""

                    if not experience_text:
                        min_c = r.get('minCareer')
                        max_c = r.get('maxCareer')
                        if min_c is not None and max_c is not None:
                            if min_c == 0 and max_c == 0:
                                experience_text = "신입"
                            elif min_c == 0:
                                experience_text = f"신입 ~ {max_c}년"
                            else:
                                experience_text = f"{min_c} ~ {max_c}년"
                        else:
                            experience_text = "경력무관"
                            
                    experience_text = str(experience_text).strip()
                    
                    # 기술 스택 목록 합치기
                    tech_stack_list = r.get('techStacks', [])
                    tech_stack = " / ".join(tech_stack_list) if tech_stack_list else "미지정"
                    
                    data_list.append({
                        '공고번호': job_id, 
                        '회사명': company_text,
                        '공고제목': title_text, 
                        '지역': location_text,
                        '경력': experience_text,
                        '기술스택/분야': tech_stack
                    })
                    collected_ids.add(str(job_id))
                    page_new_items += 1
                except Exception:
                    continue
            
            if page_new_items > 0:
                df_new = pd.DataFrame(data_list)
                
                if os.path.exists(filename):
                    df_new.to_csv(filename, mode='a', index=False, header=False, encoding='utf-8-sig')
                else:
                    df_new.to_csv(filename, mode='w', index=False, header=True, encoding='utf-8-sig')
                
                data_list = []
            
            time.sleep(random.uniform(1.5, 2.5))
            
        except Exception as e:
            print(f"네트워크 에러: {e}")
            time.sleep(5)
            
    print(f"✨ [점핏] 지정된 {max_pages}페이지까지 수집 및 파일 저장 완료!")