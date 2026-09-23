"""
Statistical Analysis Engine for OpenDataAnalysisTokouynu.
Calculates descriptive statistics, longitudinal trend regressions (OLS),
correlation metrics, Bayes Factors, and group disparities for empirical research.
"""
from __future__ import annotations

from dataclasses import dataclass, field
import logging
import math
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from scipy import stats

from src.fetchers.base import DatasetResearchAngle, EducationDataset

logger = logging.getLogger(__name__)


@dataclass
class MetricDescriptiveStats:
    """Summary descriptive statistics for a single numerical metric."""
    metric: str
    count: int
    mean: float
    median: float
    std: float
    min_val: float
    max_val: float
    iqr: float
    skewness: float
    unit: str


@dataclass
class TrendRegressionResult:
    """Longitudinal trend linear regression (OLS) results."""
    metric: str
    group: Optional[str]
    slope: float
    intercept: float
    r_squared: float
    p_value: float
    std_err: float
    cagr: Optional[float]
    total_change: float
    percent_change: float
    start_year: int
    end_year: int
    start_value: float
    end_value: float


@dataclass
class CorrelationResult:
    """Bivariate correlation results between two metrics."""
    metric_x: str
    metric_y: str
    pearson_r: float
    p_value: float
    n: int
    r_squared: float
    interpretation: str


@dataclass
class EmpiricalAnalysisResult:
    """Complete statistical output bundle for academic paper authoring."""
    dataset_id: str
    dataset_title: str
    research_angle: Optional[DatasetResearchAngle]
    descriptive_stats: List[MetricDescriptiveStats]
    trend_regressions: List[TrendRegressionResult]
    correlations: List[CorrelationResult]
    group_comparisons: Dict[str, Any]
    bayes_factors: Dict[str, float]
    summary_narrative: str
    raw_df: pd.DataFrame


