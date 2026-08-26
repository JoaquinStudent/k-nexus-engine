---
name: KNexus Engine
colors:
  surface: '#fdf8ff'
  surface-dim: '#ddd5fd'
  surface-bright: '#fdf8ff'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f7f1ff'
  surface-container: '#f1ebff'
  surface-container-high: '#ebe4ff'
  surface-container-highest: '#e6deff'
  on-surface: '#1c1735'
  on-surface-variant: '#48454e'
  inverse-surface: '#312c4b'
  inverse-on-surface: '#f4eeff'
  outline: '#79757f'
  outline-variant: '#c9c4d0'
  surface-tint: '#605889'
  primary: '#0f0535'
  on-primary: '#ffffff'
  primary-container: '#251d4b'
  on-primary-container: '#8e85b9'
  inverse-primary: '#cabff8'
  secondary: '#5f53a2'
  on-secondary: '#ffffff'
  secondary-container: '#b5a8ff'
  on-secondary-container: '#463987'
  tertiary: '#000f21'
  on-tertiary: '#ffffff'
  tertiary-container: '#0f253c'
  on-tertiary-container: '#788da8'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#e6deff'
  primary-fixed-dim: '#cabff8'
  on-primary-fixed: '#1c1442'
  on-primary-fixed-variant: '#484070'
  secondary-fixed: '#e5deff'
  secondary-fixed-dim: '#c9bfff'
  on-secondary-fixed: '#1b065c'
  on-secondary-fixed-variant: '#473b89'
  tertiary-fixed: '#d2e4ff'
  tertiary-fixed-dim: '#b3c8e5'
  on-tertiary-fixed: '#051d33'
  on-tertiary-fixed-variant: '#344860'
  background: '#fdf8ff'
  on-background: '#1c1735'
  surface-variant: '#e6deff'
typography:
  headline-lg:
    fontFamily: Montserrat
    fontSize: 32px
    fontWeight: '700'
    lineHeight: 40px
    letterSpacing: -0.02em
  headline-md:
    fontFamily: Montserrat
    fontSize: 24px
    fontWeight: '700'
    lineHeight: 32px
    letterSpacing: -0.01em
  headline-sm:
    fontFamily: Montserrat
    fontSize: 18px
    fontWeight: '600'
    lineHeight: 24px
    letterSpacing: -0.01em
  body-lg:
    fontFamily: Montserrat
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 26px
    letterSpacing: '0'
  body-md:
    fontFamily: Montserrat
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 22px
    letterSpacing: '0'
  label-md:
    fontFamily: Montserrat
    fontSize: 12px
    fontWeight: '500'
    lineHeight: 16px
    letterSpacing: 0.02em
  caption:
    fontFamily: Montserrat
    fontSize: 11px
    fontWeight: '500'
    lineHeight: 14px
    letterSpacing: 0.03em
  headline-lg-mobile:
    fontFamily: Montserrat
    fontSize: 26px
    fontWeight: '700'
    lineHeight: 32px
    letterSpacing: -0.02em
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  unit: 8px
  xs: 4px
  sm: 8px
  md: 16px
  lg: 24px
  xl: 32px
  gutter: 24px
  margin: 32px
---

## Brand & Style

The design system is engineered for an academic knowledge-connection tool where precision and clarity are paramount. The brand personality is authoritative yet unobtrusive, functioning as a sophisticated "engine" for intellectual discovery. 

The aesthetic is a refined **Minimalist-Professional** style. It utilizes a high-contrast, flat architectural approach to maintain data density without inducing cognitive overload. The UI prioritizes structural integrity over decorative flair, employing a "Paper-on-Platform" philosophy where white surfaces sit cleanly atop a cool-toned application background. Every element is aligned to a rigorous 8px grid to evoke a sense of mathematical order and reliability.

## Colors

The palette is anchored by deep indigos and cool neutrals to establish trust and focus. 

- **Primary & Interactive:** Use the Indigo (`#251D4B`) for primary actions and global navigation. Links and icons utilize the lighter Indigo (`#5B4F9E`) to differentiate interactive text from static content.
- **Surface Strategy:** The app background uses a subtle cool grey (`#F7F8FC`) to create a distinct container for white cards (`#FFFFFF`).
- **Data Accents:** Soft Blue, Lavender, and Orchid are reserved strictly for categorization (chips, badges, and graph nodes). They should never be used for primary UI actions.
- **Semantic Feedback:** High, Medium, and Low indicators use desaturated but distinct tones to signal status without disrupting the scholarly atmosphere.

## Typography

This design system uses **Montserrat** exclusively to maintain a modern, geometric clarity across all data types. 

- **Headings:** Use Bold (700) or SemiBold (600) with tight letter-spacing to create a strong visual "anchor" for sections. 
- **Body Text:** Use Regular (400) for long-form reading to ensure breathability. 
- **Data & Metadata:** Use Medium (500) for captions and labels to provide enough visual weight at smaller scales.
- **Casing:** Apply sentence case across all headers, buttons, and labels to maintain a professional, editorial tone.

## Layout & Spacing

The system operates on an **8px spacing grid** to ensure consistency in a data-heavy environment.

- **Layout Model:** Use a 12-column fluid grid for desktop views with 24px gutters. For sidebars and data panels, use fixed widths (e.g., 280px for navigation) to preserve readability of technical information.
- **Responsive Behavior:** 
  - **Desktop:** Wide margins (32px+) and multi-pane layouts.
  - **Tablet:** 8-column grid, margins reduce to 24px.
  - **Mobile:** 4-column grid, margins reduce to 16px. Typography scales down specifically for primary headers.

## Elevation & Depth

To maintain a "serious and flat" aesthetic, this design system avoids traditional drop shadows for standard UI elements. 

- **Tonal Layering:** Depth is conveyed through color contrast between the background (`#F7F8FC`) and surfaces (`#FFFFFF`).
- **Borders:** All cards and containers use a crisp 1px border (`#E4E7F0`). 
- **Modals & Overlays:** Shadows are reserved exclusively for temporary overlays (modals, dropdowns, and tooltips). These should be "Soft Shadows": highly diffused, low opacity (10-15%), and slightly tinted with the Primary color to maintain a cohesive atmosphere.

## Shapes

The shape language is structured and approachable.

- **Standard Elements:** Buttons and input fields use a 0.5rem (8px) radius.
- **Large Containers:** Cards and primary surfaces use a specific **12px radius** as requested, providing a distinct soften-edge compared to smaller UI components.
- **Chips/Tags:** Use a "Pill" (full radius) style to distinguish them as discrete meta-objects from the rectangular functional elements.

## Components

- **Buttons:** Primary buttons are solid `#251D4B` with white text. Hover state shifts to `#3A2E6E`. No gradients. Tertiary buttons are text-only using the Link color.
- **Chips & Tags:** Small, pill-shaped, and use the lighter accent palette. 
    - *Evidence Tag:* Orchid (`#CCA9E8`) background with deep orchid text.
    - *AI Tag:* Muted Indigo (`#8A86A6`) background with white text.
- **Input Fields:** 1px border (`#E4E7F0`), white background. On focus, the border thickens to 2px using the Primary color.
- **Cards:** White background, 1px border, 12px corner radius. No shadow.
- **Lists:** Use subtle 1px dividers between items. Left-align text with 16px horizontal padding.
- **Checkboxes/Radios:** Use Primary Indigo for the active state. Maintain a square profile for checkboxes and circular for radios to ensure standard affordances.
- **Knowledge Nodes:** Circular elements representing data points should use the accent palette based on their category, with a 1px border of a darker shade of the same hue.