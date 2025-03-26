""" 
expected_validation_results.py

Dictionaries mapping file names of synthetic user profiles to the result
expected when they are validated against a syntactically and semantically
correct SHACL shapes graph.
"""

arbeitslosengeld_expected = {
    "B100019_LB_576842_1.ttl": "eligible",
    "B100019_LB_576842_2.ttl": "eligible",
    "B100019_LB_576842_3.ttl": "eligible",
    "B100019_LB_576842_4.ttl": "ineligible", 
    "B100019_LB_576842_5.ttl": "ineligible", # missing info
    "B100019_LB_576842_6.ttl": "ineligible", # missing info
    "B100019_LB_576842_7.ttl": "ineligible", 
    "B100019_LB_576842_8.ttl": "ineligible", # missing info
    "B100019_LB_576842_9.ttl": "ineligible",
    "B100019_LB_576842_10.ttl": "ineligible", # missing info
    "B100019_LB_576842_11.ttl": "ineligible",
    "B100019_LB_576842_12.ttl": "ineligible", # missing info
}

kinderzuschlag_expected = {
    "B100019_LB_581863_1.ttl": "eligible",
    "B100019_LB_581863_2.ttl": "eligible",
    "B100019_LB_581863_3.ttl": "eligible",
    "B100019_LB_581863_4.ttl": "eligible",
    "B100019_LB_581863_5.ttl": "eligible",
    "B100019_LB_581863_6.ttl": "ineligible", # missing info
    "B100019_LB_581863_7.ttl": "ineligible",
    "B100019_LB_581863_8.ttl": "ineligible",
    "B100019_LB_581863_9.ttl": "ineligible",
    "B100019_LB_581863_10.ttl": "ineligible",
    "B100019_LB_581863_11.ttl": "ineligible",
    "B100019_LB_581863_12.ttl": "ineligible",
    "B100019_LB_581863_13.ttl": "ineligible",
    "B100019_LB_581863_14.ttl": "ineligible",
    "B100019_LB_581863_15.ttl": "ineligible",
    "B100019_LB_581863_16.ttl": "ineligible",
    "B100019_LB_581863_17.ttl": "ineligible", # missing info
    "B100019_LB_581863_18.ttl": "ineligible", # missing info
    "B100019_LB_581863_19.ttl": "ineligible", # missing info
    "B100019_LB_581863_20.ttl": "ineligible", # missing info
}

buergergeld_expected = {
    "B100019_LB_106311931_1.ttl": "eligible",
    "B100019_LB_106311931_2.ttl": "eligible",
    "B100019_LB_106311931_3.ttl": "eligible",
    "B100019_LB_106311931_4.ttl": "eligible",
    "B100019_LB_106311931_5.ttl": "ineligible",
    "B100019_LB_106311931_6.ttl": "ineligible",
    "B100019_LB_106311931_7.ttl": "ineligible",
    "B100019_LB_106311931_8.ttl": "ineligible",
    "B100019_LB_106311931_9.ttl": "ineligible",
    "B100019_LB_106311931_10.ttl": "ineligible", # missing info
    "B100019_LB_106311931_11.ttl": "ineligible", # missing info
    "B100019_LB_106311931_12.ttl": "ineligible", # missing info
    "B100019_LB_106311931_13.ttl": "ineligible", # missing info
    "B100019_LB_106311931_14.ttl": "ineligible", # missing info
    "B100019_LB_106311931_15.ttl": "ineligible",
    "B100019_LB_106311931_16.ttl": "ineligible", # missing info
}

insolvenzgeld_expected = {
    "B100019_LB_576848_1.ttl": "eligible",
    "B100019_LB_576848_2.ttl": "eligible",
    "B100019_LB_576848_3.ttl": "eligible",
    "B100019_LB_576848_4.ttl": "eligible",
    "B100019_LB_576848_5.ttl": "eligible",
    "B100019_LB_576848_6.ttl": "ineligible",
    "B100019_LB_576848_7.ttl": "ineligible",
    "B100019_LB_576848_8.ttl": "ineligible",
    "B100019_LB_576848_9.ttl": "ineligible",
    "B100019_LB_576848_10.ttl": "ineligible",
    "B100019_LB_576848_11.ttl": "ineligible", # missing info
    "B100019_LB_576848_12.ttl": "ineligible", # missing info
    "B100019_LB_576848_13.ttl": "ineligible", # missing info
    "B100019_LB_576848_14.ttl": "ineligible",
    "B100019_LB_576848_15.ttl": "ineligible", # missing info
}

