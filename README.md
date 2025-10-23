# Secret Santa

This tool is a secret santa name randomiser. It reads, from a csv file, a
list of would be Santas along with their email address and any dietary/present
preference they may have. This file should be of the following format.

```csv
Santa Claus, s.claus@pole.north, Cookie only
Mrs Claus, m.claus@pole.north, Please! no cookies
Rudolph R Reindeer, rudolph.r.reindeer@pole.north, If it's not carrots I'm not interested
Head Elf, elf.1@pole.north, 
```

> Note that `Head Elf` has no special requirements but a `,` must be included after their email.


## Usage

Install the package using uv, pip, etc

```sh
uv venv
uv pip install -e .
```

Then you can run the randomiser like so

```sh
uv run secret_santa -h
```

### Sending emails

Once Santas have been matched into pairs, emails can then be sent to inform
each of their chosen giftee. To do this whithout revealing the pairings to
the organiser, emails can be automatically sent using this tool.

To do this, we integrate with smtp.gmail.com. Therefore, the origin email
address, from which emails will be sent to each santa, must be a gmail account.
You will also need to provide an
[app password](https://support.google.com/mail/answer/185833?sjid=13223121393469617058-EU)
for that account. You will be prompted to provide this before emails are sent.

## Keeping the secret

This tool endeavours to make it easy for the organiser to remain ignorant of the
final pairings. However, this requires them not to look at the emails sent from
their gmail account.

If you wish to save a copy of the final pairings in an easier format, there is an
option to output the name pairs to a csv file. See the help (`-h/--help`) for details 
