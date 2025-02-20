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

1. User is subject to income tax in Germany (G)
2. User is subject to unlimited income tax liability (G)
4. User's residence situation falls into one of the covered categories:
    - they are a German national (G) OR
    - they are EEA/Swiss national AND moved to Germany before August 2019 (G) OR
    - they are EEA/Swiss national AND moved to Germany after August 2019 (G) AND meet the requirements of the Freedom of Movement Act (see below) (FoMA) from 4 months after entry onward (R: cannot be modelled with SHACL Core) OR
    - they are not an EEA/Swiss national AND have a valid settlement permit (G) OR
    - they are not an EEA/Swiss national AND another residence title that entitles to pursue gainful employment (Y: which residence titles grant that entitlement must be resolved elsewhere) OR
    - they are not an EEA/Swiss national AND legally recognized refugee (G) OR
    - they are not an EEA/Swiss national AND entitled to asylum (Y: whether someone is entitled to asylum must be resolved elsewhere)
5. FoMA requires that the (non-German EEA national) user
    - is self-employed (G) OR 
    - is employed (G) OR
    - is looking for work (G) OR
    - is involuntarily unemployed (Y: meaning of "involuntary" must possibly be resolved elsewhere. Here, simplified to "unemployed" because only involuntarily unemployed individuals are considered to be unemployed by the Federal Employment Agency [1]) OR
    - can derive their right to freedom of movement from a family member (Y: under what conditions the derivative right exists must be resolved elsewhere) OR
    - has sufficient means of subsistence AND adequate health insurance cover (R: ambiguous qualifiers "sufficient" and "adequate", possibly discretionary decision) OR
    - has acquired a permanent right of residence (Y: conditions describe at [2], must be resolved elsewhere). 
6. User has at least one child that is an EEA/Swiss resident OR ordinarily resides in an EEA/Swiss member state (G)
7. User is possibly entitled if the child lives in a household in an EEA/Swiss member state, but they or the other parent are subject to unlimited income tax liability in Germany OR are assessed as such. (R: ambiguous qualifier "possibly")

[1] Bundesagentur für Arbeit: https://statistik.arbeitsagentur.de/DE/Navigation/Grundlagen/Definitionen/Arbeitslosigkeit-Unterbeschaeftigung/Arbeitslosigkeit-Nav.html

[2] Act on the General Freedom of Movement for EU Citizens Section 4a: https://www.gesetze-im-internet.de/englisch_freiz_gg_eu/englisch_freiz_gg_eu.html