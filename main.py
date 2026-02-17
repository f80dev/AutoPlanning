import random
import datetime
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import pandas as pd

from _types import Salle, Professeur, Seance, Cours, Groupe, Plage, intersection, union, exclude_from, Distance, Config
from export import export_planning_to_excel
from tools import strtodate


def filter_plage(seances:list[Seance],dtStart:datetime,dtEnd:datetime):
    return [s for s in seances if s.plage.dtStart>=dtStart and s.plage.dtEnd<=dtEnd]


class Agenda:

    salles:list[Salle]=[]
    professeurs:list[Professeur]=[]
    cours:list[Cours]=[]
    seances:list[Seance]=[]
    groupes:list[Groupe]=[]
    distances:list[Distance]=[]

    # Si vous modifiez ces portées, supprimez le fichier token.json.
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

    def get_groupe(self, groupe_ID: int) -> Groupe | None:
        for g in self.groupes:
            if g.Groupe_ID == groupe_ID: return g
        return None

    def get_google_creds(self):
        """Authentification Google centralisée, retourne les credentials."""
        scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
        return Credentials.from_service_account_file("credentials.json")






    def load_data_from_sheet(self,spreadsheet_id, sheet_name):
        """
        Charge les données d'une feuille de calcul Google dans une liste de listes.
        :param spreadsheet_id: L'ID de votre feuille de calcul.
        :param range_name: La plage à lire, par exemple 'Feuille1!A1:B10'.
        :return: Une liste de listes contenant les données, ou None en cas d'erreur.
        """
        try:

            if "/" in spreadsheet_id:
                # La première ligne est automatiquement utilisée comme en-tête.
                df = pd.read_excel(spreadsheet_id, sheet_name=sheet_name)

                # Convertir le DataFrame en une liste de dictionnaires.
                # L'orientation 'records' crée exactement le format souhaité.
                rc = df.to_dict(orient='records')
            else:
                service = build('sheets', 'v4', credentials=self.get_google_creds())

                # Appeler l'API Sheets
                sheet = service.spreadsheets()
                result = sheet.values().get(spreadsheetId=spreadsheet_id,
                                            range=sheet_name).execute()
                values = result.get('values', [])

                cols=values[0]
                rc=[]
                for v in values[1:]:
                    rc.append(dict(zip(cols, v)))

            return rc

        except HttpError as err:
            print(f"Une erreur s'est produite: {err}")
            return None



    def convert_plage_old(self,debut, fin) -> list:
        """
        Génère une liste de créneaux horaires d'une heure entre une date de début et de fin.

        Args:
            debut (datetime): Le moment de début de la plage (inclus).
            fin (datetime): Le moment de fin de la plage (exclus).

        Returns:
            list[datetime]: Une liste d'objets datetime, un pour chaque heure
                            commençant dans l'intervalle. Retourne une liste vide
                            si la date de début est après ou égale à la date de fin.
        """

        if type(debut)==str:
            debut=debut.replace("  "," ").replace(" ","/2026 ")
            debut=datetime.datetime.strptime(debut,"%d/%m/%Y %H:%M")

        if type(fin)==str:
            fin = fin.replace("  "," ").replace(" ", "/2026 ")
            fin=datetime.datetime.strptime(fin,"%d/%m/%Y %H:%M")

        if debut >= fin:
            return []

        heures_disponibles = []
        heure_actuelle = debut

        # On continue tant que l'heure actuelle est strictement inférieure à l'heure de fin
        while heure_actuelle < fin:
            heures_disponibles.append(heure_actuelle)
            # On ajoute une heure pour passer au créneau suivant
            heure_actuelle += datetime.timedelta(hours=1)

        return heures_disponibles




    #"1e7wdfc2brpNwbefhA9dJXx81zs93bGpRM_Th_eiHwBI"
    def init_listes(self,classeur_id ="./planning.xlsx" ):
        self.professeurs = [Professeur(**p) for p in self.load_data_from_sheet(classeur_id, "Professeurs")]
        self.cours = [Cours(**p) for p in self.load_data_from_sheet(classeur_id, "Cours")]
        self.salles = [Salle(**p) for p in self.load_data_from_sheet(classeur_id, "Salles")]
        self.groupes = [Groupe(**p) for p in self.load_data_from_sheet(classeur_id, "Groupes")]
        self.distances=[Distance(**p) for p in self.load_data_from_sheet(classeur_id, "Distances")]
        excludes=[p for p in self.load_data_from_sheet(classeur_id, "Exclude")]

        dispos_prof=self.load_data_from_sheet(classeur_id, "DispoProf")
        for p in self.professeurs:
            p.dispos.clear()
            for d in dispos_prof:
                if p.Prof_ID==d["Prof_ID"]:
                    #print(f"Ajout de la plage {d}")
                    p.dispos.append(Plage(d))

            p.dispos=union(p.dispos)
            for e in excludes:
                p.dispos=exclude_from(p.dispos,Plage(e))

            random.shuffle(p.dispos)

        dispo_salle = self.load_data_from_sheet(classeur_id, "DispoSalle")
        for s in self.salles:
            s.tags="" if type(s.tags)==float else s.tags
            s.dispos.clear()
            for d in dispo_salle:
                if s.Salle_ID==d["Salle_ID"]:
                    s.dispos.append(Plage(d))

            s.dispos = union(s.dispos)
            random.shuffle(s.dispos)

        for c in self.cours:
            c.requirments="" if type(c.requirments)==float else c.requirments



        return {
            "professeurs":self.professeurs,
            "cours":self.cours,
            "salles":self.salles,
            "goupes":self.groupes,
            "distances":self.distances
        }




    def get_salle(self,min_capacite=0,requirments="") -> Salle | None:
        if min_capacite==0 and requirments=="":
            return random.choice(self.salles)
        else:
            for _ in range(1000):
                s=random.choice(self.salles)
                if s.capacite>=min_capacite and (requirments=="" or set(requirments.split(",")).issubset(s.tags.split(","))):
                    return s
            return None




    def get_cours(self) -> Cours | None:
        if len(self.cours)==0: return None
        return random.choice(self.cours)


    def check_plage(self,dispos:list,plage:Plage) -> bool:
        for d in dispos:
            if d.dtEnd>=plage.dtEnd and d.dtStart<=plage.dtStart:
                 return True
        return False


    def get_profs(self,prof_id=None):
        rc=[]
        if prof_id is None:
            rc.append(random.choice(self.professeurs))
        else:
            for p in self.professeurs:
                if p.Prof_ID in prof_id.split(","): rc.append(p)

        return rc


    def update_plage(self,dispo:Plage,plage:Plage) -> Plage | None:
        """
        reserve une plage dans une disponibilité (soit au début soit à la fin)
        :param dispo:
        :param plage:
        :return: la disponibilité
        """
        if dispo[0]>plage[0] or dispo[1]<plage[1]: return None
        if random.choice([0,1])==0:
            return (plage[1],dispo[1])
        else:
            return (dispo[0],plage[0])




    def update_dispos(self,dispo:list,plage:Plage):
        p=self.check_plage(dispo,plage)
        dispo.append(self.update_plage(p,plage))
        dispo.remove(p)
        return dispo


    def reserve(self,dispos:list[Plage],plage:Plage) -> list[Plage]:
        return exclude_from(dispos,plage)




    def find_plage_for_duration(self,disponibilite:list[Plage], duree:int) -> Plage | None:
        """
        cherche une disponiblité et met a jour les dispos suite à réservation
        :param disponibilite:
        :param duree:
        :return:
        """
        for _ in range(10000):
            #on tire au sort dans les disponibilite
            d=random.choice(disponibilite)
            if (d.dtEnd-d.dtStart).total_seconds()>=duree*3600:
                if random.choice([0,1])==0:
                    return Plage(d.dtStart,d.dtStart+datetime.timedelta(hours=duree))
                else:
                    return Plage(d.dtEnd-datetime.timedelta(hours=duree),d.dtEnd)

        return None


    def eval_distance(self):
        pass


    def run(self,filename="./planning.xlsx",max_occ=1000,finder_occ=100000) -> Config | None:
        for occ in range(max_occ):
            rc = False
            self.init_listes(filename)

            planning = []
            total_cours = len(self.cours)

            for i in range(finder_occ):
                c = self.get_cours()
                if c is None:
                    rc = True
                    break

                profs = self.get_profs(c.Prof_ID)
                if self.get_groupe(c.groupe):
                    s = self.get_salle(
                        min_capacite=self.get_groupe(c.groupe).effectif,
                        requirments=c.requirments
                    )

                    if len(s.dispos)>0:
                        plage_seance = self.find_plage_for_duration(s.dispos,c.duree)

                        if plage_seance and plage_seance.dtStart>strtodate(c.minDate) and plage_seance.dtEnd<strtodate(c.maxDate):
                            b=True
                            for p in profs:
                                if not self.check_plage(p.dispos, plage_seance):
                                    b=False
                                    break

                            if b:
                                planning.append(Seance(plage_seance, s.Salle_ID, c.Prof_ID, c.titre, c.groupe,p.Nom))
                                s.dispos = self.reserve(s.dispos, plage_seance)
                                for p in profs:
                                    p.dispos = self.reserve(p.dispos, plage_seance)
                                self.cours.remove(c)
                        # else:
                        #     print("Programmation hors plage")
                else:
                    raise RuntimeError("Groupe inconnu")

            if rc:
                return self.eval_config(planning)
            else:
                print(f"Echec de planification {occ} tentatives. {total_cours - len(self.cours)}/{total_cours} planifiés")

        return None

    def add_night_to_indisponibilite(self,indisponibilite:list[Plage],
                                     dtStart:datetime.datetime,dtEnd:datetime.datetime,
                                     open_hour:int=8,close_hour:int=20):
        rc=list()
        l=sorted(indisponibilite, key=lambda x: x.dtStart)
        for d in range(dtStart,dtEnd,3600*24):
            pass



    def create_disponibilite(self, indisponibilite:list[Plage]) -> list[Plage]:
        rc=[]
        # Tri des plages par date de début (premier élément du tuple)
        l = sorted(indisponibilite, key=lambda x: x.dtStart)
        for idx in range(len(indisponibilite)-1):
            start=l[idx].dtStart
            end=l[idx+1].dtEnd
            rc.append(Plage(start,end))
        return rc


    def get_distance_between(self,salle1:str,salle2:str):
        for d in self.distances:
            if d.Salle_1==salle1 and d.Salle_2==salle2: return d.distance
        return 0


    def eval_config(self, planning:list[Seance]) -> Config:
        groups=set([s.group for s in planning])
        distance=0
        for g in groups:
            seances=sorted([s for s in planning if s.group==g],key=lambda s: s.plage.dtStart)
            for idx in range(0,len(seances)-1):
                if seances[idx].plage.dtStart.day==seances[idx+1].plage.dtStart.day:
                    distance=distance+self.get_distance_between(seances[idx].salle,seances[idx+1].salle)

        return Config(planning,distance)



