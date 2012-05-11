import sys, traceback, inspect

def traceit(frame, event, arg):
    if event == "call":
        stack = traceback.extract_stack(frame)
        filename, linenumber, funcname, text = stack[-1]
        args = inspect.getargvalues(frame)
        indent = len(stack) * " "
        print "%s%s%s" % (indent, funcname, inspect.formatargvalues(*args))

    return traceit
