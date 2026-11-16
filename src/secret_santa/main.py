import argparse
import numpy as np
import smtplib
import pathlib
from email.mime.text import MIMEText
import csv
import getpass

def get_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Randomly pairs a provided list of secret santa participants and sends each participant an email with their pairing."
    )
    parser.add_argument(
        "-i",
        "--input-file",
        type=pathlib.Path,
        required=False,
        help=(
            "The path to the input csv file containing participants. "
            "Each line of the file must have the following format "
            "Full name, email address, gift preferences, gift restrictions. "
            "Gift preferences and restrictions may be blank but the "
            "commas preceding them must be present."
        )
    )
    parser.add_argument(
        "-x",
        "--exchange-info",
        type=str,
        required=False,
        help="The date, time and location of the gift exchange. Run with -m/--print-sample-message to see an example version of the final email.",
    )
    parser.add_argument(
        "-e",
        "--sender-email",
        type=str,
        required=False,
        help="The email address from which emails should be sent to recipients",
    )
    parser.add_argument(
        "-o",
        "--output-file",
        type=pathlib.Path,
        required=False,
        help="The path to a file at which the pairing information should be stored.",
    )
    parser.add_argument(
        "-m",
        "--print-sample-message",
        action="store_true",
        required=False,
        help="print a sample message.",
    )
    parser.add_argument(
        "-d",
        "--dry-run",
        action="store_true",
        required=False,
        help="Instead of sending emails, print all messages to the output file.",
    )

    return parser

class Person():
    def __init__(self, name, email, gift_preferences=None, gift_restrictions=None):
        self.name = name
        self.firstname=self.name.split()[0].capitalize()
        self.email = email
        self.gift_preferences = gift_preferences if gift_preferences else None
        self.gift_restrictions = gift_restrictions if gift_restrictions else None
        self.recipient=None
        
    def __repr__(self):
        return "%s, %s, %s, %s"%(self.name, self.email, self.gift_preferences, self.gift_restrictions, self.recipient)
        

def get_message_text(giver: Person, receiver: Person , args) -> str:
    gift_preferences_line = (
        f"Did you know that {receiver.firstname} and I are quite good friends? Anyway, when I asked them "
        "what gift they might enjoy, they told me:\n\n"
        f"   \"{receiver.gift_preferences}\"\n\n"
        if receiver.gift_preferences is not None
        else ""
    )
    
    gift_restrictions_line = (
        f"I then asked {receiver.firstname} if they have any dietary requirements or if there was anything "
        "they particularly dislike or would prefer not to receive. They said:\n\n"
        f"    \"{receiver.gift_restrictions}\".\n\n"
        if receiver.gift_restrictions is not None
        else ""
    )

    return (
        f"Dear {giver.firstname},\n\n"

        f"Your secret santa is {receiver.name}.\n\n"
        
        "As I'm really busy this year can you please buy them a gift for me, spending no more than "
        f"£10. The gifts will be exchanged at {args.exchange_info}.\n\n"
        
        f"{gift_preferences_line}"

        f"{gift_restrictions_line}"

        "Kind Regards,\n"
        "Father Christmas\n\n"

        "P.S. When I'm shopping for presents, I like to spread even more joy by looking in a charity shop. "
    )


def main() -> None:
    parser = get_arg_parser()
    args = parser.parse_args()

    sender_password = ""

    if args.print_sample_message:
        if not args.exchange_info:
            args.exchange_info = "Saturday 24 December at the North Pole"
        giver = Person(
            "Santa Claus",
            "s.claus@pole.north",
            gift_preferences="Traveling around the world really fast",
            gift_restrictions="Cookie only",
        )
        receiver = Person(
            "Rudolph R Reindeer",
            "rudolph.r.reindeer@pole.north",
            gift_preferences="If it's not carrots I'm not interested",
            gift_restrictions="I already said, carrots!",
        )
        print(get_message_text(giver, receiver, args))
        return
    
    if args.input_file is None:
        parser.error("the following argument is required: -i/--input-file")
    if args.exchange_info is None:
        parser.error("the following argument is required: -x/--exchange-info")
    if args.dry_run and args.output_file is None:
        parser.error("--output-file is required when using --dry-run")
    if not args.dry_run and not args.sender_email:
        parser.error("provide --sender-email to send emails, or use --dry-run")

    if args.sender_email is not None and args.dry_run is False:
        print(f"Emails will be sent from {args.sender_email}. Password is required.")
        sender_password = getpass.getpass()
        if not sender_password:
            print("A password must be provided")
            exit(0)

    # Read in list of people from the provided csv
    people = []
    with open(args.input_file, newline='') as csvfile:
        people_reader = csv.reader(csvfile, delimiter=',', skipinitialspace=True)
        for line_number, row in enumerate(people_reader, start=1):
            if len(row) != 4:
                parser.error(
                    f"incorrect CSV row at line {line_number}: expected 4 columns, got {len(row)}"
                )
            name = row[0].strip()
            email = row[1].strip()
            if not name:
                parser.error(f"missing name at CSV line {line_number}")
            if not email:
                parser.error(f"missing email address at CSV line {line_number}")

            people.append(
                Person(
                    name=name,
                    email=email,
                    gift_preferences=row[2].strip(),
                    gift_restrictions=row[3].strip(),
                )
            )

    if (len(people) < 3):
        print(f"You need at least 3 people for a secret santa gift swap. Found {len(people)}")
        exit(0)

    print("Found " + str(len(people)) + " people")

    index = np.arange(0,len(people), dtype=int)

    # Randomly assign people their secret santa
    trial = False
    while not trial:
    
        # create list and shuffle
        assignI = np.arange(0,len(people),1, dtype=int)
        np.random.shuffle(assignI)
    
        # see if anyone has themselves
        selection = np.where(index == assignI)
    
        if len(selection[0]) != 0:
            continue
    
        trial = True

    # create list of recipent
    for i in assignI:
        people[i].recipient=assignI[i]

    # save file to Text ?
    if args.output_file:
        # open file
        print(f"Saving pairings to {args.output_file}")
        with open(args.output_file,'w') as fileOUT:
            fileOUT.write("Pairings\n")
            fileOUT.write("---------------\n\n")
            fileOUT.write("Buyer, Recipient \n")
            for p in people:
                fileOUT.write(f"{p.name}, {people[p.recipient].name}\n")
            if args.dry_run:
                print(f"Saving dry run to {args.output_file}")
                fileOUT.write("\n--------------------------------------------------\n")
                fileOUT.write("\nSample messages\n")
                fileOUT.write("---------------\n\n")

    # send e-mail to people
    for p in people:
        recip=people[p.recipient]
        message_text = get_message_text(p, recip, args)

        msg = MIMEText(message_text)
        msg["Subject"] = "Secret Santa"
        msg["From"] = "Santa"
        msg["To"] = p.email
        if args.dry_run:
            with open(args.output_file,'a') as fileOUT:
                fileOUT.write(f"** Would have sent E-mail To: {p.name} at {p.email} **\n\n")
                fileOUT.write(message_text)
                fileOUT.write("\n\n--------------------------------------------------\n\n")

        elif args.sender_email:
            print("Sending E-mail To: ", p.name, " at ", p.email)
            s = smtplib.SMTP('smtp.gmail.com',587)
            s.ehlo()
            s.starttls()
            s.login(args.sender_email, sender_password)
            s.sendmail(args.sender_email, p.email, msg.as_string())
            s.quit()
            del(msg)
            print("....sent")
        else:
            print("Sender email not provided and dry run not specified")
            get_arg_parser().parse_args(["-h"])



if __name__ == "__main__":
    main()
