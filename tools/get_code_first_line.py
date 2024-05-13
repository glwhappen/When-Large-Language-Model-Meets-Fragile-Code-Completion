import re

def get_line_two(code):
    if not isinstance(code, str):
        # Handle errors or convert code to a string
        # For example, if code is None, you can set it to an empty string
        code = code or ''
    # Remove single-line and multi-line comments
    code_without_comments = re.sub(r'//.*?$|/\*.*?\*/', '', code, flags=re.DOTALL|re.MULTILINE)
    # print("Split", code_without_comments.split('\n'))
    return '\n'.join(code_without_comments.strip().split('\n')[:2])



def get_line(code):
    if not isinstance(code, str):
        # Handle errors or convert code to a string
        # For example, if code is None, you can set it to an empty string
        code = code or ''
    # Remove single-line and multi-line comments
    code_without_comments = re.sub(r'//.*?$|/\*.*?\*/', '', code, flags=re.DOTALL|re.MULTILINE)
    # Use regular expressions to match the first complete statement, i.e., all content from the beginning of the code segment to the first semicolon
    match1 = re.search(r'(.*?){', code_without_comments, re.DOTALL)
    match2 = re.search(r'(.*?);', code_without_comments, re.DOTALL)

    first_statement1 = ""
    first_statement2 = ""
    if match1:
        # Extract the first statement and replace line breaks and extra spaces inside the statement with regular expressions
        first_statement1 = re.sub(r'\s+', ' ', match1.group(1)).strip() + '{'


    if match2:
        # Extract the first statement and replace line breaks and extra spaces inside the statement with regular expressions
        first_statement2 = re.sub(r'\s+', ' ', match2.group(1)).strip() + ';'

    if first_statement1 == "":
        first_statement1 = code_without_comments.strip().split('\n')[0].strip()
    if first_statement2 == "":
        first_statement2 = code_without_comments.strip().split('\n')[0].strip()

    if len(first_statement1) == 0 and len(first_statement2) == 0:
        return None

    if len(first_statement1) == 0 and len(first_statement2) != 0:
        return first_statement2

    if len(first_statement1) != 0 and len(first_statement2) == 0:
        return first_statement1

    if len(first_statement1) > len(first_statement2):
        return first_statement2


    if len(first_statement1) < len(first_statement2):
        return first_statement1
    return first_statement1



if __name__ == '__main__':
    code_examples = [
        """
        CompilerFlagTranslator flagTranslator =
           new CompilerFlagTranslator(diagnosticGroups);
        config.setOptionsFromFlags(
           setRunOptions_options, flagTranslator, getInputCharset());
        """,

        """
        config.setOptionsFromFlags(setRunOptions_options,
           diagnosticGroups,
           !testMode);

        // If a Charset is specified, we must set it here.
        """,

        """
        FlagUsageException.checkFlags(config, diagnosticGroups);
        CompilerFlagTranslator.setOptionsFromFlags(config, options,
           diagnosticGroups);
        CompilerFlagTranslator.setOptionsToExtractProt
        """,

        """
        // Set the options directly from the flags.
        config.setOptionsForCompilationLevel(options);
        config.setOptionsForWarningLevel(options);
        config.setOptionsForTweaking(options);
        config.
        """,
        """
                    throw new UnresolvedForwardReference(p,
                        "Could not resolve Object Id ["+id+"] (for "+_beanType+").",
                        p.getCurrentLocation(), roid);
            }
            return pojo;
        """,
        """
                 .setLineNumber(entry.getSourceLine() + 1)
            .setColumnPosition(entry.getSourceColumn() + 1);

          if (entry.getNameId() != UNMAPPED) {
            x

        """,
        """
                return new BaseSettings(_classIntrospector, _annotationIntrospector, _visibilityChecker, _propertyNamingStrategy, _typeFactory,
                    _typeResolverBuilder, df, _handlerInstantiator, _locale,
                    _timeZone, _defaultBase64);
        }
        """,
        """
                        if (_deserialize(text, ctxt) != null) {
                    return _deserialize(text, ctxt);
                    }
                } catch (IllegalArgumentException iae) {
                    cause = iae;
        """,
        """
                throw new UnsupportedOperationException("Leaf Nodes do not have child nodes.");
        }
    }
        """
    ]
    import re

    first_statements = []

    for code in code_examples:
        first_statements.append(get_line_two(code))



    for i in range(len(first_statements)):
        print("complation:")
        print(code_examples[i])
        print("get line:")
        print(first_statements[i])
        print()





