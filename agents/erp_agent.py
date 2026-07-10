import sys
sys.path.insert(0, 'C:\\Raafiya\\A.R.I.A\\venv\\Lib\\site-packages')

from dotenv import load_dotenv
load_dotenv()

import requests
import os
import time
from datetime import datetime
from playwright.sync_api import sync_playwright

BASE_URL = "https://erp.sathyabama.ac.in/erp/api/v1.0"
USERNAME = os.getenv("ERP_USERNAME", "")
PASSWORD = os.getenv("ERP_PASSWORD", "")

HEADERS_BASE = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "content-type": "application/json",
    "accept": "application/json, text/plain, */*",
    "referer": "https://erp.sathyabama.ac.in/student/view"
}

DAYS = {1: "Monday", 2: "Tuesday", 3: "Wednesday", 4: "Thursday", 5: "Friday", 6: "Saturday"}

SEMESTERS = [
    {"sem": 7, "month": 1, "year": "2026-2027"},
    {"sem": 6, "month": 2, "year": "2025-2026"},
    {"sem": 5, "month": 1, "year": "2025-2026"},
    {"sem": 4, "month": 2, "year": "2024-2025"},
    {"sem": 3, "month": 1, "year": "2024-2025"},
    {"sem": 2, "month": 2, "year": "2023-2024"},
    {"sem": 1, "month": 1, "year": "2023-2024"},
]

def get_headers():
    resp = requests.post(f"{BASE_URL}/MasterStudent/login",
        json={"RegisterNumber": USERNAME, "Password": PASSWORD},
        headers=HEADERS_BASE)
    token = resp.json()["responseData"]["login"]["accessToken"]
    return {**HEADERS_BASE, "Authorization": f"Bearer {token}"}

def get_cae_marks(semester=6):
    try:
        headers = get_headers()
        sem_info = next((s for s in SEMESTERS if s["sem"] == semester), SEMESTERS[1])
        resp = requests.post(f"{BASE_URL}/CAEResult/studentCAEResult",
            headers=headers,
            json={"RegisterNumber": USERNAME,
                  "AcademicMonthId": sem_info["month"],
                  "AcademicYear": sem_info["year"],
                  "Semester": semester})
        marks = resp.json().get("responseData", [])
        if not marks:
            return f"No CAE marks found for semester {semester}."
        seen = {}
        for m in marks:
            name = m["SubjectName"]
            cae = f"CAE{m['CAEType']}"
            if name not in seen:
                seen[name] = {}
            seen[name][cae] = m["Marks"]
        result = f"CAE marks for semester {semester}:\n"
        for subject, scores in seen.items():
            parts = ", ".join([f"{k}: {v}/50" for k, v in scores.items()])
            result += f"{subject} — {parts}\n"
        return result
    except Exception as e:
        return f"Could not fetch CAE marks: {e}"

def get_semester_result(semester=5):
    try:
        headers = get_headers()
        for sem_info in SEMESTERS:
            if sem_info["sem"] != semester:
                continue
            resp = requests.post(f"{BASE_URL}/ResultMark/studentResult",
                headers=headers,
                json={"RegisterNumber": USERNAME,
                      "AcademicMonthId": sem_info["month"],
                      "AcademicYear": sem_info["year"],
                      "Semester": sem_info["sem"]})
            data = resp.json()
            sem_result = data.get("responseData", {}).get("SemResult", [])
            summary = data.get("responseData", {}).get("SemResultSummary", {})
            if sem_result:
                result = f"Semester {sem_info['sem']} results:\n"
                for m in sem_result:
                    subject = m.get("SubjectName", "Unknown")
                    obtained = m.get("TotalMark", m.get("ObtainedMark", "N/A"))
                    max_mark = m.get("MaxMark", 100)
                    grade = m.get("Grade", "")
                    result += f"{subject} — {obtained}/{max_mark} Grade: {grade}\n"
                if summary:
                    gpa = summary.get("GPA", summary.get("CGPA", ""))
                    if gpa:
                        result += f"GPA: {gpa}"
                return result
        return "Semester results not published yet."
    except Exception as e:
        return f"Could not fetch semester results: {e}"

