# Dev Mode button regressions

## Overview
The Dev Mode toggle lives in `minimal/frontend/src/App.jsx` and the accompanying `HeaderSection` component. The button should open a password modal before switching to the developer view, but some recent UI refactors disrupted that flow.

## State where the button works
Commit `ceb8fb9` ("Fix Step 1-7 button duplication in Dev Mode demo assessments") introduced `HeaderSection.jsx` with an embedded password modal. In that version the component imported and rendered `PasswordModal`, so clicking the button triggered the prompt and allowed a successful unlock:

```jsx
import PasswordModal from './PasswordModal';
...
<PasswordModal
  isOpen={showPasswordPrompt}
  password={devPassword}
  setPassword={setDevPassword}
  onSubmit={checkDevPassword}
  onCancel={cancelPasswordPrompt}
/>
```

Because `handleDevModeClick` set `showPasswordPrompt` to `true`, the modal appeared immediately and users could enter the password. After a correct password, `App.jsx` called `setViewMode('dev')`, so Dev Mode switched on without issue.

## State where the button breaks
The later refactor in commit `4164c93` ("feat: Revamp QuestionPlayground component") removed the password modal from `HeaderSection.jsx` but left the rest of the unlock logic untouched. In current `work`/`main` the button still toggles `showPasswordPrompt`, yet nothing renders the modal:

- `App.jsx` continues to maintain the unlock state and pass all modal props down. When the user clicks Dev Mode it only sets `showPasswordPrompt` without changing the view, so no unlock happens.【F:minimal/frontend/src/App.jsx†L393-L459】
- `HeaderSection.jsx` now ignores those props and no longer imports `PasswordModal`, so `showPasswordPrompt` never drives any UI. The Dev Mode button simply re-renders the same view with no feedback.【F:minimal/frontend/src/components/HeaderSection.jsx†L60-L120】
- `PasswordModal.jsx` still exists in the tree but is unused, confirming the regression came from the UI refactor rather than a deliberate feature removal.【F:minimal/frontend/src/components/PasswordModal.jsx†L1-L76】

## Suspect branches / commits
- ✅ **Working**: `minimal` branch and any commit up to `ceb8fb9` (before PR #3) where `HeaderSection` still renders the modal.
- ❌ **Broken**: `feat/question-playground-revamp` (commit `4164c93`) and all later merges (`question-playground-revamp`, `minimal2`, `work`), because they ship the refactored header without reconnecting the modal.

## Summary
If Dev Mode appears inert, you are probably on a branch derived from the QuestionPlayground revamp where the password modal JSX was dropped. Restoring the `PasswordModal` import and render (or moving that UI elsewhere) will bring the button back to life.
