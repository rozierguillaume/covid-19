# SIMULATOR CT
In this folder you will find explanations about source code of covid-19 simulator for CovidTracker. Texts will be in French for the moment. 

## Présentation du simulateur CT 

Description du modèle de calcul sur tableur

---

### Les états

Modèle épidémilogique à compartiments (états) à calcul discret (journalier), une lettre capitale = un état

S : susceptible d'être infecté
E : exposé au virus, le virus a pénétré l'organisme
I : infectieux donc contagieux
A : asymptomatique, au sens où l'individu est exposé mais il ne développera pas la maladie et ne sera pas contagieux
P : positif au dépistage et infectieux (remarque : les personnes non infectieuses sont rapidement sorties du process de calcul)
H : hospitalisé
C : critique, hospitalisation en réanimation
O : en sOins de suite, la maladie est vaincue (EN : to Overcome) mais le patient n'est pas totalement guéri.
R : retour à domicile donc guéri
D : décédé
X : en stituation eXtrange, individu qui ne rentre plus dans les calculs
V : vielle personne contaminée (EN : vintage), pensionnaire en EHPAD et EMS
W : pentionnaire EHPAD ou EMS décédé
M : malade à la maison
F : fantome (les anomalies)

---

### Les changements d'état

Une lettre minuscule = un changement d'état

i : entrée dans l'état (IN)
o : sortie de (OUT)

---

### Les opérations

Une consonne minuscule = un calcul

q : quota (un pourcentage)
s : somme (un cumul)
d : délai, avant un changement d'état
j : le jour j

---

### Liste des variables

Variable	Description	Ligne de calcul

qEI	% exposed vers infectious	S1-03
dI	Durée de contagiosité jours (ce n’est pas un changement d’état)	S1-04
dEI	Délai Exposed vers Infectious jours	S1-05
dEP	Délai Exposed vers Tested jours	S1-06
dIP	Délai Infectious vers Tested jours	S1-07
dPH	Délai entrée hôpital	S2-03
qPH	% positif vers hôpital	S2-04
qPX	% positifs scénario EXT	S2-05
dHC	délai hôpital vers réanimation jours	S2-06
qHC	% hôpital vers réanimation	S2-07
dHO	délai hôpital vers SSR	S2-08
qHO	% hôpital vers SSR	S2-09
dHR	Délai hôpital vers sortie jours	S2-10
dCD	Délai réanimation vers décès jours	S2-11
qCD	% réanimation vers décès	S2-12
dCO	Délai réanimation vers SSR jours	S2-13
dOR	Délai SSR vers sortie hôpital jours	S2-14
qXR2	% sortie effective hôp RàD scénario EXT	S2-19
dXD	délai positifs vers décès Scénario EXT	S2-20
qMV	% nv guéris seuls vers nv tests pos. EHPAD	S2-21
dMV	délai contamin. ext. vers positifs EHP. en jours	S2-22
qHD	% hôpital vers décès sans passage réanimation	S2-23
dHD	délai hôpi. vers décès sans passage réanimat.	S2-24
qVD	% positifs vers décès en EHPAD et EMS	S2-25
dVD	délai positifs vers décès en EHPAD et EMS	S2-26
dXR	délai posit. vers sortie hôp scénar EXT (max 45)	S2-27
qXR	% sortie hôp guérison scénario EXT	S2-28

---

### Explications des calculs dans les colonnes 

Sheet1 - S1

