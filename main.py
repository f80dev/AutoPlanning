import copy
import random
import datetime
from sys import argv

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import pandas as pd
from pandas.core.computation.expr import intersection

from _types import Salle, Professeur, Seance, Cours, Groupe, Plage, union, Distance, Config, \
    soustraction, check_plage,intersection
from export import export_planning_to_json, export_plages_to_json
from tools import strtodate, get_idx_day_of_string


def filter_plage(seances:list[Seance],dtStart:datetime,dtEnd:datetime):
    return [s for s in seances if s.plage.dtStart>=dtStart and s.plage.dtEnd<=dtEnd]


def convert_recurence_to_plage(recurence:str,periode_recurence=600,open_time=8,close_time=20,end_morning=12,open_afternoon=14,dtStart=datetime.datetime.now()) -> list[Plage]:
    recurence=recurence.lower()
    dt=dtStart.replace(hour=0,minute=0,second=0,microsecond=0)
    rc=[]
    for i in range(periode_recurence):
        if recurence=="week" or recurence=="semaine":
            rc.append(Plage(dt.replace(hour=open_time),dt.replace(hour=close_time)))
        else:
            idx_day = get_idx_day_of_string(recurence.split(" ")[0])
            if dt.weekday()==idx_day:
                if not " " in recurence:
                    rc.append(Plage(dt.replace(hour=open_time),dt.replace(hour=close_time)))
                else:
                    if ("am" in recurence) or ("matin" in recurence):
                        rc.append(Plage(dt.replace(hour=open_time),dt.replace(hour=end_morning)))
                    else:
                        rc.append(Plage(dt.replace(hour=open_afternoon),dt.replace(hour=close_time)))
        dt=dt+datetime.timedelta(days=1)
    return rc


