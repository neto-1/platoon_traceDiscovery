CREATE OR REPLACE VIEW convexsavings AS SELECT
test.testid,
test.datetime,
test.edges,
test.vehicles,
cg.sumsp AS shortpath,
flp.sumsp AS platoonvehiclessp,
flp.sumsps AS platoonpath,
((cg.sumsp-flp.sumsp)+flp.sumsps) as objectivevalue
FROM test
INNER JOIN candidategroups cg
    on test.testid = cg.testid
INNER JOIN forminggroupslp flp
    on flp.testid = test.testid
ORDER BY test.edges, test.vehicles;

CREATE OR REPLACE VIEW sdsavings AS SELECT
test.testid,
test.datetime,
test.edges,
test.vehicles,
cgs.sumsp AS shortpath,
flp.sumsp AS platoonvehiclessp,
flp.sumsps AS platoonpath,
((cgs.sumsp-flp.sumsp)+flp.sumsps) as objectivevalue
FROM test
INNER JOIN candidategroupssd cgs
    on test.testid = cgs.testid
INNER JOIN forminggroupslp flp
    on flp.testid = test.testid
ORDER BY test.edges, test.vehicles;


CREATE VIEW optimumsavings AS SELECT t1.edges,
    t1.vehicles,
    t2.objectivevalue
   FROM (test t1
     JOIN optimum t2 ON ((t1.testid = t2.testid)))
  ORDER BY t1.edges, t1.vehicles
;


CREATE OR REPLACE VIEW convexsdoptimumsavings AS SELECT sdsavings.edges,
    sdsavings.vehicles,
    sdsavings.shortpath,
    optimumsavings.objectivevalue as optimumov,
    sdsavings.objectivevalue as sdov,
    convexsavings.objectivevalue as convexov
   FROM ((( SELECT DISTINCT sdsavings_1.edges,
            sdsavings_1.vehicles,
            sdsavings_1.shortpath,
            sdsavings_1.platoonpath,
            sdsavings_1.platoonvehiclessp,
            sdsavings_1.objectivevalue
           FROM sdsavings sdsavings_1) sdsavings
     JOIN ( SELECT DISTINCT convexsavings_1.edges,
            convexsavings_1.vehicles,
            convexsavings_1.shortpath,
            convexsavings_1.platoonpath,
            convexsavings_1.platoonvehiclessp,
            convexsavings_1.objectivevalue
           FROM convexsavings convexsavings_1) convexsavings ON (((sdsavings.edges = convexsavings.edges) AND (sdsavings.vehicles = convexsavings.vehicles))))
     JOIN ( SELECT DISTINCT optimumsavings_1.edges,
            optimumsavings_1.vehicles,
            optimumsavings_1.objectivevalue
           FROM optimumsavings optimumsavings_1) optimumsavings ON (((sdsavings.edges = optimumsavings.edges) AND (sdsavings.vehicles = optimumsavings.vehicles))))
;