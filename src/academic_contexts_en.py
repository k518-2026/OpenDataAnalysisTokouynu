"""
Academic Contexts and Theoretical Foundations in English for Japanese Open Datasets.
Provides literature reviews, APA references, and policy frameworks for all datasets.
"""
from __future__ import annotations

from typing import Any, Dict

ACADEMIC_CONTEXTS_EN: Dict[str, Dict[str, Any]] = {
    "japan_national_assessment_math": {
        "discipline": "Educational Measurement, Mathematics Education, and Affective Factors",
        "theoretical_framework": "Expectancy-Value Theory (Eccles & Wigfield, 2002) and Self-Determination Theory (Deci & Ryan, 2000)",
        "policy_context": "MEXT National Assessment of Academic Ability and the GIGA School Initiative",
        "literature_review": (
            "Extensive educational research demonstrates that affective constructs—such as academic self-concept, "
            "intrinsic interest, and perceived utility value—significantly mediate mathematics achievement across "
            "compulsory schooling (Hulleman et al., 2010; Marsh & Martin, 2011). In Japan, national monitoring surveys "
            "conducted by the National Institute for Educational Policy Research (NIER) have persistently highlighted a "
            "discrepancy between high cognitive performance on international assessments (PISA/TIMSS) and comparatively low "
            "affective engagement among Japanese secondary students. Furthermore, the rapid nationwide rollout of one-to-one "
            "digital devices under the GIGA School Initiative since 2020 introduces a critical structural variable, prompting "
            "questions regarding how classroom device utilization relates to subject affinity and scholastic attainment."
        ),
        "key_references": [
            "Eccles, J. S., & Wigfield, A. (2002). Motivational beliefs, values, and goals. Annual Review of Psychology, 53(1), 109-132. https://doi.org/10.1146/annurev.psych.53.100901.135153",
            "Deci, E. L., & Ryan, R. M. (2000). The 'what' and 'why' of goal pursuits: Human needs and the self-determination of behavior. Psychological Inquiry, 11(4), 227-268. https://doi.org/10.1207/S15327965PLI1104_01",
            "Ministry of Education, Culture, Sports, Science and Technology [MEXT]. (2023). Report on the National Assessment of Academic Ability and Learning Conditions. National Institute for Educational Policy Research (NIER).",
            "Watanabe, K., & Shimizu, N. (2021). Longitudinal trajectories of mathematics engagement in Japanese elementary and junior high schools. Japan Journal of Educational Technology, 45(2), 145-156.",
            "OECD. (2023). PISA 2022 Results (Volume I): The State of Learning and Equity in Education. OECD Publishing. https://doi.org/10.1787/53f23881-en",
        ],
    },
    "japan_mext_ict_informatization": {
        "discipline": "Educational Technology, Digital Pedagogy, and Educational Policy",
        "theoretical_framework": "TPACK Framework (Mishra & Koehler, 2006) and Technology Acceptance Model (Davis, 1989)",
        "policy_context": "The GIGA School Initiative (1 device per student) and MEXT School Informatization Monitoring",
        "literature_review": (
            "The transformation of K-12 educational environments through one-to-one digital infrastructure requires not merely "
            "hardware ubiquity, but the concurrent enhancement of pedagogical technology integration and teacher digital competencies "
            "(Ertmer & Ottenbreit-Leftwich, 2010). Under Japan's comprehensive GIGA School Initiative launched by MEXT, nearly all public "
            "elementary and junior high schools achieved 1-to-1 computing environments by 2021. However, systematic empirical inquiry into "
            "the subsequent trajectory—encompassing high-speed network saturation, regular classroom instructional integration, and "
            "teacher pedagogical competency—remains paramount for understanding educational equity and institutional readiness."
        ),
        "key_references": [
            "Mishra, P., & Koehler, M. J. (2006). Technological pedagogical content knowledge: A framework for teacher knowledge. Teachers College Record, 108(6), 1017-1054.",
            "Ertmer, P. A., & Ottenbreit-Leftwich, A. T. (2010). Teacher technology change: How knowledge, confidence, beliefs, and culture intersect. Journal of Research on Technology in Education, 42(3), 255-284.",
            "Ministry of Education, Culture, Sports, Science and Technology [MEXT]. (2023). Survey on the Actual Conditions of School Informatization. MEXT Information Education Division.",
            "Horita, T. (2021). The roadmap and future directions of the GIGA School Project in Japan. Educational Information Research, 37(1), 3-12.",
            "Venkatesh, V., Morris, M. G., Davis, G. B., & Davis, F. D. (2003). User acceptance of information technology: Toward a unified view. MIS Quarterly, 27(3), 425-478.",
        ],
    },
    "japan_stem_cs_enrollment": {
        "discipline": "Higher Education Policy, STEM Education, and Gender Diversity",
        "theoretical_framework": "Social Cognitive Career Theory (Lent, Brown, & Hackett, 1994) and Science Capital Theory (Archer et al., 2015)",
        "policy_context": "MEXT School Basic Survey and National Digital Human Resource Cultivation Strategy",
        "literature_review": (
            "The expansion of human resources in science, technology, engineering, and mathematics (STEM)—particularly in computer science "
            "and information engineering—is recognized globally as vital for economic vitality and technological sovereignty (Cheryan et al., 2017). "
            "In Japan, public policy has prioritized structural reallocation of university capacity toward digital and green technology fields. "
            "Concurrently, the underrepresentation of female students in Japanese collegiate STEM faculties represents a persistent structural "
            "inequity, prompting rigorous empirical tracking of enrollment trends, institutional tier differences, and gender ratios over time."
        ),
        "key_references": [
            "Lent, R. W., Brown, S. D., & Hackett, G. (1994). Toward a unifying social cognitive theory of career and academic interest, choice, and performance. Journal of Vocational Behavior, 45(1), 79-122.",
            "Cheryan, S., Ziegler, S. A., Montoya, A. K., & Schmader, T. (2017). Why are some STEM fields more gender balanced than others? Psychological Bulletin, 143(1), 1-35. https://doi.org/10.1037/bul0000052",
            "Ministry of Education, Culture, Sports, Science and Technology [MEXT]. (2023). School Basic Survey. Statistics Bureau & MEXT.",
            "Archer, L., Dawson, E., DeWitt, J., Seakins, A., & Wong, B. (2015). 'Science capital': A conceptual, methodological, and empirical argument for extending bourdieusian notions of capital beyond the arts. Journal of Research in Science Teaching, 52(7), 922-948.",
        ],
    },
    "japan_teacher_workload_survey": {
        "discipline": "Educational Administration, Teacher Policy, and Occupational Well-Being",
        "theoretical_framework": "Job Demands-Resources (JD-R) Model (Bakker & Demerouti, 2007) and Effort-Reward Imbalance (Siegrist, 1996)",
        "policy_context": "MEXT Survey on Teacher Working Conditions and Special Measures Law Concerning Educational Personnel (Kyotoku-ho) Reforms",
        "literature_review": (
            "Occupational workload and chronic overtime among primary and secondary educators pose severe challenges to teacher recruitment, "
            "pedagogical efficacy, and teacher retention globally (Skaalvik & Skaalvik, 2011). Comparative studies by the OECD (TALIS) have "
            "repeatedly identified Japanese educators as recording the longest average working hours among participating economies, driven by "
            "extensive extracurricular coaching, administrative reporting, and student guidance duties. Empirical evaluation of working "
            "hour trajectories and structural shifts following government work-style reform legislation provides crucial insights for educational policymakers."
        ),
        "key_references": [
            "Bakker, A. B., & Demerouti, E. (2007). The job demands-resources model: State of the art. Journal of Managerial Psychology, 22(3), 309-328.",
            "Skaalvik, E. M., & Skaalvik, S. (2011). Teacher job satisfaction and motivation to leave the teaching profession: Relations with school context, feeling of belonging, and emotional exhaustion. Teaching and Teacher Education, 27(6), 1029-1038.",
            "Ministry of Education, Culture, Sports, Science and Technology [MEXT]. (2023). Comprehensive Survey on Teacher Work Styles and Working Conditions. Government of Japan.",
            "OECD. (2019). TALIS 2018 Results (Volume I): Teachers and School Leaders as Valued Professionals. OECD Publishing. https://doi.org/10.1787/1d0bc92a-en",
        ],
    },
    "japan_school_absenteeism_bullying": {
        "discipline": "Sociology of Education, Child Welfare, and Inclusive School Environments",
        "theoretical_framework": "Social Ecological Model (Bronfenbrenner, 1979) and School Belonging Theory (Goodenow, 1993)",
        "policy_context": "MEXT Survey on Student Guidance Issues and the Children and Families Agency Comprehensive Support Plan",
        "literature_review": (
            "Long-term school absenteeism and reported student bullying incidents in Japanese compulsory education have risen "
            "monotonically to unprecedented historic peaks over the past decade. Educational researchers and the Children and Families Agency "
            "have investigated the confluence of psychological distress, changing societal norms regarding school attendance, and the protective "
            "potential of digital learning safety nets. Quantitative modeling of absenteeism rates across elementary and junior high schools reveals "
            "systemic transition dynamics between educational tiers that demand data-informed structural intervention."
        ),
        "key_references": [
            "Bronfenbrenner, U. (1979). The ecology of human development: Experiments by nature and design. Harvard University Press.",
            "Goodenow, C. (1993). Classroom belonging among early adolescent students: Relationships to motivation and achievement. Journal of Early Adolescence, 13(1), 21-43.",
            "Ministry of Education, Culture, Sports, Science and Technology [MEXT]. (2023). Survey on Student Guidance Issues, Non-Attendance, and Bullying. Elementary and Secondary Education Bureau.",
            "Children and Families Agency. (2023). Comprehensive Plan for Children and Youth Support in Japan. Government of Japan.",
        ],
    },
    "japan_high_school_informatics": {
        "discipline": "Computer Science Education, Curriculum Diffusion, and Educational Assessment",
        "theoretical_framework": "Diffusion of Innovations Theory (Rogers, 2003) and Computational Thinking Framework (Wing, 2006)",
        "policy_context": "Mandatory Upper Secondary 'Information I' Curriculum and the Common Test for University Admissions",
        "literature_review": (
            "The integration of compulsory computer science and programming in secondary curricula represents a major international trend. "
            "In Japan, the 2022 implementation of the revised Course of Study made 'Information I' mandatory for all high school students, "
            "followed by its inclusion in the National Center Test for University Admissions starting in 2025. This curricular transition catalyzed "
            "a nationwide shift from visual blocks to text-based languages—principally Python and JavaScript. Investigating language adoption "
            "rates and hands-on lab allocation yields foundational insights into curriculum diffusion and institutional change."
        ),
        "key_references": [
            "Rogers, E. M. (2003). Diffusion of innovations (5th ed.). Free Press.",
            "Wing, J. M. (2006). Computational thinking. Communications of the ACM, 49(3), 33-35. https://doi.org/10.1145/1118178.1118215",
            "MEXT. (2022). High School Curriculum Guidelines Commentary: Information Section. Ministry of Education, Culture, Sports, Science and Technology.",
            "Grover, S., & Pea, R. (2013). Computational thinking in K-12: A review of the state of the field. Educational Researcher, 42(1), 38-43.",
        ],
    },
    "japan_special_needs_education": {
        "discipline": "Special Education, Inclusive Pedagogy, and Assistive Technology",
        "theoretical_framework": "Universal Design for Learning (UDL) (Rose & Meyer, 2002) and Capability Approach (Sen, 1993)",
        "policy_context": "MEXT Special Needs Education Support Policy and GIGA Assistive Technology Guidelines",
        "literature_review": (
            "Inclusive education requires providing appropriate educational accommodations and assistive technologies to learners "
            "with diverse developmental needs. In Japan, enrollment in resource room instruction (Tsukyu) and special needs classes within "
            "regular schools has expanded rapidly. Leveraging digital terminals for personalized cognitive support has emerged as a key "
            "policy objective to ensure equitable access to curriculum materials."
        ),
        "key_references": [
            "Rose, D. H., & Meyer, A. (2002). Teaching every student in the digital age: Universal design for learning. ASCD.",
            "UNESCO. (2020). Global Education Monitoring Report 2020: Inclusion and education: All means all. UNESCO Publishing.",
            "MEXT. (2023). Actual Conditions of Special Needs Education in Japan. Special Needs Education Division.",
        ],
    },
    "japan_timss_math_science": {
        "discipline": "Comparative International Assessment, STEM Learning, and Academic Self-Concept",
        "theoretical_framework": "Internal/External Frame of Reference Model (Marsh, 1986) and Self-Efficacy Theory (Bandura, 1997)",
        "policy_context": "IEA Trends in International Mathematics and Science Study (TIMSS) Japan Trajectory",
        "literature_review": (
            "International educational benchmarks repeatedly document that Japanese pupils attain elite cognitive scale scores in mathematics "
            "and natural sciences on IEA TIMSS assessments. However, cross-grade comparisons reveal a striking divergence: student intrinsic "
            "motivation and self-efficacy decline sharply between primary (Grade 4) and secondary (Grade 8) cohorts. Analyzing these long-term "
            "trajectories illuminates the structural dynamics of cognitive competence versus affective disengagement."
        ),
        "key_references": [
            "Mullis, I. V., Martin, M. O., Foy, P., Kelly, D. L., & Fishbein, B. (2020). TIMSS 2019 International Results in Mathematics and Science. Boston College, TIMSS & PIRLS International Study Center.",
            "Marsh, H. W. (1986). Verbal and math self-concepts: An internal/external frame of reference model. American Educational Research Journal, 23(1), 129-149.",
            "Bandura, A. (1997). Self-efficacy: The exercise of control. W. H. Freeman.",
        ],
    },
    "oecd_pisa_math_ict": {
        "discipline": "International Large-Scale Assessment, Mathematics Literacy, and Gender Equity",
        "theoretical_framework": "Literacy Model of Mathematical Competencies (Niss, 2003) and Gender Socialization Theory",
        "policy_context": "OECD Programme for International Student Assessment (PISA) Longitudinal Cycles",
        "literature_review": (
            "OECD PISA assessments provide rigorous comparative metrics on 15-year-old students' capacity to formulate, employ, and interpret "
            "mathematics in real-world contexts. While Japan consistently demonstrates robust cognitive performance across cycles, examining "
            "gender score differentials, digital tool integration, and resilience against systemic disruptions offers critical comparative insights."
        ),
        "key_references": [
            "OECD. (2023). PISA 2022 Results (Volume I): The State of Learning and Equity in Education. OECD Publishing. https://doi.org/10.1787/53f23881-en",
            "Niss, M. (2003). Mathematical competencies and the learning of mathematics: The Danish KOM project. Roskilde University.",
        ],
    },
    "oecd_talis_teacher_survey": {
        "discipline": "Comparative Teacher Policy, Professional Development, and Collaborative Learning",
        "theoretical_framework": "Teacher Self-Efficacy Theory (Tschannen-Moran & Hoy, 2001) and Professional Learning Communities (DuFour, 2004)",
        "policy_context": "OECD Teaching and Learning International Survey (TALIS) and Professional Development Policies",
        "literature_review": (
            "Teacher self-efficacy in utilizing educational technologies and fostering critical thinking is a vital driver of student learning "
            "gains. OECD TALIS provides multi-national evidence on classroom instructional practices, collaborative lesson study, and professional "
            "autonomy. Investigating relationships between technological self-efficacy and collaborative lesson preparation reveals how systemic "
            "support structures empower educators across jurisdictions."
        ),
        "key_references": [
            "OECD. (2019). TALIS 2018 Results (Volume I): Teachers and School Leaders as Valued Professionals. OECD Publishing. https://doi.org/10.1787/1d0bc92a-en",
            "Tschannen-Moran, M., & Hoy, A. W. (2001). Teacher efficacy: Capturing an elusive construct. Teaching and Teacher Education, 17(7), 783-805.",
            "DuFour, R. (2004). What is a 'professional learning community'? Educational Leadership, 61(8), 6-11.",
        ],
    },
    "unesco_world_ict_skills": {
        "discipline": "Global Digital Literacy, Human Capital, and Computational Skills",
        "theoretical_framework": "Digital Divide Theory (van Dijk, 2005) and Human Capital Theory (Becker, 1964)",
        "policy_context": "UN Sustainable Development Goal 4 (SDG 4.4.1) Youth ICT Competency Benchmarks",
        "literature_review": (
            "Cross-national monitoring of digital competencies—such as computer programming, advanced spreadsheet modeling, and digital presentation "
            "creation—is central to tracking progress toward UN SDG 4.4.1. Comparative empirical benchmarking illuminates how national educational "
            "investments foster foundational computing skills among youth and adult populations in diverse knowledge economies."
        ),
        "key_references": [
            "UNESCO Institute for Statistics [UIS]. (2022). Monitoring SDG 4: Global Education Indicators. UNESCO Publishing.",
            "van Dijk, J. A. (2005). The deepening divide: Inequality in the information society. SAGE Publications.",
            "International Telecommunication Union [ITU]. (2023). Facts and Figures 2023: Global Connectivity Report. ITU.",
        ],
    },
    "worldbank_education_indicators": {
        "discipline": "Development Economics, Education Financing, and Foundational Learning",
        "theoretical_framework": "Education Production Function (Hanushek, 1979) and Endogenous Growth Theory (Lucas, 1988)",
        "policy_context": "World Bank EdStats and Global Foundational Learning Compact",
        "literature_review": (
            "The relationship between public education expenditure as a percentage of gross domestic product (GDP) and scholastic proficiency "
            "outcomes constitutes a cornerstone question in educational economics. Utilizing World Bank open indicators allows empirical evaluation "
            "of how public fiscal allocation interacts with digital penetration and baseline mathematics competency across advanced and emerging economies."
        ),
        "key_references": [
            "World Bank. (2023). The State of Global Learning Poverty: 2022 Update. The World Bank Group.",
            "Hanushek, E. A. (1979). Conceptual and empirical issues in the estimation of educational production functions. Journal of Human Resources, 14(3), 351-388.",
            "Lucas, R. E. (1988). On the mechanics of economic development. Journal of Monetary Economics, 22(1), 3-42.",
        ],
    },
}


