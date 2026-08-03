---
name: Decision-Grade Editorial
colors:
  surface: '#fbf9f8'
  surface-dim: '#dbd9d9'
  surface-bright: '#fbf9f8'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f5f3f3'
  surface-container: '#efeded'
  surface-container-high: '#eae8e7'
  surface-container-highest: '#e4e2e2'
  on-surface: '#1b1c1c'
  on-surface-variant: '#444748'
  inverse-surface: '#303030'
  inverse-on-surface: '#f2f0f0'
  outline: '#747878'
  outline-variant: '#c4c7c7'
  surface-tint: '#5f5e5e'
  primary: '#000000'
  on-primary: '#ffffff'
  primary-container: '#1c1b1b'
  on-primary-container: '#858383'
  inverse-primary: '#c8c6c5'
  secondary: '#5f5e5b'
  on-secondary: '#ffffff'
  secondary-container: '#e5e2dd'
  on-secondary-container: '#656461'
  tertiary: '#000000'
  on-tertiary: '#ffffff'
  tertiary-container: '#311300'
  on-tertiary-container: '#b97343'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#e5e2e1'
  primary-fixed-dim: '#c8c6c5'
  on-primary-fixed: '#1c1b1b'
  on-primary-fixed-variant: '#474746'
  secondary-fixed: '#e5e2dd'
  secondary-fixed-dim: '#c9c6c2'
  on-secondary-fixed: '#1c1c19'
  on-secondary-fixed-variant: '#474743'
  tertiary-fixed: '#ffdbc7'
  tertiary-fixed-dim: '#ffb688'
  on-tertiary-fixed: '#311300'
  on-tertiary-fixed-variant: '#6f380c'
  background: '#fbf9f8'
  on-background: '#1b1c1c'
  surface-variant: '#e4e2e2'
typography:
  display-lg:
    fontFamily: Playfair Display
    fontSize: 48px
    fontWeight: '700'
    lineHeight: 56px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Playfair Display
    fontSize: 32px
    fontWeight: '600'
    lineHeight: 40px
  headline-md:
    fontFamily: Playfair Display
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
  body-lg:
    fontFamily: Geist
    fontSize: 18px
    fontWeight: '400'
    lineHeight: 28px
  body-md:
    fontFamily: Geist
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  label-caps:
    fontFamily: Geist
    fontSize: 12px
    fontWeight: '600'
    lineHeight: 16px
    letterSpacing: 0.1em
  data-mono:
    fontFamily: Geist
    fontSize: 14px
    fontWeight: '500'
    lineHeight: 20px
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  base: 8px
  container-max: 1440px
  gutter: 32px
  margin-x: 64px
  stack-sm: 16px
  stack-md: 32px
  stack-lg: 64px
---

## Brand & Style

The design system is engineered for high-stakes real estate investment decisions. The brand personality is **Institutional, Boardroom-ready, and Authoritative**, designed to evoke a sense of inevitable success and calculated risk. It avoids the fleeting trends of consumer tech in favor of a **Luxury Developer Aesthetic** that feels permanent and grounded.

The visual direction is **Modern Minimalism** with a focus on **Editorial Sophistication**. It prioritizes heavy whitespace, exceptional typography, and a "High-Fidelity" finish that mirrors a premium print publication or a bespoke investment prospectus. Visual depth is achieved through tonal layering rather than translucency, ensuring the UI feels structural and reliable.

## Colors

The palette is anchored by **Deep Charcoal (#1A1A1A)** and **Warm Stone (#F5F2ED)**, creating a high-contrast yet organic foundation. 

- **Primary:** Deep Charcoal for text, primary navigation, and structural anchors.
- **Surface:** Warm Stone and its derivatives are used for container backgrounds and sectioning to provide a sophisticated alternative to pure white.
- **Accents:** **Copper/Amber (#C67E4D)** is used sparingly for highlights, CTA focus, or indicating "Executive Insight."
- **Semantic Logic:** Strategic decisions utilize **Deep Forest Green (#1E3A2B)** for positive growth indicators and **Restrained Muted Red (#8E2A2A)** for risk warnings, ensuring clarity without breaking the refined aesthetic.

## Typography

This design system uses a high-contrast typographic pairing to establish an editorial hierarchy.

- **Headlines:** **Playfair Display** provides an authoritative, literary feel. Use it for page titles, section headers, and key investment metrics.
- **Body & Interface:** **Geist** offers a clean, technical, and precise counterpoint. Its monospaced-adjacent clarity is perfect for the data-heavy nature of real estate analytics.
- **Data Display:** For financial figures and coordinates, use Geist with medium weight to ensure maximum legibility against the Warm Stone background.

## Layout & Spacing

The layout follows a **Fixed-Width Editorial Grid** on desktop (1440px), transitioning to a fluid container on smaller screens. 

- **Grid:** A 12-column grid with wide 32px gutters creates a sense of "breathing room" typical of luxury property brochures.
- **Margins:** Large horizontal margins (64px) focus the executive's attention on the core data.
- **Rhythm:** Vertical spacing is generous. Use `stack-lg` (64px) to separate major data modules (e.g., Map View vs. Financial Table) and `stack-md` (32px) for content within those modules.

## Elevation & Depth

Hierarchy is established through **Tonal Layering** and **Subtle Outlines** rather than traditional shadows.

- **Surfaces:** Use #F5F2ED for the base background. Secondary containers or cards should use a slightly lighter tint or a pure white with a 1px border in #E5E2DD.
- **Atmospherics:** Instead of glassmorphism, use soft photographic backgrounds (e.g., aerial shots of Bagaluru development) with a 40% Deep Charcoal overlay to provide context behind text-heavy modules.
- **Shadows:** If required for depth on floating elements (modals), use a single, extremely diffused shadow: `0 20px 40px rgba(26, 26, 26, 0.05)`.

## Shapes

The shape language is **Soft and Structural**. 

- **Radius:** A consistent 0.25rem (4px) radius is applied to cards and input fields. This provides just enough softening to feel modern without losing the "institutional" architectural edge.
- **Buttons:** Primary action buttons should maintain this slight radius. Large interactive zones (like map markers) may use the same rounding to maintain consistency.
- **Charts:** Bar charts and UI accents should use sharp 0px corners to maintain a "blueprint" and "data-accurate" aesthetic.

## Components

- **Buttons:** 
  - *Primary:* Solid Deep Charcoal background, White text.
  - *Secondary:* Copper/Amber border with Copper text.
  - *Decision:* GO buttons use Deep Forest Green; NO-GO buttons use Muted Red.
- **Tables:** Streamlit-compatible tables must feature "Sophisticated Minimal" styling: no vertical lines, 1px horizontal borders in #E5E2DD, and Geist SemiBold for column headers.
- **Cards:** White background, 1px Warm Stone border, 4px corner radius. No shadow.
- **Charts:** Use a palette of Copper, Charcoal, and Muted Sage. Lines should be thin (1.5px) and markers small and precise.
- **Status Chips:** Small, uppercase labels with a 10% opacity fill of their respective semantic color (e.g., 10% Green fill for a "STABLE" status).
- **Input Fields:** Bottom-border only or very light 1px outlines. Focus state should highlight the Copper accent.