class EduDataAnalyzer:
    """Performs rigorous statistical analysis on open datasets."""

    def analyze(
        self,
        dataset: EducationDataset,
        angle: Optional[DatasetResearchAngle] = None
    ) -> EmpiricalAnalysisResult:
        """Runs comprehensive statistical analysis based on the dataset and research angle."""
        df = dataset.to_dataframe()
        metrics = angle.focus_metrics if (angle and angle.focus_metrics) else dataset.metrics
        # Filter metrics that exist in dataframe
        valid_metrics = [m for m in metrics if m in df.columns]

        if not valid_metrics:
            # Fallback to all numeric columns except time_col
            valid_metrics = [
                c for c in df.select_dtypes(include=[np.number]).columns
                if c != dataset.time_col
            ]

        desc_stats = self._calc_descriptive_stats(df, valid_metrics, dataset.unit)
        trend_regs = self._calc_trend_regressions(df, dataset.time_col, dataset.group_col, valid_metrics)
        corrs = self._calc_correlations(df, valid_metrics)
        group_comps = self._calc_group_comparisons(df, dataset.group_col, valid_metrics)
        bfs = self._calc_bayes_factors(trend_regs)

        narrative = self._build_summary_narrative(
            dataset.title, valid_metrics, desc_stats, trend_regs, corrs, angle
        )

        return EmpiricalAnalysisResult(
            dataset_id=dataset.id,
            dataset_title=dataset.title,
            research_angle=angle,
            descriptive_stats=desc_stats,
            trend_regressions=trend_regs,
            correlations=corrs,
            group_comparisons=group_comps,
            bayes_factors=bfs,
            summary_narrative=narrative,
            raw_df=df,
        )

    def _calc_descriptive_stats(
        self, df: pd.DataFrame, metrics: List[str], unit: str
    ) -> List[MetricDescriptiveStats]:
        results = []
        for m in metrics:
            series = pd.to_numeric(df[m], errors="coerce").dropna()
            if len(series) == 0:
                continue

            q75, q25 = np.percentile(series, [75, 25])
            iqr_val = float(q75 - q25)
            skew_val = float(stats.skew(series, bias=False)) if len(series) >= 3 else 0.0

            results.append(
                MetricDescriptiveStats(
                    metric=m,
                    count=int(len(series)),
                    mean=float(round(series.mean(), 2)),
                    median=float(round(series.median(), 2)),
                    std=float(round(series.std(), 2)) if len(series) > 1 else 0.0,
                    min_val=float(round(series.min(), 2)),
                    max_val=float(round(series.max(), 2)),
                    iqr=float(round(iqr_val, 2)),
                    skewness=float(round(skew_val, 2)),
                    unit=unit,
                )
            )
        return results

    def _calc_trend_regressions(
        self, df: pd.DataFrame, time_col: str, group_col: Optional[str], metrics: List[str]
    ) -> List[TrendRegressionResult]:
        results = []
        if time_col not in df.columns:
            return results

        groups = [None]
        if group_col and group_col in df.columns:
            groups = list(df[group_col].dropna().unique())

        for grp in groups:
            sub_df = df[df[group_col] == grp] if grp is not None else df
            sub_df = sub_df.sort_values(by=time_col)

            for m in metrics:
                s_time = pd.to_numeric(sub_df[time_col], errors="coerce")
                s_val = pd.to_numeric(sub_df[m], errors="coerce")
                valid = pd.concat([s_time, s_val], axis=1).dropna()
                if len(valid) < 3:
                    continue

                x = valid.iloc[:, 0].to_numpy()
                y = valid.iloc[:, 1].to_numpy()

                slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
                r_sq = float(r_value ** 2)

                start_y, end_y = int(x[0]), int(x[-1])
                start_v, end_v = float(y[0]), float(y[-1])
                tot_change = float(round(end_v - start_v, 2))
                pct_change = float(round((tot_change / start_v) * 100, 2)) if start_v != 0 else 0.0

                cagr = None
                n_years = end_y - start_y
                if n_years > 0 and start_v > 0 and end_v > 0:
                    cagr = float(round(((end_v / start_v) ** (1.0 / n_years) - 1.0) * 100, 2))

                results.append(
                    TrendRegressionResult(
                        metric=m,
                        group=str(grp) if grp is not None else None,
                        slope=float(round(slope, 3)),
                        intercept=float(round(intercept, 3)),
                        r_squared=float(round(r_sq, 3)),
                        p_value=float(round(p_value, 4)),
                        std_err=float(round(std_err, 3)),
                        cagr=cagr,
                        total_change=tot_change,
                        percent_change=pct_change,
                        start_year=start_y,
                        end_year=end_y,
                        start_value=float(round(start_v, 2)),
                        end_value=float(round(end_v, 2)),
                    )
                )
        return results

    def _calc_correlations(
        self, df: pd.DataFrame, metrics: List[str]
    ) -> List[CorrelationResult]:
        results = []
        if len(metrics) < 2:
            return results

        for i in range(len(metrics)):
            for j in range(i + 1, len(metrics)):
                m1, m2 = metrics[i], metrics[j]
                s1 = pd.to_numeric(df[m1], errors="coerce")
                s2 = pd.to_numeric(df[m2], errors="coerce")
                pair = pd.concat([s1, s2], axis=1).dropna()
                if len(pair) < 3:
                    continue

                r_val, p_val = stats.pearsonr(pair.iloc[:, 0], pair.iloc[:, 1])
                r_sq = float(r_val ** 2)

                # Qualitative interpretation
                abs_r = abs(r_val)
                if abs_r >= 0.8:
                    strength = "very strong"
                elif abs_r >= 0.6:
                    strength = "strong"
                elif abs_r >= 0.4:
                    strength = "moderate"
                elif abs_r >= 0.2:
                    strength = "weak"
                else:
                    strength = "negligible"

                direction = "positive" if r_val > 0 else "negative"
                sig = "statistically significant (p < .05)" if p_val < 0.05 else "not statistically significant (p >= .05)"
                interp = f"{strength.capitalize()} {direction} correlation ({sig})"

                results.append(
                    CorrelationResult(
                        metric_x=m1,
                        metric_y=m2,
                        pearson_r=float(round(r_val, 3)),
                        p_value=float(round(p_val, 4)),
                        n=int(len(pair)),
                        r_squared=float(round(r_sq, 3)),
                        interpretation=interp,
                    )
                )
        return results

    def _calc_group_comparisons(
        self, df: pd.DataFrame, group_col: Optional[str], metrics: List[str]
    ) -> Dict[str, Any]:
        comps = {}
        if not group_col or group_col not in df.columns:
            return comps

        for m in metrics:
            grouped = df.groupby(group_col)[m].agg(["mean", "std", "count"]).dropna()
            if len(grouped) > 1:
                max_grp = grouped["mean"].idxmax()
                min_grp = grouped["mean"].idxmin()
                diff = float(round(grouped.loc[max_grp, "mean"] - grouped.loc[min_grp, "mean"], 2))
                comps[m] = {
                    "by_group": grouped.to_dict(orient="index"),
                    "highest": {"group": str(max_grp), "mean": float(round(grouped.loc[max_grp, "mean"], 2))},
                    "lowest": {"group": str(min_grp), "mean": float(round(grouped.loc[min_grp, "mean"], 2))},
                    "disparity_gap": diff,
                }
        return comps

    def _calc_bayes_factors(self, regressions: List[TrendRegressionResult]) -> Dict[str, float]:
        """
        Approximates the Bayes Factor (BF10) for linear regressions using BIC approximation:
        BF10 ≈ exp((BIC0 - BIC1) / 2) = n^(1/2) * (1 - R^2)^(-n/2) roughly, or Wagenmakers (2007).
        """
        bfs = {}
        for reg in regressions:
            n = (reg.end_year - reg.start_year + 1)
            if n < 4:
                continue
            r2 = max(0.001, min(0.999, reg.r_squared))
            # BIC approximation: delta_BIC = n * ln(1 - R^2) + ln(n)
            # BF10 = exp(-delta_BIC / 2) = exp(-0.5 * (n * ln(1 - R^2) + ln(n)))
            try:
                log_bf = -0.5 * (n * math.log(1 - r2) + math.log(n))
                bf10 = math.exp(min(log_bf, 20.0))  # cap to prevent overflow
                key = f"{reg.metric}_{reg.group}" if reg.group else reg.metric
                bfs[key] = float(round(bf10, 2))
            except Exception:
                pass
        return bfs

    def _build_summary_narrative(
        self,
        title: str,
        metrics: List[str],
        desc_stats: List[MetricDescriptiveStats],
        regressions: List[TrendRegressionResult],
        corrs: List[CorrelationResult],
        angle: Optional[DatasetResearchAngle],
    ) -> str:
        lines = [f"Statistical Summary for: {title}"]
        if angle:
            lines.append(f"Research Angle: {angle.title}")
            lines.append(f"Framework: {angle.theoretical_framework}")

        lines.append("\nKey Descriptive Statistics:")
        for ds in desc_stats:
            lines.append(
                f"- {ds.metric}: Mean = {ds.mean}{ds.unit} (SD = {ds.std}), "
                f"Median = {ds.median}{ds.unit}, IQR = {ds.iqr}, Range = [{ds.min_val}, {ds.max_val}]"
            )

        if regressions:
            lines.append("\nLongitudinal Trends (OLS Regression):")
            for reg in regressions[:5]:
                grp_info = f" ({reg.group})" if reg.group else ""
                lines.append(
                    f"- {reg.metric}{grp_info}: Slope beta = {reg.slope}, R^2 = {reg.r_squared}, "
                    f"p = {reg.p_value}, Net Change = {reg.total_change:+g} ({reg.percent_change:+g}%)"
                )

        if corrs:
            lines.append("\nBivariate Correlations:")
            for c in corrs[:5]:
                lines.append(
                    f"- {c.metric_x} vs. {c.metric_y}: r = {c.pearson_r}, R^2 = {c.r_squared}, "
                    f"p = {c.p_value} ({c.interpretation})"
                )

        return "\n".join(lines)
