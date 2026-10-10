Editor fixed · PY
import os
 
class Node:
    def __init__(self, val):
        self.val = val
        self.next = None
        self.prev = None
 
class Line:
    def __init__(self):
        self.root = Node("Root Node")
        self.cursor = self.root
        self.cursor_posn = 0
        self.char_total = 0
        
    def add_char(self, val):
        new_charecter = Node(val)
        if self.cursor.next is not None:
            self.cursor.next.prev = new_charecter 
        new_charecter.prev = self.cursor
        new_charecter.next = self.cursor.next
        self.cursor.next = new_charecter
        self.cursor = self.cursor.next
        self.cursor_posn += 1
        self.char_total += 1
 
    def delete_char(self):
        if self.cursor != self.root:
            if self.cursor.next is not None:
                self.cursor.next.prev = self.cursor.prev
            self.cursor.prev.next = self.cursor.next
            self.cursor = self.cursor.prev
            self.cursor_posn -= 1
            self.char_total -= 1
    
    def move_right(self):
        if self.cursor.next is not None:
            self.cursor = self.cursor.next
            self.cursor_posn += 1
    
    def move_left(self):
        if self.cursor != self.root:
            self.cursor = self.cursor.prev
            self.cursor_posn -= 1
 
    def setCursor(self, val):
        self.cursor = self.root
        self.cursor_posn = 0
        for i in range(val):
            if self.cursor.next is not None:
                self.cursor = self.cursor.next
                self.cursor_posn += 1
            elif self.cursor.next is None:
                break
 
    def __str__(self):
        temp_node = self.root.next
        char = []
        if self.cursor == self.root:
            char.append("|")
        while temp_node is not None:
            char.append(temp_node.val)
            if temp_node == self.cursor:
                char.append("|")
            temp_node = temp_node.next
        return  "".join(char)
 
    def print_without_cursor(self):
        temp_node = self.root.next
        char =[]
        while temp_node is not None:
            char.append(temp_node.val)
            temp_node = temp_node.next
        return "".join(char)
 
