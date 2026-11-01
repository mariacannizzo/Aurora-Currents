# Aurora Currents
### Interactive Northern and Southern Lights: Creative Coding Project

## Project Overview

Aurora Currents is an interactive digital artwork developed using **Processing Python Mode**. The project explores how programming can recreate the natural beauty, colours and movement of the Northern and Southern Lights.

Through mathematical calculations, Perlin noise, layered colour gradients and interactive animations, the program generates flowing aurora curtains across a night sky.

The project includes two visual variations:
- **Northern Lights:** Green, blue, turquoise and purple tones.
- **Southern Lights:** Pink, orange, yellow and purple tones.

Both versions use similar programming principles while exploring different visual atmospheres.

## Key Features

### 1. Flowing Aurora Curtains
Multiple overlapping light curtains move continuously across the sky. Perlin noise, sine calculations and time-based variables create gradual changes in their positions, heights and shapes, producing organic movement.

### 2. Colour Gradients and Transparency
RGB colour palettes and linear interpolation (`lerp()`) create smooth transitions between colours. Alpha transparency allows different layers to blend together, producing a luminous appearance.

### 3. Interactive Mouse Movement
Moving the mouse across the sky influences the aurora's movement. Smoothed cursor coordinates and a displacement grid allow the lights to respond gradually rather than shifting abruptly.

### 4. Mouse-Click Effects
Clicking the canvas creates a glowing ripple that travels through the aurora, adding another form of interaction.

### 5. Animated Environment
The scene includes twinkling stars, a moon, mountains, atmospheric effects and water reflections. These elements help establish depth and create a more immersive environment.

### 6. Water Reflections
The aurora is reflected across the water using graphics buffers and mathematical distortion. Sine-based movements create a subtle rippling effect.

## Technologies and Programming Concepts

**Software:** Processing with Python Mode

**Language:** Python (Processing Python Mode)

The project uses:
- Variables and data types
- Functions and reusable code
- `for` loops and conditional statements
- Lists and classes
- Perlin noise
- Sine and other mathematical calculations
- RGB colour values and alpha transparency
- Mouse input and interactive events
- Time-based animation
- Graphics buffers and rendering optimisation

## How to Run the Project

1. Install Processing and ensure **Python Mode** is available.
2. Download or clone this GitHub repository.
3. Open the Northern Lights or Southern Lights `.pyde` sketch in Processing.
4. Make sure Python Mode is selected.
5. Click the **Run** button.
6. Interact with the animation using your mouse.

### Mouse Controls

| Action | Effect |
|---|---|
| No mouse movement | Aurora continues flowing automatically |
| Move mouse across the sky | Gently influences and disperses the aurora |
| Click in the sky | Creates a glowing wave through the lights |
| Move mouse across the water | Creates interactive water ripples |

## Development Process

Aurora Currents was developed through experimentation, testing and iterative refinement.

Early development focused on creating colour gradients and simple wave shapes. These experiments were gradually expanded into layered aurora curtains with independently animated movement.

One challenge involved balancing visual complexity with performance. Increasing the number of layers and graphical effects sometimes reduced the frame rate.

Another challenge involved mouse responsiveness. Early interactions caused overly rapid or uneven movement. This was addressed by introducing smoothed mouse coordinates, gradually updated displacement values and more consistent animation timing.

The Southern Lights variation was developed by adapting the colour palettes while retaining the underlying animation structure.

## Future Improvements

Potential developments include:
- Additional customisable colour palettes
- User controls for animation speed and brightness
- More varied aurora movements
- Improved rendering performance
- Additional interactive environmental effects

## About the Project

**Project:** Aurora Currents  
**Project type:** Interactive digital artwork  
**Programming environment:** Processing Python Mode  
**Purpose:** University creative coding assignment

Aurora Currents demonstrates how mathematical programming, experimentation and interactive design can be combined to transform code into a dynamic visual artwork.
