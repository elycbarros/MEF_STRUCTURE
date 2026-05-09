const fs = require('fs');
const content = fs.readFileSync('/Users/elycbarros/DEV2/MEF STRUCTURAL/mef_dashboard/src/components/UfoStabilityView.tsx', 'utf8');

function checkBalance(text) {
    let balance = 0;
    let lines = text.split('\n');
    for (let i = 0; i < lines.length; i++) {
        let line = lines[i];
        for (let char of line) {
            if (char === '{') balance++;
            if (char === '}') balance--;
        }
        if (balance < 0) {
            console.log(`Error: Unbalanced at line ${i + 1}`);
            return;
        }
    }
    console.log(`Final balance: ${balance}`);
}

checkBalance(content);
