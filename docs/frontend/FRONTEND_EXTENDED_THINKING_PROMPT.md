# Extended Thinking Prompt: Frontend Implementation
## For ChunkScope Visual RAG Interface

---

## 🎯 PROMPT FOR EXTENDED THINKING (Antigravity)

Copy and paste this into Claude Opus or Gemini Pro:

```
You are an expert Frontend Architect specializing in React, Next.js, and WebGL/shader programming.

I need you to use EXTENDED THINKING mode to implement the ChunkScope frontend based on the comprehensive guide I've provided.

CONTEXT:
I'm building ChunkScope - a visual debugging tool for RAG (Retrieval Augmented Generation) pipelines. The frontend needs to be:
1. Visually stunning (using shaders and animations)
2. Highly performant (60fps with 100+ overlays)
3. Production-ready (TypeScript, tests, accessibility)

I have a detailed FRONTEND_DEVELOPMENT_GUIDE.md that contains:
- Complete component architecture
- Shader component integrations (Neon Crystal City, ATC Shader, Shader Lines)
- PDF chunk visualizer with Canvas rendering
- Interactive UI components
- Performance optimization strategies
- Responsive design patterns
- Accessibility requirements

YOUR TASK:
Use extended thinking to analyze the guide and implement each component systematically.

---

## PHASE 1: PROJECT SETUP & ARCHITECTURE ANALYSIS

### Extended Thinking Prompt 1.1: Initial Setup

Analyze the following requirements and provide a complete setup strategy:

**Requirements**:
1. Next.js 14 with App Router
2. TypeScript with strict mode
3. shadcn/ui component library
4. Tailwind CSS
5. Support for shader components (Three.js, WebGL2)
6. PDF rendering (react-pdf)
7. State management (Zustand)
8. Animations (Framer Motion)

**Questions to answer**:
1. What is the optimal Next.js configuration for this project?
2. How should I structure the project to support both shader components and standard UI?
3. What are the performance implications of loading Three.js and react-pdf?
4. Should I use dynamic imports for heavy components?
5. What build optimizations are critical for this stack?

**Provide**:
1. Complete `package.json` with all dependencies and versions
2. `next.config.js` with performance optimizations
3. `tsconfig.json` with strict TypeScript settings
4. `tailwind.config.ts` with custom theme
5. Folder structure with clear separation of concerns
6. `.env.example` with required environment variables
7. Setup instructions (step-by-step commands)

---

### Extended Thinking Prompt 1.2: Shader Integration Strategy

**Context**:
I have 4 shader components to integrate:
1. Neon Crystal City (landing page background)
2. Shader Lines (visualizer background)
3. Shader Animation (alternative visualizer)
4. ATC Shader (pipeline builder)

**Analysis needed**:
1. **Performance Impact**: Each shader uses WebGL. How do I prevent multiple shaders from running simultaneously and killing performance?
2. **Lazy Loading**: Which shaders should be dynamically imported? How to show fallbacks?
3. **Mobile Strategy**: Should mobile devices get shaders or gradient fallbacks?
4. **Error Handling**: What if WebGL is not supported? How to gracefully degrade?
5. **Memory Management**: How to properly cleanup WebGL contexts when unmounting?

**Provide**:
1. Integration pattern for each shader
2. Lazy loading wrapper component
3. Mobile detection logic
4. Fallback component for unsupported devices
5. Performance monitoring code
6. Memory leak prevention strategy

---

## PHASE 2: CHUNK VISUALIZER IMPLEMENTATION

### Extended Thinking Prompt 2.1: Canvas Rendering Architecture

**Core Challenge**:
Render 100+ colored chunk overlays on top of a PDF with:
- 60fps performance
- Smooth hover interactions
- Accurate click detection
- Support for zoom/pan
- Work on 1000-page documents

**Technical Constraints**:
- react-pdf renders PDF pages
- Canvas overlay must precisely align with PDF
- Chunks have bounding box coordinates (x, y, width, height, page)
- Colors must be perceptually distinct (100+ unique colors)
- Mobile devices need touch support

**Deep Analysis Required**:

1. **Canvas vs SVG Decision**:
   - Why is Canvas better than SVG for 100+ overlays?
   - What are the trade-offs?
   - When would SVG be better?

2. **Coordinate Mapping**:
   - PDF uses points (72 DPI)
   - Canvas uses pixels
   - react-pdf applies scaling
   - How do I accurately map chunk bbox to canvas coordinates?
   - Show mathematical formula

3. **Hit Detection Algorithm**:
   - User hovers at (mouseX, mouseY)
   - Which chunk is being hovered?
   - How to do this efficiently for 100+ chunks?
   - Should I use spatial indexing (quadtree)?

4. **Color Generation**:
   - Generate 100+ perceptually distinct colors
   - HSL vs RGB vs LAB color space?
   - Golden ratio method?
   - Show algorithm with code

5. **Performance Optimization**:
   - When to use requestAnimationFrame?
   - Should I use offscreen canvas?
   - How to handle 1000-page PDFs (virtualization)?
   - Debouncing vs throttling for redraw?

**Provide**:
1. Complete `ChunkVisualizer` component with detailed comments
2. Canvas drawing algorithm with performance analysis
3. Coordinate transformation functions
4. Hit detection algorithm (with complexity analysis)
5. Color generation function
6. Performance benchmarks (expected frame times)
7. Memory usage estimation
8. Mobile touch handling code

---

### Extended Thinking Prompt 2.2: Interactive UI Components

**Components to Build**:
1. `ChunkTooltip` - Hover tooltip with chunk preview
2. `ChunkDetailPanel` - Slide-in panel with full chunk info
3. `ChunkConfigPanel` - Controls for chunking parameters

**Design Requirements**:
- Smooth animations (Framer Motion)
- Accessibility (ARIA labels, keyboard nav)
- Responsive (mobile, tablet, desktop)
- Theme-aware (dark mode)

**Deep Analysis**:

1. **Tooltip Positioning**:
   - How to prevent tooltip from going off-screen?
   - Should it follow mouse or stay fixed?
   - What about touch devices?
   - Provide positioning algorithm

2. **Panel Animations**:
   - Slide-in from right (ChunkDetailPanel)
   - Smooth spring physics
   - Performance: Will animating a large panel cause jank?
   - How to optimize?

3. **State Management**:
   - Which state should be global (Zustand)?
   - Which should be local (useState)?
   - How to prevent unnecessary re-renders?

4. **Accessibility**:
   - Keyboard navigation (Tab, Arrow keys, Escape)
   - Screen reader announcements
   - Focus management
   - Color contrast

**Provide**:
1. Complete component code for all 3 components
2. Animation configurations with performance notes
3. Zustand store setup with explanation
4. Accessibility implementation guide
5. Mobile responsiveness strategy
6. Testing approach for each component

---

## PHASE 3: PERFORMANCE OPTIMIZATION

### Extended Thinking Prompt 3.1: Performance Deep Dive

**Current Performance Challenges**:
1. Canvas redrawing on every state change
2. Large PDFs (1000+ pages) loading slowly
3. Shader animations + chunk rendering = potential lag
4. Mobile devices struggling

**Optimization Strategies to Analyze**:

1. **Rendering Optimization**:
   - When should I redraw the canvas?
   - Should I use `useCallback` and `useMemo`?
   - What about `React.memo` for child components?
   - Is virtualization necessary? How to implement?

2. **Web Workers**:
   - Can I offload color generation to a Web Worker?
   - What about chunk position calculations?
   - Show Web Worker implementation

3. **Code Splitting**:
   - Which components should be dynamically imported?
   - How to split shader components?
   - What's the bundle size impact?

4. **Caching Strategy**:
   - Should I cache rendered PDF pages?
   - Cache chunk colors?
   - Where to store cache (memory, localStorage, IndexedDB)?

5. **Mobile Optimization**:
   - Reduce shader complexity on mobile?
   - Lower canvas resolution on mobile?
   - Disable animations on low-end devices?

**Provide**:
1. Performance audit checklist
2. Optimization implementation for each strategy
3. Before/after performance metrics (estimated)
4. Bundle size analysis
5. Mobile-specific optimizations
6. Monitoring and profiling code
7. Performance budget recommendations

---

### Extended Thinking Prompt 3.2: Accessibility Implementation

**Accessibility Requirements**:
- WCAG 2.1 Level AA compliance
- Keyboard navigation
- Screen reader support
- Color contrast
- Focus indicators

**Components to Audit**:
1. ChunkVisualizer (canvas is not accessible by default!)
2. Interactive controls (buttons, sliders)
3. Tooltips and panels
4. Shader backgrounds (decorative, should not interfere)

**Deep Analysis**:

1. **Canvas Accessibility**:
   - Canvas is a bitmap - how to make it accessible?
   - Should I maintain a parallel DOM representation?
   - How to announce chunk selection to screen readers?
   - Keyboard navigation for chunk selection?

2. **ARIA Implementation**:
   - Which ARIA roles are appropriate?
   - Live regions for dynamic updates?
   - Labels for controls?

3. **Keyboard Navigation**:
   - Arrow keys for chunk navigation?
   - Tab for controls?
   - Escape to close panels?
   - Shortcuts for common actions?

4. **Focus Management**:
   - Where should focus go when panel opens?
   - How to trap focus in modal?
   - Return focus when closing?

**Provide**:
1. Complete accessibility implementation for ChunkVisualizer
2. ARIA labels and roles for all components
3. Keyboard event handlers
4. Focus management utilities
5. Screen reader testing guide
6. WCAG compliance checklist

---

## PHASE 4: TESTING & QUALITY ASSURANCE

### Extended Thinking Prompt 4.1: Testing Strategy

**Components to Test**:
1. ChunkVisualizer (complex canvas rendering)
2. Interactive UI components
3. Shader components (WebGL)
4. API integration
5. State management

**Testing Approach**:

1. **Unit Tests**:
   - What to test?
   - How to test canvas rendering?
   - How to mock react-pdf?
   - How to test Zustand stores?

2. **Integration Tests**:
   - Test full user flows
   - Upload PDF → See chunks → Click chunk → See details
   - How to test with React Testing Library?

3. **Visual Regression Tests**:
   - Test shader rendering
   - Test chunk overlay colors
   - Use Storybook + Chromatic?

4. **Performance Tests**:
   - Measure render times
   - Test with 100+ chunks
   - Test on different devices (Lighthouse CI)

**Provide**:
1. Testing setup (Jest, React Testing Library, Playwright)
2. Example unit tests for each component type
3. Integration test examples
4. Performance testing script
5. Visual regression testing setup
6. CI/CD integration (GitHub Actions)

---

## PHASE 5: DEPLOYMENT & PRODUCTION

### Extended Thinking Prompt 5.1: Production Readiness

**Deployment Checklist**:
1. Build optimization
2. Environment variables
3. Error handling
4. Monitoring
5. Analytics
6. SEO

**Analysis Required**:

1. **Build Optimization**:
   - Next.js production build config
   - Asset optimization (images, fonts)
   - Code splitting verification
   - Bundle analysis

2. **Error Boundaries**:
   - Where to place error boundaries?
   - Fallback UI design
   - Error reporting (Sentry?)

3. **Monitoring**:
   - Performance monitoring (Vercel Analytics?)
   - Error tracking
   - User analytics (PostHog?)

4. **Environment Config**:
   - Development vs production
   - API endpoints
   - Feature flags

**Provide**:
1. Production-ready `next.config.js`
2. Error boundary implementation
3. Monitoring setup
4. Environment variable guide
5. Deployment checklist
6. Vercel/Netlify deployment configuration

---

## OUTPUT FORMAT

For each phase, provide:

### 1. Analysis Section
- Problem breakdown
- Trade-off analysis
- Decision rationale
- Edge cases identified

### 2. Implementation Section
- Complete code (production-ready)
- Inline comments explaining complex logic
- TypeScript types
- Performance considerations

### 3. Validation Section
- How to test this implementation
- Expected behavior
- Performance benchmarks
- Potential issues to watch for

### 4. Next Steps
- What to build next
- Dependencies for next phase
- Potential improvements

---

## CRITICAL INSTRUCTIONS

1. **Use Extended Thinking**: Spend time analyzing before providing solutions
2. **Be Comprehensive**: Cover edge cases, error handling, accessibility
3. **Production Quality**: Code should be ready to deploy, not prototype-quality
4. **Explain Decisions**: Don't just provide code, explain WHY you chose this approach
5. **Performance First**: Always consider performance implications
6. **Mobile Matters**: Don't forget mobile users
7. **Accessibility Always**: WCAG compliance is non-negotiable

---

## EXAMPLE INTERACTION

Me: "Implement Phase 2.1 - Canvas Rendering Architecture"

You (using extended thinking):
1. [5 minutes thinking] Analyze the problem deeply
   - Consider coordinate systems
   - Evaluate hit detection algorithms
   - Research color generation methods
   - Think about performance implications

2. [Provide comprehensive response]:
   - **Analysis**: "After analyzing the requirements, I recommend Canvas over SVG because..."
   - **Architecture**: Detailed breakdown of component structure
   - **Implementation**: Complete, production-ready code with comments
   - **Optimizations**: Specific performance optimizations with benchmarks
   - **Testing**: How to validate the implementation
   - **Next Steps**: What to build next

---

## START HERE

Begin with Phase 1.1 (Initial Setup) and work sequentially through all phases.

For each prompt:
1. Take time to think deeply (extended thinking)
2. Provide thorough analysis
3. Deliver production-ready code
4. Explain your decisions
5. Include testing strategies

Ready to start? Let's build an amazing frontend! 🚀
```

