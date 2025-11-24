# Light2Max

A Python project that captures camera frames, detects bright light points using HLS (HSL) thresholding and sends the detected data to Max/MSP via OSC for sound synthesis.

**What it does**
- Captures video from a camera.
- Detects bright colored points using HLS thresholding and morphological cleanup.
- Computes centroid, area and brightness of detected region.
- Sends normalized values to Max/MSP via OSC at address `/light`.

**Install**
1. Create a virtual environment (recommended):
```
python3 -m venv venv
source venv/bin/activate
```
2. Install dependencies:
```
pip install -r YYY/Light2Max/requirements.txt
```

**Run**
```
python YYY/Light2Max/main.py --host 127.0.0.1 --port 8000
```
Options to tune H/L/S thresholds are available as CLI flags `--h_low`, `--l_low`, `--s_low`, `--h_high`, `--l_high`, `--s_high`.

**OSC messages**
- Address: `/light`
- Payload: `[x_norm, y_norm, area_norm, brightness]` where
  - `x_norm` and `y_norm` are normalized (0.0–1.0) coordinates in the frame,
  - `area_norm` is the detected area normalized by the frame area (0–1),
  - `brightness` is normalized lightness (0–1).

**Max/MSP example**
You can receive these messages in Max using `udpreceive` and `OSC-route` or a dedicated OSC object. A minimal approach:

1. Create an `udpreceive` object set to the same port (e.g. `udpreceive 8000`).
2. Connect its outlet to an `OSC-route /light` object (from the `cnmat` or `osc` externals) or parse the raw UDP bytes.
3. Map the incoming float list to synthesis parameters (frequency, amplitude, filter cutoff...).

If you don't have an OSC parser in Max, use the `udpreceive` object and the `OSC-route` external, or use the `mxj net.udp.UDPPacket` object and parse messages.

**Notes and next steps**
- You can add interactive sliders or GUI to tune thresholds in real-time.
- For better robustness, add color calibration and multiple-point tracking.

**Notes and next steps**
- You can add interactive sliders or GUI to tune thresholds in real-time.
- For better robustness, add color calibration and multiple-point tracking.

**GUI / Upload options**
This project includes two ways to provide a video file instead of using the camera:

- Command-line: use `--video <path>` with `main.py` to process a local file.
  Example:

  ```
  python YYY/Light2Max/main.py --video /path/to/file.mp4 --host 127.0.0.1 --port 8000
  ```

- macOS native picker: run the small helper `gui_uploader.py` which opens a native file dialog and launches `main.py` with the chosen file (no extra GUI dependencies required):

  ```
  python YYY/Light2Max/gui_uploader.py --host 127.0.0.1 --port 8000
  ```

The previous lightweight web UI has been removed from this repository; use one of the options above instead.
