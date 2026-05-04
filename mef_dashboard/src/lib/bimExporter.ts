/**
 * BIM EXPORTER (IFC 2x3)
 * Gera um arquivo IFC básico para interoperabilidade estrutural.
 */

export interface BimElement {
  id: string;
  type: 'BEAM' | 'COLUMN' | 'SLAB';
  name: string;
  dimensions: {
    b: number; // m
    h: number; // m
    l: number; // m
  };
  position: {
    x: number;
    y: number;
    z: number;
  };
}

export class BimExporter {
  /**
   * Gera o conteúdo de um arquivo IFC 2x3 baseado nos elementos fornecidos.
   */
  static generateIFC(elements: BimElement[]): string {
    const timestamp = new Date().toISOString().replace(/[-:T]/g, '').split('.')[0];
    
    let ifc = `ISO-10303-21;
HEADER;
FILE_DESCRIPTION(('MEF Structural Elite BIM Export'),'2;1');
FILE_NAME('structural_model_${timestamp}.ifc','${timestamp}',('Antigravity PhD'),('Elite Engineering'),'MEF Structural V6','Next.js IFC Engine','');
FILE_SCHEMA(('IFC2X3'));
ENDSEC;

DATA;
#1= IFCORGANIZATION($,'Elite Engineering',$,$,$);
#2= IFCAPPLICATION(#1,'6.0.0','MEF Structural','MEF-STR-6');
#3= IFCCARTESIANPOINT((0.,0.,0.));
#4= IFCAXIS2PLACEMENT3D(#3,$,$);
#5= IFCLOCALPLACEMENT($,#4);
#6= IFCPROJECT('0Y8y$8vX18$w$0_X$8y$8y','MEF_PROJECT','Structural Analysis Model',$,$,$,$,(#11),#7);
#7= IFCUNITASSIGNMENT((#8,#9,#10));
#8= IFCSIUNIT(*,.LENGTHUNIT.,.MILLI.,.METRE.);
#9= IFCSIUNIT(*,.AREAUNIT.,$,.SQUARE_METRE.);
#10= IFCSIUNIT(*,.VOLUMEUNIT.,$,.CUBIC_METRE.);
#11= IFCGEOMETRICREPRESENTATIONCONTEXT($,'Model',3,0.01,#4,$);
#12= IFCSITE('1Y8y$8vX18$w$0_X$8y$8y',$,'Project Site',$,$,#5,$,$,.ELEMENT.,$,$,$,$,$);
#13= IFCBUILDING('2Y8y$8vX18$w$0_X$8y$8y',$,'Main Building',$,$,#5,$,$,.ELEMENT.,$,$,$);
#14= IFCBUILDINGSTOREY('3Y8y$8vX18$w$0_X$8y$8y',$,'Ground Floor',$,$,#5,$,$,.ELEMENT.,0.);

`;

    let idCounter = 100;

    elements.forEach((el, index) => {
      const guid = `GUID_${index}_${timestamp}`;
      const name = el.name || `${el.type}_${el.id}`;
      
      // Geometria básica (Cubo/Extrusão)
      const b = el.dimensions.b * 1000; // IFC em mm
      const h = el.dimensions.h * 1000;
      const l = el.dimensions.l * 1000;

      ifc += `
#${idCounter}= IFCCARTESIANPOINT((${el.position.x * 1000},${el.position.y * 1000},${el.position.z * 1000}));
#${idCounter+1}= IFCAXIS2PLACEMENT3D(#${idCounter},$,$);
#${idCounter+2}= IFCLOCALPLACEMENT(#5,#${idCounter+1});
#${idCounter+3}= IFCBEAM('${guid}',$,'${name}',$,$,#${idCounter+2},$,$);
`;
      idCounter += 10;
    });

    ifc += `
ENDSEC;
END-ISO-10303-21;`;

    return ifc;
  }

  /**
   * Dispara o download do arquivo IFC no navegador.
   */
  static downloadIFC(elements: BimElement[]) {
    const content = this.generateIFC(elements);
    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `MEF_BIM_MODEL_${new Date().getTime()}.ifc`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  }
}
