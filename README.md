# LuminousMatrix
## Generate your own Arecibo Message from Light！
---

## Overview
[▶ Watch the prism–light–sound interaction demo]


https://github.com/user-attachments/assets/2209e582-0f89-488f-8bcf-f8d22813d72e


*LuminousMatrix* speculates on a universal communication system shared by intelligent civilisations across the cosmos.  
In this fictional framework, no species transmits language directly.  
Instead, **light itself becomes the medium of inscription**:  
its refractions, reflections, and trajectories that write information into space.

Every point touched by light is recorded as **1**, and every untouched point becomes **0**.  
The resulting binary map forms a **Luminous Matrix Language (LML)** —  
a hypothetical shared protocol for interstellar communication, built not on symbols but on **light-structured presence**.

Human history has always relied on light to communicate —  
from beacon towers and naval signal lamps to optical fibres.  
LML extends this idea to a cosmic scale:  
If light is the only element universally shared by all intelligent life, then perhaps the **Arecibo Message** was merely Earth’s first attempt at speaking this language.

This installation reconstructs and reimagines that possibility.

---

# Concept

## 1. Light as the Stroke of a Universal Script

Participants manipulate prisms to refract and redirect a beam of light.  
What appears to be a simple optical interaction is reframed, within the system’s internal logic, as an act of **writing**.

Each change in direction becomes a kind of **grammar**;  
each light-path forms a **syntactic structure**;  
each touchpoint inscribes a **1** in the matrix.

Participants are not merely interacting with optics —  
They are generating **sentences in a lost interstellar language**.

---

## 2. Sound as the Echo Field of Light

In the speculative universe of LML, every light-based message produces an **echo field** —  
not sound as air vibration, but a resonant **information-amplitude echo**.

The installation simulates this by translating light behaviour into sound:

- refraction paths → **melodic structures**  
- color → **timbre**  
- intensity → **amplitude**  
- movement → **rhythm**  
- reflection loops → **harmonic resonance**  
- binary density → **spectral saturation**  

Sound is not decorative — it is the **sub-lingual acoustic shadow** of the luminous message.

**Light writes the message;  
sound reads it back.**

---

## 3. Arecibo as a Sample of a Lost Script

Instead of treating the 1974 Arecibo Message as a historical artefact,  
The installation positions it as a **fragment of a much larger, unknown text**.

By tracking the real-time movement of the refracted beam:

- touched pixels → **1**  
- untouched pixels → **0**  

The system continuously generates new **Arecibo-like matrices**,  
unique to each gesture, moment, and spatial configuration.

Arecibo becomes not a relic, but a **template for generating new cosmic transmissions**.

---


#  Project Structure

```
📁 Aruco/
├─ maker_id.png                     # Aruco code

📁 Main/
├─ Arecibo Message/               # Detect Aruco and generate the Arecibo Message
├─ Light2Max/                     # Sound processing
├─ Maxmsp/                        # Communicate with Maxmsp
├─ Main.py                       

📁 TTT/      # Testfile (Not required)
├─ ......
📁 YYY/      # Testfile (Not required)
├─ ......

📃 README.md                # Documentation
📃 requirements.txt
```

### How to Run

1. Clone this repository (you may ignore `TTT` and `YYY`, which are **not required** for running the main program)
2. Install dependencies

```bash
pip install -r requirements.txt
```
**External Dependency**: This project requires **Max/MSP** to be installed separately.

3. Run the main script:

```bash
python Main/Main.py
```

---


#  System Architecture


### 1. Prism Setup
- Participants manipulate prisms to refract and reflect a light beam.
- Light beam acts as the medium for encoding information.

### 2. Camera Capture
- Tracks the position of the light spot in real-time.
- Extracts properties: `x`, `y`, `hue`, `intensity`, `velocity`.
- Implemented with: `OpenCV`, `cv.jit`, `jit.grab`.

### 3. Binary Matrix Encoder (Python)
- Converts light paths into a binary pixel grid (default: 73×23, customizable).
- Light-touched cells → `1`.
- Untouched cells → `0`.
- Generates dynamic arrays and bitstreams.
- Data sent via `numpy → OSC → Max/MSP`.
---

#  Sound Engine (Max/MSP)

The Max patch translates real-time OSC light data into a multilayer sonic texture.

                ┌──────────────┐
                │ LIGHT FILTER  │ ← hue/intensity
                └───────┬──────┘
                        ▼
             ┌─────────────────────┐
             │   HARMONIC ENGINE   │ ← reflection loops
             └─────────┬──────────┘
                       ▼
      ┌───────────────────────────────────┐
      │      GRANULAR SYNTHESIZER         │ ← velocity & binary density
      └──────────────────┬────────────────┘
                         ▼
      ┌───────────────────────────────────┐
      │  AMBIENT DELAY NETWORK + REVERB   │ ← x-modulated delay time
      └───────────────────────────────────┘

---

## Interaction & Experience
- Participants are **not just rotating prisms** — they are activating a dormant communication protocol.
- **Light writes the message**, **sound reads it back**, and the **pixel matrix displays a real-time transmission**.
- Every gesture creates a new, unique cosmic message — a signal sent toward the unknown.
- Communication becomes **evidence of existence**, not merely a functional exchange.

---

## Technical Stack
- **Python**: Binary matrix encoding, pixel visualizer
- **OpenCV / cv.jit / jit.grab**: Camera tracking, including **Aruco marker tracking**
- **Max/MSP**: Real-time sound synthesis
- **OSC**: Communication between Python and Max

---

## References
- Arecibo Message (1974)
- Concepts of non-linguistic communication
- Luminous Matrix Language (hypothetical)
- Granular synthesis, ambient sound design

---

## Authors
- **Huang Chuteng**
- **Guo Yueyue**
