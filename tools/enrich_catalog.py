"""
Script to enrich and translate data catalog datasets into publication-ready English datasets.
"""
import glob
import json
from pathlib import Path

CATALOG_DIR = Path("e:/GoogleAntigravity/automation/OpenDataAnalysisTokouynu/data/catalog")

ENRICHMENT_MAP = {
    "japan_national_assessment_math": {
        "title": "National Assessment of Academic Ability: Mathematics Achievement and Affective Trends in Japan",
        "description": "Longitudinal empirical monitoring of elementary (Grade 6) and lower secondary (Grade 3) mathematics test scores alongside affective engagement, perceived utility value, and digital device integration.",
        "time_col": "Year",
        "group_col": "School_Level",
        "metrics_map": {
            "平均正答率": "Mean_Score_Pct",
            "勉強が好き肯定率": "Enjoyment_Rate_Pct",
            "将来役立つ肯定率": "Perceived_Utility_Pct",
            "端末活用率": "Digital_Device_Usage_Pct",
        },
        "group_val_map": {
            "小学校_算数": "Elementary_Math",
            "中学校_数学": "JuniorHigh_Math",
        },
        "research_angles": [
            {
                "id": "math_affective_gap",
                "title": "The Decoupling of Achievement and Affective Value in Japanese Mathematics Education",
                "focus_metrics": ["Mean_Score_Pct", "Enjoyment_Rate_Pct", "Perceived_Utility_Pct"],
                "research_questions": [
                    "Does cognitive achievement in mathematics correlate positively with student subject enjoyment across educational tiers?",
                    "How has the longitudinal gap between utility valuation and intrinsic interest evolved?"
                ],
                "hypotheses": [
                    "Despite sustained high test scores, intrinsic enjoyment exhibits a statistically significant negative longitudinal trend.",
                    "Secondary school students exhibit significantly steeper declines in mathematics affinity than primary pupils."
                ],
                "theoretical_framework": "Expectancy-Value Theory (Eccles & Wigfield, 2002)"
            },
            {
                "id": "giga_device_impact",
                "title": "Evaluating the Longitudinal Impact of 1-to-1 Device Implementation on Mathematics Learning Engagement",
                "focus_metrics": ["Digital_Device_Usage_Pct", "Mean_Score_Pct", "Enjoyment_Rate_Pct"],
                "research_questions": [
                    "How rapidly has digital terminal utilization expanded under the GIGA School Initiative?",
                    "Is increased classroom digital terminal usage associated with shifts in cognitive test outcomes?"
                ],
                "hypotheses": [
                    "Digital device integration experienced an exponential structural surge post-2020.",
                    "Classroom device utilization demonstrates positive bivariate correlation with subject interest."
                ],
                "theoretical_framework": "Technology Acceptance Model & Digital Pedagogy (Davis, 1989)"
            }
        ]
    },
    "japan_mext_ict_informatization": {
        "title": "MEXT School Informatization Survey: 1-to-1 Computing and Pedagogical Competencies in Japan",
        "description": "Comprehensive institutional survey measuring digital device saturation, broadband network connectivity, classroom instructional technology integration, and teacher ICT instructional competencies across public schools in Japan.",
        "time_col": "Year",
        "group_col": "School_Type",
        "metrics_map": {
            "小学校": "Elementary_Schools",
            "中学校": "Junior_High_Schools",
            "高等学校": "High_Schools",
            "全国計": "National_Total",
        },
        "research_angles": [
            {
                "id": "teacher_ict_readiness",
                "title": "Institutional Readiness and Teacher Pedagogical Technology Integration Post-GIGA Deployment",
                "focus_metrics": ["Elementary_Schools", "Junior_High_Schools", "High_Schools", "National_Total"],
                "research_questions": [
                    "How has institutional ICT readiness evolved across elementary, junior high, and senior high school tiers in Japan?",
                    "Does high school ICT integration lag significantly behind compulsory education stages?"
                ],
                "hypotheses": [
                    "Compulsory school levels demonstrate significantly faster infrastructure saturation compared to senior high schools.",
                    "Teacher ICT guidance competency exhibits a positive linear growth trajectory across all prefectural jurisdictions."
                ],
                "theoretical_framework": "TPACK Framework (Mishra & Koehler, 2006)"
            }
        ]
    },
    "japan_stem_cs_enrollment": {
        "title": "MEXT School Basic Survey: Collegiate STEM and Computer Science Enrollment and Gender Ratios in Japan",
        "description": "Longitudinal administrative monitoring of undergraduate and graduate admissions in science, engineering, and computer science disciplines, tracking institutional expansion and female student participation rates.",
        "time_col": "Year",
        "group_col": "Academic_Field",
        "metrics_map": {
            "入学者総数": "Total_Admissions",
            "女性入学者数": "Female_Admissions",
            "女性比率": "Female_Percentage",
        },
        "group_val_map": {
            "理学": "Natural_Sciences",
            "工学": "Engineering",
            "情報科学": "Computer_Science",
        },
        "research_angles": [
            {
                "id": "female_stem_parity",
                "title": "Gender Parity Trajectories in Collegiate Computing and Engineering Admissions in Japan",
                "focus_metrics": ["Female_Percentage", "Total_Admissions", "Female_Admissions"],
                "research_questions": [
                    "To what extent has female enrollment in Japanese collegiate computer science programs shifted over the last decade?",
                    "Do computer science faculties exhibit distinct gender integration patterns relative to traditional engineering disciplines?"
                ],
                "hypotheses": [
                    "Female representation in computer science demonstrates a statistically significant positive trend.",
                    "Overall female STEM enrollment remains below OECD benchmark parity levels."
                ],
                "theoretical_framework": "Social Cognitive Career Theory & Science Capital (Archer et al., 2015)"
            }
        ]
    },
    "japan_teacher_workload_survey": {
        "title": "MEXT Teacher Working Conditions Survey: Working Hours, Extracurricular Coaching, and Overtime Trajectories",
        "description": "Administrative investigation into working hours, on-campus stay duration, lesson preparation time, and extracurricular club activity coaching among Japanese primary and secondary educators.",
        "time_col": "Year",
        "group_col": "School_Level",
        "metrics_map": {
            "在校時間": "On_Campus_Hours_Weekly",
            "授業準備時間": "Lesson_Preparation_Hours",
            "部活動時間": "Extracurricular_Coaching_Hours",
            "持ち帰り残業時間": "Take_Home_Overtime_Hours",
        },
        "group_val_map": {
            "小学校": "Elementary_School",
            "中学校": "Junior_High_School",
        },
        "research_angles": [
            {
                "id": "teacher_overtime_workstyle",
                "title": "Longitudinal Impact of Work-Style Reform on Primary and Secondary Teacher Overtime in Japan",
                "focus_metrics": ["On_Campus_Hours_Weekly", "Extracurricular_Coaching_Hours", "Lesson_Preparation_Hours"],
                "research_questions": [
                    "Have average weekly on-campus working hours decreased following government work-style reform legislation?",
                    "What proportion of non-instructional workload is driven by extracurricular sports coaching?"
                ],
                "hypotheses": [
                    "Junior high school educators record significantly longer working hours than elementary teachers, primarily driven by club activities.",
                    "Post-reform regulatory guidelines have led to a moderate reduction in extreme overtime cohorts."
                ],
                "theoretical_framework": "Job Demands-Resources (JD-R) Model (Bakker & Demerouti, 2007)"
            }
        ]
    },
    "japan_school_absenteeism_bullying": {
        "title": "MEXT Student Guidance Survey: School Absenteeism, Bullying Incidents, and ICT Learning Support in Japan",
        "description": "Nationwide empirical statistics on persistent non-attendance (Futoko), reported bullying cases, and digital learning support attendance credits across elementary and junior high schools in Japan.",
        "time_col": "Year",
        "group_col": "School_Level",
        "metrics_map": {
            "不登校児童生徒数": "Absentee_Student_Count",
            "千人あたり不登校率": "Absentee_Rate_Per_1000",
            "ICT出席扱い児童生徒数": "ICT_Recognized_Attendance_Count",
        },
        "group_val_map": {
            "小学校": "Elementary_School",
            "中学校": "Junior_High_School",
        },
        "research_angles": [
            {
                "id": "absenteeism_ict_safetynet",
                "title": "Digital Learning Support as an Institutional Safety Net for School Absenteeism in Japan",
                "focus_metrics": ["Absentee_Rate_Per_1000", "ICT_Recognized_Attendance_Count", "Absentee_Student_Count"],
                "research_questions": [
                    "How steep is the secular increase in absenteeism rates between primary and lower secondary schools in Japan?",
                    "To what extent has official ministerial accreditation of online home learning mediated student school disconnect?"
                ],
                "hypotheses": [
                    "Secondary school absenteeism rates exhibit an exponential acceleration over the past decade.",
                    "Accreditation of remote digital learning attendance exhibits a positive correlation with educational reintegration."
                ],
                "theoretical_framework": "Social Ecological Model of School Belonging (Goodenow, 1993)"
            }
        ]
    },
    "japan_high_school_informatics": {
        "title": "Japanese Upper Secondary Informatics: Programming Curricula and University Entrance Exam Preparation",
        "description": "Survey on the implementation of compulsory programming education (Information I), language selection (Python vs JavaScript), and preparatory measures for the Common Test for University Admissions.",
        "time_col": "Year",
        "group_col": "Curriculum_Track",
        "metrics_map": {
            "Python採用率": "Python_Adoption_Pct",
            "JavaScript採用率": "JavaScript_Adoption_Pct",
            "共通テスト対策実施率": "Common_Test_Prep_Pct",
            "実習時間割合": "Hands_on_Lab_Time_Pct",
        },
        "research_angles": [
            {
                "id": "programming_language_diffusion",
                "title": "Curricular Technology Diffusion: Python Adoption in Upper Secondary Informatics Education in Japan",
                "focus_metrics": ["Python_Adoption_Pct", "JavaScript_Adoption_Pct", "Common_Test_Prep_Pct"],
                "research_questions": [
                    "Which programming paradigms have achieved institutional dominance within Japan's 'Information I' curriculum?",
                    "Does university entrance exam inclusion accelerate hands-on computational lab implementation?"
                ],
                "hypotheses": [
                    "Python adoption demonstrates monotonic market dominance over legacy web scripting languages.",
                    "Schools with active university entrance exam preparation allocate higher proportions of instructional time to lab coding."
                ],
                "theoretical_framework": "Diffusion of Innovations Theory (Rogers, 2003)"
            }
        ]
    },
    "japan_timss_math_science": {
        "title": "IEA TIMSS Japan: Longitudinal Trajectories of Mathematics and Science Cognitive Attainment and Motivation",
        "description": "Comparative longitudinal data from the Trends in International Mathematics and Science Study (TIMSS), assessing fourth-grade and eighth-grade cognitive attainment, intrinsic motivation, and self-efficacy in Japan.",
        "time_col": "Year",
        "group_col": "Grade_Subject",
        "metrics_map": {
            "平均得点": "Average_Scale_Score",
            "勉強が楽しい肯定率": "Enjoyment_Positive_Pct",
            "得意である肯定率": "Self_Efficacy_Positive_Pct",
            "将来役に立つ肯定率": "Utility_Value_Positive_Pct",
        },
        "group_val_map": {
            "小4_算数": "Grade4_Math",
            "中2_数学": "Grade8_Math",
            "小4_理科": "Grade4_Science",
            "中2_理科": "Grade8_Science",
        },
        "research_angles": [
            {
                "id": "timss_affective_decline",
                "title": "Longitudinal Cross-Grade Transitions: Cognitive Resilience vs Affective Burnout in Japanese STEM",
                "focus_metrics": ["Average_Scale_Score", "Self_Efficacy_Positive_Pct", "Enjoyment_Positive_Pct"],
                "research_questions": [
                    "How does mathematics and science self-concept transition from primary (Grade 4) to secondary (Grade 8) cohorts?",
                    "Does international cognitive superiority mask persistent deficits in academic self-concept?"
                ],
                "hypotheses": [
                    "Scale scores remain statistically stable and internationally superior over multi-decade TIMSS cycles.",
                    "Student academic self-concept experiences a statistically significant drop between Grade 4 and Grade 8."
                ],
                "theoretical_framework": "Self-Concept Internal/External Frame of Reference Model (Marsh, 1986)"
            }
        ]
    },
    "oecd_pisa_math_ict": {
        "title": "OECD PISA Comparative Data: Mathematics Literacy, Gender Differentials, and Digital Device Integration",
        "description": "International triennial assessment of 15-year-old student performance in mathematics literacy, gender gap dynamics, and digital device utilization patterns across major OECD economies including Japan.",
        "time_col": "Year",
        "group_col": "Country",
        "metrics_map": {
            "数学得点": "Math_Literacy_Score",
            "男子得点": "Male_Math_Score",
            "女子得点": "Female_Math_Score",
            "男女得点差": "Gender_Score_Gap",
        },
        "research_angles": [
            {
                "id": "pisa_japan_comparative",
                "title": "Cognitive Resilience and Socio-Digital Dynamics: Evaluating Japan's PISA Mathematics Trajectory",
                "focus_metrics": ["Math_Literacy_Score", "Gender_Score_Gap", "Male_Math_Score", "Female_Math_Score"],
                "research_questions": [
                    "How does Japan's mathematics literacy trajectory compare longitudinally against OECD benchmarks?",
                    "Has the gender score gap converged toward parity over successive PISA assessment waves?"
                ],
                "hypotheses": [
                    "Japan demonstrates statistically significant resilience in mathematics literacy relative to global post-pandemic trends.",
                    "The gender score differential in mathematics remains narrow but statistically persistent."
                ],
                "theoretical_framework": "Comparative Educational Achievement Framework (OECD, 2023)"
            }
        ]
    },
}

