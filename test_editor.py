"""
Tests for the terminal text editor.            Run with:   pytest -v

SETUP: put this file next to your editor file and set MODULE below to the
editor's file name WITHOUT ".py".

How it works: the tests "type" keystrokes into your real main() loop, exactly
like a user would, then check the text and cursor that result.
    run("hello", "/", "world")   ->  types hello, Enter, "/" (break line), world
After a run you can check:   s.lines   s.line (1-based)   s.col   s.screen
"""
import builtins
import importlib
import random
import subprocess
import sys
from pathlib import Path

import pytest

# ====================== EDIT THIS ======================================
MODULE = "text_editor"
# =======================================================================

sys.path.insert(0, str(Path(__file__).parent.resolve()))
ed = importlib.import_module(MODULE)

CLEAR = "\n<<SCREEN CLEARED>>\n"
REAL_PAGE = ed.Page          # remember the real class (so test wrappers never stack up)


# ------------------------------------------------------------------ helpers
class Session:
    def __init__(self, page, output):
        self.page, self.output = page, output

    @property
    def lines(self):
        return self.page.get_lines()

    @property
    def line(self):                       # 1 = first line
        return self.page.line_index()

    @property
    def col(self):                        # 0 = before the first character
        return self.page.current_line.val.cursor_posn

    @property
    def screen(self):                     # what the user sees after the last key
        return self.output.split(CLEAR)[-1]


@pytest.fixture
def run(monkeypatch, tmp_path, capsys):
    monkeypatch.chdir(tmp_path)           # saved files land in a temp folder
    monkeypatch.setattr(ed, "clear_screen", lambda: print(CLEAR, end=""))

    def _run(*keys):
        pages = []

        class SpyPage(REAL_PAGE):         # lets the test look inside the editor
            def __init__(self):
                super().__init__()
                pages.append(self)

        monkeypatch.setattr(ed, "Page", SpyPage)
        remaining = iter(keys)

        def fake_input(prompt=""):
            try:
                return next(remaining)
            except StopIteration:
                raise EOFError            # out of keystrokes: stop the editor

        monkeypatch.setattr(builtins, "input", fake_input)
        try:
            ed.main()
        except EOFError:
            pass
        return Session(pages[0], capsys.readouterr().out)

    return _run


def check_structure(page):
    """Internal consistency: links, counters and cursor must all agree."""
    nodes, node = [], page.rootline
    while node.next is not None:
        assert node.next.prev is node, "line links broken (prev/next disagree)"
        node = node.next
        nodes.append(node)
    assert nodes and nodes[0] is page.firstline, "firstline is not the first line"
    assert len(nodes) == page.line_total, \
        f"line_total says {page.line_total} but there are {len(nodes)} lines"
    assert any(n is page.current_line for n in nodes), "current_line is not in the page"
    for ln in nodes:
        line, n, i, cursor_at = ln.val, ln.val.root, 0, None
        if line.cursor is line.root:
            cursor_at = 0
        while n.next is not None:
            assert n.next.prev is n, "character links broken (prev/next disagree)"
            n, i = n.next, i + 1
            if n is line.cursor:
                cursor_at = i
        assert i == line.char_total, f"char_total says {line.char_total} but line has {i} chars"
        assert cursor_at is not None, "cursor points at a character not in the line"
        assert cursor_at == line.cursor_posn, \
            f"cursor_posn says {line.cursor_posn} but cursor is really at {cursor_at}"


# =========================================================== typing / basics
def test_typing_text(run):
    s = run("hello")
    assert s.lines == ["hello"] and s.col == 5


def test_typing_twice_appends(run):
    assert run("ab", "cd").lines == ["abcd"]


def test_blank_enter_does_nothing(run):
    assert run("", "").lines == [""]


def test_unicode_and_spaces(run):
    assert run("café ☕ 日本語 x").lines == ["café ☕ 日本語 x"]


def test_long_line(run):
    assert run("A" * 5000).lines == ["A" * 5000]


# ===================================================================== delete
def test_delete_removes_char_before_cursor(run):
    assert run("abc", "!").lines == ["ab"]


def test_delete_in_middle(run):
    assert run("abcd", "<", "!").lines == ["abd"]


def test_delete_at_very_start_does_nothing(run):
    s = run("abc", "<", "<", "<", "!")
    assert s.lines == ["abc"] and s.col == 0


def test_delete_on_empty_page_does_nothing(run):
    assert run("!", "!").lines == [""]


# ================================================================ break/merge
def test_break_line_in_middle(run):
    s = run("ab", "<", "/")
    assert s.lines == ["a", "b"] and (s.line, s.col) == (2, 0)


