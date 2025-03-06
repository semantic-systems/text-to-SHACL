<b>Name</b>: Arbeitslosengeld

<b>IDLB</b>: B100019_LB_576842

<b>Addressee</b>: Lebenslagen für Bürgerinnen und Bürger

<b>Legal basis</b>: § 327 Sozialgesetzbuch Drittes Buch (SGB III); § 337 Sozialgesetzbuch Drittes Buch (SGB III); § 323 Sozialgesetzbuch Drittes Buch (SGB III); §§ 136 bis 164 Sozialgesetzbuch Drittes Buch (SGB III)

<b>Description</b>: 

Wenn Sie Ihre Arbeit oder Ihren Ausbildungsplatz verlieren, können Sie
Arbeitslosengeld beantragen, damit Sie finanziell abgesichert sind.

<b>Requirements text</b>:

Sie haben Anspruch auf Arbeitslosengeld, wenn

  * Sie arbeitslos sind, das heißt,
    * Sie stehen nicht in einem Beschäftigungsverhältnis oder
    * Sie üben nur eine Erwerbstätigkeit in einem Umfang von weniger als 15 Stunden wöchentlich aus und
    * Sie stehen den Vermittlungsbemühungen der Agentur für Arbeit zur Verfügung. Sie sind also in der Lage und bereit, eine versicherungspflichtige Beschäftigung unter arbeitsmarktüblichen Bedingungen aufzunehmen;
  * Sie sich 
    * elektronisch mit einem elektronischen Identitätsnachweis, zum Beispiel Personalausweis mit Online-Ausweisfunktion, im eServices-Portal der Bundesagentur für Arbeit oder
    * persönlich bei der zuständigen Agentur für Arbeit arbeitslos gemeldet haben. Mit Ihrer persönlichen Arbeitslosmeldung gilt das Arbeitslosengeld als beantragt. Zusätzlich muss noch ein Antragsformular ausgefüllt werden;
  * Sie innerhalb der letzten 30 Monate vor der Arbeitslosmeldung (der sogenannten Rahmenfrist) mindestens 12 Monate versicherungspflichtig waren. 
    * Es werden auch Zeiten berücksichtigt, in denen Sie wegen des Bezuges von Entgeltersatzleistungen, wie zum Beispiel Krankengeld, oder - unter weiteren Voraussetzungen - zum Beispiel wegen der Pflege eines Angehörigen oder der Erziehung eines Kindes versicherungspflichtig zur Arbeitsförderung waren.
    * Als Versicherungszeit können auch Zeiten berücksichtigt werden, in denen ein Antragspflichtversicherungsverhältnis (sogenannte freiwillige Weiterversicherung) vorlag, zum Beispiel  weil Sie eine selbständige Tätigkeit aufgenommen haben.
    * In Sonderfällen werden auch Zeiten berücksichtigt, in denen Sie Entwicklungsdienst nach dem Entwicklungshelfergesetz geleistet haben oder Sie auf der Grundlage eines Sekundierungsvertrages im Ausland tätig waren.

<b>Requirements decomposition</b>:

1. User is unemployed:
  - not in employment (GREEN) OR
  - employed for less than 15 hours per week (GREEN)
2. User is available for the employment agency's placement efforts (YELLOW: meaning of "normal labor market conditions" and what employment is "subject to compulsory insurance" must be inferred or explained).
3. User has registered as unemployed. (GREEN)
4. User has been subject to compulsory insurance for at least 12 months within the last 30 months before registering as unemployed. (RED: too complex for SHACL Core)
5. The period of compulsory insurance is the sum of compulsory insurance for employment promotion due to the receipt of income replacement benefits AND so-called voluntary continued insurance AND, in special cases, development service under the Development Workers ACT AND, in special cases, work abroad on the basis of a secondment contract. (RED: ambiguous qualifiers "in special cases", too complex for SHACL Core)