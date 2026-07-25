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
        
    def add_char(self, val):
        new_charecter = Node(val)
        if self.cursor.next is not None:
            self.cursor.next.prev = new_charecter 
        new_charecter.prev = self.cursor
        new_charecter.next = self.cursor.next
        self.cursor.next = new_charecter
        self.cursor = self.cursor.next
        self.cursor_posn += 1

    def delete_char(self):
        if self.cursor != self.root:
            if self.cursor.next is not None:
                self.cursor.next.prev = self.cursor.prev
            self.cursor.prev.next = self.cursor.next
            self.cursor = self.cursor.prev
            self.cursor_posn -= 1
    
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
        
    def break_line(self):
        new_line = Node(Line())
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
                self.target = self.current_line.val.cursor_posn
            else:
                if self.current_line.next is None:
                    self.current_line = self.firstline
                    self.current_line.val.setCursor(0)
            
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
        self.target = self.current_line.val.cursor_posn

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
                    print("Not a valid sting")
                    return

    def find_and_replace_next(self, target_str, replace):
        if target_str != "":
            current = self.current_line
            while current is not None:
                current_line_text = current.val.print_without_cursor()
                if target_str in current_line_text:
                    new_text = current_line_text.replace(target_str, replace, 1)
                    current.val = Line()
                    for ch in new_text:
                        current.val.add_char(ch)
                    self.current_line = current
                    self.target = current.val.cursor_posn
                    return
                current = current.next
        elif target_str == "":
                    print("Not a valid sting")
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

class History:
    def __init__(self):
        self.current = Node({"type":"root"})

    def record(self, action_dict):
        new_node = Node(action_dict)
        self.current.next = None
        self.current.next = new_node
        new_node.prev = self.current
        self.current = self.current.next

    def undo(self, page):
        if self.current.val["type"] != "root":
            if self.current.val["type"] == "add":
                page.delete()
            elif self.current.val["type"] == "delete":
                page.add(self.current.val["char"])
            elif self.current.val["type"] == "break":
                page.delete()
        self.current = self.current.prev

    def redo(self, page):
        if self.current.next is not None:
            self.current = self.current.next
            if self.current.val["type"] == "add":
                page.add(self.current.val["char"])
            elif self.current.val["type"] == "delete":
                page.delete()
            elif self.current.val["type"] == "break":
                page.break_line()

page = Page()
history = History()

def clear_screen():
    print("\033[H\033[J", end="")

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
    save = [save]
    """)
    print(str(page))
    user_input = str(input())
    if user_input == "/":
        page.break_line()
        history.record({"type": "break"})
    elif user_input == ">":
        page.move_right()
    elif user_input == "<":
        page.move_left()
    elif user_input == "^":
        page.move_up()
    elif user_input == "$":
        page.move_down()
    elif user_input == "!":
        if page.current_line.val.cursor != page.current_line.val.root:
            deleted_char = page.current_line.val.cursor.val
            page.delete()
            history.record({"type": "delete", "char": deleted_char})
        else:
            page.delete()
            history.record({"type": "break"})
    elif user_input == "{":
        target = str(input())
        clear_screen()
        page.find(target)
        input("Press enter to return to editor")
    elif user_input == "}":
        target = str(input())
        replace = str(input())
        clear_screen()
        page.find_and_replace_all(target, replace)
        print(page)
        input("Press enter to return to editor")
    elif user_input == "&":
        target = str(input())
        replace = str(input())
        clear_screen()
        page.find_and_replace_next(target, replace)
        print(page)
        input("Press enter to return to editor")
    elif user_input == "u":
        history.undo(page)
    elif user_input == "r":
        history.redo(page)
    elif user_input == "save":
        file_name = str(input("Enter file name"))
        page.save_to_file(file_name)
    else:
        for char in user_input:
            page.add(char)
            history.record({"type": "add", "char": char})