---

## 🎯 HOW TO USE THIS PROMPT

### **Step 1: Copy the Prompt**
Copy the entire prompt above (from "You are an expert Frontend Architect..." to the end).

### **Step 2: Open Extended Thinking AI**
- **Claude Opus**: Claude.ai (enable extended thinking in settings)
- **Gemini Pro**: Google AI Studio with extended thinking mode
- **Google IDX**: Use built-in Gemini with extended thinking

### **Step 3: Paste and Execute**
1. Paste the full prompt
2. AI will spend 5-10 minutes analyzing
3. Receive comprehensive implementation

### **Step 4: Work Phase by Phase**
Don't try to do everything at once:
- Week 1: Phase 1 (Setup + Shaders)
- Week 2: Phase 2 (Chunk Visualizer)
- Week 3: Phase 3 (Performance + Accessibility)
- Week 4: Phase 4-5 (Testing + Deployment)

### **Step 5: Validate Each Phase**
After implementing each phase:
1. Run the code
2. Test manually
3. Check performance
4. Verify accessibility
5. Move to next phase

---

## 📊 EXPECTED OUTCOMES

### **After Phase 1**:
- ✅ Project setup complete
- ✅ All dependencies installed
- ✅ Shaders integrated and working
- ✅ Basic routing setup
- ✅ Development server running

