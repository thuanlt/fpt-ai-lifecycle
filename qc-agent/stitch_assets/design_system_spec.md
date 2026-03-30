# Design System Specification: The Kinetic Intelligence Framework

## 1. Overview & Creative North Star: "The Synthetic Architect"
This design system moves away from the static, "flat" dashboard aesthetic of the last decade. Our Creative North Star is **The Synthetic Architect**. It envisions the interface not as a tool, but as a living, breathing blueprint of an automated ecosystem. 

To achieve this, we reject the rigid, high-contrast grids of traditional enterprise software. Instead, we embrace **Intentional Asymmetry** and **Tonal Depth**. By layering surfaces of varying dark values and utilizing "optical glows" rather than hard lines, we create a workspace that feels high-density yet calm—essential for the high-cognitive load of SDET and Multi-Agent AI monitoring.

---

## 2. Colors: The Depth of the Machine
The palette is rooted in the `surface` (#131313), designed to recede and allow data to lead.

### The "No-Line" Rule
**Explicit Instruction:** Do not use 1px solid borders to section high-level layout areas. Separation of concerns must be achieved through background shifts. Use `surface-container-low` for secondary sidebars and `surface-container-highest` for active workspaces. 

### Surface Hierarchy & Nesting
Treat the UI as a physical stack of semi-opaque materials.
*   **Base:** `surface` (#131313) – The desk.
*   **Sections:** `surface-container-low` (#1c1b1b) – The drawing board.
*   **Modules:** `surface-container-high` (#2a2a2a) – The active papers.
*   **Interactive Focus:** `surface-container-highest` (#353534) – The highlighted document.

### The "Glass & Gradient" Rule
Floating panels (Agent status popovers, Command Palettes) must utilize `surface-variant` with a `backdrop-blur` of 12px and 60% opacity. For primary actions and AI "thinking" states, use a subtle linear gradient from `primary` (#c3f5ff) to `primary-container` (#00e5ff) at a 135-degree angle to provide a "liquid neon" feel.

---

## 3. Typography: Editorial Technicality
We pair the Swiss-style precision of **Inter** with the utilitarian soul of **JetBrains Mono**.

*   **Display & Headlines:** Use `display-sm` to `headline-lg` (Space Grotesk) for system-level stats. These should be tracked tightly (-0.02em) to feel authoritative and architectural.
*   **Interface UI:** Use `body-md` (Inter) for most interactions. It is neutral and stays out of the way of the data.
*   **The Execution Layer:** All logs, code editors, and Agent "inner monologue" text must use `label-md` (JetBrains Mono). This differentiates *human-readable* UI from *machine-generated* output.

---

## 4. Elevation & Depth: Tonal Layering
In a high-density AI environment, traditional shadows feel "muddy." We use light, not just darkness, to define space.

*   **The Layering Principle:** Instead of a shadow, place a `surface-container-lowest` card on top of a `surface-container-low` background. The slight shift in hex value provides a cleaner, more modern lift.
*   **Ambient Shadows:** For floating Agent nodes, use a shadow color derived from `surface-tint` (#00daf3) at 6% opacity with a 32px blur. This mimics the glow of a monitor in a dark room.
*   **The Ghost Border:** For accessibility in cards, use `outline-variant` (#3b494c) at **15% opacity**. It should be felt, not seen.

---

## 5. Components: Precision Primitives

### Cards & Modules (The Agent Container)
*   **Style:** No internal dividers. Use `spacing-6` (1.3rem) to separate header from body.
*   **Indicator:** Active Agents feature a 4px `primary-fixed-dim` outer glow.
*   **Loading States:** For long-running AI cycles (30s-180s), use a skeleton state with a slow "breathing" opacity transition (0.3 to 0.7) using the `primary-container` color.

### Buttons & Interaction
*   **Primary:** Solid `primary-container` (#00e5ff) with `on-primary` text. No border.
*   **Secondary:** Ghost style. `outline-variant` at 20% opacity background, `primary` text.
*   **Agent Action Chips:** Small, pill-shaped (`rounded-full`). Use `tertiary-container` (#82e780) for "DONE" and `error_container` (#93000a) for "FAILED".

### Input Fields & Terminal Editors
*   **The Code Block:** Background must be `surface-container-lowest`. Use `primary-fixed` for the cursor caret. 
*   **Inputs:** Minimalist. Only a bottom border of 1px `outline-variant` until focused, at which point it transitions to a 2px `primary` underline with a soft 4px glow.

### System Status (The Top Bar)
*   **Vector DB Connectivity:** A small `tertiary` (#b6ffae) dot for "Live", pulsed with a 2s ease-in-out.
*   **Agent Status Bar:** A horizontal stack of 4x4px squares, color-coded by the last 10 execution results (Green/Amber/Red).

---

## 6. Do's and Don'ts

### Do
*   **Use Asymmetry:** Place Agent logs on a slightly wider right column and status controls in a narrower left column to break the "standard dashboard" feel.
*   **Embrace Density:** SDETs need data. Use `spacing-2` and `spacing-3` for tight information clusters.
*   **Layer with Color:** Use `surface-bright` for hover states on dark buttons to create a "lift" effect.

### Don't
*   **Don't use 100% White:** Never use #FFFFFF. Use `on-surface` (#e5e2e1) to prevent eye strain in dark mode.
*   **Don't use Dividers:** Avoid horizontal rules (`<hr>`). Use a `0.4rem` gap of `surface-container-lowest` if visual separation is required.
*   **Don't use Sharp Corners:** Follow the `md` (0.375rem) or `lg` (0.5rem) roundedness scale to keep the "Synthetic" feel organic rather than brutalist.

---

## 7. Interaction Micro-copy & Tone
The system should speak with **Technical Authority**. 
*   Instead of "Loading...", use `[SYSTEM]: INITIALIZING NEURAL AGENT...`
*   Instead of "Error", use `[STATUS]: TRACE_EXCEPTION_04X`
*   All status updates should be timestamped using `label-sm` in `outline` color for a forensic, professional feel.
