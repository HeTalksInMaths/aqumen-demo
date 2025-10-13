import React, { useEffect, useMemo, useRef, useState } from "react";
import { parseQuestion } from "../utils/parseQuestion.js";

const MAX_CLICKS = 3;
const isWhitespaceOnly = (s) => /^\s*$/.test(s);

/** Split a non-error text chunk into runs of whitespace and non-whitespace */
function splitRuns(text) {
  const runs = [];
  let i = 0;
  while (i < text.length) {
    const isWS = /\s/.test(text[i]);
    let j = i + 1;
    while (j < text.length && /\s/.test(text[j]) === isWS) j++;
    runs.push({ text: text.slice(i, j), isWhitespace: isWS });
    i = j;
  }
  return runs;
}

export default function QuestionPlayground({
  currentQuestion,
  progressPercent = 0,
  difficultyClass = "",
  onSubmit = () => {},
  onNext = () => {},
  hasMoreQuestions = false,
}) {
  const codeRef = useRef(null);
  const [clicks, setClicks] = useState([]); // {x,y,line}
  const [done, setDone] = useState(false);
  const [showSolution, setShowSolution] = useState(false);

  // Measure refs for error substrings → bounding boxes
  const errRefs = useRef({}); // key -> { el, id }
  const [callouts, setCallouts] = useState([]); // [{id, top,left,width,height,reason}]

  // Accept pre-parsed question or parse now
  const parsed = useMemo(() => {
    if (!currentQuestion) return { parsedCode: [], errorPositions: [], errors: [] };
    if (currentQuestion.parsedCode && currentQuestion.errorPositions) return currentQuestion;
    return parseQuestion(currentQuestion);
  }, [currentQuestion]);

  const reasonById = useMemo(() => {
    const m = new Map();
    (currentQuestion?.errors || []).forEach((e) => m.set(e.id, e.description || ""));
    return m;
  }, [currentQuestion?.errors]);

  useEffect(() => {
    // Reset when question changes
    setClicks([]);
    setDone(false);
    setShowSolution(false);
    setCallouts([]);
    errRefs.current = {};
  }, [currentQuestion?.title]);

  // Register a guess: only called from non-whitespace text spans or error spans
  const registerMissText = (e, line) => {
    if (done) return;
    const rect = codeRef.current?.getBoundingClientRect();
    const x = rect ? e.clientX - rect.left : 0;
    const y = rect ? e.clientY - rect.top : 0;
    setClicks((prev) => {
      const next = [...prev, { x, y, line }];
      if (next.length >= MAX_CLICKS) { setShowSolution(true); setDone(true); }
      return next;
    });
  };

  const registerHit = (e, line) => {
    if (done) return;
    const rect = codeRef.current?.getBoundingClientRect();
    const x = rect ? e.clientX - rect.left : 0;
    const y = rect ? e.clientY - rect.top : 0;
    setClicks((prev) => {
      const next = [...prev, { x, y, line }];
      if (next.length >= MAX_CLICKS) { setShowSolution(true); setDone(true); }
      return next;
    });
  };

  // Track refs used for overlay boxes
  const setErrRef = (key, el, id) => {
    if (el) errRefs.current[key] = { el, id };
    else delete errRefs.current[key];
  };

  const recomputeCallouts = () => {
    const parent = codeRef.current;
    if (!parent) return;
    const parentRect = parent.getBoundingClientRect();
    const boxes = Object.values(errRefs.current)
      .map(({ el, id }) => {
        if (!el) return null;
        const r = el.getBoundingClientRect();
        return {
          id,
          top: r.top - parentRect.top + parent.scrollTop,
          left: r.left - parentRect.left + parent.scrollLeft,
          width: r.width,
          height: r.height,
          reason: reasonById.get(id) || "",
        };
      })
      .filter(Boolean);
    setCallouts(boxes);
  };

  useEffect(() => {
    if (!showSolution) return;
    const el = codeRef.current;
    const onScroll = () => recomputeCallouts();
    const onResize = () => recomputeCallouts();
    el?.addEventListener("scroll", onScroll);
    window.addEventListener("resize", onResize);
    recomputeCallouts();
    return () => {
      el?.removeEventListener("scroll", onScroll);
      window.removeEventListener("resize", onResize);
    };
  }, [showSolution, currentQuestion]);

  // Intersection test: click point vs any callout box
  const isClickHitAfterReveal = (c) => {
    for (const b of callouts) {
      if (c.x >= b.left && c.x <= b.left + b.width && c.y >= b.top && c.y <= b.top + b.height) return true;
    }
    return false;
  };

  // Render code lines with tight, invisible error spans and non-whitespace text-only misses
  const renderCode = () => {
    const lines = parsed.parsedCode || [];
    const positions = parsed.errorPositions || [];

    // Build per-line segments
    return lines.map((line, lineIndex) => {
      const lineErrors = positions.filter((e) => e.line === lineIndex).sort((a, b) => a.startPos - b.startPos);
      const segments = [];
      let last = 0;
      for (const err of lineErrors) {
        if (err.startPos > last) segments.push({ text: line.slice(last, err.startPos), isError: false });
        segments.push({ text: line.slice(err.startPos, err.endPos), isError: true, id: err.id });
        last = err.endPos;
      }
      if (last < line.length) segments.push({ text: line.slice(last), isError: false });

      return (
        <div key={lineIndex} className="flex items-start">
          <span className="text-gray-500 mr-4 select-none text-right inline-block w-8 text-xs">{lineIndex + 1}</span>
          <span className="select-text">
            {segments.map((seg, i) => {
              if (seg.isError) {
                // ERROR: clickable, invisible; we still attach a ref for measuring boxes
                return (
                  <span
                    key={i}
                    ref={(el) => setErrRef(`${lineIndex}-${i}`, el, seg.id)}
                    style={{ whiteSpace: "pre" }}
                    onClick={(e) => { e.stopPropagation(); registerHit(e, lineIndex); }}
                    onKeyDown={(e) => {
                      if (e.key === "Enter" || e.key === " ") { e.preventDefault(); e.stopPropagation(); registerHit(e, lineIndex); }
                    }}
                    role="button"
                    tabIndex={0}
                  >
                    {seg.text}
                  </span>
                );
              }

              // NON-ERROR: split into runs; whitespace is not clickable
              const runs = splitRuns(seg.text);
              return runs.map((r, k) => (
                <span
                  key={`${i}-${k}`}
                  style={{ whiteSpace: "pre" }}
                  className={r.isWhitespace ? "pointer-events-none" : undefined}
                  onClick={r.isWhitespace ? undefined : (e) => registerMissText(e, lineIndex)}
                >
                  {r.text}
                </span>
              ));
            })}
          </span>
        </div>
      );
    });
  };

  // Derived coloring for click markers
  const clickClass = (c) => {
    if (!showSolution) return "bg-yellow-300"; // guessing phase
    return isClickHitAfterReveal(c) ? "bg-emerald-400" : "bg-rose-400";
  };

  return (
    <section className="mt-6">
      <div className="w-full bg-gray-200 rounded-full h-3 mb-6 overflow-hidden" aria-label="Progress">
        <div className="bg-gradient-to-r from-indigo-500 to-purple-600 h-3 rounded-full transition-all duration-500 ease-out" style={{ width: `${progressPercent}%` }} />
      </div>

      <div className="p-4 rounded-2xl bg-slate-900 text-slate-100 font-mono text-sm leading-7 overflow-auto border relative" ref={codeRef}>
        <div className="space-y-1">{renderCode()}</div>

        {/* Click markers */}
        <div className="absolute inset-0 pointer-events-none">
          {clicks.map((c, idx) => (
            <div
              key={idx}
              className={`absolute -translate-x-1/2 -translate-y-1/2 w-3 h-3 rounded-full opacity-90 ${clickClass(c)}`}
              style={{ left: c.x, top: c.y }}
              title={!showSolution ? "Guess" : (isClickHitAfterReveal(c) ? "Hit" : "Miss")}
            />
          ))}
        </div>

        {/* Reveal overlays (yellow boxes) */}
        {showSolution && (
          <div className="absolute inset-0 pointer-events-none">
            {callouts.map((b, idx) => (
              <React.Fragment key={`callout-${idx}`}>
                <div
                  className="absolute rounded-md border-2 border-yellow-400"
                  style={{ left: b.left, top: b.top, width: b.width, height: b.height }}
                />
                {/* Optional tooltip: uncomment if you want textual reasons */}
                {/* <div
                  className="absolute max-w-xs text-slate-900 bg-yellow-50 border border-yellow-300 rounded-lg p-2 text-xs shadow"
                  style={{ left: b.left + b.width + 8, top: Math.max(4, b.top - 2) }}
                >
                  <div className="font-semibold mb-0.5">Why</div>
                  <div>{b.reason}</div>
                </div> */}
              </React.Fragment>
            ))}
          </div>
        )}
      </div>

      <div className="mt-3 text-xs text-slate-500">
        Tip: Click exactly on buggy **text**. Whitespace isn’t clickable. 3 clicks → reveal & lock. After reveal: green = hit, red = miss.
      </div>

      <div className="mt-4 flex items-center gap-2">
        <button
          className="px-3 py-2 rounded-lg bg-indigo-600 text-white hover:bg-indigo-700 disabled:opacity-50"
          onClick={() => { setShowSolution(true); setDone(true); onSubmit?.(); }}
          disabled={showSolution}
        >
          Show answers
        </button>
        {hasMoreQuestions && (
          <button className="px-3 py-2 rounded-lg bg-slate-100 hover:bg-slate-200" onClick={onNext}>Next</button>
        )}
      </div>
    </section>
  );
}