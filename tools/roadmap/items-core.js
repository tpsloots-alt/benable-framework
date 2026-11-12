/* Kernpunten (deel A van het framework): gelden voor elke organisatie.
   tab = id van het tabblad (section#v-<tab>), laag 1–4, fase 0/1/2 = standaardperiode in de roadmap. */
const RM_CORE=[
 {id:'C-B1',tab:'basis',laag:1,groep:'Maandafsluiting',norm:'Vaste afsluitkalender; de maand is dicht op een vaste werkdag',actie:'Afsluitkalender met doelwerkdag invoeren en bewaken',eig:'Financial control',fase:0},
 {id:'C-B2',tab:'basis',laag:1,groep:'Maandafsluiting',norm:'Mapping van grootboek naar management P&L vastgelegd en onderhouden',actie:'Mappingtabel grootboek → management P&L opstellen',eig:'Financial control',fase:0},
 {id:'C-B3',tab:'basis',laag:1,groep:'Reconciliaties en beheersing',norm:'Reconciliaties maandelijks gedaan, met eigenaar en aftekening',actie:'Reconciliatieschema met eigenaren en aftekening invoeren',eig:'Financial control',fase:1},
 {id:'C-B4',tab:'basis',laag:1,groep:'Reconciliaties en beheersing',norm:'Functiescheiding en vier-ogenprincipe op stamdata en betalingen',actie:'Functiescheiding en vier-ogenprincipe inrichten',eig:'Financial control',fase:1},
 {id:'C-B5',tab:'basis',laag:1,groep:'Reconciliaties en beheersing',norm:'Kritieke Excel-bestanden zijn gedocumenteerd en beheerst',actie:'Kritieke Excel-processen inventariseren en documenteren',eig:'Business control',fase:0},
 {id:'C-P1',tab:'pl',laag:2,groep:'Verklaren en vooruitkijken',norm:'Afwijkingen worden maandelijks verklaard naar volume, prijs en efficiëntie',actie:'Standaard afwijkingsanalyse invoeren in de maandrapportage',eig:'Business control',fase:1},
 {id:'C-P2',tab:'pl',laag:2,groep:'Verklaren en vooruitkijken',norm:'Er is een Best Estimate of rolling forecast, minstens per kwartaal',actie:'Best Estimate per kwartaal invoeren',eig:'Business control',fase:1},
 {id:'C-P3',tab:'pl',laag:2,groep:'Verklaren en vooruitkijken',norm:'De belangrijkste risico\'s zijn als scenario doorgerekend',actie:'Scenario\'s voor de grootste risico\'s uitwerken',eig:'Business control',fase:2},
 {id:'C-K1',tab:'kpis',laag:3,groep:'KPI-set',norm:'Er is een vastgestelde kernset van 10–15 KPI\'s',actie:'Kernset van 10–15 KPI\'s vaststellen met directie',eig:'Business control',fase:0},
 {id:'C-K2',tab:'kpis',laag:3,groep:'KPI-set',norm:'Elke kern-KPI heeft een KPI-kaart met definitie, formule, eigenaar en norm',actie:'KPI-kaarten opstellen voor de kernset',eig:'Business control',fase:0},
 {id:'C-K3',tab:'kpis',laag:3,groep:'KPI-set',norm:'Het dashboard wordt automatisch gevuld uit één bron',actie:'Dashboard automatisch vullen vanuit één datamodel',eig:'IT / finance',fase:2},
 {id:'C-S1',tab:'sturing',laag:4,groep:'Business review',norm:'Business review met vaste agenda en actielijst (eigenaar, deadline, effect)',actie:'Vaste agenda en actielijst voor de business review invoeren',eig:'Finance business partner',fase:0},
 {id:'C-S2',tab:'sturing',laag:4,groep:'Business review',norm:'Opvolging van acties is vast agendapunt; het effect wordt gemeten',actie:'Opvolging en effectmeting van acties borgen',eig:'Directie',fase:1},
 {id:'C-O1',tab:'organisatie',laag:4,groep:'Rollen en bevoegdheden',norm:'Bevoegdhedenmatrix met drempelbedragen is vastgesteld',actie:'Bevoegdhedenmatrix vaststellen',eig:'Directie',fase:1},
 {id:'C-O2',tab:'organisatie',laag:4,groep:'Rollen en bevoegdheden',norm:'Rollen van financial control, business control en lijn zijn vastgelegd (RACI)',actie:'RACI per kernproces vastleggen',eig:'Finance',fase:1},
 {id:'C-Y1',tab:'cyclus',laag:4,groep:'Stuurcyclus',norm:'Stuurcyclus en rapportagekalender zijn vastgesteld en bekend',actie:'Stuurcyclus en rapportagekalender vaststellen en publiceren',eig:'Business control',fase:0},
 {id:'C-D1',tab:'datamodel',laag:1,groep:'Data',norm:'Eén bron per gegeven; bronsystemen en koppelingen zijn beschreven',actie:'Bronnen en koppelingen beschrijven; één bron per gegeven afspreken',eig:'IT / finance',fase:1},
 {id:'C-D2',tab:'datamodel',laag:1,groep:'Data',norm:'Standaarddimensies (project, entiteit, kostenplaats) zijn verplicht bij het boeken',actie:'Verplichte dimensies instellen in het financieel pakket',eig:'Financial control',fase:1}
];
const RM_FASES=[['Snelle verbeteringen','0–3 maanden'],['Basis op orde','3–9 maanden'],['Doorontwikkeling','9–18 maanden']];
const RM_LAGEN=['Financiële basis','Business drivers','KPI\'s','Sturing'];