kinderzuschlag_expected = {
    "B100019_LB_576986_1.ttl": "eligible",
    "B100019_LB_576986_2.ttl": "eligible",
    "B100019_LB_576986_3.ttl": "eligible",
    "B100019_LB_576986_4.ttl": "eligible",
    "B100019_LB_576986_5.ttl": "eligible",
    "B100019_LB_576986_6.ttl": "eligible",
    "B100019_LB_576986_7.ttl": "eligible",
    "B100019_LB_576986_8.ttl": "eligible",
    "B100019_LB_576986_9.ttl": "eligible",
    "B100019_LB_576986_10.ttl": "ineligible",
    "B100019_LB_576986_11.ttl": "ineligible",
    "B100019_LB_576986_12.ttl": "ineligible",
    "B100019_LB_576986_13.ttl": "ineligible",
    "B100019_LB_576986_14.ttl": "ineligible",
    "B100019_LB_576986_15.ttl": "ineligible", # missing info
    "B100019_LB_576986_16.ttl": "ineligible",
    "B100019_LB_576986_17.ttl": "ineligible",
    "B100019_LB_576986_18.ttl": "ineligible",
    "B100019_LB_576986_19.ttl": "ineligible",
    "B100019_LB_576986_20.ttl": "ineligible",
    "B100019_LB_576986_21.ttl": "ineligible",
    "B100019_LB_576986_22.ttl": "eligible",
    "B100019_LB_576986_23.ttl": "ineligible",
    "B100019_LB_576986_24.ttl": "eligible",
}

guv_rente_expected = {
    "B100019_LB_582404_1.ttl": "eligible",
    "B100019_LB_582404_2.ttl": "eligible",
    "B100019_LB_582404_3.ttl": "eligible",
    "B100019_LB_582404_4.ttl": "eligible",
    "B100019_LB_582404_5.ttl": "eligible",
    "B100019_LB_582404_6.ttl": "eligible",
    "B100019_LB_582404_7.ttl": "ineligible",
    "B100019_LB_582404_8.ttl": "ineligible",
    "B100019_LB_582404_9.ttl": "ineligible",
    "B100019_LB_582404_10.ttl": "ineligible",
    "B100019_LB_582404_11.ttl": "ineligible",
    "B100019_LB_582404_12.ttl": "ineligible", # missing info
    "B100019_LB_582404_13.ttl": "ineligible", # missing info
    "B100019_LB_582404_14.ttl": "ineligible", # missing info
}

uebergangsgeld_berufliche_reha_expected = {
    "B100019_LB_582422_1.ttl": "eligible",
    "B100019_LB_582422_2.ttl": "eligible",
    "B100019_LB_582422_3.ttl": "eligible",
    "B100019_LB_582422_4.ttl": "eligible",
    "B100019_LB_582422_5.ttl": "eligible",
    "B100019_LB_582422_6.ttl": "ineligible",
    "B100019_LB_582422_7.ttl": "ineligible",
    "B100019_LB_582422_8.ttl": "ineligible",
    "B100019_LB_582422_9.ttl": "ineligible", # missing info
    "B100019_LB_582422_10.ttl": "ineligible", # missing info
    "B100019_LB_582422_11.ttl": "ineligible", # missing info
}

guv_verletztengeld_expected = {
    "B100019_LB_582429_1.ttl": "eligible",
    "B100019_LB_582429_2.ttl": "eligible",
    "B100019_LB_582429_3.ttl": "eligible",
    "B100019_LB_582429_4.ttl": "eligible",
    "B100019_LB_582429_5.ttl": "eligible",
    "B100019_LB_582429_6.ttl": "ineligible",
    "B100019_LB_582429_7.ttl": "ineligible",
    "B100019_LB_582429_8.ttl": "ineligible",
    "B100019_LB_582429_9.ttl": "ineligible", # missing info
    "B100019_LB_582429_10.ttl": "ineligible", # missing info
}

