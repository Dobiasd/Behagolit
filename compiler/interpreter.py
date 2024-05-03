from typing import List

from parser import Definition, Call


def interpret(ast: List[Definition]):
    mains = list(filter(lambda d: d.name == "main", ast))
    assert len(mains) == 1
    main = mains[0].expression
    assert isinstance(main, Call)
    main_call: Call = main
    buildin_functions = {"printLine": print}
    buildin_functions[main_call.function].__call__(*main.args)
    pass
