const fs = require('fs');
const content = fs.readFileSync('/Users/elycbarros/DEV2/MEF STRUCTURAL/mef_dashboard/src/components/UfoStabilityView.tsx', 'utf8');

function checkBalance(text) {
    let balance = 0;
    let inString = false;
    let stringChar = '';
    
    for (let i = 0; i < text.length; i++) {
        let char = text[i];
        if (inString) {
            if (char === stringChar && text[i-1] !== '\\') {
                inString = false;
            }
        } else {
            if (char === '"' || char === "'" || char === '`') {
                inString = true;
                stringChar = char;
            } else if (char === '(') {
                balance++;
            } else if (char === ')') {
                balance--;
                if (balance < 0) {
                    let line = text.substring(0, i).split('\n').length;
                    console.log(`Error: Extra ) at line ${line}`);
                    return;
                }
            }
        }
    }
    console.log(`Final paren balance: ${balance}`);
}

checkBalance(content);
