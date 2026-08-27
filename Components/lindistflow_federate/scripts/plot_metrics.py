#!/usr/bin/env python3
"""Script to analyze and plot LinDistFlow OPF metrics from OEDISI co-simulation outputs.

This script reads recorder outputs (voltages and controls) and generates voltage profiles
and 3D wireframe plots of active and reactive control powers over all timesteps and devices.
"""

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Add the component's src directory to sys.path
SCRIPT_DIR = Path(__file__).resolve().parent
COMPONENT_DIR = SCRIPT_DIR.parent
sys.path.insert(0, str(COMPONENT_DIR / "src"))

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def format_time_str(time_val: Any) -> str:
    """Format time value to HH:MM format.

    Args:
        time_val: The raw time representation.

    Returns:
        Formatted time string in HH:MM format.
    """
    try:
        dt = pd.to_datetime(str(time_val))
        return dt.strftime("%H:%M")
    except Exception:
        return str(time_val)


def load_scenario_recorders(scenario_path: Path, data_dir: Path) -> dict[str, Path]:
    """Parse the scenario JSON file to extract recorder file paths.

    Args:
        scenario_path: Path to the scenario JSON file.
        data_dir: Path to the directory where recorders saved feather files.

    Returns:
        A dictionary mapping recorder keys to their output feather file paths.
    """
    try:
        with open(scenario_path, encoding="utf-8") as f:
            scenario = json.load(f)
    except FileNotFoundError:
        logger.error(f"Scenario file not found: {scenario_path}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing scenario JSON: {e}")
        sys.exit(1)

    # Map component name to its parameters and type
    components = {comp["name"]: comp for comp in scenario.get("components", [])}

    # Identify the LinDistFlowComponent name
    dopf_names = [name for name, comp in components.items() if comp.get("type") == "LinDistFlowComponent"]
    dopf_name = dopf_names[0] if dopf_names else None

    # Identify the Feeder component names
    feeder_names = [name for name, comp in components.items() if comp.get("type") in ["Feeder", "LocalFeeder"]]

    # Identify control and reference feeders
    control_feeder_name = next(
        (name for name in feeder_names if "control" in name.lower() or "local" in name.lower()), None
    )
    reference_feeder_name = next(
        (name for name in feeder_names if "reference" in name.lower() or "ref" in name.lower()), None
    )

    if not control_feeder_name and feeder_names:
        control_feeder_name = feeder_names[0]

    # Find incoming links to recorders
    recorder_paths: dict[str, Path] = {}
    for link in scenario.get("links", []):
        target = link.get("target")
        source = link.get("source")
        source_port = link.get("source_port")
        if target and source_port:
            target_comp = components.get(target)
            if target_comp and target_comp.get("type") == "Recorder":
                params = target_comp.get("parameters", {})
                feather_filename = params.get("feather_filename")
                if feather_filename:
                    # Resolve filepath in data_dir
                    file_path = data_dir / Path(feather_filename).name
                    # Dopf outputs
                    if source == dopf_name:
                        if source_port == "opf_voltages_magnitude":
                            recorder_paths["dopf_vmag"] = file_path
                        elif source_port == "opf_control_power_real":
                            recorder_paths["dopf_ctrl_real"] = file_path
                        elif source_port == "opf_control_power_imaginary":
                            recorder_paths["dopf_ctrl_imag"] = file_path
                    # Control Feeder outputs
                    elif source == control_feeder_name:
                        if source_port == "voltages_real":
                            recorder_paths["control_vreal"] = file_path
                        elif source_port in ["voltages_imaginary", "voltages_imag"]:
                            recorder_paths["control_vimag"] = file_path
                        elif source_port == "voltages_magnitude":
                            recorder_paths["control_vmag"] = file_path
                        elif source_port == "powers_real":
                            recorder_paths["control_preal"] = file_path
                        elif source_port == "powers_imag":
                            recorder_paths["control_pimag"] = file_path
                    # Reference Feeder outputs
                    elif source == reference_feeder_name:
                        if source_port == "voltages_real":
                            recorder_paths["reference_vreal"] = file_path
                        elif source_port in ["voltages_imaginary", "voltages_imag"]:
                            recorder_paths["reference_vimag"] = file_path
                        elif source_port == "voltages_magnitude":
                            recorder_paths["reference_vmag"] = file_path
                        elif source_port == "powers_real":
                            recorder_paths["reference_preal"] = file_path
                        elif source_port == "powers_imag":
                            recorder_paths["reference_pimag"] = file_path
                    # Backward compatibility if single feeder name matches reference
                    elif source in feeder_names and not reference_feeder_name:
                        if source_port == "voltages_real":
                            recorder_paths["feeder_vreal"] = file_path
                        elif source_port in ["voltages_imaginary", "voltages_imag"]:
                            recorder_paths["feeder_vimag"] = file_path
                        elif source_port == "voltages_magnitude":
                            recorder_paths["feeder_vmag"] = file_path

    return recorder_paths


