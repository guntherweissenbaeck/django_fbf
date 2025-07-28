def messagebody(date, bird, place, diagnosis, patient_identifier=None) -> str:
    """Returns the body of the message to be sent to UNB."""
    identifier_text = f" (Kennung: {patient_identifier})" if patient_identifier else ""
    
    body = f"""
Sehr geehrte Damen und Herren,

am {date} wurde in der NABU Wildvogelhilfe ein Vogel der Art {bird} aufgenommen{identifier_text}.
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
