---
doc_type: plan
date: 2026-05-18
parent_plan: everything-enhancement-plan-phase-1-2026-05-18.md
---

# Keyboard & Display Changes — Working Plan

Covers the keyboard shortcuts, display restructuring, and modularization work described in the [main enhancement plan](everything-enhancement-plan-phase-1-2026-05-18.md).

---

## Scope

From the main plan:
- **Keyboard changes** — Escape to close, F2 rename, Cmd-D focus search
- **Display changes** — column restructure, items-found position, tab suppression, select-all button, remove Fn/Aa/"" toggles

Prerequisite refactor added here:
- **Modularization** — extract `build_tree_item()` helper before touching columns, so column changes are made in one place

---

## Tasks

| # | Task | Status |
|---|------|--------|
| 0 | Extract `build_tree_item()` helper (prerequisite for column changes) | ⬜ Not started |
| 1 | Escape to close | ✅ Done |
| 2 | Remove Fn / Aa / `""` toggle buttons; hardcode filename-only, case-insensitive | ✅ Done |
| 3 | Column restructure — Name without extension, separate Ext column, Path dir-only | ⬜ Not started |
| 4 | Move items-found label to above results box | ⬜ Not started |
| 5 | Suppress tab bar; reuse single tab per search instead of spawning new ones | ⬜ Not started |
| 6 | Add Select All button above results | ⬜ Not started |
| 7 | F2 — wire to existing rename dialog | ✅ Done |
| 8 | Cmd-D — focus `edit_query` | ✅ Done |

---

## Implementation Notes

### Task 0 — `build_tree_item()`

`QTreeWidgetItem` creation and `display_name` building are duplicated at four call sites:
- `load_more_items()` — line ~2668
- Scan chart population — lines ~3288–3297
- Drill-down chart population — lines ~3390–3398
- Single-file and batch rename update handlers — lines ~3740, ~3797

Extract to module-level helper:

```python
def build_tree_item(name: str, size: int, mtime: float, path: str, emoji_map: dict) -> QTreeWidgetItem:
    ...
```

Column indices to use here will reflect the new layout from Task 3.

### Task 1 — Escape to close

Add `keyPressEvent` to `MdfindApp`:

```python
def keyPressEvent(self, event):
    if event.key() == Qt.Key.Key_Escape:
        self.close()
    else:
        super().keyPressEvent(event)
```

### Task 2 — Remove toggle buttons

- Delete `self.chk_file_name`, `self.chk_match_case`, `self.chk_full_match` widget creation and layout insertion.
- Remove from `search_container_layout`.
- In `start_search()` / `SearchWorker` construction, hardcode `search_by_file_name=True`, `match_case=False`, `full_match=False`.
- Remove all references to those three attributes from the rest of the file.

### Task 3 — Column restructure

New column layout (5 columns):

| Col | Header | Content |
|-----|--------|---------|
| 0 | Name | filename without extension, with emoji prefix |
| 1 | Ext | extension without leading dot (e.g. `pdf`) |
| 2 | Size | formatted size |
| 3 | Date Modified | formatted mtime |
| 4 | Path | directory only (`os.path.dirname(path)`) |

`SearchTab.__init__`: update `setColumnCount`, `setHeaderLabels`, `setColumnWidth`.

All tree item construction flows through `build_tree_item()` after Task 0.

Rename update handlers at lines ~3740 and ~3797: also update col 1 (ext) and col 4 (dir path).

### Task 4 — Items-found label position

Remove `self.lbl_items_found` from `form_layout` (current search row).  
Add it to `left_layout` just before `left_layout.addWidget(self.tab_widget, stretch=1)`.

### Task 5 — Tab suppression

Hide the tab bar:
```python
self.tab_widget.tabBar().setVisible(False)
```

Modify `create_new_tab()` (or `start_search()`) to reuse the tab at index 0 instead of inserting a new one. The current tab's tree widget is cleared and repopulated; tab title updates in-place.

Remove or hide the tab close button and tab context menu since there's only one tab.

### Task 6 — Select All button

Add a `QPushButton("Select All")` to `left_layout` just before the `tab_widget`. Connect to:

```python
lambda: self.get_current_tree().selectAll() if self.get_current_tree() else None
```

### Task 7 — F2 rename

In `keyPressEvent` (added in Task 1), add:

```python
elif event.key() == Qt.Key.Key_F2:
    self.rename_file()
```

`rename_file()` already exists and handles the single-file rename dialog.

### Task 8 — Cmd-D focus search

In `keyPressEvent`:

```python
elif event.key() == Qt.Key.Key_D and event.modifiers() == Qt.KeyboardModifier.MetaModifier:
    self.edit_query.setFocus()
    self.edit_query.selectAll()
```

---

## Files Changed

- `everything.py` — all changes

---

## Risks / Constraints

- Tab suppression: internal code (`save_pinned_tabs`, tab context menu, `close_tab`, etc.) assumes multiple tabs can exist. Reusing index-0 tab means most of that code becomes dead but still runs harmlessly. Watch for `tab_widget.count() == 0` edge cases on startup.
- Column index change from 4 to 5 columns: any code that accesses `item.text(3)` for path must move to `item.text(4)`. Search the file for `.text(3)` before merging.
