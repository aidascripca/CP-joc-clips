;fapte:
(deftemplate Agent
(field coordonata_agent (type INTEGER))
(field viteza (type INTEGER))
(field nr_saci (type INTEGER))
)
(deftemplate Obiect
(field coordonata_obiect (type INTEGER))
(field pericol (type INTEGER))
(field valoare (type INTEGER))
)

;reguli:
(defrule Idle
(declare (salience 0))
=>
(assert (comanda Idle))s
)

(defrule descarca_saci
    (declare (salience 2)) ; Prioritate maxima! Daca are 5 saci, ignora obiectele care cad
    (Agent (coordonata_agent ?ca)
           (nr_saci ?nrs&:(= ?nrs 3)) ; Daca are fix 5 saci
    )
    =>
    (assert (comanda mergi_la_platforma ?ca 20)) ; 20 este coordonata X a zonei de descarcare
)

(defrule prinde_sac
(declare (salience 1))
(Agent  (coordonata_agent ?ca)
		(viteza ?v)
		(nr_saci ?nrs&:(< ?nrs 5))
)
(Obiect (coordonata_obiect ?co)
		(pericol ?p&:(= 0 ?p))
		(valoare ?val)
)
=>
(assert (comanda prindere_libera ?ca ?co))
)

(defrule evita_pericol_stanga
    (declare (salience 3)) ; Prioritate maxima - viata e mai importanta decat sacii!
    (Agent (coordonata_agent ?ca))
    (Obiect (coordonata_obiect ?co) (pericol 1))
    (test (< ?ca ?co))              ; Pericolul e mai la dreapta de pinguin
    (test (< (- ?co ?ca) 75))       ; Diferenta de distanta e sub 75 de pixeli (pericol iminent)
    =>
    (assert (comanda evita_pericol ?ca (- ?ca 100))) ; Fugi 100 pixeli la stanga!
)

(defrule evita_pericol_dreapta
    (declare (salience 3))
    (Agent (coordonata_agent ?ca))
    (Obiect (coordonata_obiect ?co) (pericol 1))
    (test (>= ?ca ?co))             ; Pericolul e mai la stanga de pinguin
    (test (< (- ?ca ?co) 75))       ; E in raza de 75 de pixeli
    =>
    (assert (comanda evita_pericol ?ca (+ ?ca 100))) ; Fugi 100 pixeli la dreapta!
)
