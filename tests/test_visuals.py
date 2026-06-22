from content_lens.processors.visuals import frame_observations


def test_frame_observations_use_relative_paths(tmp_path):
    frame_dir = tmp_path / "assets" / "frames"
    frame_dir.mkdir(parents=True)
    frame = frame_dir / "frame_00001.jpg"
    frame.write_bytes(b"fake")

    observations = frame_observations([frame], tmp_path)

    assert len(observations) == 1
    assert observations[0].time == 0.0
    assert observations[0].asset_path == "assets/frames/frame_00001.jpg"
