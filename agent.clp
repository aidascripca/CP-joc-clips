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



(defrule prinde_sac_risc_asumat
    (declare (salience 3)) ; Prioritate MARE! Bate instinctul de descarcare.
    (Agent (coordonata_agent ?ca)
           (nr_saci ?nrs&:(< ?nrs 4))    ; E dispus sa riste atata timp cat nu e prea incarcat (sub 4 saci)
           (stamina ?st&:(>= ?st 70.0))  ; Conditia vitala: are energie mare
    )
    (Obiect (coordonata_obiect ?co)
            (inaltime ?y)
            (pericol 0)
    )
    ;  alege cel mai de jos sac
    (not (Obiect (inaltime ?y2&:(> ?y2 ?y)) (pericol 0)))
    =>
    (assert (comanda prindere_libera ?ca ?co))
)

; --- 2. DESCARCARE PREVENTIVA (Fara zone moarte) ---
(defrule decizie_descarcare_dinamica
    (declare (salience 2))
    (Agent (coordonata_agent ?ca)
           (nr_saci ?nrs&:(> ?nrs 0))
           (stamina ?st)
           (saci_scapati ?ss) 
    )

    ; Acopera absolut toate golurile de decizie dintre prindere si descarcare
    (test (or (= ?nrs 5)                                      ; Pline  -> Descarca
              (and (>= ?nrs 4) (< ?st 85.0))                  ; Limita pentru sprinturi
              (and (>= ?nrs 3) (< ?st 60.0))                  ; Limita pentru incarcare moderata
              (and (>= ?nrs 2) (< ?st 70.0) (< ?ss 8))        ; Prea obosit pentru 3 (Mod Normal)
              (and (>= ?nrs 2) (< ?st 50.0))                  ; Prea obosit pentru 3 (Mod Atentie/Panica)
              (and (>= ?nrs 1) (< ?st 40.0) (< ?ss 8))        ; Prea obosit sa mai prinda ceva (Mod Normal) -> Descarca!
              (and (>= ?nrs 1) (< ?st 20.0))                  ; Epuizare totala -> Arunca tot la platforma!
          )
    )
    (not (Obiect (coordonata_obiect ?co&:(< ?co ?ca)) (inaltime ?y&:(> ?y 100)) (pericol 1)))
    =>
    (assert (comanda mergi_la_platforma ?ca 20))
)

; --- ELIMINARE TIMPI MORTI ---
; Daca pinguinul are saci in brate, dar cerul este gol (nu cad saci),
; se va duce sa descarce imediat in loc sa stea degeaba si sa astepte.
(defrule descarca_timpi_morti
    (declare (salience 2))
    (Agent (coordonata_agent ?ca)
           (nr_saci ?nrs&:(> ?nrs 0)))

    ; NEGAM existenta oricarui obiect bun (sac) pe ecran
    (not (Obiect (pericol 0)))

    ; Ne asiguram ca drumul spre platforma e sigur (fara nicovala)
    (not (Obiect (coordonata_obiect ?co&:(< ?co ?ca))
                 (inaltime ?y&:(> ?y 100))
                 (pericol 1)))
    =>
    (assert (comanda mergi_la_platforma ?ca 20))
)

;(defrule descarca_saci_inteligent
;    (declare (salience 2))
;    (Agent (coordonata_agent ?ca)
;           (nr_saci ?nrs&:(>= ?nrs 3)) ; Vrea sa descarce daca are 3, 4 sau 5 saci
;    )
;    ; NEGAM existenta unui pericol pe traseul din stanga sa.
;    (not (Obiect (coordonata_obiect ?co&:(< ?co ?ca))
;                 (inaltime ?y&:(> ?y 100))
;                 (pericol 1)
;         )
;    )
;    =>
;    (assert (comanda mergi_la_platforma ?ca 20))
;)

