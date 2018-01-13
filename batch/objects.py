class Scope(object):
    def __init__(self, statements):
        self.statements = statements

    def __repr__(self):
        return "<Scope - {0} statements>".format(len(self.statements))

    def __str__(self):
        l = []
        for s in self.statements:
            l.append(str(s))
        return """(
  {0}
)""".format("\n".join([str(statement) for statement in self.statements]).replace("\n", "\n  "))


class Command(object):
    def __init__(self, name, params, silent=False):
        self.name = name
        self.params = params
        self.silent = silent

    def __repr__(self):
        return "<{0} {1}{2} - {3} params>".format(
            self.__class__.__name__,
            "(silent) " if self.silent else "",
            self.name,
            len(self.params))

    def __str__(self):
        return "{0}{1}{2}".format(
            "@" if self.silent else "",
            self.name,
            " " + " ".join([str(param) for param in self.params]))


class Param(object):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return "<{0} {1}>".format(self.__class__.__name__, self.value)

    def __str__(self):
        return self.value


class If(object):
    def __init__(self, inverted, test, command, else_clause=None):
        self.inverted = inverted
        self.test = test
        self.command = command
        self.else_clause = else_clause

    def _generate_params(self):
        raise NotImplementedError()

    def __str__(self):
        return "if {0}{1} {2} {3}".format(
            "not " if self.inverted else "",
            self._generate_params(),
            self.command,
            " {0}".format(self.else_clause) if self.else_clause else ""
        )


class Else(object):
    def __init__(self, command):
        self.command = command

    def __str__(self):
        return "else {0}".format(str(self.command))

    def __repr__(self):
        return "<Else - {0}>".format(self.command.name if isinstance(self.command, Command) else "(...)")


class FileIf(If):
    def __init__(self, inverted, test, command, else_clause=None):
        super(FileIf, self).__init__(inverted, test, command, else_clause)

    def __repr__(self):
        return "<If - File {0} {1} then {2}{3}>".format(
            self.test,
            "doesn't exist" if self.inverted else "exists",
            self.command.name if isinstance(self.command, Command) else "(...)",
            " else {0}".format(
                self.else_clause.command.name if isinstance(self.else_clause.command, Command) else "(...)"
            ) if self.else_clause else ""
        )

    def _generate_params(self):
        return "exist {0}".format(self.test)


class StringIf(If):
    def __init__(self, insensitive, inverted, operand1, operator, operand2, command, else_clause=None):
        super(StringIf, self).__init__(
            inverted, "{0} {1} {2}".format(operand1, operator, operand2), command, else_clause)

        self.insensitive = insensitive
        self.operand1 = operand1
        self.operator = operator
        self.operand2 = operand2

    def __repr__(self):
        return "<If - {0} then {1}{2}>".format(
            self.test,
            self.command.name if isinstance(self.command, Command) else "(...)",
            " else {0}".format(
                self.else_clause.command.name if isinstance(self.else_clause.command, Command) else "(...)"
            ) if self.else_clause else ""
        )

    def _generate_params(self):
        return "{0}{1}".format(
            "/i " if self.insensitive else "",
            self.test
        )


class ErrorIf(If):
    def __init__(self, inverted, operand1, operator, operand2, command, else_clause=None):
        super(ErrorIf, self).__init__(
            inverted, "{0} {1} {2}".format(operand1, operator, operand2), command, else_clause)

        self.operand1 = operand1
        self.operator = operator
        self.operand2 = operand2

    def __repr__(self):
        return "<If - {0} {1} {2} then {3}{4}>".format(
            self.operand1,
            self.operator,
            self.operand2,
            self.command.name if isinstance(self.command, Command) else "(...)",
            " else {0}".format(
                self.else_clause.command.name if isinstance(self.else_clause.command, Command) else "(...)"
            ) if self.else_clause else ""
        )

    def _generate_params(self):
        return "{0} {1} {2}".format(self.operand1, self.operator, self.operand2)


class Comment(object):
    def __init__(self):
        pass
