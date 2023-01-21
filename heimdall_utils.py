import re
import base64

def find_regexes(regexes, string):
    for regex in regexes:
        if re.search(regex, string):
            return True
    return False

def decode_mail(mail):
    #pattern = re.compile(r"(?:[A-Za-z0-9+/]{4})*(?:[A-Za-z0-9+/][AQgw]==|[A-Za-z0-9+/]{2}[AEIMQUYcgkosw048]=)?")
    pattern = re.compile(r"[a-zA-Z0-9/\r\n+]*={0,2}")
    matches = pattern.finditer(mail)

    decoded_mail = ""

    last_end = 0
    for match in matches:
        # Get the start and end indices of the match
        start, end = match.span()
        if end - start <= 20:
            continue  # probably not a base64 string

        # Append the text before the match to the decoded mail
        decoded_mail += mail[last_end:start]
        # Decode the base64-encoded string
        try:
            decoded_mail += base64.b64decode(match.group()).decode("utf-8")
            # print(1, name, match.group(), base64.b64decode(match.group()).decode("utf-8"))
        except (base64.binascii.Error, UnicodeDecodeError):
            decoded_mail += match.group()
        # Update the last end index
        last_end = end

    decoded_mail += mail[last_end:]

    return decoded_mail