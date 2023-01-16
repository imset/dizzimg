if __name__ == "__main__":
    import argparse
    from dizzimg import smash, tiles

    parser = argparse.ArgumentParser(description='Here be descriptions')
    parser.add_argument('type', type=str)
    parser.add_argument('--top', '-t', default="Top Text")
    parser.add_argument('--bot', '--bottom', '-b', default="Bottom Text")
    parser.add_argument('--base', default="./data/img/newcomer.png")
    parser.add_argument('--output', default="")
    parser.add_argument('--input', '-i', default="./data/img/vegeta.png")
    parser.add_argument('--slices', '-s', type=int, default=None)
    parser.add_argument('--bgcolor', '-bgc', default=None)
    parser.add_argument('--space', '-sp', type=int, default=0)
    parser.add_argument('--style', '-st', default="square")
    parser.add_argument('--rotate', '-r', type=int, default=0)

    args = parser.parse_args()


    if args.type.lower() == "smash":
        image = smash.Newcomer(toptext=args.top, bottext=args.bot, baseimg=args.base, topimg=args.input)
    elif args.type.lower() == "tiles":
        image = tiles.TileFilter(image=args.input, style=args.style, size=args.slices, bgcolor=args.bgcolor, space=args.space, rotation=args.rotate)
    else:
        print("Error: Unknown type")
        exit()

    if args.output == "":
        image.generate(show=True)
    else:
        image.generate(save=True, name=args.output)