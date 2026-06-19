import os
import sys
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random

def scrape_job_descriptions(input_filename, output_filename, limit_count):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Referer': 'https://www.saramin.co.kr/'
    }
    
    # 1. 기존 6개 컬럼 파일 로드 (공고번호를 추출하기 위함)
    if not os.path.exists(input_filename):
        print(f"❌ 원본 파일이 없습니다: {input_filename}")
        return
        
    df_input = pd.read_csv(input_filename, encoding='utf-8-sig', on_bad_lines='skip')
    print(f"📂 원본 데이터 로드 완료: 총 {len(df_input)}건")
    
    # 사용자가 입력한 파라미터(limit_count)만큼만 자르기
    df_target = df_input.head(limit_count)
    print(f"🎯 상위 {limit_count}개 공고에 대해 원문 스크래핑을 준비합니다.")

    # 2. 결과 파일 중간 점검 (이미 수집한 번호는 스킵해서 이어붙이기 가능하게)
    done_ids = set()
    if os.path.exists(output_filename):
        try:
            df_existing = pd.read_csv(output_filename, encoding='utf-8-sig', on_bad_lines='skip')
            # 기존 결과 파일에 있는 공고번호 기억
            done_ids = set(df_existing['공고번호'].astype(str))
            print(f"🔄 이어붙이기 모드: 이미 {len(done_ids)}건의 원문이 수집되어 있습니다.")
        except Exception:
            pass

    df_todo = df_input[~df_input['공고번호'].astype(str).isin(done_ids)]
    print(f"🔍 아직 원문이 수집되지 않은 남은 공고는 총 {len(df_todo)}건입니다.")
    
    if len(df_todo) == 0:
        print("✨ 이미 모든 공고의 원문 수집이 완료되어 새로 긁을 데이터가 없습니다!")
        return
    
    if limit_count is not None:
        df_target = df_todo.head(limit_count)
        print(f"🎯 남은 {len(df_todo)}건 중 상위 {len(df_target)}개 공고에 대해 스크래핑을 준비합니다.")
    else:
        df_target = df_todo
        print(f"🚀 남은 {len(df_todo)}건 전체 공고에 대해 스크래핑을 준비합니다.")

    print("🚀 공고 원문 수집을 시작합니다... (공고번호, 원문 2개 컬럼만 저장)")
    
    data_list = []
    
    # 3. 루프 돌며 원문 긁기
    for idx, (_, row) in enumerate(df_target.iterrows()):
        job_id = str(row['공고번호'])
            
        detail_url = f"https://www.saramin.co.kr/zf_user/jobs/relay/view-detail?rec_idx={job_id}"
        
        try:
            time.sleep(random.uniform(1.5, 2.8))
            response = requests.get(detail_url, headers=headers, timeout=10)
            
            if response.status_code in [403, 429]:
                print(f"⚠️ 차단 감지(상태코드 {response.status_code}). 5분간 휴식 후 재시도합니다.")
                time.sleep(300)
                continue
                
            if response.status_code != 200:
                print(f"❌ {job_id} 공고 접근 실패 (Skip)")
                continue
                
            soup = BeautifulSoup(response.text, 'html.parser')
            content_area = soup.select_one('div.user_content') or soup.select_one('div.iframe_content') or soup.select_one('body')
            
            if content_area:
                for tag in content_area(['script', 'style', 'header', 'footer']):
                    tag.decompose()
                
                raw_text = content_area.get_text(separator=' ').strip()
                clean_text = ' '.join(raw_text.split())
                clean_text = clean_text.replace('"', "'")
            else:
                clean_text = "본문 텍스트 없음"
                
            # 💡 [핵심 변형] 회사명, 제목 등 다 버리고 오직 2개만 딕셔너리에 담기
            data_list.append({
                '공고번호': job_id,
                '원문': clean_text
            })
            print(f"✅ 수집 완료 [{idx + 1}/{len(df_target)}] 공고번호: {job_id} ({len(clean_text)}자)")
            
            # 10건 쌓일 때마다 실시간 누적 저장(append)
            if len(data_list) >= 10:
                df_new = pd.DataFrame(data_list)
                if os.path.exists(output_filename):
                    df_new.to_csv(output_filename, mode='a', index=False, header=False, encoding='utf-8-sig')
                else:
                    df_new.to_csv(output_filename, mode='w', index=False, header=True, encoding='utf-8-sig')
                data_list = [] # 리스트 비우기
                
        except Exception as e:
            print(f"⚠️ {job_id} 처리 중 에러 발생: {e}")
            time.sleep(3)
            continue

    # 4. 루프가 다 끝나고 남은 짜부래기 데이터 최종 누적 저장
    if data_list:
        df_new = pd.DataFrame(data_list)
        if os.path.exists(output_filename):
            df_new.to_csv(output_filename, mode='a', index=False, header=False, encoding='utf-8-sig')
        else:
            df_new.to_csv(output_filename, mode='w', index=False, header=True, encoding='utf-8-sig')

    print(f"✨ 원문 수집 완료! 최종 파일 저장됨: '{output_filename}'")

# --- 실행부 ---
if __name__ == "__main__":
    input_file = './data/saramin_dataset.csv'          # 원본 6개 컬럼 파일
    output_file = './data/saramin_descriptions.csv'       # 새로 만들 2개 컬럼 파일 (공고번호, 원문만 존재)
    
    limit_count = 5000 
    
    if len(sys.argv) > 1:
        try:
            limit_count = int(sys.argv[1])
            print(f"📊 사용자가 지정한 수집 건수: {limit_count}건")
        except ValueError:
            print(f"⚠️ 숫자가 아닌 값이 입력되어 기본값인 {limit_count}건으로 진행합니다.")

    scrape_job_descriptions(input_file, output_file, limit_count=limit_count)