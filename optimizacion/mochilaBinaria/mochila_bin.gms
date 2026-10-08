set i contenedores /c1*c20/;

Table datos(i,*)
         peso    beneficioTon
c1         61            1100
c2         58            1147
c3         92            1442
c4         50            1591
c5        108            1078
c6         83            1385
c7         93            1777
c8        101            1196
c9         54            1753
c10        50            1371
c11        72            1517
c12        51            1675
c13       100            1193
c14       108            1177
c15        91            1365
c16       112            1143
c17        66            1314
c18        58            1526
c19       110            1470
c20        73            1605
;

Scalar capacidad /800/;

Parameter beneficio(i);
beneficio(i) = datos(i, 'beneficioTON');

Binary Variable x(i) "1 si carga el contenedor";
Variable z "Beneficio total";

Equations
    objetivo
    limitePeso;
    
objetivo .. z=e= sum(i, beneficio(i)*x(i));

limitePeso.. sum(i, datos(i, 'peso')*x(i)) =l= capacidad;

Model mochila /objetivo, limitePeso/;

option mip = cplex;
option optcr = 0;
option optca = 0;

Solve mochila using mip maximizing z;