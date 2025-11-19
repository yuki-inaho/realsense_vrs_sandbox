"""Pytest configuration and shared fixtures."""

import pytest
from pathlib import Path


@pytest.fixture
def data_dir() -> Path:
    """Return the path to the test data directory."""
    return Path(__file__).parent.parent / "data"


@pytest.fixture
def rosbag_path(data_dir: Path) -> Path:
    """Return the path to the primary test ROSbag file (outdoor scene with IMU)."""
    return data_dir / "rosbag" / "d435i_walk_around.bag"


@pytest.fixture
def sample_rosbag_paths(data_dir: Path) -> dict[str, Path]:
    """Return paths to all available sample ROSbag files."""
    rosbag_dir = data_dir / "rosbag"
    return {
        "outdoor": rosbag_dir / "d435i_walk_around.bag",
        "walking": rosbag_dir / "sample_d435i.bag",
        "user_data": rosbag_dir / "20251119_112125.bag",
    }
