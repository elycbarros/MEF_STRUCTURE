const fs = require('fs');
const content = fs.readFileSync('/Users/elycbarros/DEV2/MEF STRUCTURAL/mef_dashboard/src/components/UfoStabilityView.tsx', 'utf8');

function checkTags(text) {
    let stack = [];
    let regex = /<\/?([A-Z][a-zA-Z0-9]*|div|span|button|input|p|h[1-6]|group|mesh|boxGeometry|meshStandardMaterial|coneGeometry|ambientLight|spotLight|PerspectiveCamera|Stage|Grid|OrbitControls|Canvas|Suspense|label)(?:[^>]*?)\/?>/gs;
    let match;
    
    while ((match = regex.exec(text)) !== null) {
        let fullMatch = match[0];
        let tagName = match[1];
        let isSelfClosing = fullMatch.endsWith('/>');
        let isClosing = fullMatch.startsWith('</');
        
        let line = text.substring(0, match.index).split('\n').length;
        
        console.log(`Line ${line}: ${isClosing ? 'Closing' : (isSelfClosing ? 'Self-closing' : 'Opening')} ${tagName} [${fullMatch.replace(/\n/g, '\\n')}]`);
        
        if (isSelfClosing) {
        } else if (isClosing) {
            if (stack.length === 0) {
                console.log(`Error: Extra closing tag ${tagName} at line ${line}`);
                return;
            }
            let last = stack.pop();
            if (last !== tagName) {
                console.log(`Error: Tag mismatch: ${last} closed by ${tagName} at line ${line}`);
                return;
            }
        } else {
            stack.push(tagName);
        }
    }
}

checkTags(content);