class Page:
    def __init__(self):
        self.rootline = Node(Line())
        self.firstline = Node(Line())
        self.rootline.next = self.firstline
        self.firstline.prev = self.rootline
        self.current_line = self.firstline
        self.target = 0
        self.line_total = 1
        
    def break_line(self):
        new_line = Node(Line())
        cur = self.current_line.val
        moved = cur.char_total - cur.cursor_posn  # FIX: keep char_total correct after a split
        cur.char_total = cur.cursor_posn
        new_line.val.char_total = moved
        if self.current_line.val.cursor.next is not None:
            new_line.val.root.next = self.current_line.val.cursor.next
            new_line.val.root.next.prev = new_line.val.root
            self.current_line.val.cursor.next = None
        new_line.next = self.current_line.next
        new_line.prev = self.current_line
        if self.current_line.next is not None:
            self.current_line.next.prev = new_line
        self.current_line.next = new_line
        self.current_line = self.current_line.next
        self.current_line.val.setCursor(0)
        self.line_total += 1
        self.target = 0
 
    def setCursor(self, line, posn):
        if line <= self.line_total:
            cur_line = self.rootline
            for i in range(line):
                cur_line = cur_line.next
            self.current_line = cur_line
            cur_line.val.setCursor(posn)
            self.target = cur_line.val.cursor_posn
 
    def move_up(self):
        if self.current_line != self.firstline:
            self.current_line = self.current_line.prev
            self.current_line.val.setCursor(self.target)
        else:
            if self.current_line == self.firstline:
                current_cursor_posn = self.current_line.val.cursor_posn
                self.current_line.val.setCursor(0)
    
    def move_down(self):
        if self.current_line.next is not None:
            self.current_line = self.current_line.next
            self.current_line.val.setCursor(self.target)
        else:
            if self.current_line.next is None:
                while self.current_line.val.cursor.next is not None:
                    self.current_line.val.move_right()
    
    def move_right(self):
        if self.current_line.val.cursor.next is not None:
            self.current_line.val.move_right()
            self.target = self.current_line.val.cursor_posn
        else:
            if self.current_line.next is not None:
                self.current_line = self.current_line.next
                self.current_line.val.cursor = self.current_line.val.root
                self.current_line.val.cursor_posn = 0
                self.target = self.current_line.val.cursor_posn
            else:
                if self.current_line.next is None:
                    self.current_line = self.firstline
                    self.current_line.val.setCursor(0)
 
    def line_index(self):
        i = 0                                     
        node = self.rootline
        while node is not self.current_line:
            node = node.next
            i += 1
        return i
            
    def move_left(self):
        if self.current_line.val.cursor != self.current_line.val.root:
            self.current_line.val.move_left()
            self.target = self.current_line.val.cursor_posn
        else:
            if self.current_line != self.firstline:
                self.current_line = self.current_line.prev
                while self.current_line.val.cursor.next is not None :
                    self.current_line.val.cursor = self.current_line.val.cursor.next
                    self.current_line.val.cursor_posn += 1
                self.target = self.current_line.val.cursor_posn
            else:
                if self.current_line == self.firstline:
                    while self.current_line.next is not None:
                        self.current_line = self.current_line.next
                    while self.current_line.val.cursor.next is not None:
                        self.current_line.val.move_right()
                    self.target = self.current_line.val.cursor_posn
            
    def add(self, val):
        self.current_line.val.add_char(val)
        self.target = self.current_line.val.cursor_posn
 
    def delete(self):
        if self.current_line.val.cursor != self.current_line.val.root:
            self.current_line.val.delete_char()
        else:
            if self.current_line != self.firstline:
                self.current_line = self.current_line.prev
                while self.current_line.val.cursor.next is not None:
                    self.current_line.val.move_right()
                cursor_posn = self.current_line.val.cursor_posn
                next_line = self.current_line.next.val
                next_line.setCursor(0)
                current_cursor = next_line.cursor
                while current_cursor.next is not None:
                    self.current_line.val.add_char(current_cursor.next.val)
                    current_cursor = current_cursor.next
                self.current_line.next = self.current_line.next.next
                if self.current_line.next is not None:
                    self.current_line.next.prev = self.current_line
                self.current_line.val.setCursor(cursor_posn)
                self.line_total -= 1
        self.target = self.current_line.val.cursor_posn
 
    def get_lines(self):
        lines = []
        node = self.firstline
        while node is not None:
            lines.append(node.val.print_without_cursor())
            node = node.next
        return lines
 
    def load_lines(self, lines):
        self.firstline = Node(Line())
        self.rootline.next = self.firstline
        self.firstline.prev = self.rootline
        node = self.firstline
        for i, text in enumerate(lines or [""]):
            if i > 0:
                new_node = Node(Line())
                new_node.prev = node
                node.next = new_node
                node = new_node
            for ch in text:
                node.val.add_char(ch)
            node.val.setCursor(0)
        self.current_line = self.firstline
        self.target = 0
        self.line_total = len(lines or [""])
 
 
    def __str__(self):
        lines = []
        tempLine = self.firstline
        while tempLine is not None:
            if tempLine == self.current_line:
                lines.append(str(tempLine.val))
                tempLine = tempLine.next
            else:
                lines.append(str(tempLine.val.print_without_cursor()))
                tempLine = tempLine.next
        return "\n".join(lines)
 
    def find(self, target_str):
        found = False
        if target_str != "":
            current = self.firstline
            while current is not None:
                current_line_text = current.val.print_without_cursor()
                if target_str in current_line_text:
                    found = True
                    current_line_text = current_line_text.replace(target_str, f"<find start>{target_str}<find end>")
                print(current_line_text)
                current = current.next
            if found == True:
                print("String is found")
            else:
                print("String is not found")
        elif target_str == "":
            print("Not a valid sting")
            return
 
    def find_and_replace_all(self, target_str, replace):
        if target_str != "":
            current = self.firstline
            while current is not None:
                current_line_text = current.val.print_without_cursor()
                if target_str in current_line_text:
                    current_line_text = current_line_text.replace(target_str, replace)
                    current.val = Line()
                    for ch in current_line_text:
                        current.val.add_char(ch)
                    print(current_line_text)
                current = current.next
        elif target_str == "":
                    print("Not a valid string")
                    return
 
    def find_and_replace_next(self, target_str, replace):
        if target_str != "":
            current = self.current_line
            current_cursor_posn = current.val.cursor_posn
            while current is not None:
                current_line_text = current.val.print_without_cursor()
                current_line_text_1 = current_line_text[:current_cursor_posn]
                current_line_text_2 = current_line_text[current_cursor_posn:]
                if target_str in current_line_text_2:
                    new_text = current_line_text_2.replace(target_str, replace, 1)
                    current.val = Line()
                    for ch in current_line_text_1:
                        current.val.add_char(ch)
                    for ch in new_text:
                        current.val.add_char(ch)
                    self.current_line = current
                    self.target = current.val.cursor_posn
                    return
                current = current.next
                current_cursor_posn = 0          # later lines are searched from their start
        elif target_str == "":
                    print("Not a valid string")
                    return  
 
    def save_to_file(self, filename):
        """Traverses lines directly and saves text to file."""
        lines = []
        tempLine = self.firstline
        while tempLine is not None:
            lines.append(tempLine.val.print_without_cursor())
            tempLine = tempLine.next
            
        full_text = "\n".join(lines)
        
        with open(filename, "w", encoding="utf-8") as f:
            f.write(full_text)
            
        print(f"File saved successfully to {filename}")
 
