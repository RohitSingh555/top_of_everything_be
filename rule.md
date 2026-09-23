# General Guidelines
You must always follow the workflows and style guidelines outlined below.

## 🎨 Coding & UI Style Guidelines
- **Coding Style**: Write clean, modular, and maintainable code. Use clear variable and function names. For frontend, use TypeScript, Next.js App Router, and Tailwind CSS. For backend, use FastAPI, SQLAlchemy, and Pydantic.
- **UI/UX Style (JustWatch Inspired Layout & Theme)**: 
  - **Colors**: Support Light and Dark themes. Primary accent is Manchester City Blue (`#6CABDD`).
  - **Design**: Clean, image-heavy layout with horizontal scrolling rows (like JustWatch), generous spacing, and modern typography (Inter font). Minimize icon usage in favor of text or imagery.
  - **Animations**: Implement smooth micro-animations and staggered fade-ups using Framer Motion to make the app feel alive and dynamic.

## ✅ Phase Completion Workflow
When you complete a phase or a prompt step outlined in `implementation_plan.md`, follow this strict workflow:

1. **Completion Prompt**: Announce completion to the user using this format: 
   > *"Phase [X] completed successfully. Verification steps passed. Ready to proceed to Phase [X+1]."*
2. **Update `implementation_plan.md`**: Modify `implementation_plan.md` to visually mark the phase and its corresponding prompts as DONE (e.g., changing `# Phase X` to `# [DONE] Phase X`).
3. **Update `done_tasks.md`**: Open and edit `done_tasks.md` to append the newly completed phase. Include a brief summary of what was actually built.
4. **Pre-Phase Check**: **ALWAYS** read `done_tasks.md` before starting work on any new phase. This ensures you understand the exact state of the project and don't overwrite or duplicate existing work.
