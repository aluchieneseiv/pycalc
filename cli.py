from newlang import State, NoOutput

state = State()

while True:
    s = input('> ')

    if s.startswith('/'):
        if s == '/exit':
            break
        elif s == '/vars':
            for k, v in state.ctx.var_map.items():
                print(f'{k} =')
                print(v)
                print()
        elif s.startswith('/clear'):
            args = s.split(' ')
            args.pop(0)

            if args:
                for name in args:
                    if name in state.ctx.var_map:
                        del state.ctx.var_map[name]

                print(f'Cleared vars: {", ".join(args)}')
            else:
                state.ctx.clear()
                print("Cleared all vars")
        else:
            print(f"Unknown command: {s}")
    else:
        val, err = state.parse(s)

        if err:
            print("Error:")
            print(err)
        elif val is not NoOutput:
            print(val)