class HistNode:
    def __init__(self, val, operation, line_no, posn):
        self.val = val
        self.opr = operation
        self.line_no = line_no
        self.posn = posn
        self.next = None
        self.prev = None
 
class ActionStack:
    def __init__(self):
        self.head = HistNode(0, 0, 0, 0)
        self.ptr = self.head
        self.len = 0
 
    def push(self, node):
        self.ptr.next = node
        node.prev = self.ptr
        self.ptr = self.ptr.next
        self.len += 1
 
    def pop(self):
        node = self.ptr
        if self.len == 0:
            return None
        else:
            self.ptr = self.ptr.prev
            self.ptr.next = None
            node.prev = None
            node.next = None
            self.len -= 1
        return node
 
    def clear(self):
        self.ptr = self.head
        self.head.next = None
        self.len = 0
 
    def _len(self):
        return self.len
    
class History:
    def __init__(self):
        self.redo_stack = ActionStack()
        self.undo_stack = ActionStack()
 
    def record(self, val, opr, line_no, posn):
        self.undo_stack.push(HistNode(val, opr, line_no, posn))
        self.redo_stack.clear()
    
    def undo(self, page):
        node = self.undo_stack.pop()
        if node is not None:
            self.redo_stack.push(node)
            self.rev_action(node, page)
            return True
 
    def redo(self, page):
        node = self.redo_stack.pop()
        if node is not None:
            self.undo_stack.push(node)
            self.action(node, page)
            return True
 
    def action(self, node: HistNode, page: Page):
        if node.opr == "insert":
            page.setCursor(node.line_no, node.posn)
            for val in node.val:
                page.add(val)
 
        elif node.opr == "delete":
            page.setCursor(node.line_no, node.posn)
            page.delete()
 
        elif node.opr == "break line":
            page.setCursor(node.line_no, node.posn)
            page.break_line()
 
        elif node.opr == "merge":
            page.setCursor(node.line_no, 0)
            page.delete()
 
        elif node.opr == "replace":
            page.load_lines(node.val[1])
            page.setCursor(node.line_no, node.posn)
 
    def rev_action(self, node: HistNode, page: Page):
        if node.opr == "insert":
            page.setCursor(node.line_no, node.posn + len(node.val))
            for i in range(len(node.val)):
                page.delete()
 
        elif node.opr == "delete":
            page.setCursor(node.line_no, node.posn - 1)
            page.add(node.val)
 
        elif node.opr == "break line":
            page.setCursor(node.line_no + 1, 0)
            page.delete()
 
        elif node.opr == "merge":
            page.setCursor(node.line_no - 1, node.val)
            page.break_line()
 
        elif node.opr == "replace":
            page.load_lines(node.val[0])
            page.setCursor(node.line_no, node.posn)
        
 
            
 
