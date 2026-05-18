---
doc_type: plan
date: 2026-05-18
---

# Enhancement Plan

Add features to the everything fork, as described in tasks, to make everything capable of advanced renaming, filtering, and moving.

## Features/tasks

### Keyboard changes
Press Escape to close
Press F2 while a single file is in focus to rename that file inline.
Press command-D to put focus in search query


### Display changes
1. Alter columns - path should be path only and not the filename, separate extension column with extension not displayed for Name
2. Move items found count to right above results box
3. Disable "tabbed results" feature; show all results in the same area and re-use it and suppress tab display
4. Add Select all button above file results
5. Remove the FN, AA, and "" buttons in the search query. Search query by default should be filename only and case insensitive if it can be.

### Advanced file move
Press F6 to move selected files; dialog appears with a find-as-you type list of pre-defined folders.

### Results filter
Add a "filter results" box after the search/query box; reduce search/query box to 1/3 its current size. Filter results provides a regex-filter on the displayed results when engaged.

### Custom rename
Small cluster of buttons above search results:
lowercase - lowercases all selected filenames
simple replace - regex find and replace text boxes 
find [ textbox  ] replace [ textbox   ] _rename_button_
e.g. to replace all _ with -, you'd put `_` in the find box and `-` in the replace box and tap rename or press Alt-R


## Handoff

**Repo:** `/Users/robert.hudson/repos/python-tools/everything-fork`  
**Run:** `uv run everything.py` from the repo root.  
**Single script:** `everything.py` (~6000 lines). No package structure.  
**Config file:** `~/.everythingByMdfind.json` — read/written via `read_config()` / `write_config()` at the top of the script.

**What's already been changed from upstream:**
- `pyproject.toml` added; `uv sync` manages the venv. `requirements.txt` left in place (upstream artifact, don't delete).
- `.gitignore` has `.venv/` added.
- `import fnmatch` and `import re` added at the top of `everything.py`.
- `SearchWorker.run()` reads `exclude_patterns` from config before the result loop and skips matching filenames with `fnmatch.fnmatch`. This is the only functional change to search behaviour so far.

**Key classes/methods to know:**
- `SearchWorker(QThread)` — runs `mdfind` in a background thread, line 591. Query is built in `run()`. Results emitted via `result_signal`.
- `start_search()` — creates a new tab and a new `SearchWorker`, line 2691.
- `update_tree()` — populates the `QTreeWidget` from the result list, called when `result_signal` fires.
- `load_more_items()` — lazy loads next 100 results on scroll, line 2638. `batch_size = 100`.
- Search row widgets (all on the main window): `self.edit_query` (main search box), `self.chk_file_name` (`Fn` toggle), `self.chk_match_case` (`Aa`), `self.chk_full_match` (`""`), `self.lbl_items_found`, `self.btn_refresh`.
- `search_container` — the `QWidget` wrapping the search row, uses `QHBoxLayout`.

**Important constraint — regex via mdfind:** `kMDItemFSName` only supports glob (`*`) matching. `MATCHES[cd]` operator returns zero results for filename queries — do not attempt it. Regex filtering must be done as a post-process on results in Python.

**Next thing to implement:** Item 1 (Escape to close) is the smallest — good place to start. Then items 2 and 3 are independent of each other. Item 4 (filter box) depends on understanding `update_tree` and `load_more_items` since the filter needs to operate on `search_tab.file_data` (the full result list) not just the loaded rows.

---

## 1 — Escape to close

Press Escape to close the window.

Implementation: override `keyPressEvent` on the main window; call `self.close()` when `Qt.Key.Key_Escape` is detected.

---

## 2 — F2 inline rename

Press F2 on a selected file to rename it in-place.

- If inline editing of a `QTreeWidget` cell is feasible: make column 0 editable on demand, activate the editor, commit on Enter/focus-loss, cancel on Escape.
- Fallback: pop a `QInputDialog` pre-filled with the bare filename (no extension); append the original extension back on confirm.
- Do not change extensions this round.
- After rename: call `mdimport <new_path>` to update the Spotlight index; refresh the row in-place (no full re-search needed).

---

## 3 — F6 move file(s)

Press F6 to move the selected file(s) to a chosen destination.

Move dialog:
- A text input with autocomplete; as you type, a list below it filters matching folders from a pre-set favorites list plus system bookmarks.
- Favorites list stored in `~/.everythingByMdfind.json` under `"move_favorites"`.
- Confirmation before move.
- After move: call `mdimport <destination>` on the destination folder; remove moved items from the current result list without re-running the search.

---

## 4 — Post-filter regex + exclude list

Search is two-stage:

**Stage 1 — mdfind (existing)**
- Run mdfind with glob matching as-is, always case-insensitive (`cd` modifier).

**Stage 2 — pre-display filter (new)**
- Before results are shown, filter out filenames matching any pattern in `"exclude_patterns"` in `~/.everythingByMdfind.json` (already implemented for junk files).
- Expand this to a general exclude list — any glob or fixed string the user never wants to see.

**Stage 3 — regex filter box (new)**
- A second text box added to the search row, after the `Fn`/`Aa`/`""` toggle buttons and before the "items found" label.
- Placeholder text: "Filter results (regex)…"
- Tab from `edit_query` moves focus to `edit_filter` (set via `QWidget.setTabOrder`).
- Triggers on Enter while focused; does nothing on typing (no debounce).
- Applies `re.search(pattern, basename, re.IGNORECASE)` to the already-loaded results list — no new mdfind call.
- If the pattern matches nothing, show an empty list (not an error).
- Bad regex shows an inline error label next to the box; list is not cleared.
- Clearing the filter box and pressing Enter restores the full result set.
- Filter state is not persisted.

---

## 5 — Move all visible results

"Move all visible" action — moves every file currently shown in the results list.

- Accessible from: a toolbar button, the multi-select context menu, or a keyboard shortcut.
- Reuses the move dialog from item 3.
- "Visible" means the items currently rendered in the tree (respects the lazy-load batch) — needs a decision: move only loaded rows, or trigger a full load first. Prefer: warn the user of the total count and load all before moving.
- After move: clear the results list; optionally re-run the search to confirm.

---

## Notes

- **Spotlight refresh after rename/move:** `subprocess.run(["mdimport", path])` — fast, surgical, no full reindex needed.
- **Pagination:** results are lazy-loaded in batches of 100 via scroll position. "All visible" for item 5 means all currently loaded rows, not just what's on screen.
