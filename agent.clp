;fapte:
(deftemplate Agent
    (field coordonata_agent (type INTEGER))
    (field viteza (type INTEGER))
    (field nr_saci (type INTEGER))
    (field stamina (type FLOAT))
    (field saci_scapati (type INTEGER))
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
    (assert (comanda Idle))
)
;comportament normal

(defrule descarca_saci_inteligent
    (declare (salience 2))
    (Agent (coordonata_agent ?ca)
           (nr_saci ?nrs&:(>= ?nrs 3)) ; Vrea sa descarce daca are 3, 4 sau 5 saci
    )
    ; NEGAM existenta unui pericol pe traseul din stanga sa.
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
    ; 2. Conditia magica: NEGAM existenta oricarui alt sac care are inaltimea mai mare
    (not (Obiect (inaltime ?y2&:(> ?y2 ?y)) (pericol 0)))
    =>
    (assert (comanda prindere_libera ?ca ?co))
)

;comportament special - risc ridicat

(defrule descarca_urgenta_oboseala
    (declare (salience 2)) ; Prioritate egala cu descarcarea normala
    (Agent (coordonata_agent ?ca)
           (nr_saci ?nrs&:(>= ?nrs 1))   ; Are cel putin 1 sac
           (stamina ?st&:(< ?st 30.0))   ; ESTE EXHAUSTAT (sub 30%)
    )
    ; Verifica sa nu fie o nicovala pe drumul spre platforma
    (not (Obiect (coordonata_obiect ?co&:(< ?co ?ca))
                 (inaltime ?y&:(> ?y 100))
                 (pericol 1)
         )
    )
    =>
    (assert (comanda mergi_la_platforma ?ca 20))
)

(defrule panica_salveaza_jobul
    (declare (salience 2)) ; Suprascrie prinderea normala (salience 1) cand e urgenta
    (Agent (coordonata_agent ?ca)
           (nr_saci ?nrs&:(< ?nrs 5))
           (saci_scapati ?ss&:(>= ?ss 16)) ; Mai are putin si e concediat
    )
    (Obiect (coordonata_obiect ?co)
            (inaltime ?y&:(> ?y 350))      ; Sacul e foarte aproape de a atinge solul
            (pericol 0)
    )
    (not (Obiect (inaltime ?y2&:(> ?y2 ?y)) (pericol 0)))
    =>
    (assert (comanda prindere_libera ?ca ?co))
)

; evitare pericole

(defrule evita_pericol_stanga
    (declare (salience 3))
    (Agent (coordonata_agent ?ca))
    (Obiect (coordonata_obiect ?co) (inaltime ?y) (pericol 1))
    (test (> ?y 250))
    (not (Obiect (inaltime ?y2&:(> ?y2 ?y)) (pericol 1)))
    (test (< (+ ?ca 60) (+ ?co 30)))
    (test (< (abs (- (+ ?ca 60) (+ ?co 30))) 100))
    =>
    (assert (comanda evita_pericol ?ca (- ?ca 150)))
)

(defrule evita_pericol_dreapta
    (declare (salience 3))
    (Agent (coordonata_agent ?ca))
    (Obiect (coordonata_obiect ?co) (inaltime ?y) (pericol 1))
    (test (> ?y 250))
    (not (Obiect (inaltime ?y2&:(> ?y2 ?y)) (pericol 1)))
    (test (>= (+ ?ca 60) (+ ?co 30)))
    (test (< (abs (- (+ ?ca 60) (+ ?co 30))) 100))
    =>
    (assert (comanda evita_pericol ?ca (+ ?ca 150)))
)

(defrule evita_sac_6_stanga
    (declare (salience 3))
    (Agent (coordonata_agent ?ca) (nr_saci 5))
    (Obiect (coordonata_obiect ?co) (inaltime ?y) (pericol 0))
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