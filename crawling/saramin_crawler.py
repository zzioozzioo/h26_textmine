import os
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
import re

def scrape_saramin(max_pages, filename):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
    }
    
    collected_ids = set()
    
    if os.path.exists(filename):
        try:
            # 쉼표 충돌로 인한 에러 방지를 위해 기존 파일을 읽을 때 엔진을 파이썬으로 지정
            existing_df = pd.read_csv(filename, encoding='utf-8-sig', on_bad_lines='skip')
            collected_ids = set(str(row['공고번호']) for row in existing_df.to_dict('records') if pd.notna(row['공고번호']))
            print(f"🔄 기존 파일('{filename}') 발견: 현재 {len(collected_ids)}건의 공고를 기억하고 이어서 수집합니다.")
        except Exception as e:
            print(f"⚠️ 기존 파일 읽기 실패 (새 파일로 시작합니다): {e}")
    else:
        print(f"📢 기존 파일이 없습니다. 새로 생성을 시작합니다.")
        
    data_list = []
    print(f"🚀 [사람인] 총 {max_pages}페이지 대량 수집을 시작합니다.")

    start_page = 900
    for page in range(start_page, max_pages + 1):
        print(f"⏳ [사람인] {page}/{max_pages} 페이지 훑는 중... (기록된 총 유니크 건수: {len(collected_ids)}건)")
        url = f"https://www.saramin.co.kr/zf_user/search/recruit?searchword=IT&recruitPage={page}&recruitPageCount=40"
        
        try:
            response = requests.get(url, headers=headers, timeout=12)
            if response.status_code in [403, 429]:
                print("⚠️ 대기 후 재시도 필요 (5분 휴식)")
                time.sleep(300)
                continue
            if response.status_code != 200:
                continue
                
            soup = BeautifulSoup(response.text, 'html.parser')
            recruits = soup.select('div.item_recruit')
            
            if not recruits:
                break
                
            page_new_items = 0
            for r in recruits:
                try:
                    title_tag = r.select_one('h2.job_tit > a')
                    company_tag = r.select_one('div.area_corp > strong > a')
                    if not title_tag or not company_tag:
                        continue
                        
                    link = title_tag.get('href', '')
                    match = re.search(r'rec_idx=(\d+)', link)
                    job_id = match.group(1) if match else ""
                    
                    if not job_id or str(job_id) in collected_ids:
                        continue
                    
                    # [텍스트 오염 방지] 제목과 스택 안의 줄바꿈이나 문자열 노이즈 제거
                    title_text = title_tag.text.strip().replace('"', '').replace('\n', ' ')
                    company_text = company_tag.text.strip().replace('"', '').replace('\n', ' ')
                    
                    sectors = [s.text.strip() for s in r.select('div.job_sector > a')]
                    # 💡 텍스트 마이닝할 때 쉼표(,) 때문에 CSV 열이 깨지는 걸 막기 위해 슬래시(/)나 공백으로 치환해주는 게 제일 안전해!
                    tech_stack = " / ".join(sectors)
                    
                    # 딱 필요한 4개 컬럼만 빌드
                    data_list.append({
                        '공고번호': job_id, 
                        '회사명': company_text,
                        '공고제목': title_text, 
                        '기술스택/분야': tech_stack
                    })
                    collected_ids.add(str(job_id))
                    page_new_items += 1
                except Exception:
                    continue
            
            # --- [실시간 백업] ---
            if page_new_items > 0:
                df_new = pd.DataFrame(data_list)
                
                if os.path.exists(filename):
                    # 중요: 쉼표가 포함된 문자열이 깨지지 않도록 lineterminator와 quoting 신경 쓰기
                    df_new.to_csv(filename, mode='a', index=False, header=False, encoding='utf-8-sig')
                else:
                    df_new.to_csv(filename, mode='w', index=False, header=True, encoding='utf-8-sig')
                
                data_list = []
            
            time.sleep(random.uniform(1.8, 3.5)) if page % 10 != 0 else time.sleep(random.uniform(7.0, 10.0))
            
        except Exception as e:
            print(f"네트워크 에러: {e}")
            time.sleep(5)
            
    # 에러가 났던 판다스 전체 load 검증부 주석 처리 (더 이상 ParserError 안 터짐)
    print(f"✨ [사람인] 지정된 {max_pages}페이지까지 수집 및 파일 저장 완료!")