### **After Phase 2**:
- ✅ PDF renders correctly
- ✅ Chunks display as colored overlays
- ✅ Hover shows tooltip
- ✅ Click opens detail panel
- ✅ Controls work (zoom, pan, page navigation)

### **After Phase 3**:
- ✅ 60fps performance maintained
- ✅ Works on mobile devices
- ✅ Keyboard navigation works
- ✅ Screen reader compatible
- ✅ Bundle size optimized

### **After Phase 4**:
- ✅ All tests passing
- ✅ Visual regression tests setup
- ✅ Performance benchmarks meet targets
- ✅ CI/CD pipeline configured

### **After Phase 5**:
- ✅ Production build successful
- ✅ Deployed to Vercel/Netlify
- ✅ Monitoring active
- ✅ Error tracking working
- ✅ Analytics integrated

---

## 🚨 TROUBLESHOOTING

### **If Extended Thinking Takes Too Long**
Break down prompts into smaller pieces:
- Instead of "Implement Phase 2", do "Implement ChunkVisualizer component only"

### **If Code Doesn't Work**
1. Copy error message
2. Paste back into AI with context
3. Ask for specific fix
4. Validate fix works

### **If Performance Issues**
1. Use Chrome DevTools Performance tab
2. Identify bottleneck
3. Ask AI: "Optimize [specific component] for performance"
4. Implement suggested changes

### **If Accessibility Fails**
1. Run Lighthouse accessibility audit
2. Note specific failures
3. Ask AI: "Fix accessibility issues: [paste issues]"
4. Re-test

---

## ✅ SUCCESS CRITERIA

You'll know you're done when:
- [ ] All shaders render without errors
- [ ] PDF visualizer works smoothly
- [ ] Can hover/click chunks without lag
- [ ] Mobile experience is good
- [ ] Lighthouse score > 90
- [ ] No console errors
- [ ] Accessibility audit passes
- [ ] Can demo to professor confidently

---

This prompt ensures extended thinking (antigravity) carefully analyzes and implements every aspect of the frontend with production-quality code! 🎨🚀