S1-A : dates
S1-B : points de contrôle R pour orienter la courbe de R-effectif. Pour chaque mois il y a 4 points de contrôle, c'est à dire 4 valeurs de R à choisir, le 1er puis le 10, puis le 20, puis le 30 ou le 31 du mois. Les valeurs intermédiaires des autres jours seront calculées par interpollation de Lagrange.
S1-C : points de contrôle recalculé, possibilité de réorienter les points de contrôle à la hausse ou à la baisse (variation linéaire) pour faire des hypothèses de tendances. R = R*(1+(variation*jours))
S1-D, Reff : calculs des valeurs de R-effectif au jour le jour selon une interpollation de Lagrange en fonctions de 4 points de contrôle recalculés par mois . 
S1-E, Reff2 : calcul d'une deuxième valeur de R-effectif (Reff2) qui est augmentée pour tenir compte d'une hypothèse où seules les personnes infectieuses sont contaminantes. Reff2 = Reff/qI
S1-K, Ei : entrées quotidiennes dans l'état exposé E, dépend du nombre de personnes infectieuses I, Ei = Ii*Reff2(j-dI)
S1-L, Es : somme des personnes exposées, Es = Es(j-1)+Ei
S1-M, Ai : entrées quotidiennes dans l'état asymptomatique A, dépend du nombre de nouvelles personnes exposées et qui ne seront pas infectieuses, Ai = Ei(j-dEI)*(1-qEI)
S1-N, A : cumul des personnes asymptomatiques A, A = A(j-1)+Ai
S1-O, Ii : entrées quotidiennes à l'état infectieux I, dépend du nombre de nouvelles personnes exposées et qui seront infectieuses, Ii = Ei(j-dEI)*qEI
S1-P, Ps : sommes des personnes infectieuses et positives aux tests, dépend de la somme des personnes infectieuses I avec un décalage dans le temps. Ps = Ps(j-1) + Ii(j-dIP)
S1-Q, Ps lissé moyenne mobile 5 jours, pour amoindrir les fluctuations de calcul.
S1-R, P(tous), tous les positifs y compris les asymptomatiques, pour comparaison avec les données SPF, correspond à tous les exposés en fonction d'un délai pour le résultat aux tests, P(tous) = Es(j-dEP)
S1-S, P(SPF), tous les positifs selon les données SPF (import de données), pour comparaison

---

Sheet2 - S2