(defrule prinde_sac
    (declare (salience 1))
    (Agent  (coordonata_agent ?ca)
            (nr_saci ?nrs)
            (stamina ?st)
    )
    (Obiect (coordonata_obiect ?co) (inaltime ?y) (pericol 0))
    (not (Obiect (inaltime ?y2&:(> ?y2 ?y)) (pericol 0)))

    ; LOGICA NOUA DE OBOSEALA:
    (test (or (and (>= ?st 50.0) (< ?nrs 5))                   ; Daca are >50% stamina, prinde pana la 4 saci.
              (and (< ?st 50.0) (> ?st 0.0) (< ?nrs 2))))      ; Daca e obosit, se oprește la 2 saci. Daca e la 0.0, STA DEGEABA.
    =>
    (assert (comanda prindere_libera ?ca ?co))
)

(defrule prinde_sac_atentie
    (declare (salience 2))
    (Agent  (coordonata_agent ?ca)
            (nr_saci ?nrs)
            (saci_scapati ?ss&:(>= ?ss 8))
            (stamina ?st)
    )
    (Obiect (coordonata_obiect ?co) (inaltime ?y&:(> ?y 200)) (pericol 0))
    (not (Obiect (inaltime ?y2&:(> ?y2 ?y)) (pericol 0)))

    ; Pastram aceleasi restrictii de siguranta si aici:
    (test (or (and (>= ?st 50.0) (< ?nrs 5))
              (and (< ?st 50.0) (> ?st 0.0) (< ?nrs 2))))
    =>
    (assert (comanda prindere_libera ?ca ?co))
)

(defrule panica_salveaza_jobul
    (declare (salience 3))
    (Agent (coordonata_agent ?ca)
           (nr_saci ?nrs)
           (saci_scapati ?ss&:(>= ?ss 15)) ; E pe cale sa fie concediat!
           (stamina ?st)
    )
    (Obiect (coordonata_obiect ?co) (inaltime ?y&:(> ?y 300)) (pericol 0))
    (not (Obiect (inaltime ?y2&:(> ?y2 ?y)) (pericol 0)))

    ; EXCEPȚIA LA REGULA: Aici prinde pana la 2 saci CHIAR SI DACA stamina este 0
    (test (or (and (>= ?st 50.0) (< ?nrs 5))
              (and (< ?st 50.0) (< ?nrs 2))))
    =>
    (assert (comanda prindere_libera ?ca ?co))
)

;comportament special - risc ridicat

;(defrule descarca_urgenta_oboseala
;    (declare (salience 2)) ; Prioritate egala cu descarcarea normala
;    (Agent (coordonata_agent ?ca)
;           (nr_saci ?nrs&:(>= ?nrs 3))   ; Are cel putin 1 sac
;           (stamina ?st&:(< ?st 30.0))   ; ESTE EXHAUSTAT (sub 30%)
;    )
;    ; Verifica sa nu fie o nicovala pe drumul spre platforma
;    (not (Obiect (coordonata_obiect ?co&:(< ?co ?ca))
;                 (inaltime ?y&:(> ?y 100))
;                 (pericol 1)
;         )
;    )
;    =>
;    (assert (comanda mergi_la_platforma ?ca 20))
;)



; evitare pericole

(defrule evita_pericol_stanga
    (declare (salience 4))
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
    (declare (salience 4))
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
    (declare (salience 4))
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
    (declare (salience 4))
    (Agent (coordonata_agent ?ca) (nr_saci 5))
    (Obiect (coordonata_obiect ?co) (inaltime ?y) (pericol 0))
    (test (> ?y 250))
    (not (Obiect (inaltime ?y2&:(> ?y2 ?y)) (pericol 0)))
    (test (>= (+ ?ca 60) (+ ?co 30)))
    (test (< (abs (- (+ ?ca 60) (+ ?co 30))) 100))
    =>
    (assert (comanda evita_pericol ?ca (+ ?ca 150)))
)