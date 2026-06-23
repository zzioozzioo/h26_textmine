import pandas as pd
import json
from openai import OpenAI
import time
import os # 파일 존재 여부 확인을 위해 추가
import logging
from dotenv import load_dotenv

load_dotenv()

# --- 로깅(Logging) 설정 ---
LOG_FILENAME = "lmstudio_processing.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILENAME, encoding='utf-8'), # 파일로 저장
        logging.StreamHandler() # 화면(터미널)에도 동시에 출력
    ]
)
# 1. LM Studio 로컬 서버와 연결
client = OpenAI()

# 2. 시스템 프롬프트 세팅
SYSTEM_PROMPT = """
너는 채용 공고 텍스트에서 핵심 데이터만 추출하는 '정보 추출 전문 AI'야.
입력된 텍스트는 웹 크롤링된 데이터라 웹사이트 메뉴, 광고, 불필요한 특수기호가 섞여 있어. 너는 노이즈를 무시하고 오직 아래의 JSON 양식에 맞춰서만 답변해야 해. 다른 부연 설명이나 인사말, 마크다운 코드블록(```json 등)은 절대 출력하지 마.

[분석 지침]
hard_skills: 프로그래밍 언어, 툴, 프레임워크, 자격증 등 기술적/전문적 역량 (예: C++, SQL, 정보처리기사)
soft_skills: 태도, 성향, 대인관계 등 소프트 역량 (예: 원활한 커뮤니케이션, 리더십)
preferences: 채용에서 우대하는 조건 (예: 석사 학위자, 관련 경험자, 영어가능자)
culture_keywords: 복지, 근무 형태, 회사 분위기를 유추할 수 있는 핵심 단어 (예: 사내 동호회, 기숙사, 유연근무제)
urgency_score: 인재 채용의 시급성 및 간절함을 1~5점 사이의 정수로 평가 (1점: 여유로움/상시채용, 3점: 일반적인 채용, 5점: 매우 시급함/급구/즉시출근/파격적 보상 제시)
urgency_reason: urgency_score를 그렇게 평가한 핵심 이유 1~2문장

[출력 형식]
{
"hard_skills": [],
"soft_skills": [],
"preferences": [],
"culture_keywords": [],
"urgency_score": 3,
"urgency_reason": ""
}

주의사항:
해당되는 내용이 텍스트에 없다면 배열은 빈 배열 []을, 문자열은 빈 문자열 ""을 출력해.
본문에 없는 내용을 절대 지어내지 마 (Hallucination 금지).
"""
import re

def clean_saramin_text(text):
    if not isinstance(text, str):
        return ""

    fixed_noises = [
        "즉시지원",
        "지원하기",
        "이 공고에 지원한 지원자들의 현황이 궁금하다면?",
        "로그인/회원가입",
        "채용정보에 잘못된 내용이 있을 경우 문의 해주세요.",
        "기업 정보 기업정보 더보기",
        "TOP 궁금해요",
        "로그인 하고 비슷한 조건의 AI추천공고를 확인해 보세요!",
        "불법/허위/과장/오류 신고",
        "지도보기"
    ]
    
    for noise in fixed_noises:
        text = text.replace(noise, " ")

    text = text.replace("지원하기", " ")
    text = text.replace("카테고리 공고명 URL", " ")
    
    # text = re.sub(r'본 채용정보는 .*? 제공한 자료를 바탕으로 잡코리아가 편집.*?완성한 것입니다\.', '', text)
    # text = re.sub(r'본 정보는 잡코리아의 동의 없이.*?사용될 수 없습니다\.', '', text)
    # text = re.sub(r'잡코리아는 .*? 게재한 자료에 대한 오류와.*?책임을 지지 않습니다\.', '', text)
    # text = re.sub(r'<저작권자 ⓒ잡코리아.*?무단전재-재배포금지>', '', text)

    if "비슷한 조건의 AI추천공고" in text:
        text = text.split("비슷한 조건의 AI추천공고")[0]

    text = re.sub(r'\s+', ' ', text).strip()
    return text

