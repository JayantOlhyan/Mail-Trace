# Cinematic Scrolling UX Revamp

## The Problem
Currently, the scenes in the product tour have perfectly sequential sticky phases (`min-h-[150vh]` with `-mt-[100vh]`). This means the moment one scene finishes its sticky phase, the next one begins. Because animations are tied to this exact progress window, scenes end up either awkwardly fading to black (leaving blank dead space) or scrolling out of the viewport abruptly. The scroll distance is also too short, making the transitions feel rushed.

## The Solution
We will implement an overlapping crossfade architecture typical of high-end Apple-style product pages:

1. **Slower Pacing**: Increase all scene heights from `150vh` to `250vh`. This extends the sticky scrolling duration, making animations feel smoother and more deliberate.
2. **Crossfade Overlap**: Adjust the negative margin stacking in `page.tsx` from `-100vh` to `-150vh`. This creates a mathematical `50vh` scroll overlap between adjacent scenes.
3. **Unified Animation Timing**: 
   - `progress: 0.0 -> 0.33`: Scene fades in (crossfading over the previous scene).
   - `progress: 0.33 -> 0.66`: Scene is fully visible; primary internal animations happen.
   - `progress: 0.66 -> 1.0`: Scene fades out (crossfading under the next scene).
4. **First/Last Scene Exceptions**: The first scene (`IncidentScene`) will start fully visible (no fade in). The last scene will not fade out.

## Action Plan
- Update `page.tsx` overlap to `-mt-[150vh]`.
- Update all 14 scene components to use `min-h-[250vh]`.
- Refactor the `opacity` logic in all scenes to follow the `0.33` fade in / `0.66` fade out rule to eliminate all blank dead zones.
