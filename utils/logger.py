import logging

f = open("lists/attention.txt", "a", encoding="utf-8")


def special_attention(s: str):
    f.write(s)
    f.flush()