guv_witwenrente = {
    "B100019_LB_582441_1.ttl": "eligible",
    "B100019_LB_582441_2.ttl": "eligible",
    "B100019_LB_582441_3.ttl": "eligible",
    "B100019_LB_582441_4.ttl": "eligible",
    "B100019_LB_582441_5.ttl": "eligible",
    "B100019_LB_582441_6.ttl": "ineligible",
    "B100019_LB_582441_7.ttl": "ineligible",
    "B100019_LB_582441_8.ttl": "ineligible",
    "B100019_LB_582441_9.ttl": "ineligible", # missing info
    "B100019_LB_582441_10.ttl": "ineligible", # missing info
    "B100019_LB_582441_11.ttl": "ineligible", # missing info
}

guv_waisenrente = {
    "B100019_LB_582435_1.ttl": "eligible",
    "B100019_LB_582435_2.ttl": "eligible",
    "B100019_LB_582435_3.ttl": "eligible",
    "B100019_LB_582435_4.ttl": "eligible",
    "B100019_LB_582435_5.ttl": "eligible",
    "B100019_LB_582435_6.ttl": "eligible",
    "B100019_LB_582435_7.ttl": "eligible",
    "B100019_LB_582435_8.ttl": "ineligible",
    "B100019_LB_582435_9.ttl": "ineligible",
    "B100019_LB_582435_10.ttl": "ineligible",
    "B100019_LB_582435_11.ttl": "ineligible",
    "B100019_LB_582435_12.ttl": "ineligible",
    "B100019_LB_582435_13.ttl": "ineligible",
    "B100019_LB_582435_14.ttl": "ineligible", # missing info
    "B100019_LB_582435_15.ttl": "ineligible", # missing info
    "B100019_LB_582435_16.ttl": "ineligible", # missing info
    "B100019_LB_582435_17.ttl": "ineligible", # missing info
    "B100019_LB_582435_18.ttl": "ineligible", # missing info
    "B100019_LB_582435_19.ttl": "eligible",
    "B100019_LB_582435_20.ttl": "ineligible",
}

bildung_und_teilhabe = {
    "L100040_LB_12280162_1.ttl": "eligible",
    "L100040_LB_12280162_2.ttl": "eligible",
    "L100040_LB_12280162_3.ttl": "eligible",
    "L100040_LB_12280162_4.ttl": "eligible",
    "L100040_LB_12280162_5.ttl": "eligible",
    "L100040_LB_12280162_6.ttl": "ineligible",
    "L100040_LB_12280162_7.ttl": "ineligible",
    "L100040_LB_12280162_8.ttl": "ineligible",
    "L100040_LB_12280162_9.ttl": "ineligible", # missing info
    "L100040_LB_12280162_10.ttl": "ineligible", # missing info
    "L100040_LB_12280162_11.ttl": "ineligible", # missing info
}

ausbildungsgeld_expected = {
    "B100019_LB_574711_1.ttl": "eligible",
    "B100019_LB_574711_2.ttl": "eligible",
    "B100019_LB_574711_3.ttl": "eligible",
    "B100019_LB_574711_4.ttl": "ineligible",
    "B100019_LB_574711_5.ttl": "ineligible",
    "B100019_LB_574711_6.ttl": "ineligible",
    "B100019_LB_574711_7.ttl": "ineligible",
    "B100019_LB_574711_8.ttl": "ineligible", # missing info
    "B100019_LB_574711_9.ttl": "ineligible", # missing info
    "B100019_LB_574711_10.ttl": "ineligible", # missing info
}

einstiegsgeld_expected = {
    "B100019_LB_102713860_1.ttl": "eligible",
    "B100019_LB_102713860_2.ttl": "eligible",
    "B100019_LB_102713860_3.ttl": "eligible",
    "B100019_LB_102713860_4.ttl": "ineligible", # missing info
    "B100019_LB_102713860_5.ttl": "ineligible",
}

