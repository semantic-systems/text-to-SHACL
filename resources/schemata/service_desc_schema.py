"""  
service_desc_schema.py

Information about the possible values of datafields in the social service
descriptions, including:
- addressees: Maps plain text names of addressees to codes
- personal_matters: Maps plain text names of personal matters to codes
"""
from typing import Dict

addressees: Dict[str,str] = {
    "Geschäftslagen für Unternehmen": "2000000",
    "Lebenslagen für Bürgerinnen und Bürger": "1000000",
    "Bürger": "1000000",
    "Unternehmen": "2000000"
}

personal_matters: Dict[str,str] = {
    "Unternehmensstart und Gewerbezulassung": "2010000",
    "Arbeitgeber sein": "2030000",
    "Anlagen, Waren und Stoffe": "2120000",
    "Wahlen, Engagement und Beteiligung": "1100000",
    "Partnerschaft und Familie": "1020000",
    "Schule, Ausbildung und Studium": "1030000",
    "Ausweise und Dokumente": "1070000",
    "Arbeit": "1040000",
    "Steuern und Abgaben": "1060000",
    "Verbraucherschutz, Compliance und Recht": "2140000",
    "Migration und Integration": "1080000",
    "Auslandsgeschäft": "2070000",
    "Bauen und Wohnen": "1050000",
    "Mobilität und Fahrzeuge": "1090000",
    "Gesundheit und Vorsorge": "1130000",
    "Geschäftsauflösung und Unternehmensübergang": "2160000",
    "Geburt": "1010000",
    "Reisen und Auslandsaufenthalt": "1120000",
    "Sterbefall und Nachlass": "1190000",
    "Logistik und Transport": "2110000",
    "Abfall und Umweltschutz": "2130000",
    "Bauen und Immobilien": "2050000",
    "Register und Kataster": "2020000",
    "Finanzierung und Förderung": "2060000",
    "Hobby und Freizeit": "1110000",
    "Veranstaltungen": "2150000",
    "Recht und Verbraucherschutz": "1150000",
    "Statistik- und Berichtspflichten": "2090000",
    "Umwelt und Klima": "1170000",
    "Sozialleistungen": "1140000",
    "Notlagen und Opferhilfen": "1160000",
    "Forschung und Entwicklung": "2100000",
    "Altersvorsorge und Ruhestand": "1180000",
    "Ausschreibungen und öffentliche Aufträge": "2080000",
    "Fahrzeug und Verkehr": "1090000"
}