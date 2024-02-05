# the message body for the email should have placeholders for the bird name, the date found and the diagnosis


def messagebody(
    date,
    bird,
    place,
    diagnosis,
) -> str:
    text = f"""
        Guten Tag,

        am {date} wurde in der NABU Wildvogelhilfe ein Vogel der Art {bird} aufgenomen.
        Der Fundort laut Finder*in war: {place}
        Die Diagnose bei Fund lautet: {diagnosis}

        Mit freundlichen Grüßen

        NABU Wildvogelhilfe Jena
        Untergliederung des
        NABU Kreisverband Jena e.V.
        Schillergässchen 5
        07745 Jena
        """
    return text