uebergangsgeld_behinderung_expected = {
    "B100019_LB_102716305_1.ttl": "eligible",
    "B100019_LB_102716305_2.ttl": "eligible",
    "B100019_LB_102716305_3.ttl": "eligible",
    "B100019_LB_102716305_4.ttl": "eligible",
    "B100019_LB_102716305_5.ttl": "eligible",
    "B100019_LB_102716305_6.ttl": "eligible",
    "B100019_LB_102716305_7.ttl": "ineligible",
    "B100019_LB_102716305_8.ttl": "ineligible",
    "B100019_LB_102716305_9.ttl": "ineligible",
    "B100019_LB_102716305_10.ttl": "ineligible",
    "B100019_LB_102716305_11.ttl": "ineligible",
    "B100019_LB_102716305_12.ttl": "ineligible",
    "B100019_LB_102716305_13.ttl": "ineligible",
    "B100019_LB_102716305_14.ttl": "ineligible",
    "B100019_LB_102716305_15.ttl": "ineligible", # missing info
    "B100019_LB_102716305_16.ttl": "ineligible", # missing info
    "B100019_LB_102716305_17.ttl": "ineligible", # missing info
    "B100019_LB_102716305_18.ttl": "ineligible", # missing info
    "B100019_LB_102716305_19.ttl": "ineligible", # missing info
    "B100019_LB_102716305_20.ttl": "ineligible", # missing info
    "B100019_LB_102716305_21.ttl": "ineligible", # missing info
    "B100019_LB_102716305_22.ttl": "ineligible",
    "B100019_LB_102716305_23.ttl": "ineligible", # missing info
}

grundausbildung_expected = {
    "B100019_LB_102717659_1.ttl": "eligible",
    "B100019_LB_102717659_2.ttl": "eligible",
    "B100019_LB_102717659_3.ttl": "eligible",
    "B100019_LB_102717659_4.ttl": "eligible",
    "B100019_LB_102717659_5.ttl": "eligible",
    "B100019_LB_102717659_6.ttl": "ineligible",
    "B100019_LB_102717659_7.ttl": "ineligible",
    "B100019_LB_102717659_8.ttl": "ineligible",
    "B100019_LB_102717659_9.ttl": "ineligible",
    "B100019_LB_102717659_10.ttl": "ineligible",
    "B100019_LB_102717659_11.ttl": "ineligible",
    "B100019_LB_102717659_12.ttl": "ineligible", # missing info
    "B100019_LB_102717659_13.ttl": "ineligible", # missing info
    "B100019_LB_102717659_14.ttl": "ineligible", # missing info
    "B100019_LB_102717659_15.ttl": "ineligible", # missing info
    "B100019_LB_102717659_16.ttl": "ineligible", # missing info
}

guv_kinderverletztengeld_expected = {
    "B100019_LB_102799515_1.ttl": "eligible",
    "B100019_LB_102799515_2.ttl": "eligible",
    "B100019_LB_102799515_3.ttl": "eligible",
    "B100019_LB_102799515_4.ttl": "eligible",
    "B100019_LB_102799515_5.ttl": "ineligible",
    "B100019_LB_102799515_6.ttl": "ineligible",
    "B100019_LB_102799515_7.ttl": "ineligible", # missing info
    "B100019_LB_102799515_8.ttl": "ineligible",
    "B100019_LB_102799515_9.ttl": "ineligible",
    "B100019_LB_102799515_10.ttl": "ineligible",
    "B100019_LB_102799515_11.ttl": "ineligible",
    "B100019_LB_102799515_12.ttl": "ineligible", # missing info
    "B100019_LB_102799515_13.ttl": "ineligible", # missing info
}

