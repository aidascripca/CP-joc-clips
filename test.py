import clips


def testeaza_agentul():
    # 1. Inițializăm mediul CLIPS
    env = clips.Environment()

    # 2. Încărcăm regulile și template-urile (asigură-te că agent.clp e în același folder)
    env.load("agent.clp")

    # 3. Resetăm mediul (golește faptele vechi)
    env.reset()

    # 4. Adăugăm fapte "dummy" (simulăm starea jocului dintr-un anumit cadru)
    print("--- Inseram datele curente ale jocului ---")
    # Pinguinul e la x=400, are viteza 10 și 2 saci în brațe
    env.assert_string("(Agent (coordonata_agent 400) (viteza 10) (nr_saci 2))")

    # Un sac (pericol 0, valoare 10) cade la x=450
    env.assert_string("(Obiect (coordonata_obiect 450) (pericol 0) (valoare 10))")

    # O nicovală (pericol 1) cade la x=300
    env.assert_string("(Obiect (coordonata_obiect 300) (pericol 1) (valoare 0))")

    # 5. Rulăm motorul de inferențe (lasă CLIPS să gândească)
    env.run()

    # 6. Citim concluziile (faptele noi generate de agent)
    print("\n--- Comenzi generate de Agent ---")
    for fact in env.facts():
        # Căutăm faptele nestructurate care reprezintă comenzi
        if fact.template.name == "comanda":
            print(f"Agentul a decis: {fact}")


if __name__ == "__main__":
    testeaza_agentul()