def clear_screen():
    print("\033[H\033[J", end="")
 
 
def main():
    page = Page()
    history = History()
    message = ""
 
    while True:
        clear_screen()
        print(""" 
    up - [^]
    down - [$]
    left - [<]
    right - [>]
    delete - [!]
    break line - [/]
    find - [{]
    find and replace - [}]
    find and replace the next found word - [&]
    undo - [u]
    redo - [r]
    save = [save]
    """)
        print(str(page))
        if message:
            print(f"\n[{message}]")
            message = ""
        user_input = str(input())
        if user_input == "/":
            line_no = page.line_index()                       # position BEFORE the edit
            posn = page.current_line.val.cursor_posn
            page.break_line()
            history.record(None, "break line", line_no, posn)
        elif user_input == ">":
            page.move_right()
        elif user_input == "<":
            page.move_left()
        elif user_input == "^":
            page.move_up()
        elif user_input == "$":
            page.move_down()
        elif user_input == "!":
            cur = page.current_line.val
            if cur.cursor != cur.root:                        # normal delete of one character
                line_no = page.line_index()
                posn = cur.cursor_posn
                deleted_char = cur.cursor.val
                page.delete()
                history.record(deleted_char, "delete", line_no, posn)
            elif page.current_line != page.firstline:         # column 0 of a later line: join upward
                line_no = page.line_index()
                prev_len = page.current_line.prev.val.char_total
                page.delete()
                history.record(prev_len, "merge", line_no, 0)
            # first line, column 0: nothing changes, nothing is recorded
        elif user_input == "{":
            target = str(input("Please enter the string to be found: "))
            clear_screen()
            page.find(target)
            input("Press enter to return to editor")
        elif user_input == "}":
            target = str(input("Please enter the string to be found: "))
            replace = str(input("Please enter what the string should be replaced with: "))
            line_no = page.line_index()
            posn = page.current_line.val.cursor_posn
            before = page.get_lines()                         # snapshot of the text before
            clear_screen()
            page.find_and_replace_all(target, replace)
            after = page.get_lines()
            if before != after:                               # record only if something changed
                history.record((before, after), "replace", line_no, posn)
            print(page)
            input("Press enter to return to editor")
        elif user_input == "&":
            target = str(input("Please enter the string to be found: "))
            replace = str(input("Please enter what the string should be replaced with: "))
            line_no = page.line_index()
            posn = page.current_line.val.cursor_posn
            before = page.get_lines()
            clear_screen()
            page.find_and_replace_next(target, replace)
            after = page.get_lines()
            if before != after:
                history.record((before, after), "replace", line_no, posn)
            print(page)
            input("Press enter to return to editor")
        elif user_input == "u":
            if not history.undo(page):
                message = "Nothing to undo"
        elif user_input == "r":
            if not history.redo(page):
                message = "Nothing to redo"
        elif user_input == "save":
            file_name = str(input("Enter file name"))
            try:
                page.save_to_file(file_name)
                message = f"Saved to {file_name}"
            except OSError as e:
                message = f"Could not save: {e}"
        elif user_input != "":
            line_no = page.line_index()                       # position BEFORE typing
            posn = page.current_line.val.cursor_posn
            for char in user_input:
                page.add(char)
            history.record(user_input, "insert", line_no, posn)   # whole typed text is one undo step
 
 
if __name__ == "__main__":
    main()
