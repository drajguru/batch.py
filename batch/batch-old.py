import re


# http://snatverk.blogspot.co.il/2012/01/how-to-work-with-states-in-ply.html
# http://www.dabeaz.com/ply/ply.html#ply_nn21
# http://snatverk.blogspot.co.il/2012/01/how-to-work-with-states-in-ply.html

class Expression(object):
    def __init__(self):
        pass


class Command(Expression):
    def __init__(self, command, parameters):
        super(Command, self).__init__()


class Scope(Expression):
    def __init__(self):
        super(Scope, self).__init__()


class BatchFile(object):
    def __init__(self):
        self.expressions = []


class Flag(object):
    def __init__(self, name, has_value=False):
        reg = r"()"


def lex(text, indent=0):
    if not text:
        return

    text = text.strip()

    if text[0] == "(":
        bracket_counter = 1
        pos = 1

        while bracket_counter != 0:
            char = text[pos]
            if char == "(":
                bracket_counter += 1
            if char == ")":
                bracket_counter -= 1
            pos += 1

        chunk = text[1:pos - 1]  # Strip parentheses

        print ("\t" * indent) + "Parentheses"

        lex(chunk, indent + 1)

        text = text[pos:]

    batch = r"(?P<command>(?P<command_name>[a-z]+)(?=[$ \t\n])(?:[ \t])?(?P<parameters>[^)\n&|(]+?(?=[$\t\n()]))?)"
    # r"(?P<brackets>\((?P<scope>.*?)\))|(?P<command>(?P<command_name>[a-z]+?)(?P<parameters>(?:[ \t]+?).+?)?
    # (?=[$\n(])(?P<inline_brackets>\((?P<inline_scope>.*?)\))?)"

    match = re.match(batch, text, re.DOTALL)
    groups = match.groupdict()

    command = groups["command"]
    if command:
        print ("\t" * indent) + "Command:", command.replace("\n", r"\n")
        print ("\t" * indent) + "\tName:", groups["command_name"]
        if groups["parameters"]:
            print ("\t" * indent) + "\tParameters:", groups["parameters"].replace("\n", r"\n")

    if match is not None:
        next_chunk = text[match.end():]
        lex(next_chunk, indent)
