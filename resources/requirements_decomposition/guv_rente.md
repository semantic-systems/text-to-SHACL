<b>Name</b>: Gesetzliche Unfallversicherung Rente

<b>IDLB</b>: B100019_LB_582404

<b>Addressee</b>: Lebenslagen für Bürgerinnen und Bürger

<b>Legal basis</b>: § 56 Sozialgesetzbuch Siebtes Buch (SGB VII)

<b>Description</b>: 

Wenn Sie nach einem Arbeitsunfall oder wegen einer Berufskrankheit in Ihrer
Erwerbsfähigkeit gemindert sind, erhalten Sie von der gesetzlichen
Unfallversicherung eine Rente.

<b>Requirements text</b>:

Wenn Sie gesetzlich unfallversichert sind, haben Sie unter folgenden
Voraussetzungen Anspruch auf Rente:

  * Ihre Erwerbsfähigkeit ist gemindert: 
    * infolge eines oder mehrerer Versicherungsfälle,
    * über die 26. Woche nach dem Versicherungsfall hinaus,
    * um mindestens 20 Prozent.

<b>Requirements decomposition</b>:

1. User has statutory accident insurance. (GREEN)
2. User had one OR more* insurance events** (YELLOW: definition of the terms in a legal sense must be inferred or explained):
    - accident at work OR 
    - a commuting accident OR
    - a recognized occupational disease.
3. The insurance event reduces earning capacity for more than 26 weeks after the event. (GREEN)
4. The reduction in earning capacity is at least 20%. (YELLOW: reduction of earning capacity in percentage must be inferred or explained)

*RED: multiple insurance events are too complex for SHACL Core, hence simplified to one event
**The types of statutory accident insurance events are known from other requirements texts and, in principle, accessible to the LLM via the ontology