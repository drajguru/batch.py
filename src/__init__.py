import re
from recordtype import recordtype

from ply import lex

from src.objects import Scope, Command, Param, FileIf, StringIf, ErrorIf, Else


IfState = recordtype("IfState", "else_clause inverted test statement type i operand1 operand2 operator")


states = (
    ("parens", "exclusive"),
    ("silent", "exclusive"),
    ("flag", "exclusive"),
    ("command", "exclusive"),
    ("if", "exclusive"),
    ("else", "exclusive"),
    ("ifnot", "exclusive"),
    ("fileif", "exclusive"),
    ("stringif", "exclusive"),
    ("endif", "exclusive"),
    ("errorifnum", "exclusive"),
    ("errorifvar", "exclusive")
)

# List of token names.   This is always required
tokens = (
    "silent",
    # "VARIABLE",
    "if",
    "ifelse",
    "command",
    "scope",
    # "ESCAPE",
    # "STRING",
    # "FLAG",
    # "LABEL",
    "comment",
    # "LPARENS",
    # "RPARENS"
)

# Regular expression rules for simple tokens
# t_SILENT = r"\@"
# t_VARIABLE = r"%.+?\b"
# t_command = r"[a-z1-9_\-]+"
# t_ESCAPE = r"\^"
# t_STRING = "\".+?\""
# t_FLAG = r"/\w"
# t_LABEL = r":.+?\b"
t_comment = r"::.+"


def t_ANY_begin_parens(t):
    r"""\("""
    t.lexer.scope_start = t.lexer.lexpos

    if t.lexer.current_state() == "parens":
        t.lexer.level += 1
    else:
        t.lexer.statements = {}
        t.lexer.level = 1

    t.lexer.statements[t.lexer.level] = []

    t.lexer.push_state("parens")


def t_INITIAL_parens_if_silent(t):
    r"""@"""
    t.lexer.push_state("silent")


def t_INITIAL_parens_endif_begin_if(t):
    r"""if"""
    if t.lexer.current_state() == "INITIAL":
        t.lexer.if_state = {}
        t.lexer.if_level = 1
    else:
        t.lexer.if_level += 1

    t.lexer.push_state("if")

    t.lexer.if_state[t.lexer.if_level] = IfState(None, False, None, None, None, False, None, None, None)


def t_if_endif_begin_else(t):
    r"""else"""
    t.lexer.push_state("else")
    t.lexer.if_state[t.lexer.if_level].else_clause = None


def t_if_i(t):
    r"""/i"""
    t.lexer.if_state[t.lexer.if_level].i = True


def t_if_stringif_begin_ifnot(t):
    r"""not"""
    t.lexer.if_state[t.lexer.if_level].inverted = True
    t.lexer.push_state("ifnot")


def t_if_ifnot_errorif(t):
    r"""defined|errorlevel|cmdextversion"""
    t.lexer.if_state[t.lexer.if_level].type = "error"
    t.lexer.if_state[t.lexer.if_level].operand1 = t.value

    if t.value.lower() in ["errorlevel", "cmdextversion"]:
        t.lexer.push_state("errorifnum")
    else:
        t.lexer.push_state("errorifvar")


def t_errorifnum_num(t):
    r"""\d"""
    t.lexer.if_state[t.lexer.if_level].operand2 = int(t.value)
    t.lexer.pop_state()
    t.lexer.push_state("endif")


def t_errorifnum_operator(t):
    r"""==|<=|>="""
    t.lexer.if_state[t.lexer.if_level].operator = t.value


def t_errorifvar_var(t):
    r"""[a-z0-9_\-]+"""
    t.lexer.if_state[t.lexer.if_level].operand2 = t.value
    t.lexer.pop_state()
    t.lexer.push_state("endif")


def t_if_ifnot_begin_fileif(t):
    r"""exist"""
    t.lexer.if_state[t.lexer.if_level].type = "file"
    t.lexer.push_state("fileif")


def t_fileif_test(t):
    r"""\"(.+)\"|(\S+)"""
    t.lexer.if_state[t.lexer.if_level].test = t.value
    t.lexer.pop_state()


def t_if_ifnot_begin_stringif(t):
    r"""\"(.+?)\"|([^ \t\r\n]+?)(?=[ \t\r\n])"""
    t.lexer.if_state[t.lexer.if_level].type = "string"

    if "==" in t.value:
        t.lexer.if_state[t.lexer.if_level].operand1, t.lexer.if_state[t.lexer.if_level].operand2 = t.value.split("==")
        t.lexer.if_state[t.lexer.if_level].operator = "=="
        t.lexer.push_state("endif")
    else:
        if t.lexer.if_state[t.lexer.if_level].operand1:
            t.lexer.if_state[t.lexer.if_level].operand2 = t.value
            t.lexer.push_state("endif")
        else:
            t.lexer.if_state[t.lexer.if_level].operand1 = t.value
            t.lexer.push_state("stringif")


