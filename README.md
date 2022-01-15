# Sireum

Versiune web rudimentară a jocului lui Marius Ghinea, descris aici:

https://leftclickghinea.ro/sireum-prezentare/

https://leftclickghinea.ro/sireum-argument/

Scrisă în Python curat (fără niciun framework), un pic de HTML și CSS, zero JavaScript. Include doar Sireum Push, nu și stilul Flip. Și are o mică nepotriveală cu regulile: numărul pieselor roșii nu e neapărat egal cu numărul pieselor albastre.

Fiecare joc - așezarea inițială a pieselor și istoria mutărilor - e conținut în URL. Pentru remote play va fi nevoie de o mică bază de date. Multiplayer-ul e doar hotseat deocamdată. Mno, zic „deocamdată”, dar nu știu dacă o să mai lucrez la el. Accept contribuții.

Pe o tablă 5x5, adversarul AI prezice tot jocul - deci, în funcție de pozițiile pieselor, se poate ori să nu ai nicio șansă de a-l bate, ori să ai șanse, de obicei mici (depinde foarte mult de norocul pe care-l ai la așezarea pieselor). Jocul te anunță că „The AI will win” atunci când e sigur de asta. Pe 5x5, de cele mai multe ori vei vedea mesajul după prima mutare. Pe table de la 7x7 în sus, AI-ul vede doar cu 10 mutări în avans și nu e prea grozav, dar are potențial. :)