grundsicherung_expected = {
    "L100040_LB_8664880_1.ttl": "eligible",
    "L100040_LB_8664880_2.ttl": "eligible",
    "L100040_LB_8664880_3.ttl": "eligible",
    "L100040_LB_8664880_4.ttl": "eligible",
    "L100040_LB_8664880_5.ttl": "eligible",
    "L100040_LB_8664880_6.ttl": "ineligible",
    "L100040_LB_8664880_7.ttl": "ineligible",
    "L100040_LB_8664880_8.ttl": "ineligible",
    "L100040_LB_8664880_9.ttl": "ineligible",
    "L100040_LB_8664880_10.ttl": "ineligible",
    "L100040_LB_8664880_11.ttl": "ineligible",
    "L100040_LB_8664880_12.ttl": "ineligible",
    "L100040_LB_8664880_13.ttl": "ineligible",
    "L100040_LB_8664880_14.ttl": "eligible",
    "L100040_LB_8664880_15.ttl": "eligible",
    "L100040_LB_8664880_16.ttl": "ineligible", # missing info
    "L100040_LB_8664880_17.ttl": "ineligible", # missing info
    "L100040_LB_8664880_18.ttl": "ineligible", # missing info
    "L100040_LB_8664880_19.ttl": "ineligible", # missing info
    "L100040_LB_8664880_20.ttl": "ineligible", # missing info
    "L100040_LB_8664880_21.ttl": "ineligible", # missing info
    "L100040_LB_8664880_22.ttl": "ineligible", # missing info
}

aktivierung_und_eingliederung_expected = {
    "B100019_LB_102730340_1.ttl": "eligible",
    "B100019_LB_102730340_2.ttl": "eligible",
    "B100019_LB_102730340_3.ttl": "ineligible",
    "B100019_LB_102730340_4.ttl": "ineligible", # missing info
}

guv_rentenabfindung_expected = {
    "B100019_LB_102799525_1.ttl": "eligible",
    "B100019_LB_102799525_2.ttl": "eligible",
    "B100019_LB_102799525_3.ttl": "eligible",
    "B100019_LB_102799525_4.ttl": "ineligible",
    "B100019_LB_102799525_5.ttl": "ineligible",
    "B100019_LB_102799525_6.ttl": "ineligible",
    "B100019_LB_102799525_7.ttl": "ineligible", # missing info
    "B100019_LB_102799525_8.ttl": "ineligible", # missing info
    "B100019_LB_102799525_9.ttl": "ineligible", # missing info
}

berufsausbildungsbeihilfe_expected = {
    "B100019_LB_574724_1.ttl": "eligible",
    "B100019_LB_574724_2.ttl": "eligible",
    "B100019_LB_574724_3.ttl": "eligible",
    "B100019_LB_574724_4.ttl": "eligible",
    "B100019_LB_574724_5.ttl": "eligible",
    "B100019_LB_574724_6.ttl": "eligible",
    "B100019_LB_574724_7.ttl": "eligible",
    "B100019_LB_574724_8.ttl": "eligible",
    "B100019_LB_574724_9.ttl": "eligible",
    "B100019_LB_574724_10.ttl": "eligible",
    "B100019_LB_574724_11.ttl": "eligible",
    "B100019_LB_574724_12.ttl": "eligible",
    "B100019_LB_574724_13.ttl": "ineligible",
    "B100019_LB_574724_14.ttl": "ineligible",
    "B100019_LB_574724_15.ttl": "ineligible",
    "B100019_LB_574724_16.ttl": "ineligible",
    "B100019_LB_574724_17.ttl": "ineligible",
    "B100019_LB_574724_18.ttl": "ineligible",
    "B100019_LB_574724_19.ttl": "ineligible",
    "B100019_LB_574724_20.ttl": "ineligible",
    "B100019_LB_574724_21.ttl": "ineligible",
    "B100019_LB_574724_22.ttl": "ineligible",
    "B100019_LB_574724_23.ttl": "ineligible",
    "B100019_LB_574724_24.ttl": "ineligible",
    "B100019_LB_574724_25.ttl": "ineligible",
    "B100019_LB_574724_26.ttl": "ineligible",
    "B100019_LB_574724_27.ttl": "ineligible",
    "B100019_LB_574724_28.ttl": "ineligible",
    "B100019_LB_574724_29.ttl": "ineligible",
}