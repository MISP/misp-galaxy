python3 adoc_galaxy.py >a.txt
asciidoctor a.txt
asciidoctor-pdf -a allow-uri-read a.txt
cp a.html ../../misp-website/galaxy.html
cp a.pdf ../../misp-website/galaxy.pdf
scp a.html circl@cpab.circl.lu:/var/www/nwww.circl.lu/doc/misp-galaxy/index.html
scp a.pdf  circl@cpab.circl.lu:/var/www/nwww.circl.lu/doc/misp-galaxy/galaxy.pdf