# if __name__ == '__main__':
#     a=Agenda()
#     config=a.run(max_occ=200)
#     if config:
#         export_planning_to_excel(
#             filter_plage(config["planning"],datetime.datetime.now(),datetime.datetime.now()+datetime.timedelta(days=30)),
#             min_hour=8,
#             max_hour=20
#         )


import concurrent.futures


def execute_run(filename, max_occ):
    # On crée une instance propre à chaque processus
    agenda_instance = Agenda()
    return agenda_instance.run(filename=filename, max_occ=max_occ)

if __name__ == '__main__':
    n_executions = 10

    # On utilise ProcessPoolExecutor pour le vrai parallélisme CPU
    with concurrent.futures.ProcessPoolExecutor() as executor:
        # Création des futurs : on lance 10 fois la méthode run
        # Note : On passe les arguments nécessaires à run()
        futures = [executor.submit(execute_run, "./planning.xlsx", 20) for _ in range(n_executions)]

        results = []
        for future in concurrent.futures.as_completed(futures):
            config = future.result()
            if config:
                results.append(config)
                print(f"Planification réussie terminée. Distance : {config['distance']}")


    # Optionnel : Trier par la meilleure distance (la plus faible)
    if results:
        best_config = min(results, key=lambda x: x['distance'])
        print(f"Meilleure configuration trouvée avec une distance de : {best_config['distance']}")

        export_planning_to_excel(
            filter_plage(best_config["planning"], datetime.datetime.now(),
                         datetime.datetime.now() + datetime.timedelta(days=60)),
            min_hour=8,
            max_hour=20
        )