# Copilot Design — Executive Guide

## Intent

A **quiet product guide** for executives — not a sci-fi HUD.

## Explicitly avoided (credibility)

- Rotating 3D / holograms / Iron Man HUD  
- Floating FAB pulse, radar sweeps, waveforms, particle fields  
- Neon cyberpunk chrome  
- Continuous or ambient audio  

## Surfaces

1. Sidebar — Open / Close Copilot  
2. On-page panel when open — questions, personas, answers  
3. Standard Streamlit spinner while answering  

## Behaviour

- Page-aware rule guide (`copilot_guide_service`)  
- Personas: Default · CEO · Sales Head · Simple  
- Optional one-shot sound (off by default; never looping)  
- Does **not** issue a second GO / HOLD / NO-GO  

## Future

Grounded LLM with citations; feedback log — still no decorative theater.
