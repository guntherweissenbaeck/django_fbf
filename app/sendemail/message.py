def messagebody(date, bird, place, diagnosis,) -> str:
    """Returns the body of the message to be sent to UNB."""
    body = f"""
        Sehr geehrte Damen und Herren,

        am {date} wurde in der NABU Wildvogelhilfe ein Vogel der Art {bird} aufgenomen.
        Der Fundort laut Finder*in war: {place}.
        Die Diagnose bei Fund lautet: {diagnosis}.

        Mit freundlichen Grüßen

        NABU Wildvogelhilfe Jena
        Untergliederung des
        NABU Kreisverband Jena e.V.
        Schillergässchen 5
        07745 Jena
        """
    return body
