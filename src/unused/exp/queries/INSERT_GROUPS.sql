BEGIN;

BEGIN;
INSERT INTO groupset VALUES (DEFAULT)  RETURNING groupsetid;
COMMIT ;


BEGIN;
INSERT INTO candidategroups (edges, vehicles, alpha, groupquantity, initializationt, pairwiseincentivest, initialgroupst,
                             persistgroupst, sumsp, formedgroups, groupsetid)
VALUES('0','0','0','0','0',
           '0','0','0','0','0',
           (SELECT groupsetid FROM groupset ORDER BY groupsetid DESC LIMIT 1));
COMMIT ;


BEGIN;
INSERT INTO public.groups (groupsetid, vehicles)
VALUES ( (SELECT groupsetid FROM groupset ORDER BY groupsetid DESC LIMIT 1), '{0,1}');
COMMIT;



COMMIT;