<b>Name</b>: Kindergeld

<b>IDLB</b>: B100019_LB_576986

<b>Addressee</b>: Lebenslagen für Bürgerinnen und Bürger

<b>Legal basis</b>: § 32 Einkommensteuergesetz (EStG); §§ 62 bis 78 Einkommensteuergesetz (EStG)

<b>Description</b>: 

Wenn Sie ein Kind haben, können Sie Kindergeld beantragen.

<b>Requirements text</b>:

Voraussetzungen, die für Sie als Eltern gelten:

  * Sie sind in Deutschland unbeschränkt einkommensteuerpflichtig oder werden so veranlagt. Dies gilt auch für Staatangehörige der EU, des EWR oder der Schweiz. Ein inländischer Wohnsitz ist nicht zwingend erforderlich.
  * Für Staatsangehörige der EU oder des EWR, die ab August 2019 nach Deutschland ziehen, gelten weitere Voraussetzungen. Ab dem 4. Monat ab Einreise müssen die Voraussetzungen des Freizügigkeitsgesetzes erfüllt sein. Unionsbürgerinnen und Unionsbürger sind freizügigkeitsberechtigt, wenn sie 
    * selbständig oder unselbständig erwerbstätig sind
    * arbeitsuchend oder unfreiwillig arbeitslos sind
    * ihr Freizügigkeitsrecht von einem Familienangehörigen ableiten können
    * über ausreichende Existenzmittel und ausreichenden Krankenversicherungsschutz verfügen oder
    * ein Daueraufenthaltsrecht erworben haben.

  * Sie sind zwar nicht Staatsbürgerin oder Staatsbürger der EU, des EWR oder der Schweiz, aber besitzen eine gültige Niederlassungserlaubnis oder einen bestimmten anderen Aufenthaltstitel, der zur Ausübung einer Erwerbstätigkeit berechtigt oder
  * Sie sind rechtskräftig anerkannter Flüchtling oder asylberechtigt.

Voraussetzungen, die für Ihr Kind gelten:

  * Ihr Kind muss seinen Wohnsitz oder gewöhnlichen Aufenthalt in Deutschland oder in einem anderen EU beziehungsweise EWR-Staat oder der Schweiz haben.
  * Eventuell haben Sie auch dann Anspruch auf Kindergeld, wenn Ihr Kind zwar in einem Haushalt in der EU, der EWR oder der Schweiz lebt, beispielsweise Sie oder der andere Elternteil aber in Deutschland unbeschränkt einkommensteuerpflichtig ist oder so veranlagt wird.

<b>Requirements decomposition</b>:

1. User is subject to income tax in Germany (GREEN)
2. User is subject to unlimited income tax liability (GREEN)
4. User's residence situation falls into one of the covered categories:
    - they are a German national (GREEN) OR
    - they are EEA/Swiss national AND 
      - moved to Germany before August 2019 (GREEN) OR
      - less than 4 months ago (RED: too complex for SHACL Core)
    - they are EEA/Swiss national AND moved to Germany after August 2019 (GREEN) AND more than 4 months ago (RED: too complex for SHACL Core) AND meet the requirements of the Freedom of Movement Act (FoMA) (BELOW) OR
    - they are not an EEA/Swiss national AND have a valid settlement permit (GREEN) OR
    - they are not an EEA/Swiss national AND another residence title that entitles to pursue gainful employment (YELLOW: which residence titles grant that entitlement must be inferred or explained) OR
    - they are not an EEA/Swiss national AND legally recognized refugee (GREEN) OR
    - they are not an EEA/Swiss national AND entitled to asylum (YELLOW: whether someone is entitled to asylum must be inferred or explained)
5. FoMA requires that the (non-German EEA national) user
    - is self-employed (GREEN) OR 
    - is employed (GREEN) OR
    - is looking for work (YELLOW: legal definition must be resolved elsewhere)  OR
    - is involuntarily unemployed (YELLOW: legal definition must be resolved elsewher. Here, simplified to "unemployed" because only involuntarily unemployed individuals are considered "unemployed" by the Federal Employment Agency [1]) OR
    - can derive their right to freedom of movement from a family member (YELLOW: under what conditions the derivative right exists must be inferred or explained) OR
    - has sufficient means of subsistence AND adequate health insurance cover (RED: ambiguous qualifiers "sufficient" and "adequate", possibly discretionary decision) OR
    - has acquired a permanent right of residence (YELLOW: prerequisites for permanent right of residence must be inferred or explained, see definition at [2]). 
6. User has at least one child that is an EEA/Swiss resident OR ordinarily resides in an EEA/Swiss member state (YELLOW: "residence" and "ordinary residence" must be inferred or explained)
7. User is possibly entitled if the child lives in a household in an EEA/Swiss member state, but they or the other parent are subject to unlimited income tax liability in Germany OR are assessed as such. (RED: ambiguous qualifier "possibly")

[1] Bundesagentur für Arbeit: https://statistik.arbeitsagentur.de/DE/Navigation/Grundlagen/Definitionen/Arbeitslosigkeit-Unterbeschaeftigung/Arbeitslosigkeit-Nav.html

[2] Act on the General Freedom of Movement for EU Citizens Section 4a: https://www.gesetze-im-internet.de/englisch_freiz_gg_eu/englisch_freiz_gg_eu.html