from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
import math
from collections import defaultdict

def crawl_schedule(url):
    # ✅ Chrome WebDriver 옵션 설정
    chrome_options = Options()
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920x1080")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--headless")  # 백그라운드 실행
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    # ✅ WebDriver 실행
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)

    # ✅ 페이지가 완전히 로드될 때까지 대기
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "tablebody")))
    except:
        driver.quit()
        return {"code": "400", "message": "페이지를 불러올 수 없습니다.", "is_success": False}

    # ✅ `tablehead` 찾기 (요일 추출)
    try:
        tablehead = driver.find_element(By.CLASS_NAME, "tablehead")
        days = [td.text.strip() for td in tablehead.find_elements(By.TAG_NAME, "td") if td.text.strip()]
    except:
        driver.quit()
        return {"code": "400", "message": "요일 정보를 찾을 수 없습니다.", "is_success": False}

    # ✅ `tablebody` 찾기 (시간표 블록들 가져오기)
    try:
        tablebody = driver.find_element(By.CLASS_NAME, "tablebody")
        subjects = tablebody.find_elements(By.CLASS_NAME, "subject")
    except:
        driver.quit()
        return {"code": "400", "message": "시간표 데이터를 찾을 수 없습니다.", "is_success": False}

    # ✅ 요일별 스케줄 저장용
    schedules = defaultdict(list)

    # ✅ 블록 정보 분석
    for subject in subjects:
        style = subject.get_attribute("style")

        # ⏳ height, top 값 추출
        height_match = re.search(r'height:\s*(\d+)px', style)
        top_match = re.search(r'top:\s*(\d+)px', style)

        if not height_match or not top_match:
            continue

        height = int(height_match.group(1))
        top = int(top_match.group(1))

        # **시작 시간 계산**
        start_total_minutes = ((top - 450) // 25) * 30
        start_hour = 9 + (start_total_minutes // 60)
        start_minute = start_total_minutes % 60

        # **종료 시간 계산**
        duration_total_minutes = math.ceil((height - 1) / 25) * 30
        end_total_minutes = start_total_minutes + duration_total_minutes
        end_hour = 9 + (end_total_minutes // 60)
        end_minute = end_total_minutes % 60

        # ⏳ 변환 완료
        start_time = f"{int(start_hour):02}:{int(start_minute):02}"
        end_time = f"{int(end_hour):02}:{int(end_minute):02}"

        # 📌 **요일 찾기**
        parent_td = subject.find_element(By.XPATH, "./ancestor::td")
        td_index = list(parent_td.find_element(By.XPATH, "./ancestor::tr").find_elements(By.TAG_NAME, "td")).index(parent_td)
        day = days[td_index] if td_index < len(days) else "알 수 없음"

        schedules[day].append((start_time, end_time))

    driver.quit()

    # ✅ **시간 정제: 연속된 시간 합치기 & 30분 단위 변환**
    final_schedules = []
    for day, times in schedules.items():
        times.sort()
        merged_times = set()
        
        for start, end in times:
            start_h, start_m = map(int, start.split(":"))
            end_h, end_m = map(int, end.split(":"))

            current_h, current_m = start_h, start_m
            while (current_h, current_m) < (end_h, end_m):
                merged_times.add(f"{current_h:02}:{current_m:02}")
                current_m += 30
                if current_m >= 60:
                    current_h += 1
                    current_m = 0

        sorted_times = sorted(merged_times)

        final_schedules.append({
            "time_point": day,
            "times": sorted_times
        })

    return {
        "code": "200",
        "message": "유저 고정 스케줄 조회에 성공했습니다.",
        "payload": {
            "schedules": final_schedules
        },
        "is_success": True
    }
    