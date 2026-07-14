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

    # Identify the Feeder component name
    feeder_names = [name for name, comp in components.items() if comp.get("type") in ["Feeder", "LocalFeeder"]]
    feeder_name = feeder_names[0] if feeder_names else None

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
                    # Feeder outputs
                    elif source == feeder_name:
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
    cols = [col for col in v_df.columns if col != time_col]

    if not cols:
        logger.warning("No voltage columns found to plot.")
        return

    # Process OPF voltages
    df_temp = v_df.set_index(time_col)[cols]
    v_min = df_temp.min(axis=1)
    v_max = df_temp.max(axis=1)
    v_mean = df_temp.mean(axis=1)
    timesteps = v_df[time_col].apply(format_time_str).tolist()

    fig, ax = plt.subplots(figsize=(10, 6))

    # 1. Plot Uncontrolled Feeder Voltages if available
    if feeder_df is not None:
        feeder_cols = [c for c in feeder_df.columns if c != time_col]
        if feeder_cols:
            df_feeder_temp = feeder_df.set_index(time_col)[feeder_cols]
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

    # Load Controlled Voltages (OPF)
    v_df = None
    if "dopf_vmag" in recorder_paths:
        v_path = recorder_paths["dopf_vmag"]
        logger.info(f"Loading voltage magnitude data from: {v_path}")
        v_df = load_dataframe(v_path)
    else:
        logger.warning("No voltage recorder configured in scenario. Skipping voltage plot.")

    # Load Feeder Voltages (Uncontrolled) & Normalize
    feeder_v_pu_df = None
    if "feeder_vreal" in recorder_paths or "feeder_vmag" in recorder_paths:
        vreal_path = recorder_paths.get("feeder_vreal")
        vimag_path = recorder_paths.get("feeder_vimag")
        vmag_path = recorder_paths.get("feeder_vmag")

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

    # 2. Plot 3D Real Control Power Wireframe
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

    # 3. Plot 3D Reactive Control Power Wireframe
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
