#!/bin/bash
md_html='<!-- Markdeep: --><style class="fallback">body{visibility:hidden;white-space:pre;font-family:monospace}</style><script src="../markdeep.min.js" charset="utf-8"></script></script><script>window.alreadyProcessedMarkdeep||(document.body.style.visibility="visible")</script>'
cp -f */*.md publish/
cd  publish
rename -f 's/\.md/\.md\.html/' *.md
sed -i '1 i\<meta charset="utf-8">' *.html
#sed -i $md_html *.html
(echo $md_html |tee -a *.html) > /dev/null 2>&1 
/mnt/c/Program\ Files\ \(x86\)/Google/Chrome/Application/chrome.exe http://127.0.0.1:8000
if [ "$1" = bg ]; then
    (python3 -m http.server --bind 127.0.0.1  > /dev/null  2>&1 &) 
else
    python3 -m http.server --bind 127.0.0.1
fi 
cd ..