export const pipelineBlueprint = [
  {
    _id: 'blueprint-step-1',
    step_number: 1,
    title: 'Generate Difficulty Categories',
    description: 'Map the requested topic into beginner, intermediate, and expert bands with skill descriptors.',
    prompt:
      'Design three learner tiers (Beginner, Intermediate, Expert) for the requested topic. For each tier, list the target skills, typical misconceptions, success criteria, and a concise rationale for why the tier builds toward the next level.',
    model: 'claude-sonnet-4',
    success: null,
    response_full: null,
    timestamp: null,
  },
  {
    _id: 'blueprint-step-2',
    step_number: 2,
    title: 'Generate Error Catalog',
    description: 'List likely conceptual mistakes and code patterns the weak model should miss.',
    prompt:
      'Produce a structured catalog of high-impact bugs for the topic. Include bug names, short descriptions, why the issue matters in real production code, and how likely a junior reviewer is to miss the bug compared with a senior reviewer.',
    model: 'claude-opus-4',
    success: null,
    response_full: null,
    timestamp: null,
  },
  {
    _id: 'blueprint-step-3',
    step_number: 3,
    title: 'Generate Adversarial Question',
    description: 'Create a buggy code snippet embedding multiple high-impact mistakes from the catalog.',
    prompt:
      'Write a runnable code snippet that intentionally bakes in several of the catalogued issues without calling them out. The snippet should feel realistic, compile, and hide the bugs behind plausible naming and control flow choices.',
    model: 'claude-opus-4',
    success: null,
    response_full: null,
    timestamp: null,
  },
  {
    _id: 'blueprint-step-4',
    step_number: 4,
    title: 'Test with Strong Model',
    description: 'Validate the adversarial question with a high-tier reviewer to confirm it catches all bugs.',
    prompt:
      'Have the strong reviewer critique the adversarial question in detail. Capture every embedded bug they find, the reasoning they used, and the anticipated production impact if the bug shipped unnoticed.',
    model: 'claude-sonnet-4',
    success: null,
    response_full: null,
    timestamp: null,
  },
  {
    _id: 'blueprint-step-5',
    step_number: 5,
    title: 'Test with Weak Model',
    description: 'Attempt the question with a weaker reviewer to ensure differentiation between skill levels.',
    prompt:
      'Run the weaker reviewer on the adversarial code. Record their answer verbatim, highlight the bugs they miss, and explain why each miss demonstrates weaker debugging or domain reasoning skills.',
    model: 'claude-haiku-4',
    success: null,
    response_full: null,
    timestamp: null,
  },
  {
    _id: 'blueprint-step-6',
    step_number: 6,
    title: 'Judge Model Differentiation',
    description: 'Compare strong versus weak results to confirm the question differentiates reviewer skill.',
    prompt:
      'Summarize how the strong and weak reviewers performed. Call out overlap, unique findings, and provide a confidence score explaining whether the assessment truly differentiates reviewer skill.',
    model: 'claude-opus-4',
    success: null,
    response_full: null,
    timestamp: null,
  },
  {
    _id: 'blueprint-step-7',
    step_number: 7,
    title: 'Create Student Assessment',
    description: 'Package the question, errors, and metadata for gameplay inside the student experience.',
    prompt:
      'Produce the final assessment JSON with clickable error spans, topic metadata, difficulty, weak model failure counts, and a short summary teachers can read before assigning the assessment.',
    model: 'claude-opus-4',
    success: null,
    response_full: null,
    timestamp: null,
  },
];

export const pipelineDemoCopy =
  'Two domain-agnostic assessments: (1) Quadratic Equations - Math optimization with 3 errors, (2) Executive Assistant - Meeting coordination plan with 2 errors. Use tabs to switch between assessments.';
