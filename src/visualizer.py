"""
Academic Data Visualization Engine for OpenDataAnalysisTokouynu.
Generates publication-ready, 300-DPI charts entirely in English.
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import List, Optional

import matplotlib
matplotlib.use("Agg")  # Non-interactive backend
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from src.analyzer import EmpiricalAnalysisResult
from src.config import TEMP_DIR
from src.fetchers.base import EducationDataset

logger = logging.getLogger(__name__)

# Academic publication aesthetic styling
plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["DejaVu Sans", "Helvetica", "Arial"],
    "font.size": 11,
    "axes.titlesize": 14,
    "axes.titleweight": "bold",
    "axes.labelsize": 12,
    "axes.labelweight": "medium",
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "legend.fontsize": 10,
    "figure.titlesize": 16,
    "figure.dpi": 200,
    "savefig.dpi": 200,
    "savefig.bbox": "tight",
})

ACADEMIC_PALETTE = ["#1e3a8a", "#0284c7", "#059669", "#d97706", "#dc2626", "#7c3aed", "#475569"]


class EduDataVisualizer:
    """Generates publication-ready scientific figures in English."""

    def __init__(self, output_dir: Optional[Path] = None):
        self.output_dir = output_dir or TEMP_DIR
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_figures(
        self, dataset: EducationDataset, analysis: EmpiricalAnalysisResult
    ) -> List[Path]:
        """
        Creates publication-ready charts (Trend Line, Correlation Scatter, or Group Comparison).
        Returns a list of saved image paths.
        """
        figures: List[Path] = []
        df = analysis.raw_df

        # Figure 1: Longitudinal Trend Analysis
        fig1_path = self._plot_longitudinal_trends(dataset, analysis, df)
        if fig1_path and fig1_path.exists():
            figures.append(fig1_path)

        # Figure 2: Bivariate Scatter / Regression or Group Disparity Bar Chart
        if analysis.correlations:
            fig2_path = self._plot_correlation_scatter(dataset, analysis, df)
            if fig2_path and fig2_path.exists():
                figures.append(fig2_path)
        elif dataset.group_col and dataset.group_col in df.columns:
            fig2_path = self._plot_group_disparity(dataset, analysis, df)
            if fig2_path and fig2_path.exists():
                figures.append(fig2_path)

        return figures

    def _plot_longitudinal_trends(
        self, dataset: EducationDataset, analysis: EmpiricalAnalysisResult, df: pd.DataFrame
    ) -> Optional[Path]:
        """Draws multi-series longitudinal trend curves."""
        if dataset.time_col not in df.columns:
            return None

        # Determine metrics to plot
        metrics = (
            analysis.research_angle.focus_metrics
            if (analysis.research_angle and analysis.research_angle.focus_metrics)
            else dataset.metrics
        )
        valid_metrics = [m for m in metrics if m in df.columns]
        if not valid_metrics:
            return None

        fig, ax = plt.subplots(figsize=(10, 5.5))
        ax.set_facecolor("#f8fafc")
        fig.patch.set_facecolor("#ffffff")

        time_vals = pd.to_numeric(df[dataset.time_col], errors="coerce")
        has_group = bool(dataset.group_col and dataset.group_col in df.columns)

        color_idx = 0
        if has_group:
            groups = df[dataset.group_col].dropna().unique()
            # If multiple groups, plot primary metric across groups
            primary_metric = valid_metrics[0]
            for grp in groups:
                grp_df = df[df[dataset.group_col] == grp].sort_values(by=dataset.time_col)
                x = pd.to_numeric(grp_df[dataset.time_col], errors="coerce")
                y = pd.to_numeric(grp_df[primary_metric], errors="coerce")
                mask = x.notna() & y.notna()
                if mask.sum() >= 2:
                    color = ACADEMIC_PALETTE[color_idx % len(ACADEMIC_PALETTE)]
                    ax.plot(
                        x[mask],
                        y[mask],
                        marker="o",
                        linewidth=2.5,
                        markersize=6,
                        label=f"{grp}",
                        color=color,
                    )
                    color_idx += 1
            ax.set_ylabel(f"{primary_metric} ({dataset.unit})", fontweight="semibold")
        else:
            # Plot multiple metrics over time
            for m in valid_metrics[:4]:
                sorted_df = df.sort_values(by=dataset.time_col)
                x = pd.to_numeric(sorted_df[dataset.time_col], errors="coerce")
                y = pd.to_numeric(sorted_df[m], errors="coerce")
                mask = x.notna() & y.notna()
                if mask.sum() >= 2:
                    color = ACADEMIC_PALETTE[color_idx % len(ACADEMIC_PALETTE)]
                    ax.plot(
                        x[mask],
                        y[mask],
                        marker="s",
                        linewidth=2.5,
                        markersize=6,
                        label=m,
                        color=color,
                    )
                    color_idx += 1
            ax.set_ylabel(f"Value ({dataset.unit})", fontweight="semibold")

        ax.set_xlabel(f"Time ({dataset.time_col})", fontweight="semibold")
        angle_title = analysis.research_angle.title if analysis.research_angle else dataset.title
        ax.set_title(f"Figure 1. Longitudinal Trajectory: {angle_title}", pad=14, loc="left")

        # Grid and spines
        ax.grid(True, linestyle="--", alpha=0.5, color="#cbd5e1")
        for spine in ["top", "right"]:
            ax.spines[spine].set_visible(False)
        ax.spines["left"].set_color("#64748b")
        ax.spines["bottom"].set_color("#64748b")

        ax.legend(frameon=True, facecolor="#ffffff", edgecolor="#e2e8f0", loc="best")

        # English Source Translation mapping
        source_name = self._translate_source(dataset.source_name)

        # Annotate source
        fig.text(
            0.99,
            0.01,
            f"Source: {source_name} | Empirical Analysis Pipeline",
            ha="right",
            fontsize=9,
            color="#64748b",
            style="italic",
        )

        output_path = self.output_dir / f"{dataset.id}_trend.png"
        fig.savefig(output_path, dpi=200, bbox_inches="tight")
        plt.close(fig)
        logger.info(f"Generated Figure 1: {output_path.name}")
        return output_path

    def _plot_correlation_scatter(
        self, dataset: EducationDataset, analysis: EmpiricalAnalysisResult, df: pd.DataFrame
    ) -> Optional[Path]:
        """Draws bivariate scatter plot with OLS linear regression line and statistics."""
        if not analysis.correlations:
            return None

        # Pick strongest correlation
        top_corr = max(analysis.correlations, key=lambda c: abs(c.pearson_r))
        m1, m2 = top_corr.metric_x, top_corr.metric_y

        s1 = pd.to_numeric(df[m1], errors="coerce")
        s2 = pd.to_numeric(df[m2], errors="coerce")
        valid = pd.concat([s1, s2], axis=1).dropna()
        if len(valid) < 3:
            return None

        fig, ax = plt.subplots(figsize=(8.5, 6))
        ax.set_facecolor("#f8fafc")
        fig.patch.set_facecolor("#ffffff")

        x = valid.iloc[:, 0]
        y = valid.iloc[:, 1]

        # Scatter points
        ax.scatter(
            x,
            y,
            color="#1e3a8a",
            alpha=0.8,
            s=60,
            edgecolor="#ffffff",
            linewidth=1.2,
            zorder=3,
            label="Observed Data",
        )

        # Regression line
        slope, intercept = np.polyfit(x, y, 1)
        x_seq = np.linspace(x.min(), x.max(), 100)
        ax.plot(
            x_seq,
            slope * x_seq + intercept,
            color="#dc2626",
            linewidth=2.2,
            linestyle="-",
            label=f"OLS Fit: y = {slope:.2f}x + {intercept:.2f}",
            zorder=4,
        )

        # Annotate statistical metrics
        stat_box = (
            f"Pearson r = {top_corr.pearson_r:+.3f}\n"
            f"R² = {top_corr.r_squared:.3f}\n"
            f"p-value = {top_corr.p_value:.4f}\n"
            f"N = {top_corr.n}"
        )
        ax.text(
            0.05,
            0.92,
            stat_box,
            transform=ax.transAxes,
            fontsize=10,
            verticalalignment="top",
            bbox=dict(boxstyle="round,pad=0.5", facecolor="#ffffff", edgecolor="#cbd5e1", alpha=0.9),
        )

        ax.set_xlabel(f"{m1}", fontweight="semibold")
        ax.set_ylabel(f"{m2}", fontweight="semibold")
        ax.set_title(f"Figure 2. Empirical Correlation: {m1} vs. {m2}", pad=14, loc="left")

        ax.grid(True, linestyle="--", alpha=0.5, color="#cbd5e1")
        for spine in ["top", "right"]:
            ax.spines[spine].set_visible(False)

        ax.legend(frameon=True, facecolor="#ffffff", edgecolor="#e2e8f0", loc="lower right")

        fig.text(
            0.99,
            0.01,
            f"Source: {self._translate_source(dataset.source_name)}",
            ha="right",
            fontsize=9,
            color="#64748b",
            style="italic",
        )

        output_path = self.output_dir / f"{dataset.id}_correlation.png"
        fig.savefig(output_path, dpi=200, bbox_inches="tight")
        plt.close(fig)
        logger.info(f"Generated Figure 2: {output_path.name}")
        return output_path

    def _translate_source(self, raw_source: str) -> str:
        """Translates Japanese official agency names into formal English."""
        mapping = {
            "文部科学省・国立教育政策研究所": "MEXT / National Institute for Educational Policy Research (NIER)",
            "文部科学省": "Ministry of Education, Culture, Sports, Science and Technology (MEXT)",
            "国立教育政策研究所": "National Institute for Educational Policy Research (NIER)",
            "総務省": "Ministry of Internal Affairs and Communications (MIC)",
            "総務省統計局": "Statistics Bureau, Government of Japan",
            "OECD": "OECD Education Statistics",
            "UNESCO / ITU": "UNESCO Institute for Statistics & ITU",
            "世界銀行": "The World Bank Open Data",
        }
        for k, v in mapping.items():
            if k in raw_source:
                return v
        return raw_source

    def _plot_group_disparity(
        self, dataset: EducationDataset, analysis: EmpiricalAnalysisResult, df: pd.DataFrame
    ) -> Optional[Path]:
        """Draws group disparity horizontal ranking bar chart."""
        group_col = dataset.group_col
        if not group_col or group_col not in df.columns:
            return None

        metric = (
            analysis.research_angle.focus_metrics[0]
            if (analysis.research_angle and analysis.research_angle.focus_metrics)
            else dataset.metrics[0]
        )
        if metric not in df.columns:
            return None

        # Compute latest values per group
        latest_df = df.sort_values(by=dataset.time_col).groupby(group_col).last().reset_index()
        latest_df[metric] = pd.to_numeric(latest_df[metric], errors="coerce")
        latest_df = latest_df.dropna(subset=[metric]).sort_values(by=metric, ascending=True)

        if len(latest_df) < 2:
            return None

        fig, ax = plt.subplots(figsize=(9, max(4.5, len(latest_df) * 0.45)))
        ax.set_facecolor("#f8fafc")
        fig.patch.set_facecolor("#ffffff")

        bars = ax.barh(
            latest_df[group_col],
            latest_df[metric],
            color="#0284c7",
            edgecolor="#0369a1",
            height=0.6,
        )

        # Add data values on bar ends
        for bar in bars:
            width = bar.get_width()
            ax.text(
                width + (latest_df[metric].max() * 0.01),
                bar.get_y() + bar.get_height() / 2,
                f"{width:.1f}{dataset.unit}",
                ha="left",
                va="center",
                fontsize=9.5,
                fontweight="semibold",
                color="#1e293b",
            )

        ax.set_xlabel(f"{metric} ({dataset.unit})", fontweight="semibold")
        ax.set_title(f"Figure 2. Cross-Category Disparities: {metric}", pad=14, loc="left")

        ax.grid(True, axis="x", linestyle="--", alpha=0.5, color="#cbd5e1")
        for spine in ["top", "right"]:
            ax.spines[spine].set_visible(False)

        fig.text(
            0.99,
            0.01,
            f"Source: {dataset.source_name}",
            ha="right",
            fontsize=9,
            color="#64748b",
            style="italic",
        )

        output_path = self.output_dir / f"{dataset.id}_disparity.png"
        fig.savefig(output_path, dpi=200, bbox_inches="tight")
        plt.close(fig)
        logger.info(f"Generated Figure 2 (Disparity): {output_path.name}")
        return output_path
