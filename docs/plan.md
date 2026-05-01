# Enhancement Plan

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

## 4 — Regex search + always case-insensitive

Add a "Regex" toggle on the main search bar, defaulted to on.

- When regex is on: pass the query as an `NSPredicate` regex using `kMDItemFSName MATCHES[cd] "<pattern>"` (the `[cd]` modifier enforces case-insensitive, diacritic-insensitive matching — can't be disabled without a separate code path).
- When regex is off: existing glob/wildcard behaviour, but still force `cd` modifiers so search is always case-insensitive regardless of the Match Case checkbox state.
- Regex toggle state persisted in config.

Note: `mdfind` regex support is limited to what `NSPredicate` supports (no lookaheads etc). May need a post-filter pass for full regex support.

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
