<b>Name</b>: Rente gesetzliche Unfallversicherung

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

1. User has statutory accident insurance. (G)
2. User experienced one or more events covered by the statutory accident insurance. (Y: which events are covered must be resolved elsewhere, simplified to "User experienced an insurance event" because we cannot sum over multiple events with SHACL Core.)
3. The insurance event reduced earning capacity for more than 26 weeks after the event. (Y: how to establish if earning capacity is reduced must be resolved elsewhere)
4. The reducation in earning capacity was at least 20%. (Y: how to establish the percentage of reduction must be resolved elsewhere)