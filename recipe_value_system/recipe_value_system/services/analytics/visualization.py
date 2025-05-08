"""Visualization module for analytics."""

from typing import Dict, List

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from numpy.typing import NDArray


def plot_value_distribution(
    values: NDArray[np.float64],
    title: str = "Value Distribution",
) -> None:
    """Plot the distribution of recipe values.

    Args:
        values: Array of recipe values
        title: Plot title

    Raises:
        TypeError: If values is not an NDArray[np.float64]
    """
    if not isinstance(values, np.ndarray):
        raise TypeError("Values must be an NDArray[np.float64]")

    plt.figure(figsize=(10, 6))
    sns.histplot(values, kde=True)
    plt.title(title)
    plt.xlabel("Value")
    plt.ylabel("Count")
    plt.show()


def plot_value_heatmap(
    values: Dict[str, NDArray[np.float64]],
    title: str = "Value Heatmap",
) -> None:
    """Plot a heatmap of recipe values.

    Args:
        values: Dictionary mapping value types to arrays of values
        title: Plot title

    Raises:
        TypeError: If values is not a Dict[str, NDArray[np.float64]]
    """
    if not isinstance(values, dict):
        raise TypeError("Values must be a Dict[str, NDArray[np.float64]]")

    data = np.array(list(values.values()))
    plt.figure(figsize=(12, 8))
    sns.heatmap(data, xticklabels=list(values.keys()), cmap="YlOrRd")
    plt.title(title)
    plt.xlabel("Value Type")
    plt.ylabel("Recipe")
    plt.show()


def plot_value_trends(
    values: List[NDArray[np.float64]],
    labels: List[str],
    title: str = "Value Trends",
) -> None:
    """Plot trends in recipe values over time.

    Args:
        values: List of arrays containing value histories
        labels: List of value type labels
        title: Plot title

    Raises:
        TypeError: If values is not a List[NDArray[np.float64]]
        ValueError: If lengths of values and labels do not match
    """
    if not isinstance(values, list):
        raise TypeError("Values must be a List[NDArray[np.float64]]")
    if not isinstance(labels, list):
        raise TypeError("Labels must be a List[str]")
    if len(values) != len(labels):
        raise ValueError("Length of values must match length of labels")

    plt.figure(figsize=(12, 6))
    for value, label in zip(values, labels):
        plt.plot(value, label=label)
    plt.title(title)
    plt.xlabel("Time")
    plt.ylabel("Value")
    plt.legend()
    plt.show()


def plot_value_radar(
    values: Dict[str, float],
    title: str = "Value Radar",
) -> None:
    """Plot a radar chart of recipe values.

    Args:
        values: Dictionary mapping value types to scores
        title: Plot title

    Raises:
        TypeError: If values is not a Dict[str, float]
    """
    if not isinstance(values, dict):
        raise TypeError("Values must be a Dict[str, float]")

    categories = list(values.keys())
    scores = list(values.values())

    angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False)
    scores = np.concatenate((scores, [scores[0]]))
    angles = np.concatenate((angles, [angles[0]]))

    fig = plt.figure(figsize=(8, 8))
    ax = fig.add_subplot(111, polar=True)
    ax.plot(angles, scores)
    ax.fill(angles, scores, alpha=0.25)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories)
    plt.title(title)
    plt.show()
