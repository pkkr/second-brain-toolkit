# Second Brain – Project Memory

The private Second Brain is available at `~/.second-brain/`. It stores
durable project context across sessions, tools, and machines. Keep it
useful by loading and writing only what matters for the current task.

## Instruction priority

When instructions conflict, follow this order:

1. The user's explicit request for the current task
2. Instructions in the current project repository
3. Project-specific notes and processes in the Second Brain
4. General guidance in `~/.second-brain/workflow/working-style.md`
5. This file

At the same level, prefer the more specific and more recently verified
instruction. Never weaken security, privacy, or legal constraints.

## Identify the project

Use the git remote URL as the primary key:

1. Run `git remote get-url origin`.
2. Find a matching project note by searching the `repo:` field under
   `~/.second-brain/projects/`.
3. If there is no match or no remote, search the `path:` field.
4. If no note exists, create `projects/<repo-name>/project.md` from
   `workflow/project-template.md`. Start with `path:` and add `repo:`
   when one becomes available.

## Load context progressively

At the start of a coding session:

1. Read `~/.second-brain/workflow/working-style.md`.
2. Read the project's `project.md`, focusing first on its frontmatter,
   goal, stack and architecture, decisions, and open items.
3. Follow linked notes only when they are relevant to the current task.
4. Treat `processes.md` as a router. Load only the detailed process
   whose trigger matches the work being performed.
5. Do not read the full project log by default. Use the newest ISO-week
   section, the latest five entries, or a targeted search when history
   is actually needed.

Do not load unrelated projects, complete archives, generated indexes,
or all linked notes "just in case." Expand context only when the task,
an ambiguity, or a failed assumption requires it.

## Project-specific processes

- Recurring workflows live in
  `~/.second-brain/projects/<name>/processes/`.
- `projects/<name>/processes.md` is a short router listing each trigger,
  process file, and last verification date.
- Before deploying, migrating, releasing, rotating credentials, or
  performing another recurring operation, load and follow the matching
  process.
- When a workflow is established or materially changes, update its
  detailed process and the router's verification date immediately.
- Guidance that applies to every project belongs in
  `workflow/working-style.md`, not in a project process.

## AGENTS.md in project repositories

- Each project repository should have a root `AGENTS.md` pointing to
  its Second Brain notes; use
  `workflow/project-agents-template.md`.
- If the repository already has an `AGENTS.md`, add only the missing
  Second Brain section. Preserve all existing instructions.

## Process the inbox selectively

- `~/.second-brain/inbox.md` is a quick-capture space with one item per
  bullet.
- If the user asks to add something to the inbox, add it without an
  extra confirmation.
- When writing to the Second Brain, process only inbox items that can be
  confidently assigned to the current project or topic.
- Move a project task to that project's `Open items`; move durable
  knowledge to an appropriate note; remove only successfully processed
  lines. Leave unrelated or ambiguous items untouched.

## OKF conventions

Notes follow [Open Knowledge Format (OKF)](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md)
with these additional conventions:

- Every indexed note has YAML frontmatter containing `title`,
  `description`, and `type`.
- Use standard Markdown links, not wikilinks.
- `connect_neurons.py` generates each folder's `index.md` and the
  global `log/` roll-up. Never edit generated files by hand.

## Progress log and tasks

- End a noteworthy session with at most one to three durable bullets in
  the project's `log.md`.
- Log only decisions and their rationale, user-visible released
  outcomes, incidents and lessons, new or changed recurring workflows,
  and unresolved risks that matter to a future session.
- Do not repeat commit messages, test results, routine status updates,
  or every small implementation step. Merge closely related follow-ups
  into one entry.
- Format logs with newest ISO week first: `## YYYY-Www`, followed by
  `- YYYY-MM-DD: <summary>`.
- `Open items` contains only active `- [ ]` tasks. Move completed work
  to the project log or an optional `completed-items.md` archive rather
  than accumulating checked boxes in the active list.

## During and after the work

- Update `project.md` only when durable facts change: goal, stack,
  architecture, key decisions, deployment destination, or active work.
- Keep transient implementation detail in git, issues, or the task at
  hand. The Second Brain stores what those systems do not explain.
- Never store production or personal secrets, tokens, private keys, or
  reusable passwords. Throwaway local-only demo credentials may be
  documented only when clearly labeled, contain no real data, and are
  never reused elsewhere.
- After changing the Second Brain, regenerate indexes with
  `second-brain generate` and validate them with `second-brain check`.