def load_dataframe(file_path: Path) -> pd.DataFrame | None:
    """Load recorder data from a feather file.

    Args:
        file_path: Path to the feather file.

    Returns:
        The loaded pandas DataFrame or None if loading failed.
    """
    if not file_path.exists():
        logger.warning(f"Required recorder file does not exist: {file_path}")
        return None

    try:
        df = pd.read_feather(file_path)
        logger.info(f"Loaded {file_path.name} with shape {df.shape}")
        return df
    except Exception as e:
        logger.error(f"Error loading {file_path}: {e}")
        return None


def plot_voltages(v_df: pd.DataFrame, feeder_df: pd.DataFrame | None, output_path: Path) -> None:
    """Generate plots of the voltage profiles over time, comparing controlled vs uncontrolled.

    Args:
        v_df: DataFrame containing the controlled voltage magnitude measurements.
        feeder_df: Optional DataFrame containing the uncontrolled feeder voltage magnitudes.
        output_path: Path to save the output plot.
    """
    try:
        import seaborn as sns

        sns.set_theme(style="whitegrid")
    except ImportError:
        logger.warning("Seaborn not installed, falling back to matplotlib defaults.")

    time_col = "time" if "time" in v_df.columns else v_df.columns[0]

    # Align DataFrames by common timestamps
    v_times = v_df[time_col].unique()
    if feeder_df is not None:
        f_times = feeder_df[time_col].unique()
        common_times = np.intersect1d(v_times, f_times)
        feeder_df_aligned = feeder_df[feeder_df[time_col].isin(common_times)].sort_values(by=time_col)
    else:
        common_times = v_times
        feeder_df_aligned = None

    v_df_aligned = v_df[v_df[time_col].isin(common_times)].sort_values(by=time_col)

    cols = [col for col in v_df_aligned.columns if col != time_col]

    if not cols:
        logger.warning("No voltage columns found to plot.")
        return

    # Process OPF voltages
    df_temp = v_df_aligned.set_index(time_col)[cols]
    v_min = df_temp.min(axis=1)
    v_max = df_temp.max(axis=1)
    v_mean = df_temp.mean(axis=1)
    timesteps = v_df_aligned[time_col].apply(format_time_str).tolist()

    fig, ax = plt.subplots(figsize=(10, 6))

    # 1. Plot Uncontrolled Feeder Voltages if available
    if feeder_df_aligned is not None:
        feeder_cols = [c for c in feeder_df_aligned.columns if c != time_col]
        if feeder_cols:
            df_feeder_temp = feeder_df_aligned.set_index(time_col)[feeder_cols]
            f_min = df_feeder_temp.min(axis=1)
            f_max = df_feeder_temp.max(axis=1)
            f_mean = df_feeder_temp.mean(axis=1)

            # Shaded area
            ax.fill_between(
                range(len(timesteps)),
                f_min,
                f_max,
                color="#ea4335",
                alpha=0.08,
                label="Uncontrolled Range (Feeder)",
            )
            # Mean line
            ax.plot(
                range(len(timesteps)),
                f_mean,
                color="#ea4335",
                linestyle="--",
                linewidth=1.8,
                label="Uncontrolled Mean (Feeder)",
            )

    # 2. Plot Controlled OPF Voltages
    # Shaded area
    ax.fill_between(
        range(len(timesteps)),
        v_min,
        v_max,
        color="#1a73e8",
        alpha=0.15,
        label="Controlled Range (LinDistFlow OPF)",
    )
    # Mean line
    ax.plot(
        range(len(timesteps)),
        v_mean,
        color="#1a73e8",
        linewidth=2.2,
        label="Controlled Mean (LinDistFlow OPF)",
    )

    # ANSI C84.1 voltage limits
    ax.axhline(1.05, color="#5f6368", linestyle=":", alpha=0.8, label="Upper Limit (1.05 p.u.)")
    ax.axhline(0.95, color="#5f6368", linestyle=":", alpha=0.8, label="Lower Limit (0.95 p.u.)")

    ax.set_title(
        "Voltage Profile Comparison (Controlled vs Uncontrolled)",
        fontsize=14,
        fontweight="bold",
        pad=15,
    )
    ax.set_xlabel("Time (HH:MM)", fontsize=12)
    ax.set_ylabel("Voltage Magnitude (p.u.)", fontsize=12)

    # Set x-ticks
    step = max(1, len(timesteps) // 10)
    ax.set_xticks(range(0, len(timesteps), step))
    ax.set_xticklabels([timesteps[i] for i in range(0, len(timesteps), step)], rotation=15, ha="right")

    ax.set_ylim(0.90, 1.10)
    ax.legend(loc="upper right", frameon=True)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()
    logger.info(f"Saved voltage comparison profile plot to: {output_path}")


def plot_power_comparison(
    control_p_real_df: pd.DataFrame,
    control_p_imag_df: pd.DataFrame,
    ref_p_real_df: pd.DataFrame,
    ref_p_imag_df: pd.DataFrame,
    output_path: Path,
) -> None:
    """Generate plots of the power injection profiles over time, comparing controlled vs reference.

    Args:
        control_p_real_df: DataFrame containing controlled real power injections.
        control_p_imag_df: DataFrame containing controlled reactive power injections.
        ref_p_real_df: DataFrame containing uncontrolled reference real power injections.
        ref_p_imag_df: DataFrame containing uncontrolled reference reactive power injections.
        output_path: Path to save the output plot.
    """
    try:
        import seaborn as sns

        sns.set_theme(style="whitegrid")
    except ImportError:
        logger.warning("Seaborn not installed, falling back to matplotlib defaults.")

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)

    time_col = "time" if "time" in control_p_real_df.columns else control_p_real_df.columns[0]

    # Align DataFrames by common timestamps
    c_times = control_p_real_df[time_col].unique()
    r_times = ref_p_real_df[time_col].unique()
    common_times = np.intersect1d(c_times, r_times)

    c_p_df = control_p_real_df[control_p_real_df[time_col].isin(common_times)].sort_values(by=time_col)
    c_q_df = control_p_imag_df[control_p_imag_df[time_col].isin(common_times)].sort_values(by=time_col)
    r_p_df = ref_p_real_df[ref_p_real_df[time_col].isin(common_times)].sort_values(by=time_col)
    r_q_df = ref_p_imag_df[ref_p_imag_df[time_col].isin(common_times)].sort_values(by=time_col)

    # Calculate sum over all buses for each timestep
    # Sum only numeric columns (excluding time)
    c_p_cols = [c for c in c_p_df.columns if c != time_col]
    ref_p_cols = [c for c in r_p_df.columns if c != time_col]
    c_q_cols = [c for c in c_q_df.columns if c != time_col]
    ref_q_cols = [c for c in r_q_df.columns if c != time_col]

    c_p_sum = c_p_df.set_index(time_col)[c_p_cols].sum(axis=1)
    ref_p_sum = r_p_df.set_index(time_col)[ref_p_cols].sum(axis=1)

    c_q_sum = c_q_df.set_index(time_col)[c_q_cols].sum(axis=1)
    ref_q_sum = r_q_df.set_index(time_col)[ref_q_cols].sum(axis=1)

    timesteps = c_p_df[time_col].apply(format_time_str).tolist()

    # Plot active power
    ax1.plot(
        range(len(timesteps)),
        ref_p_sum,
        color="#ea4335",
        marker="o",
        linestyle="--",
        linewidth=2.0,
        label="Reference (Uncontrolled)",
    )
    ax1.plot(
        range(len(timesteps)), c_p_sum, color="#1a73e8", marker="s", linewidth=2.0, label="Control (LinDistFlow OPF)"
    )
    ax1.set_ylabel("Total Real Power Injection (kW)", fontsize=11)
    ax1.set_title("Total Grid Real and Reactive Power Injection Comparison", fontsize=13, fontweight="bold", pad=10)
    ax1.legend(loc="upper right", frameon=True)
    ax1.grid(True, linestyle=":", alpha=0.6)

    # Plot reactive power
    ax2.plot(
        range(len(timesteps)),
        ref_q_sum,
        color="#ea4335",
        marker="o",
        linestyle="--",
        linewidth=2.0,
        label="Reference (Uncontrolled)",
    )
    ax2.plot(
        range(len(timesteps)), c_q_sum, color="#1a73e8", marker="s", linewidth=2.0, label="Control (LinDistFlow OPF)"
    )
    ax2.set_ylabel("Total Reactive Power Injection (kVar)", fontsize=11)
    ax2.set_xlabel("Time (HH:MM)", fontsize=11)
    ax2.set_xticks(range(len(timesteps)))
    ax2.set_xticklabels(timesteps, rotation=15, ha="right")
    ax2.legend(loc="upper right", frameon=True)
    ax2.grid(True, linestyle=":", alpha=0.6)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()
    logger.info(f"Saved power flow comparison plot to: {output_path}")


