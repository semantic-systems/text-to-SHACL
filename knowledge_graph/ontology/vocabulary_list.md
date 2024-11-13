# Ontology Vocabulary List

**Note**: The ontology is intended to conceptualize social service descriptions from the perspective of user profiles. It is not intended to capture the logic of the SHACL shapes graphs derived from the social service descriptions. Thus, when passing the ontology as context to an LLM, it can reuse the datafields that serve as building blocks for user profiles (otherwise we could not control the modelling depth and no meaningful comparison or validation would be possible) but it cannot simply copy the constraint logic used in the groundtruth.


## Classes (Subclasses)

- ff:Person (ff:User, ff:Child)
- ff:MaritalStatus

## Object properties (Domain, Range)

- ff:hasChild (ff:Person, ff:Child)
- ff:hasMaritalStatus (ff:Person, ff:MaritalStatus)

## Data properties (Domain, Range)

- ff:hasAge (ff:Person, Literal^^xsd:integer)
- ff:livesWithUser (ff:Person, Literal^^xsd:boolean)
- ff:receivesChildBenefit (ff:Child, Literal^^xsd:float)
- ff:singleParent (ff:Person, Literal^^xsd:boolean)

## Annotation properties

## Individuals (instance of this class)

- ff:single (ff:MaritalStatus)
- ff:married (ff:MaritalStatus)
- ff:registeredPartnership (ff:MaritalStatus)
- ff:divorced (ff:MaritalStatus)
- ff:widowed (ff:MaritalStatus)
