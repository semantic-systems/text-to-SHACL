""" 
expected_resits.py

Dictionaries mapping file names of synthetic user profiles to the result
expected when they are validated against a syntactically and semantically
correct SHACL shapes graph.
"""

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