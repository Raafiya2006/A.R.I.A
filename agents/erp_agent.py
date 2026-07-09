import sys
sys.path.insert(0, 'C:\\Raafiya\\A.R.I.A\\venv\\Lib\\site-packages')

from dotenv import load_dotenv
load_dotenv()

import requests
import os
from datetime import datetime

BASE_URL = "https://erp.sathyabama.ac.in/erp/api/v1.0"
USERNAME = os.getenv("ERP_USERNAME", "")
PASSWORD = os.getenv("ERP_PASSWORD", "")

HEADERS_BASE = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "content-type": "application/json",
    "accept": "application/json, text/plain, */*",
    "referer": "https://erp.sathyabama.ac.in/student/view"
}

SEMESTERS = [
    {"sem": 6, "month": 1, "year": "2025-2026"},
    {"sem": 5, "month": 2, "year": "2025-2026"},
    {"sem": 4, "month": 1, "year": "2024-2025"},
    {"sem": 3, "month": 2, "year": "2024-2025"},
    {"sem": 2, "month": 1, "year": "2023-2024"},
    {"sem": 1, "month": 2, "year": "2023-2024"},
]

DAYS = {1: "Monday", 2: "Tuesday", 3: "Wednesday", 4: "Thursday", 5: "Friday", 6: "Saturday"}

def get_headers():
    resp = requests.post(f"{BASE_URL}/MasterStudent/login",
        json={"RegisterNumber": USERNAME, "Password": PASSWORD},
        headers=HEADERS_BASE)
    token = resp.json()["responseData"]["login"]["accessToken"]
    return {**HEADERS_BASE, "Authorization": f"Bearer {token}"}

def get_cae_marks(semester=6):
    try:
        headers = get_headers()
        sem_info = next((s for s in SEMESTERS if s["sem"] == semester), SEMESTERS[0])
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
        # Try each semester until we find one with data
        semesters_to_try = [s for s in SEMESTERS if s["sem"] == semester]
        if not semesters_to_try:
            semesters_to_try = SEMESTERS[1:]  # Skip current sem, try older ones
        
        for sem_info in semesters_to_try:
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
                result = f"Semester {sem_info['sem']} ({sem_info['year']}) results:\n"
                for m in sem_result:
                    subject = m.get("SubjectName", "Unknown")
                    obtained = m.get("TotalMark", m.get("ObtainedMark", "N/A"))
                    max_mark = m.get("MaxMark", 100)
                    grade = m.get("Grade", "")
                    status = m.get("Result", m.get("Status", ""))
                    result += f"{subject} — {obtained}/{max_mark} Grade: {grade} {status}\n"
                if summary:
                    gpa = summary.get("GPA", summary.get("CGPA", ""))
                    if gpa:
                        result += f"GPA: {gpa}"
                return result
        
        return "Semester exam results are not yet published for the current semester. Previous semester results may not be available."
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
            return "Not enough data across semesters to compare."

        result = "Your CAE performance across semesters:\n"
        prev_avg = None
        for sem in sorted(results.keys()):
            avg = results[sem]
            if prev_avg is not None:
                diff = avg - prev_avg
                if diff > 0:
                    trend = f"improved by {diff:.1f} marks"
                elif diff < 0:
                    trend = f"dropped by {abs(diff):.1f} marks"
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

        # If no day specified, use today
        if day is None:
            day_num = datetime.now().weekday() + 1  # Monday=1
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
        # Use full semester date range like the ERP does
        resp = requests.post(
            f"{BASE_URL}/StudentDailyAttendance/StudentWiseAttendance",
            headers=headers,
            json={"FromDate": "2026-6-10",
                  "ToDate": "2026-8-31",
                  "StudentId": "25680"})
        data = resp.json().get("responseData", {})
        
        attended = data.get("AttendanceDetails", [])
        working_days = data.get("ActualWorkingDays", [])
        holidays = data.get("HolidayList", [])
        
        # Count only past working days up to today
        today_str = today.strftime("%Y-%m-%d")
        past_working = [d for d in working_days if d["Date"] <= today_str]
        
        total = len(past_working)
        present = len(attended)
        absent = total - present
        
        if total == 0:
            return "No working days recorded yet this semester."
        
        percentage = (present / total * 100)
        result = f"Your attendance: {present} present, {absent} absent out of {total} working days — {percentage:.1f}%"
        
        if percentage < 75:
            result += ". Warning: below 75%!"
        else:
            result += ". You're doing great!"
        
        return result
    except Exception as e:
        return f"Could not fetch attendance: {e}"