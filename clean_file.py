import re
from mblanguage import *


def capitaliseStatements(word):
    """capitalises a valid mapbasic statement, otherwise returns word unchanged"""
    try:
        statement_position = [statement.lower()
                              for statement in statements].index(word.lower())
    except:
        return word, None

    found_statement = statements[statement_position]
    return found_statement, found_statement


def capitaliseFunctions(word):
    """capitalises a valid mapbasic function, otherwise returns word unchanged"""
    try:
        function_position = [function.lower()
                             for function in functions].index(word.lower())
        return functions[function_position]
    except:
        return word


def capitaliseKeywords(word):
    """capitalises a valid mapbasic keyword, otherwise returns word unchanged"""
    try:
        keyword_position = [keyword.lower()
                            for keyword in keywords].index(word.lower())
        return keywords[keyword_position]
    except:
        return word


def capitaliseClause(word):
    """capitalises a valid mapbasic clause, otherwise returns word unchanged"""
    try:
        clause_position = [clause.lower()
                           for clause in clauses].index(word.lower())
        return clauses[clause_position]
    except:
        return word


def scanDef(def_file):
    print "scanning " + def_file


def cleanFile(mb_file, out_file):
    f = open(mb_file, 'r')
    c = open(out_file, 'w')

    changed_lines = 0
    bad_variables = []
    custom_types = []
    warnings = 0

    indent = 0
    following_line_indent = 0
    in_dialog = False
    in_if = False

    dialog_first_control_found = False

    dimming_type = False

    for line in f:
        original_line = line

        # Get first word
        first_word = line.strip().split(' ')[0].lower()

        if first_word.lower() == 'define':
            c.write(line)
            continue

        try:
            second_word = line.strip().split(' ')[1].lower()
        except:
            second_word = None

        # Update current indent
        if first_word in ['next', 'loop']:
            indent -= 1

        if first_word == 'end' and not 'program' in line.lower():
            indent -= 1

        # Indention for this line
        line_indent = indent

        # temporary unindents, which only apply to this line
        if first_word in ['else', 'elseif']:
            line_indent -= 1

        if first_word in ['control']:
            if not dialog_first_control_found:
                indent += 1
                dialog_first_control_found = True
            else:
                line_indent -= 1

        # temporary indents:
        if in_dialog:
            line_indent += 1

        starts_with_operator = False
        if line.strip()[:1] in ['+', '-', '*', '\/', ',', '&', '"', '(', ')']:
            line_indent += 2
            following_line_indent = 0
            starts_with_operator = True

        starts_with_clause = False
        if not in_dialog and not following_line_indent > 0 and first_word in [clause.lower() for clause in clauses]:
            # line starts with a clause or function
            line_indent += 2
            starts_with_clause = True
            following_line_indent = 0

        starts_with_function = False
        if not in_dialog and first_word in [function.lower() + "(" for function in functions]:
            # line starts with a clause or function
            line_indent += 2
            starts_with_function = True
            following_line_indent = 0

        starts_with_number = False
        if re.match(r'^\d+$', first_word):
            # line starts with a number
            line_indent += 2
            starts_with_number = True
            following_line_indent = 0

        line_indent += following_line_indent
        following_line_indent = 0

        if in_if and not (starts_with_operator or starts_with_clause or starts_with_function or starts_with_number):
            line_indent += 1
        elif in_if:
            line_indent -= 1

        # print line.strip()
        match = re.match(
            r'declare (?:sub|function) ([a-zA-Z_0-9]+).*', line.strip(), re.IGNORECASE)
        if match:
            sub_name = match.group(1)
            match = re.match(r'^[A-Z][a-zA-Z0-9]+$', sub_name)
            if not match:
                print "Warning - bad sub/function name: " + sub_name
                warnings += 1

        dimming_variables = False
        global_variables = False
        including_file = False
        line_has_comment = False

        # Split string on quotation marks
        parts = line.strip().split('"')
        # even number parts are literals, odd are code
        formatted_parts = []
        in_comment = False

        for index, part in enumerate(parts):
            # enumerate starts on 0, so our test for even/odd parts looks
            # strange:
            if index % 2 == 1 or in_comment:
                # even part, literal
                # don't do any processing
                formatted_parts.append(part)

                if including_file:
                    print "including: " + part
                    if part.lower() not in ['mapbasic.def', 'menu.def']:
                        scanDef(part.lower().strip())

                continue

            # odd part, non-literal
            # format nicely

            if not part or part.strip() == '':
                formatted_parts.append(part)
                continue

            if part.strip()[0] == "'":
                # comment, don't format rest of line
                in_comment = True
                line_has_comment = True
                formatted_parts.append(part)
                continue

            if "'" in part:
                # a comment appears mid way through this part
                part, comment = part.split("'", 1)
                in_comment = True
                line_has_comment = True

            # make sure commas are always followed by a single space
            part = re.sub(",\s*", ", ", part)
            # make sure =, <=, >= are always surrounded by single spaces
            part = re.sub("\s*([<>]?=)\s*", " \g<1> ", part)
            # make sure <, > are always surrounded by single spaces
            part = re.sub("\s*(\<\>?)(?!=)\s*", " \g<1> ", part)
            part = re.sub("\s*\>(?!=)\s*", " > ", part)
            part = re.sub("\< \>", "<>", part)
            # operators are always surrounded by single spaces
            part = re.sub("\s*([+\-*\/])\s*", " \g<1> ", part)

            # make sure brackets are always followed by a space, unless it's a
            # double bracket () or ((
            part = re.sub("\((?![()])", "( ", part)
            part = re.sub("(?<![()])\)", " )", part)
            # one exception is array indices such as array(1), which should
            # have no brackets
            part = re.sub("\(\s*(\d+)\s*\)", "(\g<1>)", part)
            # another exception is array indices which are single characters,
            # eg array(i)
            part = re.sub("\(\s*(\w)\s*\)", "(\g<1>)", part)

            # now process words in part
            words = re.split('([ ()])', part)
            processed_words = []
            for word in words:
                word, statement = capitaliseStatements(word)
                if statement:
                    #in_dialog = statement in ['Dialog', 'Control']
                    if statement == 'Dialog' and not re.search(r'\bremove\b', line.lower()) and not re.search(r'\bpreserve\b', line.lower()):
                        in_dialog = True
                        dialog_first_control_found = False
                    elif statement == 'Control' and first_word != 'alter':
                        in_dialog = True
                    elif in_dialog:
                        in_dialog = False
                        line_indent -= 2
                        indent -= 1

                    if statement == "Case" and not re.search(r'\bdo\b', line.lower()):
                        line_indent -= 1

                    if statement == "Include":
                        including_file = True

                    if statement == 'Dim':
                        dimming_variables = True

                    if statement == 'Global' and first_word.lower().strip() == 'global':
                        global_variables = True

                    if statement == 'Type':
                        if re.search(r'\bend\b', line.lower()):
                            dimming_type = False
                        else:
                            dimming_type = True

                    if statement == 'Then':
                        in_if = False

                    if statement in ['If', 'ElseIf']:
                        if re.search(r'\bend\b', line.lower()):
                            in_if = False
                        else:
                            in_if = True

                word = capitaliseFunctions(word)
                word = capitaliseKeywords(word)
                word = capitaliseClause(word)

                # Check for type names
                if dimming_type and not statement and word.strip() != '':
                    custom_types.append(word.strip())
                    dimming_type = False

                # Check for defining variables
                if dimming_variables and not statement:
                    if word.lower().strip() not in ['string', 'integer', 'smallint', 'float', 'object', 'logical', 'date', 'time', 'datetime', 'alias', 'as', 'brush', 'symbol', 'pen', 'font', '(', ')', ',', ''] and not re.match(r'^\d+$', word):

                        match = re.match(r'\s*([a-zA-Z0-9_])+', word)
                        variable_name = match.group(0)

                        match = re.match(
                            r'^[aifsdtobpl](?:t|ym|on)?[A-Z][a-zA-Z0-9_]*$', variable_name)
                        if not match and not re.match(r'^[i-n]$', variable_name) and not variable_name in bad_variables and not variable_name in custom_types:
                            bad_variables.append(variable_name)
                            print "Warning - old style variable name: " + variable_name
                            warnings += 1

                if global_variables and not statement:
                    if word.lower().strip() not in ['string', 'integer', 'smallint', 'float', 'object', 'logical', 'date', 'time', 'datetime', 'alias', 'as', 'brush', 'symbol', 'pen', 'font', '(', ')', ',', ''] and not re.match(r'^\d+$', word):

                        match = re.match(r'\s*([a-zA-Z0-9_])+', word)
                        variable_name = match.group(0)

                        print "Warning - global variable: " + variable_name
                        print " avoid using global variables were possible"
                        warnings += 1

                processed_words.append(word)

            part = ''.join(processed_words)

            # remove double spaces
            part = re.sub(" {2,}", " ", part)

            if in_comment:
                formatted_parts.append(part + "'" + comment)
            else:
                formatted_parts.append(part)

        line = '"'.join(formatted_parts)

        if line.strip()[-1:] in ['+', '-', '*', '\/', ',', '&', '('] and not line_has_comment:
            following_line_indent = 2

        line = '\t' * line_indent + line.strip() + "\n"

        # calculate extra indentation for following lines
        if first_word in ['function', 'sub', 'type']:
            indent += 1

        if line.strip().lower().startswith('do case'):
            indent += 2
        elif line.strip().lower().startswith('end case'):
            indent -= 1
        elif first_word == 'do':
            indent += 1

        if first_word == 'for' and '=' in line and second_word and second_word != 'input':
            indent += 1

        if first_word == 'if' and not 'end if' in line.lower():
            indent += 1

        if original_line != line:
            changed_lines += 1
        c.write(line)

    c.close()
    f.close()
    print "\n\nCompleted"
    if changed_lines > 0:
        print "Changed " + str(changed_lines) + " lines"
    else:
        print "No changes made"
    if warnings > 0:
        print " with " + str(warnings) + " warnings"

    return warnings, changed_lines
