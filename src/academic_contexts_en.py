"""
Academic Contexts and Theoretical Foundations in English for Japanese Open Datasets.
Provides literature reviews, APA references, and policy frameworks.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

# Master academic context repository mapped by dataset ID
ACADEMIC_CONTEXTS_EN: Dict[str, Dict[str, Any]] = {
    "japan_national_assessment_math": {
        "discipline": "Educational Measurement, Mathematics Education, and Affective Factors",
        "theoretical_framework": "Expectancy-Value Theory (Eccles & Wigfield, 2002) and Self-Determination Theory (Deci & Ryan, 2000)",
        "policy_context": "MEXT National Assessment of Academic Ability (Zenkoku Gakuryoku Chosa) and the GIGA School Initiative",
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
        "theoretical_framework": "TPACK Framework (Mishra & Koehler, 2006) and Unified Theory of Acceptance and Use of Technology (Venkatesh et al., 2003)",
        "policy_context": "The GIGA School Initiative (1 device per student) and MEXT Annual Survey on Educational Informatization in Schools",
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
        "policy_context": "MEXT School Basic Survey (Gakko Kihon Chosa) and the Government Strategic Council for University Functional Enhancement",
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
            "Ministry of Education, Culture, Sports, Science and Technology [MEXT]. (2023). School Basic Survey (Gakko Kihon Chosa). Statistics Division, MEXT.",
            "Archer, L., Dawson, E., DeWitt, J., Seakins, A., & Wong, B. (2015). 'Science capital': A conceptual, methodological, and empirical argument for extending bourdieusian notions of capital beyond the arts. Journal of Research in Science Teaching, 52(7), 922-948.",
        ],
    },
    "japan_teacher_workload_survey": {
        "discipline": "Educational Administration, Teacher Policy, and Occupational Well-Being",
        "theoretical_framework": "Job Demands-Resources (JD-R) Model (Bakker & Demerouti, 2007) and Effort-Reward Imbalance (Siegrist, 1996)",
        "policy_context": "MEXT Survey on Teacher Working Conditions (Kyoin Kinmu Jittai Chosa) and the Central Council for Education Reform Recommendations",
        "literature_review": (
            "Occupational workload and chronic overtime among primary and secondary educators pose severe challenges to teacher recruitment, "
            "pedagogical efficacy, and teacher retention globally (Skaalvik & Skaalvik, 2011). Comparative studies by the OECD (TALIS) have "
            "repeatedly identified Japanese educators as recording the longest average working hours among participating economies, driven by "
            "extensive extracurricular coaching (bukatsudo), administrative reporting, and student guidance duties. Empirical evaluation of working "
            "hour trajectories and structural shifts following government work-style reform legislation provides crucial insights for educational policymakers."
        ),
        "key_references": [
            "Bakker, A. B., & Demerouti, E. (2007). The job demands-resources model: State of the art. Journal of Managerial Psychology, 22(3), 309-328.",
            "Skaalvik, E. M., & Skaalvik, S. (2011). Teacher job satisfaction and motivation to leave the teaching profession: Relations with school context, feeling of belonging, and emotional exhaustion. Teaching and Teacher Education, 27(6), 1029-1038.",
            "Ministry of Education, Culture, Sports, Science and Technology [MEXT]. (2023). Survey on Teacher Working Conditions (Kyoin Kinmu Jittai Chosa). Primary and Secondary Education Bureau.",
            "OECD. (2019). TALIS 2018 Results (Volume I): Teachers and School Leaders as Valued Professionals. OECD Publishing. https://doi.org/10.1787/1d0bc92a-en",
        ],
    },
    "japan_school_absenteeism_bullying": {
        "discipline": "Sociology of Education, Child Welfare, and Inclusive School Environments",
        "theoretical_framework": "Social Ecological Model (Bronfenbrenner, 1979) and School Belonging Theory (Goodenow, 1993)",
        "policy_context": "MEXT Survey on Student Guidance Issues (Jido Seito no Mondai Kodo To Seito Shidojo no Sho-Kadai)",
        "literature_review": (
            "Long-term school absenteeism (Futoko) and reported student bullying incidents in Japanese compulsory education have risen "
            "monotonically to unprecedented historic peaks over the past decade. Educational researchers and the Children and Families Agency "
            "have investigated the confluence of psychological distress, changing societal norms regarding school attendance, and the protective "
            "potential of digital learning safety nets. Quantitative modeling of absenteeism rates across elementary and junior high schools reveals "
            "systemic transition dynamics between educational tiers that demand data-informed structural intervention."
        ),
        "key_references": [
            "Bronfenbrenner, U. (1979). The ecology of human development: Experiments by nature and design. Harvard University Press.",
            "Goodenow, C. (1993). Classroom belonging among early adolescent students: Relationships to motivation and achievement. Journal of Early Adolescence, 13(1), 21-43.",
            "Ministry of Education, Culture, Sports, Science and Technology [MEXT]. (2023). Survey on Student Guidance Issues, Absenteeism, and Bullying. Elementary and Secondary Education Bureau.",
            "Children and Families Agency. (2023). Comprehensive Plan for Children and Youth Support in Japan. Government of Japan.",
        ],
    },
}


def get_academic_context(dataset_id: str) -> Dict[str, Any]:
    """Retrieves academic context or provides a robust fallback."""
    if dataset_id in ACADEMIC_CONTEXTS_EN:
        return ACADEMIC_CONTEXTS_EN[dataset_id]

    # Universal academic context fallback
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
            "Cabinet Office, Government of Japan. (2022). Annual Report on the Japanese Economy and Public Finance. National Printing Bureau.",
            "Statistics Bureau, Ministry of Internal Affairs and Communications. (2023). e-Stat: Portal Site of Official Statistics of Japan. https://www.e-stat.go.jp/",
            "Wooldridge, J. M. (2020). Introductory Econometrics: A Modern Approach (7th ed.). Cengage Learning.",
        ],
    }
