const STAGES = {
  'stage-1': {
    number: '01',
    id: 'stage-1',
    label: 'DISCOVERY',
    title: 'Market & User Research',
    weeks: 'Week 1–2',
    color: '#9c6ee8',
    icons: '🔍 🧠 📊',
    goal: 'Deeply understand the problem before building anything',
    tools: [
      { name: 'Perplexity', color: 'purple', use: 'AI-powered market & competitor research' },
      { name: 'Dovetail', color: 'teal', use: 'Tag & cluster user interview insights' },
      { name: 'Amplitude', color: 'blue', use: 'Analyze funnel drop-off & behavioral data' },
      { name: 'ChatGPT / Claude', color: 'green', use: 'Synthesize insights, draft PRD, define personas' },
    ],
    steps: [
      {
        step: 1,
        title: 'Define a Clear Business Goal',
        desc: 'Write one crisp sentence that captures the outcome.',
        example: '"Increase trial → paid conversion rate by 20%"',
        icon: '🎯',
      },
      {
        step: 2,
        title: 'Collect Current Data',
        desc: 'Use Amplitude to find where users drop off. Run Perplexity to benchmark competitors. Interview 5–10 real users.',
        icon: '📡',
      },
      {
        step: 3,
        title: 'Synthesize with AI',
        desc: 'Feed interview transcripts into Claude. Generate a draft PRD, map user personas, and size the opportunity.',
        icon: '🧠',
      },
    ],
    mistakes: [
      'Skipping discovery → building the wrong thing',
      'Only using quantitative data — mix with qual interviews',
      'Writing a PRD nobody reads — keep it to 1 page',
    ],
    output: {
      label: 'Required Output',
      items: ['PRD (1-page)', 'User Personas (2–3)', 'Success Metrics defined'],
    },
  },

  'stage-2': {
    number: '02',
    id: 'stage-2',
    label: 'IDEATION',
    title: 'Rapid Prototyping & Validation',
    weeks: 'Week 2–3',
    color: '#4caf50',
    icons: '💡 ✏️ 🧪',
    goal: 'Have a testable prototype BEFORE writing any production code',
    tools: [
      { name: 'v0.dev', color: 'green', use: 'Paste PRD → get working UI in seconds' },
      { name: 'Lovable / Bolt.new', color: 'teal', use: 'Rapid full-stack prototype generation' },
      { name: 'Figma AI', color: 'blue', use: 'Refine design, spacing, branding & design system' },
    ],
    steps: [
      {
        step: 1,
        title: 'Generate UI with AI',
        desc: 'Paste the PRD into v0.dev or Lovable. Iterate quickly with follow-up prompts — no code needed yet.',
        icon: '⚡',
      },
      {
        step: 2,
        title: 'Polish in Figma',
        desc: 'Refine spacing, typography, and brand consistency. Create or extend a design system for reuse.',
        icon: '🎨',
      },
      {
        step: 3,
        title: 'Test with Real Users',
        desc: 'Show the prototype to 3–5 real users. Record their feedback. Feed notes into Claude → update PRD.',
        icon: '🧪',
      },
    ],
    mistakes: [
      'Writing production code before validating the idea',
      'Testing only with teammates — get real users',
      'Ignoring negative feedback — it is the most valuable signal',
    ],
    output: {
      label: 'Required Output',
      items: ['Validated Prototype (clickable)', 'Updated PRD with user feedback', 'Tech Spec document'],
    },
  },

  'stage-3': {
    number: '03',
    id: 'stage-3',
    label: 'ENGINEERING',
    title: 'Development & AI-Pair Coding',
    weeks: 'Week 3–6',
    color: '#00bcd4',
    icons: '⚙️ 💻 🔧',
    goal: 'Build exactly what was validated — nothing more, nothing less',
    tools: [
      { name: 'Claude Code', color: 'blue', use: 'Scaffold structure, write features, review code' },
      { name: 'GitHub Copilot', color: 'teal', use: 'In-editor AI completions and PR review' },
      { name: 'Snyk / SonarQube', color: 'orange', use: 'Automated security & code quality scans' },
      { name: 'GitHub Actions', color: 'green', use: 'CI/CD: lint → test → scan → deploy staging' },
    ],
    steps: [
      {
        step: 1,
        title: 'AI-Scaffold the Project',
        desc: 'Use Claude Code to generate folder structure, naming conventions, and boilerplate from the tech spec.',
        icon: '🏗️',
      },
      {
        step: 2,
        title: 'Daily Dev Rhythm',
        desc: 'Morning: Claude Code writes features per spec.\nAfternoon: Review + Snyk/SonarQube scan.\nEOD: Push → CI/CD runs automatically.',
        icon: '🔄',
      },
      {
        step: 3,
        title: 'AI-Assisted Code Review',
        desc: 'Use Copilot to review every PR. Merge only when both AI and human approve. No --no-verify shortcuts.',
        icon: '🔍',
      },
    ],
    mistakes: [
      'Adding features beyond the validated spec (scope creep)',
      'Skipping code review to "save time" — always review',
      'Manual deploys — automate everything from day one',
    ],
    output: {
      label: 'Required Output',
      items: ['All features on staging', 'Test coverage >80%', 'Zero critical security issues'],
    },
  },

  'stage-4': {
    number: '04',
    id: 'stage-4',
    label: 'QA & TESTING',
    title: 'Comprehensive Automated Testing',
    weeks: 'Week 3–6 (parallel)',
    color: '#ff9800',
    icons: '✅ 🛡️ 🐛',
    goal: 'Zero bugs reach production',
    tools: [
      { name: 'Playwright', color: 'green', use: 'E2E browser automation for critical user journeys' },
      { name: 'Checkly', color: 'orange', use: 'API health checks & uptime monitoring post-deploy' },
      { name: 'Axe / a11y', color: 'teal', use: 'Automated accessibility scanning' },
      { name: 'Claude Code', color: 'blue', use: 'Generate unit & integration test cases from code' },
    ],
    steps: [
      {
        step: 1,
        title: 'Write Tests While Writing Code',
        desc: 'Use Claude Code to auto-generate unit tests. Write Playwright E2E tests for every happy path in parallel with feature dev.',
        icon: '✍️',
      },
      {
        step: 2,
        title: 'Three-Layer Test Structure',
        desc: 'tests/unit/ — each function in isolation\ntests/integration/ — API + DB interaction\ntests/e2e/ — full user journeys',
        icon: '🏛️',
        code: true,
      },
      {
        step: 3,
        title: 'Monitor After Deploy',
        desc: 'Configure Checkly health checks on all API endpoints. Set up Slack alerts for any failures or degraded responses.',
        icon: '📡',
      },
    ],
    mistakes: [
      'Writing tests after the feature is "done" — write them together',
      'Only happy-path tests — test edge cases and error states',
      'No monitoring post-deploy — bugs are silent without alerts',
    ],
    output: {
      label: 'Required Output',
      items: ['All tests green before launch', 'Test coverage >80%', 'Checkly monitors active'],
    },
  },

  'stage-5': {
    number: '05',
    id: 'stage-5',
    label: 'LAUNCH',
    title: 'Safe Deployment via Feature Flags',
    weeks: 'Week 6–7',
    color: '#ff5722',
    icons: '🚀 🚩 📡',
    goal: 'Launch safely — no production downtime',
    tools: [
      { name: 'LaunchDarkly', color: 'orange', use: 'Feature flags, canary releases, instant rollback' },
      { name: 'Datadog', color: 'purple', use: 'APM, error rate, latency, infra monitoring' },
      { name: 'PagerDuty', color: 'red', use: 'On-call alerting when error rate spikes' },
    ],
    steps: [
      {
        step: 1,
        title: 'Never Release to 100% Immediately',
        desc: 'Use LaunchDarkly to roll out in stages:\nCanary (internal) → 5% → 25% → 50% → 100%\nMonitor 24h between each step.',
        icon: '🎯',
        code: true,
      },
      {
        step: 2,
        title: 'Monitor from Minute One',
        desc: 'Watch Datadog dashboard: error rate, p99 latency, CPU, memory. Set an alert if error rate exceeds 1%.',
        icon: '📊',
      },
      {
        step: 3,
        title: 'Keep a Rollback Plan Ready',
        desc: 'Flip the feature flag OFF = instant rollback, no redeploy needed. Keep a hotfix branch ready for critical patches.',
        icon: '🛡️',
      },
    ],
    mistakes: [
      'Releasing 100% on day one — always use feature flags',
      'No monitoring dashboard open during launch — watch it live',
      'Rollback plan is just "hope it works" — define it explicitly',
    ],
    output: {
      label: 'Required Output',
      items: ['Successful launch, error rate <0.1%', 'Monitoring dashboards live', 'Rollback tested & confirmed'],
    },
  },

  'stage-6': {
    number: '06',
    id: 'stage-6',
    label: 'LEARN & ITERATE',
    title: 'Feedback Analysis & Optimization',
    weeks: 'Week 7+ (continuous)',
    color: '#e91e63',
    icons: '📈 🔄 🎯',
    goal: 'Use data to decide what to build next',
    tools: [
      { name: 'Mixpanel', color: 'purple', use: 'Track feature adoption & user behavior funnels' },
      { name: 'Amplitude', color: 'teal', use: 'Conversion analysis & cohort comparisons' },
      { name: 'Intercom AI', color: 'blue', use: 'Read support conversations, detect pain points' },
      { name: 'LaunchDarkly', color: 'orange', use: 'Run A/B experiments on live users' },
    ],
    steps: [
      {
        step: 1,
        title: 'Read Data Daily (Week 1 Post-Launch)',
        desc: 'Mixpanel: are users actually using the new feature?\nAmplitude: did conversion improve as expected?\nTrack the success metric defined in Stage 1.',
        icon: '📊',
        code: true,
      },
      {
        step: 2,
        title: 'Collect Qualitative Feedback',
        desc: 'Use Intercom AI to scan support conversations for recurring themes. Send an NPS survey after 7 days of usage.',
        icon: '💬',
      },
      {
        step: 3,
        title: 'Bi-Weekly Retrospective',
        desc: 'Feed data + feedback into Claude for synthesis. Decide: continue / pivot / abandon the feature. Update the backlog → restart at Stage 1.',
        icon: '🔄',
      },
    ],
    mistakes: [
      'No data = no learning — define metrics from Stage 1',
      'Only reading quantitative data — talk to users too',
      "Never killing features — cut what's not working",
    ],
    output: {
      label: 'Required Output',
      items: ['Decision: continue / pivot / abandon', 'Updated backlog for next iteration', 'Retrain AI model if custom (optional)'],
    },
  },
};
