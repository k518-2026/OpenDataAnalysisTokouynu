"""
Comprehensive catalog translator to convert all remaining Japanese keys/values to clear academic English.
"""
import json
from pathlib import Path

CATALOG_DIR = Path("e:/GoogleAntigravity/automation/OpenDataAnalysisTokouynu/data/catalog")

FULL_MAP = {
    "japan_high_school_informatics.json": {
        "metrics": ["Python_Adoption_Pct", "JavaScript_Adoption_Pct", "Common_Test_Prep_Pct", "Inquiry_Lab_Adoption_Pct"],
        "rename_keys": {
            "Python活用率": "Python_Adoption_Pct",
            "JavaScript活用率": "JavaScript_Adoption_Pct",
            "共通テスト情報対策実施率": "Common_Test_Prep_Pct",
            "探究演習導入率": "Inquiry_Lab_Adoption_Pct",
        },
        "group_vals": {
            "公立高等学校": "Public_High_Schools",
            "私立高等学校": "Private_High_Schools",
        }
    },
    "japan_mext_ict_informatization.json": {
        "metrics": ["Elementary_Schools", "Junior_High_Schools", "High_Schools", "National_Average"],
        "rename_keys": {
            "全国平均": "National_Average",
        },
        "group_vals": {
            "端末の日常的利用率(週3日以上)": "Daily_Device_Usage_Rate",
            "教員のICT指導力達成率": "Teacher_ICT_Instruction_Competency",
            "普通教室の無線LAN整備率": "Classroom_WiFi_Coverage",
            "指導者用端末整備率": "Teacher_Device_Ratio",
        }
    },
    "japan_school_absenteeism_bullying.json": {
        "metrics": ["Absentee_Student_Count", "Absentee_Rate_Per_1000", "ICT_Recognized_Attendance_Count"],
        "rename_keys": {
            "ICT出席扱い生徒数": "ICT_Recognized_Attendance_Count",
        },
        "group_vals": {
            "小学校": "Elementary_School",
            "中学校": "Junior_High_School",
        }
    },
    "japan_special_needs_education.json": {
        "title": "MEXT Special Needs Education: Resource Rooms and Assistive Technology in Japan",
        "description": "Longitudinal survey on students receiving instruction in resource rooms (Tsukyu), special classes, support staff counts, and digital assistive device integration in Japan.",
        "time_col": "Year",
        "group_col": "School_Type",
        "metrics": ["Resource_Room_Students", "Special_Class_Enrollment", "Support_Staff_Count", "Assistive_Device_Usage_Pct"],
        "rename_keys": {
            "年度": "Year",
            "学校種": "School_Type",
            "通級指導児童生徒数": "Resource_Room_Students",
            "特別支援学級在籍数": "Special_Class_Enrollment",
            "特別支援教育支援員数": "Support_Staff_Count",
            "端末支援活用率": "Assistive_Device_Usage_Pct",
        },
        "group_vals": {
            "小学校": "Elementary_School",
            "中学校": "Junior_High_School",
        }
    },
    "japan_stem_cs_enrollment.json": {
        "group_vals": {
            "情報科学・工学": "Computer_Science_Engineering",
            "理学": "Natural_Sciences",
            "人文社会": "Humanities_Social_Sciences",
        }
    },
    "japan_teacher_workload_survey.json": {
        "metrics": ["On_Campus_Hours_Weekly", "Lesson_Preparation_Hours", "Extracurricular_Coaching_Hours", "Take_Home_Work_Hours"],
        "rename_keys": {
            "在校等時間": "On_Campus_Hours_Weekly",
            "部活動指導時間": "Extracurricular_Coaching_Hours",
            "持ち帰り仕事時間": "Take_Home_Work_Hours",
        },
        "group_vals": {
            "小学校_平日": "Elementary_Weekdays",
            "中学校_平日": "JuniorHigh_Weekdays",
            "小学校_土日": "Elementary_Weekends",
            "中学校_土日": "JuniorHigh_Weekends",
        }
    },
    "japan_timss_math_science.json": {
        "metrics": ["Average_Scale_Score", "Enjoyment_Positive_Pct", "Self_Efficacy_Positive_Pct", "Utility_Positive_Pct"],
        "rename_keys": {
            "将来役立つ肯定率": "Utility_Positive_Pct",
        },
        "group_vals": {
            "小学校4年_算数": "Grade4_Math",
            "中学校2年_数学": "Grade8_Math",
            "小学校4年_理科": "Grade4_Science",
            "中学校2年_理科": "Grade8_Science",
        }
    },
    "oecd_pisa_math_ict.json": {
        "group_vals": {
            "日本": "Japan",
            "韓国": "South_Korea",
            "エストニア": "Estonia",
            "フィンランド": "Finland",
            "シンガポール": "Singapore",
            "OECD平均": "OECD_Average",
            "アメリカ": "United_States",
        }
    },
    "oecd_talis_teacher_survey.json": {
        "title": "OECD TALIS Teacher Survey: ICT Instruction and Collaborative Professional Development",
        "description": "Comparative cross-national analysis of teacher professional development in ICT, self-efficacy in critical thinking facilitation, and inter-teacher collaborative lesson study across OECD nations.",
        "time_col": "Year",
        "group_col": "Country",
        "metrics": ["ICT_Instruction_Self_Efficacy_Pct", "Critical_Thinking_Facilitation_Pct", "Collaborative_Lesson_Study_Pct"],
        "rename_keys": {
            "調査年": "Year",
            "国・地域": "Country",
            "ICT活用指導肯定率": "ICT_Instruction_Self_Efficacy_Pct",
            "批判的思考促進自己効力感": "Critical_Thinking_Facilitation_Pct",
            "教員間協働指導実施率": "Collaborative_Lesson_Study_Pct",
        },
        "group_vals": {
            "日本": "Japan",
            "OECD平均": "OECD_Average",
            "シンガポール": "Singapore",
            "フィンランド": "Finland",
        }
    },
    "unesco_world_ict_skills.json": {
        "title": "UNESCO / ITU Global ICT Skills: Youth Programming and Digital Competency Benchmarks",
        "description": "Cross-national indicators measuring youth and adult digital proficiency, computational programming skills, advanced spreadsheet modeling, and presentation creation across global economies.",
        "time_col": "Year",
        "group_col": "Country",
        "metrics": ["Programming_Skill_Rate_Pct", "Advanced_Spreadsheet_Usage_Pct", "Presentation_Creation_Rate_Pct"],
        "rename_keys": {
            "年": "Year",
            "国名": "Country",
            "プログラミングスキル保有率": "Programming_Skill_Rate_Pct",
            "表計算高度利用率": "Advanced_Spreadsheet_Usage_Pct",
            "プレゼン作成スキル保有率": "Presentation_Creation_Rate_Pct",
        },
        "group_vals": {
            "フィンランド": "Finland",
            "シンガポール": "Singapore",
            "韓国": "South_Korea",
            "日本": "Japan",
            "世界平均": "World_Average",
        }
    },
    "worldbank_education_indicators.json": {
        "title": "World Bank EdStats: Public Education Expenditure and Minimum Proficiency Benchmarks",
        "description": "Global longitudinal indicators from the World Bank assessing public education expenditure as a percentage of GDP, mathematics baseline proficiency attainment, and Internet penetration rates across leading economies.",
        "time_col": "Year",
        "group_col": "Country",
        "metrics": ["Math_Proficiency_Attainment_Pct", "Govt_Edu_Expenditure_Pct_GDP", "Internet_Usage_Rate_Pct"],
        "rename_keys": {
            "年": "Year",
            "国名": "Country",
            "数学最低習熟度達成率": "Math_Proficiency_Attainment_Pct",
            "教育支出対GDP比": "Govt_Edu_Expenditure_Pct_GDP",
            "インターネット利用率": "Internet_Usage_Rate_Pct",
        },
        "group_vals": {
            "日本": "Japan",
            "ノルウェー": "Norway",
            "イギリス": "United_Kingdom",
            "アメリカ": "United_States",
            "世界平均": "World_Average",
        }
    },
}

for fname, conf in FULL_MAP.items():
    fpath = CATALOG_DIR / fname
    if not fpath.exists():
        continue
    with open(fpath, "r", encoding="utf-8") as f:
        d = json.load(f)

    if "title" in conf:
        d["title"] = conf["title"]
    if "description" in conf:
        d["description"] = conf["description"]
    if "time_col" in conf:
        d["time_col"] = conf["time_col"]
    if "group_col" in conf:
        d["group_col"] = conf["group_col"]
    if "metrics" in conf:
        d["metrics"] = conf["metrics"]

    rename_keys = conf.get("rename_keys", {})
    group_vals = conf.get("group_vals", {})
    grp_col = d.get("group_col")

    new_data = []
    for row in d.get("data", []):
        new_row = {}
        for k, v in row.items():
            new_k = rename_keys.get(k, k)
            new_v = v
            if (new_k == grp_col or k == grp_col) and isinstance(v, str) and v in group_vals:
                new_v = group_vals[v]
            new_row[new_k] = new_v
        new_data.append(new_row)

    d["data"] = new_data

    with open(fpath, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=2)

    print(f"Updated {fname}")