def plot_voltage_scatter_at_timestep(
    control_v_df: pd.DataFrame,
    ref_v_df: pd.DataFrame,
    output_path: Path,
    timestep_idx: int = -1,
) -> None:
    """Generate a scatter plot.

    Comparing individual bus voltage magnitudes at a single timestep.
    """
    time_col = "time" if "time" in control_v_df.columns else control_v_df.columns[0]
    c_times = control_v_df[time_col].unique()
    r_times = ref_v_df[time_col].unique()
    common_times = np.intersect1d(c_times, r_times)

    if len(common_times) == 0:
        logger.warning("No common timestamps found for voltage scatter plot.")
        return

    c_v = control_v_df[control_v_df[time_col].isin(common_times)].sort_values(by=time_col)
    r_v = ref_v_df[ref_v_df[time_col].isin(common_times)].sort_values(by=time_col)

    t_val = c_v.iloc[timestep_idx][time_col]
    t_str = format_time_str(t_val)
    v_cols = [c for c in c_v.columns if c != time_col and c in r_v.columns]

    if not v_cols:
        logger.warning("No matching voltage columns found for scatter plot.")
        return

    v_ref = r_v.iloc[timestep_idx][v_cols].values.astype(float)
    v_ctrl = c_v.iloc[timestep_idx][v_cols].values.astype(float)

    fig, ax = plt.subplots(figsize=(6.5, 6))
    ax.scatter(v_ref, v_ctrl, color="#1a73e8", alpha=0.7, edgecolors="none", s=50, label="Buses")

    min_v = min(v_ref.min(), v_ctrl.min(), 0.94)
    max_v = max(v_ref.max(), v_ctrl.max(), 1.06)
    ax.plot([min_v, max_v], [min_v, max_v], color="#5f6368", linestyle="--", alpha=0.7, label="No Change (y=x)")

    ax.axhspan(0.95, 1.05, color="#34a853", alpha=0.08, label="ANSI C84.1 Range")
    ax.axvspan(0.95, 1.05, color="#34a853", alpha=0.08)

    ax.set_xlabel("Reference Voltage (p.u.)", fontsize=11)
    ax.set_ylabel("Control Voltage (p.u.)", fontsize=11)
    ax.set_title(f"Individual Bus Voltages at Timestep {t_str}", fontsize=12, fontweight="bold")
    ax.grid(True, linestyle=":", alpha=0.6)
    ax.legend(loc="lower right")

    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()
    logger.info(f"Saved voltage scatter plot to: {output_path}")