def extract_info(job_text):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini", 
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": job_text}
            ],
            temperature=0.1, 
            response_format={"type": "json_object"}
        )
        
        result_text = response.choices[0].message.content.strip()
        
        if result_text.startswith("```json"):
            result_text = result_text.replace("```json", "").replace("```", "").strip()
            
        return json.loads(result_text) 
        
    except Exception as e:
        logging.info(f"Error 추출 실패: {e}")
        return None

# --- 설정 ---
INPUT_FILE = './data/saramin_descriptions_최최최수종.csv'
OUTPUT_FILE = './data/extracted_saramin_jobs_result.json'
SAVE_INTERVAL = 50 # 50건마다 파일에 중간 저장

# 3. 데이터 불러오기 및 처리 상태 확인
df = pd.read_csv(INPUT_FILE)
total_rows = len(df)
results = []

processed_ids = set()

if os.path.exists(OUTPUT_FILE):
    try:
        with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
            results = json.load(f)
            
            # 🔥 [수정] 이미 처리된 데이터에서 '공고번호'만 추출하여 저장
            # CSV의 컬럼명에 맞게 '공고번호'를 수정하세요 (예: 'id', 'job_id' 등)
            for item in results:
                if '공고번호' in item:
                    processed_ids.add(item['공고번호'])
                    
        logging.info(f"🔄 기존 저장 파일에서 {len(processed_ids)}개의 고유 공고를 확인했습니다. 이어서 시작합니다.")
    except Exception as e:
        logging.error(f"⚠️ 기존 저장 파일을 읽는 중 에러 발생, 처음부터 시작합니다: {e}")
        results = []
        processed_ids = set()

logging.info(f"▶️ 데이터 처리를 시작합니다... (전체 {total_rows}건)")

for index, row in df.iterrows():
    
    start_time = time.time()
    current_num = index + 1 
    
    # 🔥 [추가] 현재 행의 공고번호가 이미 처리된 세트에 있다면 건너뜁니다.
    job_id = row['공고번호'] # 👈 여기에 실제 공고번호 컬럼명을 적어주세요.
    if job_id in processed_ids:
        # 매번 로그를 남기면 너무 과하므로, 500건 단위나 혹은 패스 로그 생략 가능
        if current_num % 500 == 0:
            logging.info(f"[{current_num}/{total_rows}] 이미 처리된 공고번호({job_id})이므로 건너뜁니다.")
        continue
        
    logging.info(f"[{current_num}/{total_rows}] 처리 중... (공고번호: {job_id})")
    
    clean_text = clean_saramin_text(row['원문']) 
    extracted_data = extract_info(clean_text)
    
    if extracted_data:
        row_dict = row.to_dict()
        row_dict.update(extracted_data)
        results.append(row_dict)
        processed_ids.add(job_id) # 🔥 [추가] 성공적으로 처리된 번호 세트에 추가
    
    # 주기적으로 중간 저장
    if current_num % SAVE_INTERVAL == 0:
        pd.DataFrame(results).to_json(OUTPUT_FILE, orient='records', force_ascii=False, indent=4)
        logging.info(f"💾 [{current_num}/{total_rows}] 데이터 중간 저장 완료!")
    
    elapsed_time = time.time() - start_time
    MIN_CYCLE_TIME = 0.65
    
    if elapsed_time < MIN_CYCLE_TIME:
        time.sleep(MIN_CYCLE_TIME - elapsed_time)
    else:
        time.sleep(0.05)

# 4. 루프 종료 후 최종 결과 저장
pd.DataFrame(results).to_json(OUTPUT_FILE, orient='records', force_ascii=False, indent=4)
logging.info(f"✅ 모든 처리({total_rows}건)가 완료되어 {OUTPUT_FILE}에 최종 저장되었습니다.")