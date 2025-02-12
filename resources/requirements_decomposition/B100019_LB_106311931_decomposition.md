<b>Name</b>: Bürgergeld

<b>IDLB</b>: B100019_LB_106311931

<b>Addressee</b>: Lebenslagen für Bürgerinnen und Bürger

<b>Legal basis</b>: Zweites Buch Sozialgesetzbuch (SGB II)

<b>Description</b>: 

Wenn Sie nicht genügend Geld zur Verfügung haben, um Ihren notwendigen
Lebensunterhalt selbst zu finanzieren, dann können Sie Bürgergeld beantragen.

<b>Requirements text</b>:

  * Sie sind erwerbsfähig. Das heißt, dass Sie 
    * mindestens 3 Stunden täglich arbeiten können und
    * mindestens 15 Jahre alt sind und die Altersgrenze der gesetzlichen Rentenversicherung noch nicht erreicht haben. Wenn Sie nach 1963 geboren sind, liegt diese bei 67 Jahren. Sind Sie vor 1964 geboren, können Sie die für Sie geltende Altersgrenze in der Tabelle in § 7a Sozialgesetzbuch II (SGB II) nachschauen.
  * Sie sind hilfebedürftig. Das heißt, dass Sie Ihren eigenen notwendigen Lebensunterhalt und den Lebensunterhalt der mit Ihnen in einer Bedarfsgemeinschaft lebenden, nicht erwerbsfähigen Angehörigen weder aus eigenen Mitteln (Einkommen und Vermögen) und Kräften (Einsatz der Arbeitskraft) noch mithilfe anderer beziehungsweise vorrangiger Leistungen (zum Beispiel Arbeitslosengeld, Wohngeld, Kinderzuschlag) bestreiten können.
  * Sie haben keine vorrangigen Ansprüche gegenüber anderen Leistungsträgern (zum Beispiel Wohngeld) oder anderen Personen, wie beispielsweise gegen geschiedene Ehepartner oder den Vater oder die Mutter Ihres Kindes.
  * Sie leben in der Bundesrepublik Deutschland.

<b>Requirements decomposition</b>:

1. User is able to work at least 3 hours per day (G)
2. User is at least 15 years old (G)
3. User has not yet reached the legal retirement age (Y)
4. User income cannot cover the basic needs of themselves and the unemployed individuals in their benefit unit. (Y)
5. User income is the sum of salary, assets, and granted benefits. (R: cannot be expressed with SHACL Core)
6. User is not eligible for other benefits with priority over citizen benefit (Y)
7. User lifes in Germany (G)