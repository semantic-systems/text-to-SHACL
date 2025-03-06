<b>Name</b>: Gesetzliche Unfallversicherung Waisenrente

<b>IDLB</b>: B100019_LB_582435

<b>Addressee</b>: Lebenslagen für Bürgerinnen und Bürger

<b>Legal basis</b>: § 68 Sozialgesetzbuch Siebtes Buch (SGB VII); § 70 Sozialgesetzbuch Siebtes Buch (SGB VII); § 67 Sozialgesetzbuch Siebtes Buch (SGB VII)

<b>Description</b>: 

Wenn Ihr Elternteil infolge eines Versicherungsfalls gestorben ist, erhalten
Sie unter bestimmten Voraussetzungen eine Waisenrente von der gesetzlichen
Unfallversicherung.

<b>Requirements text</b>:

Sie erhalten die Waisenrente, wenn die Person infolge eines Versicherungsfalls
gestorben ist. Dazu gehören Arbeitsunfälle, Unfälle auf dem Arbeitsweg und
Berufskrankheiten.

Sie erhalten die Waisenrente als

  * leibliches Kind,
  * Stiefkind oder Pflegekind, wenn Sie im Haushalt der verstorbenen Person gelebt haben und dort versorgt und betreut wurden und als
  * Enkel oder Geschwisterteil, wenn Sie im Haushalt der verstorbenen Person gelebt haben und dort versorgt und betreut wurden.
  * Sie können zudem die Waisenrente erhalten, wenn die verstorbene Person überwiegend für Ihren Lebensunterhalt aufgekommen ist.

Unter diesen Voraussetzungen erhalten Sie die Waisenrente auch dann, wenn Sie
18 bis unter 27 Jahre alt sind:

  * Sie befinden sich in Schul- oder Berufsausbildung oder
  * Sie können wegen einer körperlichen, geistigen oder seelischen Behinderung nicht selbst für Ihren Unterhalt aufkommen oder
  * Sie befinden sich in einer Übergangszeit von höchstens 4 Kalendermonaten 
    * zwischen einem Ausbildungsabschnitt und dem nächsten Ausbildungsabschnitt oder
    * der Ableistung des gesetzlichen Wehr- oder Zivildienstes oder
    * der Ableistung eines freiwilligen Dienstes.

<b>Requirements decomposition</b>:

1. A person died with whom the user had one of the following relationships: (GREEN)
  - the user was the person's natural child (GREEN) OR
  - lived in the same household as the deceased person (GREEN) AND was cared for there (RED: unclear how his is different from living in the household) AND was the person's
    - stepchild (GREEN) OR 
    - foster child (GREEN) OR 
    - grandchild (GREEN) OR
  - the deceased person had the main responsibility for the user's living expenses (YELLOW: meaning of main responsibility in a legal sense must be inferred or explained)
2. The person who died had statutory accident insurance. (GREEN)
3. The cause of death was an insurance event (YELLOW: definition of the terms in a legal sense must be inferred or explained):
  - accident at work OR 
  - a commuting accident OR
  - a recognized occupational disease.
4. User is 
  - younger than 18 years (GREEN) OR
  - younger than 27 years (GREEN) AND
    - in school (GREEN) OR
    - in vocational training (GREEN) OR
    - cannot support themselves because of a disability (YELLOW: how this is defined legally must be inferred or explained) OR
    - in a transitional period of 4 calendar months or less between one formal education AND
      - another formal education OR
      - the completion of compulsory military service OR 
      - the completion of community service OR
      - the completion of a voluntary service
      (RED: too complex for SHACL Core because it requires arithmetics)