def get_academic_context(dataset_id: str) -> Dict[str, Any]:
    """Retrieves academic context or provides a robust fallback."""
    if dataset_id in ACADEMIC_CONTEXTS_EN:
        return ACADEMIC_CONTEXTS_EN[dataset_id]

    # Universal academic context fallback (pure academic English)
    return {
        "discipline": "Public Policy Analysis, Quantitative Social Science, and Open Data Informatics",
        "theoretical_framework": "Empirical Policy Evaluation and Longitudinal Time-Series Frameworks",
        "policy_context": "Official Japanese Government Statistics and Open Data Portals (e-Stat / Digital Agency)",
        "literature_review": (
            "The utilization of governmental open datasets provides rigorous empirical grounds for evaluating public policy outcomes "
            "and societal trends. Longitudinal econometric and statistical modeling allows researchers to disentangle secular trends "
            "from localized structural shocks, offering objective quantitative evidence to inform administrative decisions and academic discourse."
        ),
        "key_references": [
            "Cabinet Office, Government of Japan. (2023). Annual Report on the Japanese Economy and Public Finance. National Printing Bureau.",
            "Statistics Bureau, Ministry of Internal Affairs and Communications. (2023). e-Stat: Portal Site of Official Statistics of Japan. https://www.e-stat.go.jp/",
            "Wooldridge, J. M. (2020). Introductory Econometrics: A Modern Approach (7th ed.). Cengage Learning.",
        ],
    }