def plot_power_scatter_at_timestep(
    control_p_df: pd.DataFrame,
    ref_p_df: pd.DataFrame,
    control_q_df: pd.DataFrame,
    ref_q_df: pd.DataFrame,
    output_path: Path,
    timestep_idx: int = -1,
) -> None:
    """Generate scatter plots.

    Comparing individual bus active and reactive power injections at a single timestep.
    """
    time_col = "time" if "time" in control_p_df.columns else control_p_df.columns[0]
    c_times = control_p_df[time_col].unique()
    r_times = ref_p_df[time_col].unique()
    common_times = np.intersect1d(c_times, r_times)

    if len(common_times) == 0:
        logger.warning("No common timestamps found for power scatter plot.")
        return

    c_p = control_p_df[control_p_df[time_col].isin(common_times)].sort_values(by=time_col)
    r_p = ref_p_df[ref_p_df[time_col].isin(common_times)].sort_values(by=time_col)
    c_q = control_q_df[control_q_df[time_col].isin(common_times)].sort_values(by=time_col)
    r_q = ref_q_df[ref_q_df[time_col].isin(common_times)].sort_values(by=time_col)

    t_val = c_p.iloc[timestep_idx][time_col]
    t_str = format_time_str(t_val)
    p_cols = [c for c in c_p.columns if c != time_col and c in r_p.columns]
    q_cols = [c for c in c_q.columns if c != time_col and c in r_q.columns]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5.5))

    if p_cols:
        p_ref = r_p.iloc[timestep_idx][p_cols].values.astype(float)
        p_ctrl = c_p.iloc[timestep_idx][p_cols].values.astype(float)
        ax1.scatter(p_ref, p_ctrl, color="#ea4335", alpha=0.7, edgecolors="none", s=40, label="Buses")
        min_p = min(p_ref.min(), p_ctrl.min())
        max_p = max(p_ref.max(), p_ctrl.max())
        ax1.plot([min_p, max_p], [min_p, max_p], color="#5f6368", linestyle="--", alpha=0.7, label="y=x")
        ax1.set_xlabel("Reference Injection (kW)", fontsize=11)
        ax1.set_ylabel("Control Injection (kW)", fontsize=11)
        ax1.set_title("Real Power Injection Comparison", fontsize=12, fontweight="bold")
        ax1.grid(True, linestyle=":", alpha=0.6)
        ax1.legend(loc="lower right")

    if q_cols:
        q_ref = r_q.iloc[timestep_idx][q_cols].values.astype(float)
        q_ctrl = c_q.iloc[timestep_idx][q_cols].values.astype(float)
        ax2.scatter(q_ref, q_ctrl, color="#f9ab00", alpha=0.7, edgecolors="none", s=40, label="Buses")
        min_q = min(q_ref.min(), q_ctrl.min())
        max_q = max(q_ref.max(), q_ctrl.max())
        ax2.plot([min_q, max_q], [min_q, max_q], color="#5f6368", linestyle="--", alpha=0.7, label="y=x")
        ax2.set_xlabel("Reference Injection (kVar)", fontsize=11)
        ax2.set_ylabel("Control Injection (kVar)", fontsize=11)
        ax2.set_title("Reactive Power Injection Comparison", fontsize=12, fontweight="bold")
        ax2.grid(True, linestyle=":", alpha=0.6)
        ax2.legend(loc="lower right")

    plt.suptitle(f"Individual Bus Power Comparison at Timestep {t_str}", fontsize=14, fontweight="bold", y=0.98)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()
    logger.info(f"Saved power scatter plot to: {output_path}")


