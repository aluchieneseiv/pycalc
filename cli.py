from newlang import State

state = State()

while True:
    s = input('> ')

    if s.startswith('/'):
        if s == '/exit':
            break
        elif s == '/vars':
            for k, v in state.ctx.dict.items():
                print(f'{k} =')
                print(v)
                print()
        elif s.startswith('/clear'):
            args = s.split(' ')
            args.pop(0)

            if args:
                for name in args:
                    if name in state.ctx.dict:
                        del state.ctx.dict[name]

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
        else:
            print(val)
