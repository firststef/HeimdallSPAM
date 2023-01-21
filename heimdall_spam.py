import os
import re
from heimdall_train import heimdall_classify, heimdall_decide, heimdall_decide_multi
from heimdall_utils import decode_mail, find_regexes

def check_suspicious_http(content):
    whitelisted_links = [
        "http://www.w3.org/1999/xhtml",
        "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd"
    ]
    for link in re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', content):
        if link not in whitelisted_links:
            return True
    return False

def stop_blacklisted_words(content):
    blacklisted_regexes = [
        re.compile(r"for\s?free", re.IGNORECASE),
        re.compile(r'viagra|cialis|phentermine|levitra', re.IGNORECASE),
        re.compile(r'earn\s?cash', re.IGNORECASE),
        re.compile(r'100%\s?free', re.IGNORECASE),
        re.compile(r'remove\s?(?:me|myself|my\semail)\s?(?:from\s?list|unsubscribe)', re.IGNORECASE),
        re.compile(r'Congratulations', re.IGNORECASE),
        re.compile(r'You\s?are\s?a\s?winner', re.IGNORECASE),
        re.compile(r'(?i)extra\s?income', re.IGNORECASE),
        re.compile(r'Work\s?from\s?home', re.IGNORECASE),
    ]
    return find_regexes(blacklisted_regexes, content)

def hd_filter_multi(folder):
    filenames = []
    contents = []
    for filename in os.listdir(folder):
        with open(f"{folder}/{filename}", 'r', errors="ignore") as f:
            filenames.append(filename)
            contents.append(decode_mail(f.read())) # decode base64
    
    verdicts = heimdall_decide_multi(contents)
    
    return [(filenames[i], verdicts[i]) for i in range(len(verdicts))]

def hd_filter(path):
    with open(path, 'r', errors="ignore") as f:
        content = f.read()
    aux = content

    content = decode_mail(content)

    score = 0
    if check_suspicious_http(content):
        score += 1
    
    if stop_blacklisted_words(content):
        score += 1

    # if heimdall_classify(content):
    #     score += 1

    if heimdall_decide(content):
        score += 3

    if score >= 3:
        return 'inf'

    return 'cln'