def compare_semesters():
    try:
        headers = get_headers()
        results = {}
        for sem_info in SEMESTERS:
            resp = requests.post(f"{BASE_URL}/CAEResult/studentCAEResult",
                headers=headers,
                json={"RegisterNumber": USERNAME,
                      "AcademicMonthId": sem_info["month"],
                      "AcademicYear": sem_info["year"],
                      "Semester": sem_info["sem"]})
            marks = resp.json().get("responseData", [])
            if marks:
                totals = []
                for m in marks:
                    try:
                        totals.append(float(m.get("Marks", 0)))
                    except:
                        pass
                if totals:
                    results[sem_info["sem"]] = sum(totals) / len(totals)

        if len(results) < 2:
            return "Not enough data to compare semesters."

        result = "Your CAE performance across semesters:\n"
        prev_avg = None
        for sem in sorted(results.keys()):
            avg = results[sem]
            if prev_avg is not None:
                diff = avg - prev_avg
                if diff > 0:
                    trend = f"improved by {diff:.1f}"
                elif diff < 0:
                    trend = f"dropped by {abs(diff):.1f}"
                else:
                    trend = "same as before"
                result += f"Semester {sem}: {avg:.1f}/50 avg ({trend})\n"
            else:
                result += f"Semester {sem}: {avg:.1f}/50 avg\n"
            prev_avg = avg

        latest = results[max(results.keys())]
        prev = results[sorted(results.keys())[-2]]
        if latest > prev:
            result += "You have improved compared to last semester!"
        elif latest < prev:
            result += "Your performance dropped compared to last semester."
        else:
            result += "Your performance is consistent."
        return result
    except Exception as e:
        return f"Could not compare semesters: {e}"

def get_timetable(day=None):
    try:
        headers = get_headers()
        resp = requests.post(f"{BASE_URL}/TimetableDetails/getdatabyprogramme",
            headers=headers,
            json={"TimeTableId": 3964, "ProgrammeSectionId": 3966})
        records = resp.json().get("responseData", [])
        if not records:
            return "No timetable found."

        if day is None:
            day_num = datetime.now().weekday() + 1
        else:
            day_map = {"monday": 1, "tuesday": 2, "wednesday": 3,
                      "thursday": 4, "friday": 5, "saturday": 6}
            day_num = day_map.get(day.lower(), datetime.now().weekday() + 1)

        day_name = DAYS.get(day_num, "Today")
        day_records = [r for r in records
                      if r.get("DayId") == day_num
                      and r.get("HourType") == 1
                      and r.get("SubjectName")]

        if not day_records:
            return f"No classes found for {day_name}."

        day_records.sort(key=lambda x: x.get("Hour", 0))
        result = f"{day_name}'s timetable:\n"
        for r in day_records:
            time_from = r.get("TimeFrom", "")[:5]
            time_to = r.get("TimeTo", "")[:5]
            subject = r.get("SubjectName", "").strip()
            result += f"{time_from}-{time_to}: {subject}\n"
        return result
    except Exception as e:
        return f"Could not fetch timetable: {e}"

def get_attendance():
    try:
        headers = get_headers()
        today = datetime.now()

        resp = requests.post(
            f"{BASE_URL}/StudentDailyAttendance/StudentWiseAttendance",
            headers=headers,
            json={"FromDate": "2026-6-10",
                  "ToDate": "2026-8-31",
                  "StudentId": "25680"})
        data = resp.json().get("responseData", {})

        attended = data.get("AttendanceDetails", [])
        working_days = data.get("ActualWorkingDays", [])

        today_str = today.strftime("%Y-%m-%d")
        past_working = [d for d in working_days if d.get("Date", "") <= today_str]

        total = len(past_working)
        present = len(attended)
        absent = total - present

        if total == 0:
            return "No working days recorded yet this semester."

        percentage = (present / total * 100)
        result = f"Attendance: {present} present, {absent} absent out of {total} working days — {percentage:.1f}%"

        if percentage < 75:
            result += ". Warning: below 75%!"
        else:
            result += ". Looking good!"

        return result
    except Exception as e:
        return f"Could not fetch attendance: {e}"

def auto_login_erp():
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            page.goto("https://erp.sathyabama.ac.in/account/login")
            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(2000)
            page.fill('input[placeholder="Register Number"]', USERNAME)
            page.fill('input[placeholder="Enter Password"]', PASSWORD)
            page.click('button:has-text("LOG IN")')
            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(3000)
            # Keep browser open for 2 minutes for user to interact
            time.sleep(120)
            browser.close()
        return "Logged into ERP."
    except Exception as e:
        import webbrowser
        webbrowser.open("https://erp.sathyabama.ac.in")
        return "Opening ERP — please log in manually."

def auto_login_lms():
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()
            page.goto("https://lms.sathyabama.ac.in")
            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(5000)
            time.sleep(60)
            browser.close()
        return "Opened LMS."
    except Exception as e:
        import webbrowser
        webbrowser.open("https://lms.sathyabama.ac.in")
        return "Opening LMS."