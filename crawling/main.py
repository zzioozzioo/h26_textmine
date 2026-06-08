import sys
from saramin_crawler import scrape_saramin
from wanted_crawler import scrape_wanted
from jumpit_crawler import scrape_jumpit

def main():
    """
    사용법: python main.py [사이트명] [페이지수]
    예시 1: python main.py saramin 250
    예시 2: python main.py wanted 100
    """
    
    # 터미널 파라미터가 없거나 부족할 때 가이드 출력
    if len(sys.argv) < 3:
        print("\n❌ 실행 파라미터가 부족합니다.")
        print("💡 [사용법] python main.py [사이트이름] [페이지수]")
        print("   - 예시 1 (사람인 3페이지 수집): python main.py saramin 3")
        return

    # 파라미터 매핑
    target_site = sys.argv[1].lower().strip()
    try:
        max_pages = int(sys.argv[2])
    except ValueError:
        print("❌ 페이지 수는 반드시 숫자로 입력해야 합니다.")
        return

    # 사이트별 분기 처리 가동
    if target_site == "saramin":
        output_file = "./data/saramin_dataset.csv"
        print(f"🎯 대량 수집 대상 사이트: [사람인]")
        scrape_saramin(max_pages=max_pages, filename=output_file)
        
    elif target_site == "jumpit":  # 💡 점핏 분기 추가
        output_file = "jumpit_dataset.csv"
        print(f"🎯 대량 수집 대상 사이트: [점핏]")
        # 점핏 API는 1페이지당 16건씩 기본 호출됩니다.
        scrape_jumpit(max_pages=max_pages, filename=output_file)
        
    else:
        print(f"❌ '{target_site}'은(는) 지원하지 않는 사이트 카테고리입니다.")
        print("   현재 지원 목록: saramin, jumpit")

if __name__ == "__main__":
    main()