def enrich_all():
    files = list(CATALOG_DIR.glob("*.json"))
    for file_path in files:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        dataset_id = data.get("id")
        if dataset_id not in ENRICHMENT_MAP:
            continue

        info = ENRICHMENT_MAP[dataset_id]
        data["title_ja"] = data.get("title", "")
        data["title"] = info["title"]
        data["description"] = info["description"]
        data["research_angles"] = info["research_angles"]

        # Rename columns if needed
        old_time = data.get("time_col", "年度")
        new_time = info.get("time_col", "Year")
        data["time_col"] = new_time

        old_group = data.get("group_col")
        new_group = info.get("group_col", old_group)
        data["group_col"] = new_group

        metrics_map = info.get("metrics_map", {})
        data["metrics"] = [metrics_map.get(m, m) for m in data.get("metrics", [])]

        group_val_map = info.get("group_val_map", {})

        # Transform data rows
        new_rows = []
        for row in data.get("data", []):
            new_row = {}
            for k, v in row.items():
                target_k = k
                if k == old_time:
                    target_k = new_time
                elif k == old_group:
                    target_k = new_group
                elif k in metrics_map:
                    target_k = metrics_map[k]

                # Map group value if string
                target_v = v
                if target_k == new_group and isinstance(v, str) and v in group_val_map:
                    target_v = group_val_map[v]

                new_row[target_k] = target_v
            new_rows.append(new_row)

        data["data"] = new_rows

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"Successfully enriched {file_path.name}")

if __name__ == "__main__":
    enrich_all()