def test_break_line_at_end(run):
    assert run("ab", "/").lines == ["ab", ""]


def test_break_line_at_start(run):
    assert run("ab", "<", "<", "/").lines == ["", "ab"]


def test_break_then_type(run):
    assert run("hello", "/", "world").lines == ["hello", "world"]


def test_merge_with_delete_at_line_start(run):
    s = run("ab", "/", "cd", "<", "<", "!")
    assert s.lines == ["abcd"] and (s.line, s.col) == (1, 2)


def test_merge_with_empty_line(run):
    assert run("ab", "/", "!").lines == ["ab"]


# ================================================================== movement
def test_right_at_line_end_goes_to_next_line(run):
    s = run("ab", "/", "cd", "^", ">")
    assert (s.line, s.col) == (2, 0)


def test_right_at_very_end_wraps_to_start(run):
    s = run("ab", ">")
    assert (s.line, s.col) == (1, 0)


def test_left_at_line_start_goes_to_end_of_previous_line(run):
    s = run("ab", "/", "cd", "<", "<", "<")
    assert (s.line, s.col) == (1, 2)


def test_left_at_very_start_wraps_to_end(run):
    s = run("ab", "<", "<", "<")
    assert (s.line, s.col) == (1, 2)


def test_up_on_first_line_goes_to_column_zero(run):
    assert run("abc", "^").col == 0


def test_down_on_last_line_goes_to_line_end(run):
    assert run("abc", "<", "<", "$").col == 3


def test_up_and_down_remember_column(run):
    s = run("abcd", "/", "ef", "/", "ghij", "^", "^")
    assert (s.line, s.col) == (1, 4)
    s = run("abcd", "/", "ef", "/", "ghij", "^", "^", "$", "$")
    assert (s.line, s.col) == (3, 4)


def test_up_after_break_line_uses_new_column(run):
    # After Enter the cursor is at column 0, so Up should land at column 0.
    s = run("abc", "/", "^")
    assert (s.line, s.col) == (1, 0)


def test_down_after_moving_left_across_a_line_boundary(run):
    # Cursor ends at column 3 of line 1; Down should aim for column 3 of line 2.
    s = run("abc", "/", "de", "<", "<", "<", "$")
    assert (s.line, s.col) == (2, 2)


def test_up_after_enter_in_middle_of_text(run):
    s = run("abcdef", "<", "<", "<", "/", "^")
    assert (s.line, s.col) == (1, 0)


def test_undo_after_left_wraps_to_the_end_removes_the_right_text(run):
    # Left at the very start wraps to the end; typing there then undoing must remove what was typed.
    s = run("abcd", "<", "<", "<", "<", "<", "X", "u")
    assert s.lines == ["abcd"]


def test_cursor_counter_is_right_after_left_wraps(run):
    s = run("abcd", "<", "<", "<", "<", "<")
    assert (s.line, s.col) == (1, 4)


# ================================================================ find / replace
def test_find_highlights_matches(run):
    s = run("hello world", "{", "wor", "")
    assert "<find start>wor<find end>" in s.output
    assert "String is found" in s.output


def test_find_not_found(run):
    assert "String is not found" in run("hello", "{", "zzz", "").output


def test_find_empty_string_rejected(run):
    assert "Not a valid" in run("hello", "{", "", "").output


def test_replace_all(run):
    assert run("cat cat", "/", "a cat", "}", "cat", "dog", "").lines == ["dog dog", "a dog"]


def test_replace_all_with_empty_text_deletes_matches(run):
    assert run("a-b-c", "}", "-", "", "").lines == ["abc"]


def test_replace_all_when_replacement_contains_target(run):
    assert run("a", "}", "a", "aa", "").lines == ["aa"]


def test_replace_all_empty_target_changes_nothing(run):
    assert run("abc", "}", "", "x", "").lines == ["abc"]


def test_replace_all_not_found_is_not_an_undo_step(run):
    # the single undo must undo the typing, proving nothing was recorded for the replace
    assert run("abc", "}", "zzz", "y", "", "u").lines == [""]


def test_replace_next_replaces_match_after_cursor(run):
    # cursor sits between the two "cat"s, so the NEXT cat is the second one
    s = run("cat cat", "<", "<", "<", "<", "&", "cat", "dog", "")
    assert s.lines == ["cat dog"]


def test_replace_next_looks_on_later_lines(run):
    s = run("aaa", "/", "bbb", "/", "ccc", "^", "^", "&", "bbb", "X", "")
    assert s.lines == ["aaa", "X", "ccc"]


