# Assignment 1 — Task Management Analyser

**Spec:** `CNG445-Assignment1.pdf`
**Topic:** Python basics (regex, OOP, file I/O, CLI args) — parse a `data.txt` log of members/managers/teams/tasks and serve a menu-driven report tool (managers by expertise, urgent tasks, team workloads pie chart, busiest members, tasks by property).

## Contents
- `taskanalyser.py` — the submission (single-file implementation)
- `data.txt` — sample input data matching the spec's member/manager/team/task line formats
- `CNG445-Assignment1.pdf` — assignment spec

## Why this grouping
No zip existed for Assignment 1. `taskanalyser.py` and `data.txt` were loose files at the top of the course folder. `data.txt`'s content (member/manager `<username>`/`<!username>` lines, `Team <code> -> user,user` lines, `[code] Name @user #prop:val #tag` task lines) is a verbatim match for the exact sample data block reproduced in the Assignment 1 PDF, and `taskanalyser.py` implements the `Team`/`Member`/`Manager`/`Task` classes and the 5-option menu (Manager by Expertise / Urgent Tasks / Team Workloads / Busiest Members / Tasks by Property) described in that same PDF. This is Assignment 1.

## Completeness assessment — actually executed with Python 3 + matplotlib

Overall: **runs successfully end-to-end, and the one bug predicted by static reading was confirmed by running it.**

**Confirmed correct by running `python3 taskanalyser.py data.txt`:**
- Loads the sample data and reaches the menu with no errors.
- Option 1 (Managers by Expertise), Option 2 (Urgent Tasks), Option 3 (Team Workloads pie
  chart, via matplotlib), and Option 5 (Tasks by Property, tested with
  `estimatedhours=10` → correctly returns only `[D2] Optimize queries`) all run without
  exceptions and produce sensible output.
- Regex-based parsing correctly distinguishes members/managers/teams/tasks and rejects
  `data.txt`'s intentionally-invalid tail lines.

**Confirmed bug (reproduced live, not just predicted from reading the code):**
- Running Option 4 (Busiest Member) prints, for the Backend team:
  `Backend  <__main__.Member object at 0x7fbde587f7d0> Total workload: 20 hours` — the exact
  broken default-object output predicted from a static read. Cause: `Member.__str__` is defined
  nested inside `Member.__init__` (wrong indentation — indented to the `__init__` body, not the
  class level), so plain `Member` objects (as opposed to `Manager`s) fall back to Python's
  default `object.__str__` instead of the intended readable format. Every other team's busiest
  member happens to be a `Manager` (which has its own working `__str__`), so this only surfaces
  for Backend in the supplied sample data — but it would surface for any team whose busiest
  member is a plain `Member`.

**Spec-conformance gaps (cosmetic, don't affect running behavior):**
- Method names use PascalCase (`GetWorkload`, `AddTask`, etc.) instead of the camelCase names in
  the spec's class diagram.
- `Team.isManagerExperiencedWith` and `Team.getManager` (required by the class diagram) are not
  implemented at all.
- `Task.addTag`/`Task.addProperty` aren't separate methods — tags/properties are set directly in
  the constructor from `LoadData` instead.
- A few bare `except:` clauses; a local variable named `any` shadows the Python builtin.

**Verdict: works, with one confirmed real bug.** Runs cleanly end-to-end against the supplied
`data.txt` for 4 of 5 menu options; Option 4 (Busiest Member) prints a broken `<object at
0x...>` line instead of a readable name for any team whose busiest member is a non-manager
`Member` — reproduced by actually running the program, not just inferred from the source.