def plot_control_wireframe_3d(
    df: pd.DataFrame,
    title: str,
    z_label: str,
    output_path: Path,
    wireframe_color: str = "#1a73e8",
) -> None:
    """Plot the control variable in a 3D wireframe style for all devices and timesteps.

    The plot is rendered as a 3-column, 1-row set of subplots corresponding to Phases A, B, and C.
    Devices are color-coded consistently across phases and sorted by their average value descending.

    Args:
        df: DataFrame containing the control variables (real or reactive power).
        title: Title of the plot.
        z_label: Label for the Z axis.
        output_path: Path to save the output plot.
        wireframe_color: Optional default color (unused as devices are color-coded).
    """
    time_col = "time" if "time" in df.columns else df.columns[0]
    device_cols = [col for col in df.columns if col != time_col]

    if not device_cols:
        logger.warning(f"No device columns found for 3D plot: {title}")
        return

    # Extract unique device base names
    unique_devices = sorted(list(set(col.rsplit(".", 1)[0] for col in device_cols)))

    # Generate distinct colors for each unique device
    try:
        colormap = plt.colormaps.get("tab10")
    except AttributeError:
        colormap = plt.cm.get_cmap("tab10")
    colors_list = colormap(np.linspace(0, 1, max(10, len(unique_devices))))
    device_colors = {dev: colors_list[idx % len(colors_list)] for idx, dev in enumerate(unique_devices)}

    fig = plt.figure(figsize=(20, 7))
    phases = ["1", "2", "3"]
    phase_labels = ["Phase A (1)", "Phase B (2)", "Phase C (3)"]

    for idx, (phase, phase_label) in enumerate(zip(phases, phase_labels, strict=True)):
        phase_cols = [col for col in device_cols if col.endswith(f".{phase}")]
        if not phase_cols:
            ax = fig.add_subplot(1, 3, idx + 1, projection="3d")
            ax.set_title(f"{phase_label} - No Data", fontsize=12, fontweight="bold")
            continue

        ax = fig.add_subplot(1, 3, idx + 1, projection="3d")

        # Sort columns by their average value descending (max average on the left, min average on the right)
        averages = df[phase_cols].mean()
        sorted_cols = averages.sort_values(ascending=False).index.tolist()

        x_coords = np.arange(len(sorted_cols))
        y_coords = np.arange(len(df))

        # Plot cross-connecting wireframe lines (across devices at each timestep)
        for t_idx in y_coords:
            ax.plot(
                x_coords,
                np.full(len(x_coords), t_idx),
                df[sorted_cols].iloc[t_idx].to_numpy(),
                color="#e5e5e5",
                alpha=0.4,
                linewidth=0.8,
                zorder=1,
            )

        # Plot device curves along time (Y-axis) with their device color
        for col_idx, col in enumerate(sorted_cols):
            device_name = col.rsplit(".", 1)[0]
            color = device_colors.get(device_name, wireframe_color)

            ax.plot(
                np.full(len(df), col_idx),
                y_coords,
                df[col].to_numpy(),
                color=color,
                linewidth=2.2,
                label=device_name,
                zorder=2,
            )

        # Configure subplot axes
        ax.set_title(phase_label, fontsize=12, fontweight="bold", pad=10)
        ax.set_xlabel("Devices", fontsize=10, labelpad=12)
        ax.set_ylabel("Time (HH:MM)", fontsize=10, labelpad=12)
        ax.set_zlabel(z_label, fontsize=10, labelpad=8)

        # X-axis ticks (Devices)
        short_names = [col.rsplit(".", 1)[0] for col in sorted_cols]
        if len(sorted_cols) > 5:
            step_x = max(1, len(sorted_cols) // 5)
            tick_indices_x = np.arange(0, len(sorted_cols), step_x)
            ax.set_xticks(tick_indices_x)
            ax.set_xticklabels([short_names[i] for i in tick_indices_x], rotation=30, ha="right", fontsize=8)
        else:
            ax.set_xticks(x_coords)
            ax.set_xticklabels(short_names, rotation=30, ha="right", fontsize=8)

        # Y-axis ticks (Timesteps)
        timesteps = df[time_col].apply(format_time_str).tolist()
        if len(timesteps) > 6:
            step_y = max(1, len(timesteps) // 6)
            tick_indices_y = np.arange(0, len(timesteps), step_y)
            ax.set_yticks(tick_indices_y)
            ax.set_yticklabels([timesteps[i] for i in tick_indices_y], rotation=-15, ha="left", fontsize=8)
        else:
            ax.set_yticks(y_coords)
            ax.set_yticklabels(timesteps, rotation=-15, ha="left", fontsize=8)

        # Add legend if not too many devices
        handles, labels = ax.get_legend_handles_labels()
        by_label = dict(zip(labels, handles, strict=True))
        if len(by_label) <= 10:
            ax.legend(by_label.values(), by_label.keys(), loc="upper right", fontsize=8)

    # Set overall title
    fig.suptitle(title, fontsize=14, fontweight="bold", y=0.98)

    # Adjust spacing explicitly instead of tight_layout to avoid the warning
    fig.subplots_adjust(wspace=0.3, left=0.05, right=0.95, bottom=0.15, top=0.88)

    # Save
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()
    logger.info(f"Saved 3D control wireframe plot to: {output_path}")


def main() -> None:
    """Main execution function to load data and generate plots."""
    parser = argparse.ArgumentParser(description="Plot LinDistFlow OPF metrics and 3D control power wireframes.")
    parser.add_argument(
        "scenario_path",
        type=str,
        help="Path to the scenario JSON file",
    )
    parser.add_argument(
        "--data-dir",
        type=str,
        default=str(COMPONENT_DIR.parent.parent / "outputs"),
        help="Path to the directory where recorders saved feather files",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=str(COMPONENT_DIR.parent.parent / "outputs"),
        help="Path to save the generated plots",
    )
    args = parser.parse_args()

    data_dir = Path(args.data_dir).resolve()
    scenario_path = Path(args.scenario_path).resolve()
    output_dir = Path(args.output_dir).resolve()

    if not data_dir.exists():
        logger.error(f"Data directory does not exist: {data_dir}")
        sys.exit(1)

    if not scenario_path.exists():
        logger.error(f"Scenario file does not exist: {scenario_path}")
        sys.exit(1)

    logger.info(f"Loading scenario configuration from: {scenario_path}")
    recorder_paths = load_scenario_recorders(scenario_path, data_dir)

    # Load Topology & Base Voltages
    topology_path = data_dir / "topology.json"
    base_voltages: dict[str, float] = {}
    if topology_path.exists():
        logger.info(f"Loading grid topology for base voltages from: {topology_path}")
        try:
            with open(topology_path, encoding="utf-8") as f:
                topology_data = json.load(f)
            base_volts_info = topology_data.get("base_voltage_magnitudes", {})
            ids = base_volts_info.get("ids", [])
            values = base_volts_info.get("values", [])
            base_voltages = dict(zip(ids, values, strict=True))
        except Exception as e:
            logger.warning(f"Could not parse topology.json for base voltages: {e}")
    else:
        logger.warning(f"Topology file not found at {topology_path}. Feeder voltages cannot be normalized.")

    # Load Controlled Voltages (OPF or control_feeder)
    v_df = None
    if "control_vmag" in recorder_paths or "control_vreal" in recorder_paths:
        c_vmag_path = recorder_paths.get("control_vmag")
        c_vreal_path = recorder_paths.get("control_vreal")
        c_vimag_path = recorder_paths.get("control_vimag")

        control_v_df = None
        if c_vmag_path and c_vmag_path.exists():
            control_v_df = load_dataframe(c_vmag_path)
        elif c_vreal_path and c_vreal_path.exists():
            c_vreal_df = load_dataframe(c_vreal_path)
            if c_vreal_df is not None:
                if c_vimag_path and c_vimag_path.exists():
                    c_vimag_df = load_dataframe(c_vimag_path)
                    if c_vimag_df is not None:
                        # Combine real and imag to find magnitude
                        time_col = "time" if "time" in c_vreal_df.columns else c_vreal_df.columns[0]
                        cols = [c for c in c_vreal_df.columns if c != time_col]
                        control_v_df = c_vreal_df.copy()
                        for col in cols:
                            if col in c_vimag_df.columns:
                                control_v_df[col] = (c_vreal_df[col] ** 2 + c_vimag_df[col] ** 2) ** 0.5
                else:
                    # Only real part is available, use it as magnitude
                    control_v_df = c_vreal_df.copy()
                    time_col = "time" if "time" in c_vreal_df.columns else c_vreal_df.columns[0]
                    cols = [c for c in c_vreal_df.columns if c != time_col]
                    for col in cols:
                        control_v_df[col] = control_v_df[col].abs()

        if control_v_df is not None:
            # Normalize by base_voltages
            time_col = "time" if "time" in control_v_df.columns else control_v_df.columns[0]
            cols = [c for c in control_v_df.columns if c != time_col]
            v_df = control_v_df.copy()
            for col in cols:
                base_v = base_voltages.get(col, 1.0)
                if base_v <= 0:
                    base_v = 1.0
                v_df[col] = v_df[col] / base_v
    elif "dopf_vmag" in recorder_paths:
        v_path = recorder_paths["dopf_vmag"]
        logger.info(f"Loading voltage magnitude data from: {v_path}")
        v_df = load_dataframe(v_path)
    else:
        logger.warning("No voltage recorder configured in scenario. Skipping voltage plot.")

    # Load Feeder Voltages (Uncontrolled or reference_feeder) & Normalize
    feeder_v_pu_df = None
    ref_vmag_key = (
        "reference_vmag" if "reference_vmag" in recorder_paths or "reference_vreal" in recorder_paths else "feeder_vmag"
    )
    ref_vreal_key = (
        "reference_vreal"
        if "reference_vmag" in recorder_paths or "reference_vreal" in recorder_paths
        else "feeder_vreal"
    )
    ref_vimag_key = (
        "reference_vimag"
        if "reference_vmag" in recorder_paths or "reference_vreal" in recorder_paths
        else "feeder_vimag"
    )

    if ref_vreal_key in recorder_paths or ref_vmag_key in recorder_paths:
        vreal_path = recorder_paths.get(ref_vreal_key)
        vimag_path = recorder_paths.get(ref_vimag_key)
        vmag_path = recorder_paths.get(ref_vmag_key)

        feeder_v_df = None
        if vmag_path and vmag_path.exists():
            feeder_v_df = load_dataframe(vmag_path)
        elif vreal_path and vreal_path.exists():
            vreal_df = load_dataframe(vreal_path)
            if vreal_df is not None:
                if vimag_path and vimag_path.exists():
                    vimag_df = load_dataframe(vimag_path)
                    if vimag_df is not None:
                        # Combine real and imag to find magnitude
                        time_col = "time" if "time" in vreal_df.columns else vreal_df.columns[0]
                        cols = [c for c in vreal_df.columns if c != time_col]
                        feeder_v_df = vreal_df.copy()
                        for col in cols:
                            if col in vimag_df.columns:
                                feeder_v_df[col] = (vreal_df[col] ** 2 + vimag_df[col] ** 2) ** 0.5
                else:
                    # Only real part is available, use it as magnitude
                    feeder_v_df = vreal_df.copy()
                    time_col = "time" if "time" in vreal_df.columns else vreal_df.columns[0]
                    cols = [c for c in vreal_df.columns if c != time_col]
                    for col in cols:
                        feeder_v_df[col] = feeder_v_df[col].abs()

        if feeder_v_df is not None:
            # Normalize by base_voltages
            time_col = "time" if "time" in feeder_v_df.columns else feeder_v_df.columns[0]
            cols = [c for c in feeder_v_df.columns if c != time_col]
            feeder_v_pu_df = feeder_v_df.copy()
            for col in cols:
                base_v = base_voltages.get(col, 1.0)
                if base_v <= 0:
                    base_v = 1.0
                feeder_v_pu_df[col] = feeder_v_pu_df[col] / base_v

    # Generate plots directory if needed
    output_dir.mkdir(parents=True, exist_ok=True)

    # 1. Plot Voltages
    if v_df is not None:
        plot_voltages(v_df, feeder_v_pu_df, output_dir / "lindistflow_voltage_profile.png")
    else:
        logger.warning("Controlled voltage dataframe not loaded. Skipping voltage plot.")

    # 2. Plot Powers Comparison (Controlled vs Reference)
    c_preal = None
    c_pimag = None
    r_preal = None
    r_pimag = None
    if "control_preal" in recorder_paths and "reference_preal" in recorder_paths:
        c_preal = load_dataframe(recorder_paths["control_preal"])
        c_pimag = load_dataframe(recorder_paths["control_pimag"])
        r_preal = load_dataframe(recorder_paths["reference_preal"])
        r_pimag = load_dataframe(recorder_paths["reference_pimag"])

        if all(df is not None for df in [c_preal, c_pimag, r_preal, r_pimag]):
            plot_power_comparison(c_preal, c_pimag, r_preal, r_pimag, output_dir / "lindistflow_power_comparison.png")
    else:
        logger.warning(
            "Reference or Control power recorders not configured in scenario. Skipping power comparison plot."
        )

    # 3. Plot Voltage Scatter Comparison at a Single Timestep
    if v_df is not None and feeder_v_pu_df is not None:
        plot_voltage_scatter_at_timestep(
            v_df, feeder_v_pu_df, output_dir / "lindistflow_voltage_scatter.png", timestep_idx=-1
        )

    # 4. Plot Power Scatter Comparison at a Single Timestep
    if all(df is not None for df in [c_preal, r_preal, c_pimag, r_pimag]):
        plot_power_scatter_at_timestep(
            c_preal, r_preal, c_pimag, r_pimag, output_dir / "lindistflow_power_scatter.png", timestep_idx=-1
        )

    # 3. Plot 3D Real Control Power Wireframe
    if "dopf_ctrl_real" in recorder_paths:
        p_path = recorder_paths["dopf_ctrl_real"]
        logger.info(f"Loading real control power data from: {p_path}")
        p_df = load_dataframe(p_path)
        if p_df is not None:
            plot_control_wireframe_3d(
                p_df,
                title="LinDistFlow Real Power Control (Active Setpoints)",
                z_label="Real Power Setpoint (kW)",
                output_path=output_dir / "lindistflow_control_real_3d.png",
                wireframe_color="#1a73e8",  # Google Blue
            )
    else:
        logger.warning("No real control power recorder configured in scenario. Skipping real control plot.")

    # 4. Plot 3D Reactive Control Power Wireframe
    if "dopf_ctrl_imag" in recorder_paths:
        q_path = recorder_paths["dopf_ctrl_imag"]
        logger.info(f"Loading reactive control power data from: {q_path}")
        q_df = load_dataframe(q_path)
        if q_df is not None:
            plot_control_wireframe_3d(
                q_df,
                title="LinDistFlow Reactive Power Control (Var Setpoints)",
                z_label="Reactive Power Setpoint (kVar)",
                output_path=output_dir / "lindistflow_control_imaginary_3d.png",
                wireframe_color="#12b5cb",  # Google Cyan
            )
    else:
        logger.warning("No reactive control power recorder configured in scenario. Skipping reactive control plot.")

    logger.info("Plotting complete.")


if __name__ == "__main__":
    main()
