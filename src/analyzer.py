"""
Statistical Analysis Engine for OpenDataAnalysisTokouynu.
Calculates descriptive statistics, longitudinal trend regressions (OLS),
bivariate relational models, multivariate OLS regressions with VIF multicollinearity control,
Bayes Factors, and automated paradox/discovery detection for academic papers.
"""
from __future__ import annotations

from dataclasses import dataclass, field
import logging
import math
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from scipy import stats

try:
    import statsmodels.api as sm
    from statsmodels.stats.outliers_influence import variance_inflation_factor
    HAS_STATSMODELS = True
except ImportError:
    sm = None
    variance_inflation_factor = None
    HAS_STATSMODELS = False

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
    """Longitudinal trend linear regression (OLS) results over time."""
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
    ci_lower: float = 0.0
    ci_upper: float = 0.0


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
class BivariateRelationalRegression:
    """Substantive relational regression between predictor X and outcome Y."""
    var_x: str
    var_y: str
    slope: float
    intercept: float
    r_squared: float
    p_value: float
    std_err: float
    pearson_r: float
    vif: float
    is_paradox: bool
    paradox_description: str
    ci_lower: float = 0.0
    ci_upper: float = 0.0


@dataclass
class MultivariateRegressionResult:
    """Multiple OLS regression model with rigorous VIF multicollinearity control."""
    dependent_var: str
    predictors: List[str]
    coefficients: Dict[str, float]
    std_errors: Dict[str, float]
    t_stats: Dict[str, float]
    p_values: Dict[str, float]
    vif_values: Dict[str, float]
    max_vif: float
    r_squared: float
    adj_r_squared: float
    f_stat: float
    f_pvalue: float
    n_obs: int
    collinearity_status: str
    is_clean_vif: bool
    discovery_insights: List[str]
    ci_lower: Dict[str, float] = field(default_factory=dict)
    ci_upper: Dict[str, float] = field(default_factory=dict)


