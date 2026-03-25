;fapte:
(deftemplate Agent
(field coordonata_agent (type INTEGER))
(field viteza (type INTEGER))
(field nr_saci (type INTEGER))
)
(deftemplate Obiect
    (field coordonata_obiect (type INTEGER))
    (field inaltime (type INTEGER))
    (field pericol (type INTEGER))
    (field valoare (type INTEGER))
)
;reguli:
(defrule Idle
(declare (salience 0))
=>
(assert (comanda Idle))s
)

(defrule descarca_saci_inteligent
    (declare (salience 2))
    (Agent (coordonata_agent ?ca)
           (nr_saci ?nrs&:(>= ?nrs 3)) ; Vrea sa descarce daca are 3, 4 sau 5 saci
    )
    ; NEGAM existenta unui pericol pe traseul din stanga sa.
    ; Am mutat conditia direct pe campul 'coordonata_obiect'.
    (not (Obiect (coordonata_obiect ?co&:(< ?co ?ca))
                 (inaltime ?y&:(> ?y 100))
                 (pericol 1)
         )
    )
    =>
    (assert (comanda mergi_la_platforma ?ca 20))
)
(defrule prinde_sac
    (declare (salience 1))
    (Agent  (coordonata_agent ?ca)
            (nr_saci ?nrs&:(< ?nrs 5))
    )
    ; 1. Cautam un sac si ii retinem inaltimea in ?y
    (Obiect (coordonata_obiect ?co)
            (inaltime ?y)
            (pericol 0)
    )
    ; 2. Conditia magica: NEGAM existenta oricarui alt sac care are inaltimea mai mare decat ?y
    (not (Obiect (inaltime ?y2&:(> ?y2 ?y)) (pericol 0)))
    =>
    (assert (comanda prindere_libera ?ca ?co))
)

(defrule evita_pericol_stanga
    (declare (salience 3))
    (Agent (coordonata_agent ?ca))
    (Obiect (coordonata_obiect ?co) (inaltime ?y) (pericol 1))

    ; Ne ferim de cel mai de jos pericol (care a trecut de y=250)
    (test (> ?y 250))
    (not (Obiect (inaltime ?y2&:(> ?y2 ?y)) (pericol 1)))

    ; Comparam centrele: Daca centrul pinguinului e mai la stanga decat centrul obiectului
    (test (< (+ ?ca 60) (+ ?co 30)))

    ; Distanta in modul (abs) dintre centre este mai mica de 100 de pixeli
    (test (< (abs (- (+ ?ca 60) (+ ?co 30))) 100))
    =>
    (assert (comanda evita_pericol ?ca (- ?ca 150))) ; Sare 150 de pixeli la stanga
)

(defrule evita_pericol_dreapta
    (declare (salience 3))
    (Agent (coordonata_agent ?ca))
    (Obiect (coordonata_obiect ?co) (inaltime ?y) (pericol 1))

    (test (> ?y 250))
    (not (Obiect (inaltime ?y2&:(> ?y2 ?y)) (pericol 1)))

    ; Daca centrul pinguinului e mai la dreapta decat centrul obiectului
    (test (>= (+ ?ca 60) (+ ?co 30)))

    (test (< (abs (- (+ ?ca 60) (+ ?co 30))) 100))
    =>
    (assert (comanda evita_pericol ?ca (+ ?ca 150))) ; Sare 150 de pixeli la dreapta
)

(defrule evita_sac_6_stanga
    (declare (salience 3)) ; Prioritate maxima de supravietuire
    (Agent (coordonata_agent ?ca) (nr_saci 5)) ; Doar cand are bratele pline
    (Obiect (coordonata_obiect ?co) (inaltime ?y) (pericol 0)) ; Se uita la saci

    (test (> ?y 250))
    (not (Obiect (inaltime ?y2&:(> ?y2 ?y)) (pericol 0)))

    (test (< (+ ?ca 60) (+ ?co 30)))
    (test (< (abs (- (+ ?ca 60) (+ ?co 30))) 100))
    =>
    (assert (comanda evita_pericol ?ca (- ?ca 150)))
)

(defrule evita_sac_6_dreapta
    (declare (salience 3))
    (Agent (coordonata_agent ?ca) (nr_saci 5))
    (Obiect (coordonata_obiect ?co) (inaltime ?y) (pericol 0))

    (test (> ?y 250))
    (not (Obiect (inaltime ?y2&:(> ?y2 ?y)) (pericol 0)))

    (test (>= (+ ?ca 60) (+ ?co 30)))
    (test (< (abs (- (+ ?ca 60) (+ ?co 30))) 100))
    =>
    (assert (comanda evita_pericol ?ca (+ ?ca 150)))
)