class Agenda:
    salles:list[Salle]=[]
    professeurs:list[Professeur]=[]
    cours:list[Cours]=[]
    seances:list[Seance]=[]
    groupes:list[Groupe]=[]
    distances:list[Distance]=[]
    intern_log=""

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




    def log(self,text):
        self.intern_log+=datetime.datetime.now().strftime("%H:%M")+" - " +text + "\n"


    def load_data_from_sheet(self,spreadsheet_id, sheet_name):
        """
        Charge les données d'une feuille de calcul Google dans une liste de listes.
        :param spreadsheet_id: L'ID de votre feuille de calcul.
        :param range_name: La plage à lire, par exemple 'Feuille1!A1:B10'.
        :return: Une liste de listes contenant les données, ou None en cas d'erreur.
        """
        try:
            #print(f"Chargement de {sheet_name}")
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
    def init_listes(self,classeur_id ="./planning.xlsm",periode_recurence=300 ):
        self.professeurs = [Professeur(**p) for p in self.load_data_from_sheet(classeur_id, "Professeurs")]
        self.cours = [Cours(p) for p in self.load_data_from_sheet(classeur_id, "Cours")]
        self.salles = [Salle(**p) for p in self.load_data_from_sheet(classeur_id, "Salles")]
        self.groupes = [Groupe(**p) for p in self.load_data_from_sheet(classeur_id, "Groupes")]
        self.distances=[Distance(**p) for p in self.load_data_from_sheet(classeur_id, "Distances")]
        excludes=[Plage(p) for p in self.load_data_from_sheet(classeur_id, "Exclude")]

        dispos_prof=self.load_data_from_sheet(classeur_id, "DispoProf")
        for p in self.professeurs:
            p.dispos.clear()
            for d in dispos_prof:
                if p.Prof_ID==d["Prof_ID"]:
                    #print(f"Ajout de la plage {d}")
                    if type(d["Recurence"])!=float:
                        p.dispos=p.dispos+convert_recurence_to_plage(d["Recurence"],periode_recurence)
                    else:
                        p.dispos.append(Plage(d))

            p.dispos=union(p.dispos)
            #Procéde à la supression des périodes d'indisponibilité
            p.dispos=self.update_dispo_with_exclude(p.dispos,excludes)
            random.shuffle(p.dispos)

        #export_plages_to_json(p.dispos,"planning_output_profs.json",titre=p.Nom)

        dispo_salle = self.load_data_from_sheet(classeur_id, "DispoSalle")
        for s in self.salles:
            s.tags="" if type(s.tags)==float else s.tags
            s.dispos.clear()
            for d in dispo_salle:
                if s.Salle_ID==d["Salle_ID"]:
                    if type(d["Recurence"]) != float:
                        s.dispos = s.dispos + convert_recurence_to_plage(d["Recurence"], periode_recurence)
                    else:
                        s.dispos.append(Plage(d))

            s.dispos = union(s.dispos)
            s.dispos = self.update_dispo_with_exclude(s.dispos, excludes)
            check_plage(s.dispos)

            random.shuffle(s.dispos)

        for c in self.cours:
            c.requirments="" if type(c.requirments)==float else c.requirments


        return {
            "professeurs":self.professeurs,
            "cours":self.cours,
            "salles":self.salles,
            "groupes":self.groupes,
            "distances":self.distances
        }




    def get_salle(self,min_capacite=0,requirments="",white_list=[]) -> Salle | None:
        if min_capacite==0 and requirments=="":
            return random.choice(self.salles)
        else:
            random.shuffle(self.salles)
            for s in self.salles:
                if (len(white_list)==0 or s.Salle_ID in white_list) and s.capacite>=min_capacite and (requirments=="" or set(requirments.split(",")).issubset(s.tags.split(","))):
                    return s
            return None


    def get_cours(self,index=-1) -> Cours | None:
        if len(self.cours)==0: return None
        if index>0:
            #TODO a vérifier
            return sorted(self.cours,key=lambda x: x.duree,reverse=True)[index]
        else:
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
        random.shuffle(dispos)
        rc=[]
        for d in dispos: rc=rc+soustraction(d,plage)
        return rc




    def find_plage_for_duration(self,disponibilite:list[Plage], duree:int,requirment_day:str,try_to_save_lunch=6) -> Plage | None:
        """
        cherche une disponiblité et met a jour les dispos suite à réservation
        :param disponibilite:
        :param duree:
        :return:
        """
        random.shuffle(disponibilite)
        for d in disponibilite:
            #on tire au sort dans les disponibilite
            if (d.dtEnd-d.dtStart).total_seconds()>=duree*3600:
                creneaux=int(((d.dtEnd-d.dtStart).total_seconds()/3600)-duree)

                lunch=Plage(d.dtStart.replace(hour=12),d.dtStart.replace(hour=14))
                rc=d
                for _ in range(try_to_save_lunch):
                    option_placement=random.randint(0,creneaux)
                    rc = Plage(d.dtStart + datetime.timedelta(hours=option_placement),
                               d.dtStart + datetime.timedelta(hours=duree + option_placement))

                    if  rc.requirment_day(requirment_day) and intersection(rc,lunch) is None:
                        break

                return rc

        return None


    def placement_force(self):
        pass
        #TODO ici ne plus prendre aux hasard et balayé toutes les possibilités

    def run(self,filename="./planning.xlsm",max_occ=10,finder_occ=100000,log=False,start_agenda=None) -> Config | None:
        reliquats=[]
        for occ in range(max_occ):
            rc = False
            if start_agenda is None:
                self.init_listes(filename,periode_recurence=360)
            else:
                self.professeurs=copy.deepcopy(start_agenda["professeurs"])
                self.cours=copy.deepcopy(start_agenda["cours"])
                self.salles=copy.deepcopy(start_agenda["salles"])
                self.groupes=copy.deepcopy(start_agenda["groupes"])
                self.distances=copy.deepcopy(start_agenda["distances"])


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
                        requirments=c.requirments,
                        white_list=c.forces["salles"]
                    )

                    if s is None:
                        self.log(f"Le cours {c} est imcompatible avec les salles existantes")
                        break

                    if s and len(s.dispos)>0:
                        check_plage(s.dispos)
                        plage_seance = self.find_plage_for_duration(s.dispos,c.duree,",".join(c.forces["day"]))

                        if plage_seance and plage_seance.dtStart>strtodate(c.minDate) and plage_seance.dtEnd<strtodate(c.maxDate):
                            b=True
                            for p in profs:
                                if not self.check_plage(p.dispos, plage_seance):
                                    b=False
                                    break

                            if b:
                                for k in c.props:
                                    if type(c.props[k])==float: c.props[k]=""

                                planning.append(Seance(plage_seance, s.Salle_ID, c.Prof_ID, c.titre,c.props,c.groupe))
                                s.dispos = self.reserve(s.dispos, plage_seance)
                                for p in profs:
                                    p.dispos = self.reserve(p.dispos, plage_seance)
                                self.cours.remove(c)
                                i=i-1
                                if log: print(f"\rNb de cours restant : {len(self.cours)}",end="")
                        else:
                            pass
                else:
                    raise RuntimeError("Groupe inconnu")

            if rc:
                return self.eval_config(planning)
            else:
                print(f" - Echec de planification {occ} tentatives. {total_cours - len(self.cours)}/{total_cours} planifiés")
                reliquats = reliquats + self.cours

        return Config(planning, reliquat=reliquats, result=False,log=self.intern_log)



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

        return Config(planning,distance,reliquat=[],result=True)



    def update_dispo_with_exclude(self, l:list[Plage], excludes:list[Plage]) -> list[Plage]:
        for e in excludes:
            rc = []
            for d in l:
                rc = rc + soustraction(d, e)
            l=rc
        return rc


import concurrent.futures


def execute_run(filename, max_occ=20,finder_occ=80000,log=False):
    # On crée une instance propre à chaque processus
    agenda_instance = Agenda()

    config=agenda_instance.run(filename=filename, max_occ=max_occ,finder_occ=finder_occ,log=log,start_agenda=Agenda().init_listes(filename))
    print(f"{config}")

    return config





if __name__ == '__main__':
    n_executions = int(argv[1] if len(argv)>1 else 1)

    # On utilise ProcessPoolExecutor pour le vrai parallélisme CPU
    with concurrent.futures.ProcessPoolExecutor() as executor:
        # Création des futurs : on lance 10 fois la méthode run
        # Note : On passe les arguments nécessaires à run()
        futures = [executor.submit(execute_run, "./planning.xlsm", log=(n_executions==1)) for _ in range(n_executions)]

        results = []
        for future in concurrent.futures.as_completed(futures):
            config = future.result()
            if config.result:
                results.append(config)
                print(f"Planification réussie terminée. Distance : {config.distance}")


    # Optionnel : Trier par la meilleure distance (la plus faible)
    if len(results)>0:
        best_config = min(results, key=lambda x: x.distance)
        print(f"Meilleure configuration trouvée avec une distance de : {best_config.distance}")

        # export_planning_to_excel(
        #     filter_plage(best_config.planning, datetime.datetime.now(),
        #                  datetime.datetime.now() + datetime.timedelta(days=60)),
        #     min_hour=8,
        #     max_hour=20
        # )

        export_planning_to_json(
            filter_plage(best_config.planning, datetime.datetime.fromisoformat("2026-01-01"),
                         datetime.datetime.fromisoformat("2026-12-31"))
        )

