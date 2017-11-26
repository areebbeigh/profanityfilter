import argparse
from sys import exit

from profanityfilter import ProfanityFilter

pf = ProfanityFilter()


def main():
    parser = argparse.ArgumentParser(description='Profanity filter console utility')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-t', '--text', dest='text', help='Test the given text for profanity')
    group.add_argument('-f', '--file', dest='path', help='Test the given file for profanity')
    parser.add_argument('-o', '--output', dest='output_file', help='Write the censored output to a file')
    parser.add_argument('--show', action='store_true', help='Print the censored text')

    args = parser.parse_args()

    if args.text and args.path:
        parser.print_help()
        exit()

    if args.text:
        text = args.text
    elif args.path:
        with open(args.path, 'r') as f:
            text = "".join(f.readlines())

    censored_text = pf.censor(text)

    if args.output_file:
        with open(args.output_file, 'w') as f:
            f.write(censored_text)
        print("Censored text written to output file at: " + args.output_file)

    if args.show:
        print("Censored text:\n")
        print(censored_text)

    if args.show or args.output_file:
        return

    if pf.is_clean(text):
        print("This text is clean.")
    else:
        print("This text is not clean!")

if __name__ == "__main__":
    main()