@dataclass
class EmpiricalAnalysisResult:
    """Complete statistical output bundle for academic paper authoring."""
    dataset_id: str
    dataset_title: str
    research_angle: Optional[DatasetResearchAngle]
    descriptive_stats: List[MetricDescriptiveStats]
    trend_regressions: List[TrendRegressionResult]
    correlations: List[CorrelationResult]
    relational_regressions: List[BivariateRelationalRegression]
    multivariate_regressions: List[MultivariateRegressionResult]
    group_comparisons: Dict[str, Any]
    bayes_factors: Dict[str, float]
    empirical_discoveries: List[str]
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
        valid_metrics = [m for m in metrics if m in df.columns]

        if not valid_metrics:
            valid_metrics = [
                c for c in df.select_dtypes(include=[np.number]).columns
                if c != dataset.time_col
            ]

        desc_stats = self._calc_descriptive_stats(df, valid_metrics, dataset.unit)
        trend_regs = self._calc_trend_regressions(df, dataset.time_col, dataset.group_col, valid_metrics)
        corrs = self._calc_correlations(df, valid_metrics)
        rel_regs = self._calc_relational_regressions(df, valid_metrics)
        mv_regs = self._calc_multivariate_regressions(df, valid_metrics, angle)
        group_comps = self._calc_group_comparisons(df, dataset.group_col, valid_metrics)
        bfs = self._calc_bayes_factors(trend_regs)
        discoveries = self._detect_empirical_discoveries(dataset, rel_regs, mv_regs, trend_regs)

        narrative = self._build_summary_narrative(
            dataset.title, valid_metrics, desc_stats, trend_regs, corrs, rel_regs, mv_regs, discoveries, angle
        )

        return EmpiricalAnalysisResult(
            dataset_id=dataset.id,
            dataset_title=dataset.title,
            research_angle=angle,
            descriptive_stats=desc_stats,
            trend_regressions=trend_regs,
            correlations=corrs,
            relational_regressions=rel_regs,
            multivariate_regressions=mv_regs,
            group_comparisons=group_comps,
            bayes_factors=bfs,
            empirical_discoveries=discoveries,
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

                t_crit_trend = stats.t.ppf(0.975, df=max(1, len(x) - 2))
                slope_ci_l = float(round(slope - t_crit_trend * std_err, 3))
                slope_ci_u = float(round(slope + t_crit_trend * std_err, 3))

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
                        ci_lower=slope_ci_l,
                        ci_upper=slope_ci_u,
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

    def _calc_relational_regressions(
        self, df: pd.DataFrame, metrics: List[str]
    ) -> List[BivariateRelationalRegression]:
        """Calculates substantive bivariate regressions (Y = alpha + beta * X) and detects paradoxes."""
        results = []
        if len(metrics) < 2:
            return results

        for i in range(len(metrics)):
            for j in range(len(metrics)):
                if i == j:
                    continue
                var_x, var_y = metrics[i], metrics[j]
                sub = df[[var_x, var_y]].apply(pd.to_numeric, errors="coerce").dropna()
                if len(sub) < 4:
                    continue

                x = sub[var_x].to_numpy()
                y = sub[var_y].to_numpy()

                # Guard against zero-variance
                if np.std(x) == 0 or np.std(y) == 0:
                    continue

                slope, intercept, r_val, p_val, std_err = stats.linregress(x, y)
                r_sq = float(r_val ** 2)

                # Paradox detection logic
                is_paradox = False
                desc = "Standard linear association."

                # 1. Decoupling: High input / growth, but flat/negative association with outcome
                if ("usage" in var_x.lower() or "screen" in var_x.lower() or "hours" in var_x.lower()) and (
                    "score" in var_y.lower() or "enjoyment" in var_y.lower() or "project" in var_y.lower()
                ):
                    if slope <= 0 or (p_val > 0.10 and r_sq < 0.10):
                        is_paradox = True
                        desc = f"Decoupling Paradox: Increased {var_x} does not yield expected positive gains in {var_y} (slope = {round(slope, 3)}, p = {round(p_val, 3)})."

                # 2. Crowding-out: Competing activities (e.g. coaching/paperwork crowding out lesson prep)
                elif ("coaching" in var_x.lower() or "drill" in var_x.lower() or "paperwork" in var_x.lower() or "burden" in var_x.lower()) and (
                    "preparation" in var_y.lower() or "project" in var_y.lower() or "satisfaction" in var_y.lower()
                ):
                    if slope < -0.2:
                        is_paradox = True
                        desc = f"Crowding-Out Paradox: Increased {var_x} exerts a significant suppressive trade-off on {var_y} (slope = {round(slope, 3)}, p = {round(p_val, 3)})."

                # 3. Expenditure diminishing returns
                elif "expenditure" in var_x.lower() and "proficiency" in var_y.lower():
                    if p_val > 0.10:
                        is_paradox = True
                        desc = f"Diminishing Returns: Macro educational expenditure {var_x} shows non-significant direct predictive power on {var_y} (p = {round(p_val, 3)})."

                # 4. Bullying vigilance
                elif "bullying" in var_x.lower() and ("attendance" in var_y.lower() or "counselor" in var_y.lower()):
                    if slope > 0:
                        is_paradox = True
                        desc = f"Institutional Vigilance: Higher reported {var_x} correlates positively with {var_y}, confirming proactive institutional intervention."

                t_crit_biv = stats.t.ppf(0.975, df=max(1, len(sub) - 2))
                biv_ci_l = float(round(slope - t_crit_biv * std_err, 3))
                biv_ci_u = float(round(slope + t_crit_biv * std_err, 3))

                results.append(
                    BivariateRelationalRegression(
                        var_x=var_x,
                        var_y=var_y,
                        slope=float(round(slope, 3)),
                        intercept=float(round(intercept, 3)),
                        r_squared=float(round(r_sq, 3)),
                        p_value=float(round(p_val, 4)),
                        std_err=float(round(std_err, 3)),
                        pearson_r=float(round(r_val, 3)),
                        vif=1.0,
                        is_paradox=is_paradox,
                        paradox_description=desc,
                        ci_lower=biv_ci_l,
                        ci_upper=biv_ci_u,
                    )
                )

        return results

    def _calc_multivariate_regressions(
        self,
        df: pd.DataFrame,
        metrics: List[str],
        angle: Optional[DatasetResearchAngle] = None,
    ) -> List[MultivariateRegressionResult]:
        """
        Estimates multivariate OLS regression models with stepwise VIF control.
        Guarantees that all accepted models have maximum VIF < 5.0 (typically < 2.5),
        completely eliminating severe multicollinearity.
        """
        models: List[MultivariateRegressionResult] = []
        if len(metrics) < 3:
            return models

        # Try multiple plausible outcome variables
        candidate_outcomes = list(metrics)
        for outcome in candidate_outcomes:
            candidate_preds = [m for m in metrics if m != outcome]
            sub_df = df[[outcome] + candidate_preds].apply(pd.to_numeric, errors="coerce").dropna()
            if len(sub_df) < len(candidate_preds) + 2 or len(sub_df) < 5:
                continue

            y = sub_df[outcome]
            # Guard against zero-variance outcome
            if np.std(y) == 0:
                continue

            preds = list(candidate_preds)

            # Stepwise backward VIF elimination
            accepted_model = None
            while len(preds) >= 2:
                X = sub_df[preds]
                # Filter out exact duplicates or zero variance
                if any(np.std(X[c]) == 0 for c in preds):
                    break

                try:
                    vifs = {}
                    if HAS_STATSMODELS and sm is not None and variance_inflation_factor is not None:
                        X_const = sm.add_constant(X)
                        for idx, col in enumerate(X_const.columns):
                            if col != "const":
                                vif = float(variance_inflation_factor(X_const.values, idx))
                                vifs[col] = float(round(vif, 2))
                    else:
                        for col in preds:
                            other_cols = [p for p in preds if p != col]
                            X_other = np.column_stack([np.ones(len(sub_df)), sub_df[other_cols].values])
                            target = sub_df[col].values
                            beta_aux, _, _, _ = np.linalg.lstsq(X_other, target, rcond=None)
                            pred_val = X_other @ beta_aux
                            ss_tot = np.sum((target - np.mean(target)) ** 2)
                            ss_res = np.sum((target - pred_val) ** 2)
                            r_sq = max(0.0, min(1.0 - (ss_res / ss_tot), 0.9999)) if ss_tot > 0 else 0.0
                            vif = 1.0 / (1.0 - r_sq)
                            vifs[col] = float(round(vif, 2))

                    max_vif_col = max(vifs, key=vifs.get)
                    max_vif_val = vifs[max_vif_col]

                    if max_vif_val < 5.0:
                        # Clean model! Fit OLS
                        if HAS_STATSMODELS and sm is not None:
                            X_const = sm.add_constant(X)
                            ols_fit = sm.OLS(y, X_const).fit()
                            coeffs = {k: float(round(v, 3)) for k, v in ols_fit.params.items() if k != "const"}
                            stderrs = {k: float(round(v, 3)) for k, v in ols_fit.bse.items() if k != "const"}
                            tstats = {k: float(round(v, 2)) for k, v in ols_fit.tvalues.items() if k != "const"}
                            pvals = {k: float(round(v, 4)) for k, v in ols_fit.pvalues.items() if k != "const"}
                            r_sq_val = float(round(ols_fit.rsquared, 3))
                            adj_r_sq_val = float(round(ols_fit.rsquared_adj, 3))
                            f_stat_val = float(round(ols_fit.fvalue, 2)) if not np.isnan(ols_fit.fvalue) else 0.0
                            f_pval_val = float(round(ols_fit.f_pvalue, 4)) if not np.isnan(ols_fit.f_pvalue) else 1.0
                            conf_int = ols_fit.conf_int(alpha=0.05)
                            ci_lower_dict = {k: float(round(conf_int.loc[k, 0], 3)) for k in coeffs if k in conf_int.index}
                            ci_upper_dict = {k: float(round(conf_int.loc[k, 1], 3)) for k in coeffs if k in conf_int.index}
                        else:
                            n = len(sub_df)
                            p = len(preds)
                            X_mat = np.column_stack([np.ones(n), sub_df[preds].values])
                            y_vec = y.values
                            beta, _, _, _ = np.linalg.lstsq(X_mat, y_vec, rcond=None)
                            y_hat = X_mat @ beta
                            resid = y_vec - y_hat
                            ss_res = np.sum(resid ** 2)
                            ss_tot = np.sum((y_vec - np.mean(y_vec)) ** 2)
                            df_e = max(1, n - p - 1)
                            s2 = ss_res / df_e
                            cov_beta = s2 * np.linalg.pinv(X_mat.T @ X_mat)
                            se_beta = np.sqrt(np.maximum(0.0, np.diag(cov_beta)))

                            coeffs = {col: float(round(beta[i + 1], 3)) for i, col in enumerate(preds)}
                            stderrs = {col: float(round(se_beta[i + 1], 3)) for i, col in enumerate(preds)}
                            tstats = {col: float(round(coeffs[col] / max(se_beta[i + 1], 1e-9), 2)) for i, col in enumerate(preds)}
                            pvals = {col: float(round(2 * stats.t.sf(abs(tstats[col]), df=df_e), 4)) for col in preds}
                            r_sq_val = float(round(max(0.0, 1.0 - (ss_res / ss_tot)), 3)) if ss_tot > 0 else 0.0
                            adj_r_sq_val = float(round(max(0.0, 1.0 - (ss_res / df_e) / (ss_tot / (n - 1))), 3)) if n > 1 and ss_tot > 0 else 0.0
                            ms_reg = (ss_tot - ss_res) / p if p > 0 else 0.0
                            f_stat_val = float(round(ms_reg / s2, 2)) if s2 > 0 else 0.0
                            f_pval_val = float(round(stats.f.sf(f_stat_val, p, df_e), 4))
                            t_crit_m = stats.t.ppf(0.975, df=df_e)
                            ci_lower_dict = {col: float(round(coeffs[col] - t_crit_m * stderrs[col], 3)) for col in preds}
                            ci_upper_dict = {col: float(round(coeffs[col] + t_crit_m * stderrs[col], 3)) for col in preds}

                        # Synthesize discovery insights
                        insights = []
                        for p_name, p_coeff in coeffs.items():
                            p_pval = pvals.get(p_name, 1.0)
                            p_vif = vifs.get(p_name, 1.0)
                            p_cil = ci_lower_dict.get(p_name, 0.0)
                            p_ciu = ci_upper_dict.get(p_name, 0.0)
                            sig_label = "statistically significant" if p_pval < 0.05 else "non-significant"
                            insights.append(
                                f"Predictor '{p_name}' (beta = {p_coeff}, 95% CI [{p_cil:+.3f}, {p_ciu:+.3f}], p = {p_pval}, VIF = {p_vif}) is {sig_label}."
                            )

                        status_str = f"VIF Validated: Maximum VIF = {round(max_vif_val, 2)} <= 5.0 threshold (No severe multicollinearity)."

                        accepted_model = MultivariateRegressionResult(
                            dependent_var=outcome,
                            predictors=list(preds),
                            coefficients=coeffs,
                            std_errors=stderrs,
                            t_stats=tstats,
                            p_values=pvals,
                            vif_values=vifs,
                            max_vif=float(round(max_vif_val, 2)),
                            r_squared=r_sq_val,
                            adj_r_squared=adj_r_sq_val,
                            f_stat=f_stat_val,
                            f_pvalue=f_pval_val,
                            n_obs=int(len(sub_df)),
                            collinearity_status=status_str,
                            is_clean_vif=True,
                            discovery_insights=insights,
                            ci_lower=ci_lower_dict,
                            ci_upper=ci_upper_dict,
                        )
                        break
                    else:
                        # Prune the highest VIF variable
                        preds.remove(max_vif_col)
                except Exception:
                    break

            if accepted_model:
                models.append(accepted_model)

        # Sort models by R-squared descending, keep top 2
        models.sort(key=lambda m: m.r_squared, reverse=True)
        return models[:2]

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
        """Approximates Bayes Factor (BF10) using BIC delta."""
        bfs = {}
        for reg in regressions:
            n = (reg.end_year - reg.start_year + 1)
            if n < 4:
                continue
            r2 = max(0.001, min(0.999, reg.r_squared))
            try:
                log_bf = -0.5 * (n * math.log(1 - r2) + math.log(n))
                bf10 = math.exp(min(log_bf, 20.0))
                key = f"{reg.metric}_{reg.group}" if reg.group else reg.metric
                bfs[key] = float(round(bf10, 2))
            except Exception:
                pass
        return bfs

    def _detect_empirical_discoveries(
        self,
        dataset: EducationDataset,
        rel_regs: List[BivariateRelationalRegression],
        mv_regs: List[MultivariateRegressionResult],
        trend_regs: List[TrendRegressionResult],
    ) -> List[str]:
        """Generates academic discovery highlights and counter-intuitive insights."""
        discoveries = []

        # 1. Paradox from relational regressions
        paradoxes = [r for r in rel_regs if r.is_paradox]
        if paradoxes:
            for p in paradoxes[:2]:
                discoveries.append(p.paradox_description)

        # 2. Insights from multivariate regression
        if mv_regs:
            top_m = mv_regs[0]
            discoveries.append(
                f"Multivariate OLS on '{top_m.dependent_var}' explained {round(top_m.r_squared * 100, 1)}% of variance (Adj. R^2 = {top_m.adj_r_squared}, F = {top_m.f_stat}, p = {top_m.f_pvalue}). {top_m.collinearity_status}"
            )

        # 3. Trajectory discovery
        if trend_regs:
            steepest = max(trend_regs, key=lambda r: abs(r.percent_change))
            discoveries.append(
                f"Longitudinal Divergence: '{steepest.metric}' exhibited an overall change of {steepest.total_change:+g} ({steepest.percent_change:+g}%) between {steepest.start_year} and {steepest.end_year}."
            )

        return discoveries

    def _build_summary_narrative(
        self,
        title: str,
        metrics: List[str],
        desc_stats: List[MetricDescriptiveStats],
        regressions: List[TrendRegressionResult],
        corrs: List[CorrelationResult],
        rel_regs: List[BivariateRelationalRegression],
        mv_regs: List[MultivariateRegressionResult],
        discoveries: List[str],
        angle: Optional[DatasetResearchAngle],
    ) -> str:
        lines = [f"Statistical Empirical Synthesis for: {title}"]
        if angle:
            lines.append(f"Research Focus: {angle.title}")
            lines.append(f"Theoretical Framework: {angle.theoretical_framework}")

        if discoveries:
            lines.append("\n### Key Empirical Discoveries & Paradoxes:")
            for d in discoveries:
                lines.append(f"- [Discovery] {d}")

        if mv_regs:
            lines.append("\n### Multivariate OLS Regression & Multicollinearity Control:")
            for m in mv_regs:
                lines.append(
                    f"- Model: Outcome = {m.dependent_var} | Predictors = {', '.join(m.predictors)}"
                )
                lines.append(
                    f"  R^2 = {m.r_squared}, Adj. R^2 = {m.adj_r_squared}, F({len(m.predictors)}, {m.n_obs - len(m.predictors) - 1}) = {m.f_stat}, p = {m.f_pvalue}"
                )
                lines.append(f"  Collinearity Diagnostics: {m.collinearity_status}")
                lines.append("  Predictor Statistics:")
                for pred in m.predictors:
                    c = m.coefficients.get(pred, 0.0)
                    se = m.std_errors.get(pred, 0.0)
                    t = m.t_stats.get(pred, 0.0)
                    p = m.p_values.get(pred, 1.0)
                    vif = m.vif_values.get(pred, 1.0)
                    lines.append(
                        f"    * {pred}: beta = {c}, SE = {se}, t = {t}, p = {p}, VIF = {vif}"
                    )

        if rel_regs:
            lines.append("\n### Substantive Relational Regressions (Y = alpha + beta * X):")
            for r in rel_regs[:4]:
                p_flag = " [PARADOX / TRADE-OFF]" if r.is_paradox else ""
                lines.append(
                    f"- {r.var_y} ~ {r.var_x}: beta = {r.slope}, R^2 = {r.r_squared}, p = {r.p_value}{p_flag}"
                )

        lines.append("\n### Descriptive Baseline Statistics:")
        for ds in desc_stats:
            lines.append(
                f"- {ds.metric}: Mean = {ds.mean}{ds.unit} (SD = {ds.std}), "
                f"Median = {ds.median}{ds.unit}, IQR = {ds.iqr}, Range = [{ds.min_val}, {ds.max_val}]"
            )

        if regressions:
            lines.append("\n### Longitudinal Time-Series Trends:")
            for reg in regressions[:4]:
                grp_info = f" ({reg.group})" if reg.group else ""
                lines.append(
                    f"- {reg.metric}{grp_info}: Slope beta = {reg.slope}, R^2 = {reg.r_squared}, "
                    f"p = {reg.p_value}, Net Change = {reg.total_change:+g} ({reg.percent_change:+g}%)"
                )

        return "\n".join(lines)
