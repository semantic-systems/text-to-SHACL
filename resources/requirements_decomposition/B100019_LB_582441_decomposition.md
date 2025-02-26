<b>Name</b>: Witwen- und Witwerrente

<b>IDLB</b>: B100019_LB_582441

<b>Addressee</b>: Lebenslagen für Bürgerinnen und Bürger

<b>Legal basis</b>: § 65 Sozialgesetzbuch Siebtes Buch (SGB VII)

<b>Description</b>: 

Als Witwe, Witwer oder Teil einer Lebenspartnerschaft mit der verstorbenen
Person können Sie von der gesetzlichen Unfallversicherung eine Rente erhalten.

<b>Requirements text</b>:

Sie haben unter folgenden Voraussetzungen einen Anspruch auf die Witwen- und
Witwerrente für Hinterbliebene:

  * Tod der (Ehe-)Partnerin oder des (Ehe-)Partners infolge eines Versicherungsfalles: 
    * Arbeitsunfall,
    * Wegeunfall oder
    * Berufskrankheit
  * Sie haben schon davor in einer rechtsgültigen Ehe oder Lebenspartnerschaft nach dem Lebenspartnerschaftsgesetz gelebt.

Sie haben in der Regel keinen Anspruch, wenn

  * Sie die Ehe oder Lebenspartnerschaft erst nach dem Versicherungsfall geschlossen haben und
  * der Tod innerhalb des ersten Jahres dieser Ehe oder Lebenspartnerschaft eingetreten ist.

<b>Requirements decomposition</b>:

1. User's spouse OR civil partner died (G).
2. The reason of the spouse's or civil partner's death was an insurance event, i.e. an accident at work (G) OR on the way to work (G) OR a recognized occupational disease (Y: what constitutes a recognized occupational disease must be resolved elsewhere).
3. User was married OR lived in a registered partnership with the deceased person prior to the insured event (R: temporal dependency cannot be modelled with SHACL Core).
4. Typically, the death may not have occured within the first year of marriage or the registered partnership (R: ambiguous qualifier "Typically").