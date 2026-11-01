# Aurora Currents

> An interactive creative coding project that recreates the movement, colours and atmosphere of the Northern and Southern Lights using Python Mode in Processing.

## Table of Contents

- [General Information](#general-information)
- [Technologies Used](#technologies-used)
- [Features](#features)
- [Screenshots](#screenshots)
- [Setup](#setup)
- [Usage](#usage)
- [Project Status](#project-status)
- [Room for Improvement](#room-for-improvement)
- [Acknowledgements](#acknowledgements)
- [Contact](#contact)

## General Information

Aurora Currents is a creative coding project developed using Processing Python Mode. It explores how programming can be used to recreate natural phenomena through digital animation and interactive visual effects.

The project was inspired by the Northern and Southern Lights, particularly their flowing movements, vibrant colour transitions and atmospheric appearance.

The main purpose was to investigate how mathematical calculations, Perlin noise, colour interpolation and interactive programming could transform simple graphical elements into a dynamic digital artwork.

Two variations were developed:

- **Northern Lights:** Featuring green, turquoise, blue and purple colour palettes.
- **Southern Lights:** Featuring warmer pink, orange, yellow and purple tones.

The project also provided an opportunity to develop my understanding of programming concepts through experimentation, debugging and iterative refinement.

## Technologies Used

- **Processing**: Creative coding environment
- **Python Mode for Processing**: Programming language and execution environment
- **Python `math` module**: Mathematical calculations for movement and wave effects
- **Processing graphics functions**: Rendering shapes, colours, transparency and animation

## Features

The main features of Aurora Currents include:

- **Animated aurora curtains:** Multiple overlapping layers that move continuously using Perlin noise and mathematical calculations.
- **Colour gradients:** RGB values, interpolation and alpha transparency create smooth transitions and glowing effects.
- **Interactive mouse movement:** Moving the cursor across the sky influences and disperses the aurora.
- **Mouse-click interaction:** Clicking generates a glowing ripple through the curtains.
- **Autonomous animation:** The aurora continues flowing naturally when the mouse is stationary.
- **Atmospheric environment:** Twinkling stars, a moon, distant mountains, clouds and snowfall.
- **Water reflections:** Animated reflections that use mathematical distortion to simulate movement across the water.
- **Two visual variations:** Northern and Southern Lights versions using different colour palettes.

## Screenshots

Screenshots of the completed Northern and Southern Lights prototypes can be added here.

**Northern Lights**

<img width="467" height="512" alt="Screenshot 2026-11-01 181138" src="https://github.com/user-attachments/assets/dabfb86a-6fc4-4c84-80cd-52cdebe18c5b" />

**Southern Lights**

<img width="468" height="527" alt="Screenshot 2026-11-01 181354" src="https://github.com/user-attachments/assets/7c24c3d1-a26f-4072-8305-d51720ddfa84" />

These screenshots demonstrate the differences in colour palettes and visual atmosphere while highlighting the shared animation techniques.

## Setup

To run Aurora Currents, you will need:

- Processing installed on your computer
- Python Mode installed and selected within Processing
- The project sketch files (`.pyde`)

**Installation instructions:**

1. Download or clone this repository from GitHub.
2. Open Processing.
3. Ensure that Python Mode is installed and selected.
4. Open the relevant `.pyde` sketch file.
5. Click the **Run** button to launch the program.

Both versions can be run separately.

## Usage

Once the program is running, the aurora begins moving automatically.

Users can interact with the artwork using their mouse.

| User Action | Result |
|---|---|
| Leave the mouse stationary | The aurora continues flowing naturally |
| Move the mouse across the sky | The light curtains respond and disperse |
| Click the sky | A glowing wave travels through the aurora |
| Move the mouse across the water | Interactive ripples appear in the reflection |

The program uses smoothed mouse coordinates and displacement calculations to create gradual, flowing interactions.

For example, this section of the Northern Lights code smooths the cursor's position:

```python
mx += (mouseX - mx) * follow
my += (mouseY - my) * follow
```

Rather than immediately moving the aurora to the cursor's location, these calculations allow the interaction to respond progressively, making the movement appear more natural.

## Project Status

Project is: **Complete: university creative coding prototype.**

The Northern and Southern Lights variations have been developed, with the main animation, interaction and environmental effects implemented.

The project was refined through multiple stages of testing, visual experimentation and debugging.

## Room for Improvement

Although the prototype achieves its main visual and interactive goals, there are still opportunities for improvement.

**Room for improvement:**

- Further optimise rendering performance when multiple visual effects are active.
- Refine the balance between mouse responsiveness and natural movement.
- Increase variation between individual aurora curtains to create more realistic patterns.
- Improve the organisation and documentation of the code for readability.

**To do / Future Development:**

- Introduce adjustable animation speeds and brightness controls.
- Allow users to select and customise colour palettes.
- Experiment with additional aurora movement patterns.
- Develop a more immersive and responsive environment.

## Acknowledgements

Aurora Currents was inspired by the natural appearance and movement of the Northern and Southern Lights.

The project was developed through experimentation with creative coding techniques and learning resources, including:

- [Processing](https://processing.org/) — Creative coding environment and documentation.
- [Processing Python Mode](https://py.processing.org/) — Python programming within Processing.
- [futurecoder](https://futurecoder.io/) — Interactive Python learning exercises.
- [Harvard CS50's Introduction to Programming with Python](https://cs50.harvard.edu/python/) — Python programming concepts.
- [Automate the Boring Stuff with Python](https://automatetheboringstuff.com/) — Practical Python programming reference.
- Reas, C., & Fry, B. (2015). Getting started with Processing. Maker Media.
- Zhang, Y., & Funk, M. (2023). Coding art: A guide to Unlocking Your Creativity with the Processing Language p5.js in Four Simple Steps. Apress.

Peer feedback also contributed to the refinement of the animation, interaction and overall code structure.

## Contact

Created as part of a university Creative Coding assignment.

For questions or feedback, please use the GitHub repository's Issues section.