def test_replace_next_on_later_line_when_cursor_is_far_right(run):
    # cursor is at column 6 of line 1, but "bb" sits at the START of line 2
    s = run("aaaaaa", "/", "bb", "^", ">", ">", ">", ">", "&", "bb", "X", "")   # cursor: line 1, col 6
    assert s.lines == ["aaaaaa", "X"]


def test_replace_next_not_found_changes_nothing(run):
    assert run("abc", "&", "zzz", "y", "").lines == ["abc"]


def test_replace_next_empty_target_changes_nothing(run):
    assert run("abc", "&", "", "y", "").lines == ["abc"]


# ======================================================================= save
def test_save_writes_file(run, tmp_path):
    run("hello", "/", "world", "save", "out.txt")
    assert (tmp_path / "out.txt").read_text(encoding="utf-8") == "hello\nworld"


def test_save_unicode(run, tmp_path):
    run("café ☕", "save", "u.txt")
    assert (tmp_path / "u.txt").read_text(encoding="utf-8") == "café ☕"


def test_save_message_is_visible_to_the_user(run):
    # The screen is cleared right after saving, so the user must still see a confirmation.
    assert "saved" in run("hi", "save", "o.txt").screen.lower()


def test_save_with_empty_filename_does_not_crash(run):
    run("my precious work", "save", "")


def test_save_into_missing_folder_does_not_crash(run):
    run("my precious work", "save", "no_such_folder/out.txt")


# ================================================================ undo / redo
def test_undo_typing(run):
    assert run("abc", "u").lines == [""]


def test_redo_typing(run):
    assert run("abc", "u", "r").lines == ["abc"]


def test_undo_with_nothing_shows_message(run):
    assert "Nothing to undo" in run("u").screen


def test_redo_with_nothing_shows_message(run):
    assert "Nothing to redo" in run("r").screen


def test_undo_delete_and_redo(run):
    assert run("abc", "!", "u").lines == ["abc"]
    assert run("abc", "!", "u", "r").lines == ["ab"]


def test_undo_delete_restores_cursor(run):
    assert run("abc", "!", "u").col == 3


def test_undo_break_line_and_redo(run):
    assert run("ab", "<", "/", "u").lines == ["ab"]
    assert run("ab", "<", "/", "u", "r").lines == ["a", "b"]


def test_undo_merge_and_redo(run):
    assert run("ab", "/", "cd", "<", "<", "!", "u").lines == ["ab", "cd"]
    assert run("ab", "/", "cd", "<", "<", "!", "u", "r").lines == ["abcd"]


def test_undo_replace_all_and_redo(run):
    assert run("cat", "}", "cat", "dog", "", "u").lines == ["cat"]
    assert run("cat", "}", "cat", "dog", "", "u", "r").lines == ["dog"]


def test_undo_replace_next_and_redo(run):
    home = ["<", "<", "<"]                      # cursor to the start, so "cat" is ahead of it
    assert run("cat", *home, "&", "cat", "dog", "", "u").lines == ["cat"]
    assert run("cat", *home, "&", "cat", "dog", "", "u", "r").lines == ["dog"]


def test_new_edit_after_undo_clears_redo(run):
    s = run("a", "u", "b", "r")
    assert s.lines == ["b"] and "Nothing to redo" in s.screen


def test_many_undos_then_many_redos(run):
    keys = ["a", "b", "/", "c", "!", "!"]
    assert run(*keys, *["u"] * 10).lines == [""]
    assert run(*keys, *["u"] * 10, *["r"] * 10).lines == run(*keys).lines


# ==================================================== history building blocks
def test_action_stack_is_last_in_first_out():
    st = ed.ActionStack()
    for n in (1, 2, 3):
        st.push(ed.HistNode(n, "insert", 1, 0))
    assert [st.pop().val for _ in range(3)] == [3, 2, 1]
    assert st.pop() is None


def test_action_stack_clear():
    st = ed.ActionStack()
    st.push(ed.HistNode(1, "insert", 1, 0))
    st.clear()
    assert st.pop() is None and st._len() == 0


def test_line_set_cursor_beyond_end_stops_at_end():
    ln = ed.Line()
    for c in "abc":
        ln.add_char(c)
    ln.setCursor(99)
    assert ln.cursor_posn == 3


# ============================================ random "monkey" sessions (the
# part that finds bugs you would never think to write a test for)
WORDS = ["ab", "cd", "xyz", "hello", "a b", "café"]       # none equal a command key
PICK = ["a", "b", "c", "xy", "ab"]