def t_stringif_operator(t):
    r"""EQU|NEQ|LSS|LEQ|GTR|GEQ|=="""
    t.lexer.if_state[t.lexer.if_level].operator = t.value
    t.lexer.pop_state()


def t_stringif_operand(t):
    r"""\"(.+)\"|(.+?)(?=[\s])"""
    if "==" in t.value:
        t.lexer.if_state[t.lexer.if_level].operand1, t.lexer.if_state[t.lexer.if_level].operand2 = t.value.split("==")
        t.lexer.if_state[t.lexer.if_level].operator = "=="
    else:
        t.lexer.if_state[t.lexer.if_level].operand2 = t.value
    t.lexer.pop_state()
    t.lexer.push_state("endif")


def t_INITIAL_parens_silent_if_endif_else_command(t):
    r"""[a-z1-9_\-]+"""
    t.lexer.command = t.value
    t.lexer.params = []
    t.lexer.push_state("command")


def t_command_param(t):
    r"""\"(.+)\"|([^\s\n\r)&|(]+?)(?=[\s\n\r)&|(])"""
    # r"""\"(.+)\"|(\S+)"""
    t.lexer.params.append(Param(t.value))


def t_command_end(t):
    r"""(.*?)(?=[\n\r)&|(])"""
    params = t.lexer.params

    t.lexer.pop_state()

    if t.lexer.current_state() == "silent":
        t.type = "silent"
        obj = Command(t.lexer.command, params, True)
        t.lexer.pop_state()
    else:
        t.type = "command"
        obj = Command(t.lexer.command, params)

    if t.lexer.current_state() == "parens":
        t.lexer.statements[t.lexer.level].append(obj)
    elif t.lexer.current_state() in ["if", "endif"]:
        t.lexer.if_state[t.lexer.if_level].statement = obj
    elif t.lexer.current_state() == "else":
        t.lexer.else_statement = obj
    else:
        t.value = obj
        return t


def t_ANY_parens_end(t):
    r"""\)"""
    statements = t.lexer.statements.pop(t.lexer.level)
    t.lexer.level -= 1

    # t.value = Scope(t.lexer.lexdata[t.lexer.scope_start:t.lexer.lexpos])
    scope = Scope(statements)
    t.value = scope
    t.type = "scope"
    t.lexer.pop_state()

    if t.lexer.current_state() == "parens":
        t.lexer.statements[t.lexer.level].append(scope)
    elif t.lexer.current_state() in ["if", "endif"]:
        t.lexer.if_state[t.lexer.if_level].statement = scope
    elif t.lexer.current_state() == "else":
        t.lexer.else_statement = scope
    else:
        return t


def t_else_end(t):
    r"""(.*?)(?=[\n\r&|])"""
    t.lexer.pop_state()
    t.lexer.if_state[t.lexer.if_level].else_clause = Else(t.lexer.else_statement)


def t_if_endif_else_end(t):
    r"""(.*?)(?=[\n\r&|])"""
    if t.lexer.current_state() == "endif":
        t.lexer.pop_state()
    if t.lexer.current_state() == "ifnot":
        t.lexer.pop_state()

    t.lexer.pop_state()

    if_state = t.lexer.if_state.pop(t.lexer.if_level)
    t.lexer.if_level -= 1

    if if_state.else_clause:
        t.type = "ifelse"
    else:
        t.type = "if"

    if if_state.type == "file":
        t.value = FileIf(if_state.inverted, if_state.test, if_state.statement, if_state.else_clause)
    elif if_state.type == "string":
        t.value = StringIf(
            if_state.i,
            if_state.inverted,
            if_state.operand1,
            if_state.operator,
            if_state.operand2,
            if_state.statement,
            if_state.else_clause
        )
    elif if_state.type == "error":
        t.value = ErrorIf(
            if_state.inverted,
            if_state.operand1,
            if_state.operator,
            if_state.operand2,
            if_state.statement,
            if_state.else_clause
        )

    if t.lexer.current_state() == "parens":
        t.lexer.statements[t.lexer.level].append(t.value)
    elif t.lexer.current_state() == "endif":
        t.lexer.if_state[t.lexer.if_level].statement = t.value
    else:
        return t


t_INITIAL_ignore = " \t\r\n"
t_parens_ignore = " \r\n"
t_command_ignore = " \t"
t_if_ifnot_fileif_stringif_endif_errorifvar_errorifnum_else_ignore = " "


# Error handling rule
def t_ANY_error(t):
    print("State {0}: Illegal character '{1}' ({2})".format(t.lexer.current_state(), t.value[0], ord(t.value[0])))
    # t.lexer.skip(1)


# Build the lexer
lexer = lex.lex(reflags=re.IGNORECASE)
