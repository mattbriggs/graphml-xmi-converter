import xml.etree.ElementTree as ET
import sys

# GraphML (Yed) to XMI (StarUML)
def parse_graphml_to_xmi(graphml_path, xmi_output_path):
    ns = {
        'graphml': 'http://graphml.graphdrawing.org/xmlns',
        'y': 'http://www.yworks.com/xml/graphml'
    }
    tree = ET.parse(graphml_path)
    root = tree.getroot()

    nodes = {}
    for node in root.findall('.//graphml:node', ns):
        node_id = node.attrib['id']
        label_element = node.find('.//y:NodeLabel', ns)
        label = label_element.text if label_element is not None else 'Unnamed'
        nodes[node_id] = label

    associations = []
    for edge in root.findall('.//graphml:edge', ns):
        source = edge.attrib['source']
        target = edge.attrib['target']
        associations.append((source, target))

    xmi_root = ET.Element('xmi:XMI', {
        'xmi:version': '2.1',
        'xmlns:uml': 'http://schema.omg.org/spec/UML/2.0',
        'xmlns:xmi': 'http://schema.omg.org/spec/XMI/2.1'
    })
    model = ET.SubElement(xmi_root, 'uml:Model', {'xmi:id': 'model_1', 'name': 'ConvertedModel'})

    class_ids = {}
    for idx, (node_id, class_name) in enumerate(nodes.items(), start=1):
        class_id = f'class_{idx}'
        class_ids[node_id] = class_id
        ET.SubElement(model, 'packagedElement', {
            'xmi:type': 'uml:Class',
            'xmi:id': class_id,
            'name': class_name
        })

    for idx, (src, tgt) in enumerate(associations, start=1):
        assoc_id = f'association_{idx}'
        assoc = ET.SubElement(model, 'packagedElement', {
            'xmi:type': 'uml:Association',
            'xmi:id': assoc_id
        })
        ET.SubElement(assoc, 'ownedEnd', {
            'xmi:id': f'{assoc_id}_src',
            'visibility': 'public',
            'type': class_ids[src],
            'aggregation': 'none',
            'xmi:type': 'uml:Property'
        })
        ET.SubElement(assoc, 'ownedEnd', {
            'xmi:id': f'{assoc_id}_tgt',
            'visibility': 'public',
            'type': class_ids[tgt],
            'aggregation': 'none',
            'xmi:type': 'uml:Property'
        })

    ET.ElementTree(xmi_root).write(xmi_output_path, encoding='utf-8', xml_declaration=True)

# XMI (StarUML) to GraphML (Yed) - Corrected
def parse_xmi_to_graphml(xmi_input_path, graphml_output_path):
    ns = {
        'uml': 'http://schema.omg.org/spec/UML/2.0',
        'xmi': 'http://schema.omg.org/spec/XMI/2.1'
    }
    tree = ET.parse(xmi_input_path)
    root = tree.getroot()

    # Correct extraction of classes
    classes = {}
    for cls in root.findall(".//packagedElement[@xmi:type='uml:Class']", ns):
        class_id = cls.get('{http://schema.omg.org/spec/XMI/2.1}id')
        class_name = cls.get('name')
        classes[class_id] = class_name

    # Correct extraction of associations
    associations = []
    for assoc in root.findall(".//packagedElement[@xmi:type='uml:Association']", ns):
        ends = assoc.findall("ownedEnd", ns)
        if len(ends) == 2:
            associations.append((ends[0].attrib['type'], ends[1].attrib['type']))

    ET.register_namespace('', "http://graphml.graphdrawing.org/xmlns")
    ET.register_namespace('y', "http://www.yworks.com/xml/graphml")

    graphml = ET.Element('graphml', {
        'xmlns': 'http://graphml.graphdrawing.org/xmlns',
        'xmlns:y': 'http://www.yworks.com/xml/graphml'
    })

    # Yed-required keys
    ET.SubElement(graphml, 'key', id="d6", attrib={'for': "node", 'yfiles.type': "nodegraphics"})
    ET.SubElement(graphml, 'key', id="d10", attrib={'for': "edge", 'yfiles.type': "edgegraphics"})

    graph = ET.SubElement(graphml, 'graph', edgedefault='directed', id='G')

    node_map = {}
    for idx, (class_id, class_name) in enumerate(classes.items()):
        node_id = f'n{idx}'
        node_map[class_id] = node_id
        node = ET.SubElement(graph, 'node', id=node_id)
        data = ET.SubElement(node, 'data', key='d6')
        uml_node = ET.SubElement(data, 'y:UMLClassNode')
        ET.SubElement(uml_node, 'y:Geometry', height="50.0", width="100.0", x=str(100 + idx * 120), y="100.0")
        ET.SubElement(uml_node, 'y:Fill', color="#FFCC00", transparent="false")
        ET.SubElement(uml_node, 'y:BorderStyle', color="#000000", type="line", width="1.0")
        ET.SubElement(uml_node, 'y:NodeLabel').text = class_name
        ET.SubElement(uml_node, 'y:UML', clipContent="true", use3DEffect="true")

    for idx, (src, tgt) in enumerate(associations):
        edge = ET.SubElement(graph, 'edge', id=f'e{idx}', source=node_map[src], target=node_map[tgt])
        data = ET.SubElement(edge, 'data', key='d10')
        poly_edge = ET.SubElement(data, 'y:PolyLineEdge')
        ET.SubElement(poly_edge, 'y:LineStyle', color='#000000', type='line', width='1.0')
        ET.SubElement(poly_edge, 'y:Arrows', source='none', target='standard')
        ET.SubElement(poly_edge, 'y:BendStyle', smoothed='false')

    ET.ElementTree(graphml).write(graphml_output_path, encoding='utf-8', xml_declaration=True)

# Main execution logic
if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python script.py <direction> <input_file> <output_file>")
        print("Directions: graphml2xmi OR xmi2graphml")
    else:
        direction, input_file, output_file = sys.argv[1], sys.argv[2], sys.argv[3]
        if direction == 'graphml2xmi':
            parse_graphml_to_xmi(input_file, output_file)
            print(f'GraphML converted to XMI: {output_file}')
        elif direction == 'xmi2graphml':
            parse_xmi_to_graphml(input_file, output_file)
            print(f'XMI converted to GraphML: {output_file}')
        else:
            print("Invalid direction. Use 'graphml2xmi' or 'xmi2graphml'.")