def random_ops(rng, n, with_undo_redo=False):
    ops = []
    for _ in range(n):
        kind = rng.choice(["type"] * 4 + ["/"] * 2 + ["!"] * 3 + ["move"] * 3 + ["burst"] * 3 +
                          ["all", "next", "find"] + (["u", "r"] * 2 if with_undo_redo else []))
        if kind == "type":
            ops.append([rng.choice(WORDS)])
        elif kind == "move":
            ops.append([rng.choice(["<", ">", "^", "$"])])
        elif kind == "burst":                    # many presses in a row: reaches line starts/ends
            ops.append([rng.choice(["<", ">", "^", "$"])] * rng.randint(3, 9))
        elif kind in ("/", "!", "u", "r"):
            ops.append([kind])
        elif kind == "all":
            ops.append(["}", rng.choice(PICK), rng.choice(["", "Q", "zz", "a"]), ""])
        elif kind == "next":
            ops.append(["&", rng.choice(PICK), rng.choice(["", "Q", "zz", "a"]), ""])
        else:
            ops.append(["{", rng.choice(PICK), ""])
    return ops


def flat(ops):
    return [k for op in ops for k in op]


def failure_of(check, run, ops):
    try:
        check(run, ops)
    except Exception as e:                       # noqa: BLE001
        return f"{type(e).__name__}: {e}"
    return None


def hunt(check, run, with_undo_redo=False, tries=250, max_ops=9):
    """Try random sessions; on the first failure shrink it to a minimal repro."""
    rng = random.Random(2024)
    for _ in range(tries):
        ops = random_ops(rng, rng.randint(1, max_ops), with_undo_redo)
        if failure_of(check, run, ops):
            i = 0
            while i < len(ops):                  # drop steps that aren't needed
                trial = ops[:i] + ops[i + 1:]
                if trial and failure_of(check, run, trial):
                    ops = trial
                else:
                    i += 1
            return flat(ops), failure_of(check, run, ops)
    return None


def structure_ok(run, ops):
    check_structure(run(*flat(ops)).page)


def undo_all_redo_all(run, ops):
    keys = flat(ops)
    final = run(*keys).lines
    s = run(*keys, *["u"] * 40)
    check_structure(s.page)
    assert s.lines == [""], f"undoing everything left {s.lines}, expected the empty page"
    s = run(*keys, *["u"] * 40, *["r"] * 40)
    check_structure(s.page)
    assert s.lines == final, f"redoing everything gave {s.lines}, expected {final}"


def undo_walks_back_one_step_at_a_time(run, ops):
    states = [[""]] + [run(*flat(ops[:k])).lines for k in range(1, len(ops) + 1)]
    changes = [states[0]]                        # the distinct text states, in order
    for st in states[1:]:
        if st != changes[-1]:
            changes.append(st)
    keys = flat(ops)
    for j in range(len(changes)):
        got = run(*keys, *["u"] * j).lines
        assert got == changes[-1 - j], f"after {j} undo(s) got {got}, expected {changes[-1 - j]}"
    for j in range(len(changes)):
        got = run(*keys, *["u"] * len(changes), *["r"] * j).lines
        assert got == changes[j], f"after undo-all then {j} redo(s) got {got}, expected {changes[j]}"


def show(result):
    keys, why = result
    return "\n  type these lines, in order: " + repr(keys) + "\n  problem: " + why


def test_random_sessions_keep_the_editor_consistent(run):
    r = hunt(structure_ok, run)
    assert r is None, show(r) if r else ""


def test_random_sessions_with_undo_redo_keep_the_editor_consistent(run):
    r = hunt(structure_ok, run, with_undo_redo=True)
    assert r is None, show(r) if r else ""


def test_random_sessions_undo_everything_then_redo_everything(run):
    r = hunt(undo_all_redo_all, run)
    assert r is None, show(r) if r else ""


def test_random_sessions_undo_goes_back_one_step_at_a_time(run):
    r = hunt(undo_walks_back_one_step_at_a_time, run)
    assert r is None, show(r) if r else ""


# ======================================================== real program, real terminal
def test_real_program_saves_a_file(tmp_path):
    script = Path(ed.__file__).resolve()
    r = subprocess.run([sys.executable, str(script)], cwd=tmp_path, timeout=20,
                       input="hello\n/\nworld\nsave\nout.txt\n",
                       capture_output=True, encoding="utf-8", errors="replace")
    assert (tmp_path / "out.txt").read_text(encoding="utf-8") == "hello\nworld", r.stderr
