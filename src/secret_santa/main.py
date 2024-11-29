import argparse
import numpy
import smtplib
import pathlib
from email.mime.text import MIMEText
import csv

# Email config
def get_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Randomly pairs a provided list of secret santa participants and sends each participant an email with their pairing."
    )
    parser.add_argument(
        "-i",
        "--input-file",
        type=pathlib.Path,
        required=True,
        help=(
            "The path to the input csv file containing participants."
            "Each line of the file must have the following format"
            "Full name, email address, dietary requirement (leave blank, after trailing comma if none)"
        )
    )
    parser.add_argument(
        "-d",
        "--exchange-date",
        type=str,
        required=True,
        help="The date at which gifts will be exchanged."
    )
    parser.add_argument(
        "-e",
        "--sender-email",
        type=str,
        required=False,
        help="The email address from which emails should be sent to recipients",
    )
    parser.add_argument(
        "-p",
        "--sender-password",
        type=str,
        required=False,
        help="The password for the email address from which emails should be sent to recipients",
    )
    parser.add_argument(
        "-o",
        "--output-file",
        type=pathlib.Path,
        required=False,
        help="The path to a file at which the pairing information should be stored.",
    )
    return parser

class Person():
    def __init__(self, name, email, diet):
        self.name = name
        self.firstname=self.name.split()[0]
        self.email = email
        self.diet=diet if diet else None
        self.recipient=None
        
    def __repr__(self):
        return "%s, %s, %s, %s"%(self.name, self.email, self.diet, self.recipient)
        

def main() -> None:
    parser = get_argument_parser()
    args = parser.parse_args()

    # Read in list of people from the provided csv
    people = []
    with open(args.input_file, newline='') as csvfile:
        people_reader = csv.reader(csvfile, delimiter=',')
        i = 0
        for row in people_reader:
            if (len(row) < 3):
                print("Incorrect row format at " + str(i) + ": " + ", ".join(row))
                exit(0)
            people.append(Person(row[0], row[1], row[2]))
            i += 1

    print("Found " + str(len(people)) + " people")

    index = numpy.arange(0,len(people), dtype=int)

    # Randomly assign people their secret santa
    trial = False
    while not trial:
    
        # create list and shuffle
        assignI = numpy.arange(0,len(people),1, dtype=int)
        numpy.random.shuffle(assignI)
    
        # see if anyone has themselves
        selection = numpy.where(index == assignI)
    
        if len(selection[0]) != 0:
            continue
    
        trial = True

    # create list of recipent
    for i in assignI:
        people[i].recipient=assignI[i]

    # save file to Text ?
    if args.output_file:
        # open file
        with open(args.output_file,'w') as fileOUT:
            line = "Buyer, Recipient \n"
            fileOUT.write(line)
            for p in people:
                line = p.name + ", " + people[p.recipient].name + "\n"
                fileOUT.write(line)

    # send e-mail to people
    for p in people:
        recip=people[p.recipient]
        dietry_requirements_line = (
            f"However, before you buy, please be aware {recip.firstname} "
            f"has some special requirements: {recip.diet}.\n\n" if recip.diet is not None else "\n\n"
        )
        
        messageText = (
            f"Dear {p.firstname},\n\n"

            f"Your secret santa is {recip.name}.\n\n"

            "As I'm really busy this year can you please buy them a gift for me, spending no more than £10. "
            f"The gifts will be exchanged at the Winter Social on {args.exchange_date}.\n\n"
            "When I'm shopping for presents, I like to spread even more joy by looking in a charity shop. "
            f"{dietry_requirements_line}"

            "Kind Regards,\n\n"
            "Father Christmas"
        )

        if args.sender_email:
            print("Sending E-mail To: ", p.name, " at ", p.email)
            msg = MIMEText(messageText)
            msg["Subject"] = "Secret Santa"
            msg["From"] = "Santa"
            msg["To"] = p.email
            s = smtplib.SMTP('smtp.gmail.com',587)
            s.ehlo()
            s.starttls()
            s.login(args.sender_email, args.sender_password)
            s.sendmail(args.sender_email,p.email, msg.as_string())
            s.quit()
            del(msg)
            print("....sent")


if __name__ == "__main__":
    main()