S2-A : dates (les mêmes qu'en S1-A)
S2-J, P(tous) : tous les positifs, rappel de la colonne S1-R
S2-K, A : tous les asymptomatiques, rappel de la colonne S1-N
S2-L, P(SPF) : tous les positifs selon SPF, rappel de la colonne S1-S
S2-M, Pi : incidence quotidienne de nouveaux Positifs à l'état P, Pi=Ps-Ps(j-1)
S2-N, Hi : incidence quotidienne des nouvelles entrées en hospitalisation, dépend du pourcentage de positifs qui passent à l'hôpital selon un délai dPI, Hi=Pi(j-dPH)*qPH
S2-O, His : somme de toutes les entrées à l'hôpital, Hs = Hs(j-1)+Hi
S2-P, Ci : incidence quotidienne de nouvelles entrées en réanimation, dépend des nouvelles entrées en hospitalisation selon un délai, Ci = Hi(j-dHC)*qHC
S2-Q, Cis : somme de toutes les entrées en réanimation, Cis = Cis(j-1)+Ci
S2-S, CDi : incidence quotidienne des nouveaux décès en services de réanimation, dépend des nouvelle entrées en réanimation selon un quota de décès et un délai, CDi = Ci(j-dCD)*qCD
S2-T, HDi : incidence quotidienne des nouveaux décès en hospitalisation conventionnelle, dépend des nouvelles entrées en hospitalisation, selon un délai et un quota, HDi = Hi(j-dHD)*qHD
S2-U, HDs : somme des patients décédés en hospitalisation conventionnelle, HDs = HDs(j-1)+HDi
S2-V, Di : incidence quotidienne des nouveaux décès, somme des décès quotidiens en réanimation et en hospitalisation conventionnelle, Di = CDi+HDi
S2-W, D : somme des décès hospitaliers, Ds = Ds(j-1) + Di
S2-X, CDs : somme des décès en services de réanimation, CDs = CDs(j-1)+CDi
S2-Y, C2Os : somme des patients en réanimation qui iront en SSR (ils ne vont pas décéder), C2Os = Cis-CDs
S2-Z, COis : somme des patients entrés en SSR, c'est un décalage dans le temps de C2Os, COis = C2Os(j-dCO)
S2-AA, COi : incidence quotidienne des nouvelles entrées en SSR, COi = COis-COis(j-1)
S2-AC, Cos : cumul des sorties des services de réanimation, soit sute à décès, soit suite à passage en SSR, Cos = Cos(j-1)+CDi+COi
S2-AD, HOi : incidence quotidienne des arrivées en SSR directement depuis l'hospitalisation conventionelle, dépend des nouvelles arrivées en hospitalisation selon un quota et un délai, HOi = Hi(j-dHO)*qHO
S2-AE, HOis : somme des entrées en SSR de la part de personnes arrivant depuis l'hospitalisation conventionnelle, HOis = HOis(j-1)+HOi
S2-AF, Ois : somme de toutes les entrées en SSR, les entrées depuis les services de réanimation et depuis l'hospitalisation conventionelle, Ois = Ois(j-1)+COi+HOi
S2-AG, Oi : incidence quotidienne des entrées en SSR, Oi = Ois-Ois(j-1)
S2-AH, Oos : somme de toutes les sorties de service SSR, dépend de toutes les entrées en SSR avec un décalage dans le temps, Oss = Ois(j-dOR)
S2-AI, Oo : sorties quotitiennes des services de SSR, Oo = Oos - Oos(j-1)
S2-AJ, O : nombre de patients en SSR, différence entre la somme des entrées et la somme des sorties, O = Ois-Oos
S2-AK, H2Rs : nombre de patients qui pourront sortir de l'hôpital sans passer par un service de réanimation ou de SSR, vu comme le reste des patients qui étant entrés à l'hôpital n'ont pas été dirigés vers un service SSR ou réa, H2Rs = His - (HDs+Cis+HOis)
S2-AL, HRs : somme des sorties de l'hôpital pour les patients ne passant pas par des services de réa ou SSR, vu comme un décalage dans le temps de H2Rs, HRs = H2Rs(j-dHR)
S2-AM, HRi : nombre d'entrées quotidiennes à l'état R (qui en en fait une sortie de l'hôpital), de la part des patients en hospitalisation conventionnelle (ni en Rea ni en SSR), HRi = HRs-HRs(j-1)
S2-AN, Ri : nombre d'entrées quotidiennes à l'état R, c'est à dire toutes les sorties quotidiennes de l'hôpital, Ri = Oo+HRi
S2-AO, Hos : somme de toutes les sorties de l'hôpital, toutes causes confondues, Hos = Hos(j-1)+Ri+Di
S2-AP, H : nombre de patients hospitalisés, H = His-Hos
S2-AQ, D : nombre de patients décédés, rappel de S2-W.
S2-AR, R : nombre de patients retournés à domicile, R = Oos + HRs
S2-AS, C : nombre de patients en soins critiques, C = Cis-Cos
S2-AT, Mi : incidence quotidienne des nouvelles personnes positives qui ne vont pas être prise en charge l'hôpital, Mi = Pi-Hi
S2-AU, M : personnes positives qui se sont soignées à domicile, M = M(j-1)+Mi
S2-AV, Oref : Nombre de patients en SSR, référence SPF
S2-AW, Href : nombre de patients hospitalisés, référence SPF
S2-AX, Cref : nombre de patients en réanimation, référence SPF
S2-AY, Rref : nombre de patients retounés à domicile, référence SPF
S2-AZ, Dref : nombre de patients décédés, référence SPF
S2-BA, Vref : nombre de pensionnaires détectés positifs en EHPAD et EMS, référence SPF
S2-BB, Wref : nombre de pensionaires EHPAD ou EMS décédés, référence SPF
S2-BC, Hiref : incidence quotidienne des entrées hospitalières, référence SPF
S2-BD, Ciref : incidence quotidienne des entrées en réanimation, référence SPF
S2-BE, Diref : incidence quotidienne des nouveaux décès à l'hôpital, référence SPF
S2-BF, Riref : incidence quotidienne des nouveaux retours à domicile, référence SPF
S2-BG, Hsref : somme des incidences de référence des entrées hospitalières, Hsref = Hsref(j-1)+Hiref
S2-BH, Csref : somme des incidences de référence des entrées en réanimation, Csref = Csref(j-1)+Ciref
S2-BI, Rsref : somme des incidences de référence des sorties hospitalières, Rsref = Rsref(j-1)+Riref
S2-BJ, Dsref : somme des incidences de référence des décès hospirtaliers, Dsref = Dsref(j-1)+Diref
S2-BK, Tous : somme des états des personnes passées par l'état P, vu comme toutes les personnes qui se sont soignées à domicile plus tous les patients en cours d'hospitalisation plus tous les patients décédés à l'hôpital plus tous les patients retournés à domicile plus tous les asymptomatiques, Tous = M + H + D + R + A
S2-BL, dTous : écart delta de Tous avec le nombre de personnes détectées positives, vérification générale, dTous = (P(tous) - Tous)/P(tous)
S2-BP, Vi : incidence nouveaux cas de contaminations en EHPAD et EMS, vu comme un quota avec un délai du nombre des nouvelles personnes qui se soignent sans passer par l'hôpital, Vi = Mi(j-dMV)*qMV
S2-BQ, Vs : cumul du nombre de cas de contamination en EHPAD et EMS, Vs = Vs(j-1)+Vi
S2-BR, VDi : incidence quotidienne des décès de pensionnaires EHPAD et EMS, vu comme un décalage avec un quota sur le nombre des nouveaux cas positifs, VDi = Vi(j-dVD)*qVD
S2-BS, VD : cumul des décès de pensionnaires EHPAD et EMS, VD = VD(j-1)+VDi
S2-BT, Xi : incidence quotidienne de nouvelles personnes dirigées vers le scénario hospitalier eXtrange, et ne rentrant plus dans les calculs hospitaliers standard, vu comme une partie des nouveaux cas détectés positifs, Xi = Pi*qPX
S2-BU, Xis : cumul de personnes comptabilisées dans le scénario hospitalier eXtrange, X = X(j-1)+Xi
S2-BV, HXis : somme des entrées dans les deux scénario hospitaliers, HXis = His+Xis
S2-BW, XDs : cumul des décès dans le scénario hospitalier eXtrange, vu comme un déclage et un quota des entrées dans ce scénario, XDs = XDs(j-1)+Xi(j-dXD)*(1-qXR)
S2-BX, XRs : cumul des retours à domicile possibles avec le scénario eXtrange, vu comme un décalage temporel des pensionnaires positifs qui ne sont pas décédés, XRs = Xis(j-dXR)-XDs(dXR-dXD)
S2-BY, XRi : nouvelles sorties quotidiennes effectives pour retour à domicile avec le scénario hospitalier eXtrange, vu comme un différentiel quotidien de XRs mais diminé d'un quota qXY, XRi = XRs-XRs(j-1)*qXR2
S2-BZ, XR2s : cumul des retours à domiciles effectifs avec le scénario eXtrange, XR2s = XR2s(j-1)+XRi
S2-CA, Fi : nouvelles entrées dans la situation très eXtrange F, des personnes du scénario eXtrange qui ne sont ni décédées ni hospitalisées ni sorties, Fi = XRs-XRs(j-1)*(1-qXR2)
S2-CB, F : somme des patients du scénario hospitalier eXtrange passés à l'état F, F = F(j-1)+Fi
S2-CC, RR : somme des retours à domicile avec les deux scénarios, RR = R + XR2s
S2-CD, DD : somme des décès avec les deux scénarios, DD = D+XDs
S2-CE, Xio : calcul du nombre de patients en hospitalisation avec le scénario eXtrange, vu comme la différence entre toutes les entrées et toutes les sorties, Xio = Xis-(XDs+XRs)
S2-CF, gDelta : grand écart de calcul vérification toutes hospitalisations




