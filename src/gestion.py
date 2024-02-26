import tkinter as tk
import sqlite3 as sql
import tkinter.font as tkFont
from tkinter import filedialog
from tkinter import messagebox
import pickle
import os
from random import randrange
from terrain import Terrain


class Gestion( tk.Frame):
    """Fenêtre d'Application principale"""

    def __init__(self, master=None, mb=None, fichier=None):
        tk.Frame.__init__(self)
        self.master.title("Les plantes et leur classification")
        self.master.geometry("1920x1080")
        self.mb= mb
        self.pack()
        self.createMenuBar()

        # variables globales
        self.resultvar =  tk.StringVar()
        self.nomvar=  tk.StringVar()
        self.detailvar=  tk.StringVar()
        self.periodefleurvar=  tk.StringVar()
        self.couleurfleurvar=  tk.StringVar()
        self.typeplantevar= tk.StringVar()
        self.typevegetationvar=  tk.StringVar()
        self.typefeuillagevar=  tk.StringVar()
        self.hauteurvar=  tk.StringVar()
        self.rusticitevar=  tk.StringVar()
        self.expositionvar=  tk.StringVar()
        self.typesolvar=  tk.StringVar()
        self.aciditesolvar=  tk.StringVar()
        self.humiditesolvar=  tk.StringVar()
        self.utilisationvar=  tk.StringVar()
        self.detailsource=[]


        # les différents widget de l'interface
        fonttitre= tkFont.Font(family='helvetica', size='14', weight='bold')
        bt1=  tk.Button(self, text="recherche par nom", command=self.recherche1)
        bt2=  tk.Button(self, text="recherche par critères", command=self.recherche2)
        bt3=  tk.Button(self, text="recherche phylogénique", command=self.recherche3)

        interro1 =  tk.LabelFrame(self, text="Saisissez un ou plusieurs noms séparés par des virgules", font=fonttitre, \
            foreground= "dark slate grey", bg='dark grey', bd=3,  padx=10, pady=10)
        tk.Entry(interro1, textvariable= self.nomvar, width = 50).pack(anchor=  "w", pady=30)
        tk.Label(interro1, text="Les noms seront recherchés dans tous les champs 'nom' de l'encyclopédie", bg='dark grey').pack(anchor= "w", pady=30)
        tk.Button(interro1, text="Rechercher", bg= "dark slate grey",foreground="white", command= self.rechercher).pack(pady=30)
        interro2 =  tk.LabelFrame(self, text="Choisissez un ou plusieurs critères", font= fonttitre, \
            foreground= "dark slate grey", bg='dark grey', bd=3, padx=10, pady=10)
        listeOptions1= ('été', 'automne', 'hiver', 'printemps', 'janvier', 'février', 'mars', 'avril', 'mai', 'juin','juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre')
        self.periodefleur=  tk.OptionMenu(interro2, self.periodefleurvar, *listeOptions1)
        listeOptions= ('blanc', 'rose', 'jaune', 'orange', 'bleu', 'rouge', 'violette', 'mauve', 'lilas', 'rougeâtre', 'vert', 'verdâtre', 'crème', 'pourpre', 'jaunâtre', 'violet', 'saumon', 'fuchsia', 'noir', 'blanchâtre', 'brun', 'marron', 'magenta', 'doré', 'carmin', 'beige', 'blanche', 'ocre', 'brunâtre', 'rosé', 'orangé', 'bleuté', 'violacé', 'pêche', 'lavande', 'aubergine', 'indigo', 'paille', 'gris', 'orangé', 'anis', 'roussâtre')
        listeOptions2= sorted(listeOptions)
        self.couleurfleur=  tk.OptionMenu(interro2, self.couleurfleurvar, *listeOptions2)
        listeOptions= ('fleur', 'plante dappartement', 'plante tropicale', 'plante verte décorative', "plante d'intérieur", 'arbuste à fleurs', 'plante ornementale', 'plante de massif', 'grimpant', 'arbre', 'arbuste', 'petit arbre', 'liane', 'succulente', 'vivace', 'vivace succulente', 'plante grasse', 'exotique', 'plante méditerranéenne', 'vivace arbustive exotique', 'plante verte', 'plante xérophyte', 'sous-abrisseau', 'légume', 'plante potagère','plante au feuillage ornementale', 'plante tubéreuse', 'bulbeuse à fleurs', 'bulbe', 'herbacée', "plante fleurie d'intérieur", 'vivace à rhizomes', 'fruitier','vivace tapissante', 'adventice', 'aromatique', 'plante de rocaille', 'plante aquatique', 'plante à caudex', 'plante de bassin', 'plante indigène', 'palmier', 'conifère',  'plante à tubercule', 'plante médicinale', 'Fougère', 'annuelle ou bisannuelle', 'plante officinale', 'plante alpine', 'mauvaise herbe', 'bisannuelle', 'épiphyte', 'couvre-sol', 'condiment', 'cactus', 'arbrisseau', 'volubile', 'arbustif', 'fruit', 'graminée', 'carnivore', 'bruyère', 'tourbière', 'plante semi-arbustive', 'sous-arbrisseau', 'orchidée', 'champignon', 'herbe', 'rampant', 'rosier', 'agrume')
        listeOptions3= sorted(listeOptions)
        self.typeplante= tk.OptionMenu(interro2, self.typeplantevar, *listeOptions3)
        listeOptions=('vivace', 'arbustive', 'vivace arbustive', 'vivace cultivé en annuelle', 'feuillu', 'succulente', 'arbuste', 'annuel', 'bulbe', 'persistant', 'rhizomateuse', 'petit arbre', 'bisannuel', 'herbacée', 'intérieur', 'arborescente', 'cespiteuse', 'buissonnante','tubercule', 'sauvage', 'adventice', 'arbirée', 'arbrisseau', 'sous-arbrisseau', 'semi-arbustive', 'volubile', 'carnivore', 'arbustif', 'semi-grimpante', 'rampant', 'arbre', 'luxuriant',  'caduc', 'liane', 'fruitier')
        listeOptions4= sorted(listeOptions)
        self.typevegetation=  tk.OptionMenu(interro2, self.typevegetationvar, *listeOptions4)
        listeOptions= ('persistant', 'caduc', 'rigide', 'charnu', 'succulent', 'semi-persistant', 'semi-caduc', 'réduit', 'liane', 'pas de feuille', 'marescent', 'petites feuilles', 'variable', 'caduque', 'épines', 'non persistant', 'perd', 'dormance', 'disparait', 'cornet', 'bec de perroquet', 'annuel', 'perte', 'rustique')
        ListeOptions5= sorted(listeOptions)
        self.typefeuillage=  tk.OptionMenu(interro2, self.typefeuillagevar, *ListeOptions5)
        self.dict_hauteur= {'moins de 20 cm': ('5 cm', 'de 4 à 7 cm', 'de 2 à 4 cm', '8 cm', '10 cm','15 à 20 cm','15 cm','5 à 25 cm','de 15 à 25 cm','de 10 à 15 cm',
                                                'de 10à 60 cm selon les variétés','10 à 20 cm','15 à 30 cm','5 à 15 cm','de 15 cm à 30 cm selon les variétés','12 cm',
                                                '6 à 15 cm','15 à 40 cm','2cm, étalement 10 cm','de 5 à 15 cm de haut','de 15 cm à 60 cm selon les variétés'),
                            'entre 20 et 50 cm': ('30 à 45 cm','20 cm','50 cm','40 cm','25 cm','12 cm à 50 cm','20 à 50 cm','20 à 45 cm','20 à 30 cm','5 à 25 cm','40 à 60 cm','30 à 60 cm',
                                                "jusqu'à 40cm",'de 30 à 40 cm',"jusqu'à 50cm",'de 15 à 25 cm','de 30 à 50 cm','40 cm pour le feuillage','45 cm','45 à 70 cm',
                                                '20cm','de 30 à 60 cm','15 à 30 cm','35 à 60 cm',"40 à 80 cm",'30 cm','de 20 cm à 40 cm','de 15 cm à 30 cm selon les variétés',
                                                '0.30 à 3 m selon les variétés','de 30 à 50 cm',"20cm, avec des racines de 50cm sous l'eau",'25 à 30 cm','environ 20 cm',
                                                '15 à 40 cm','20 à 35 cm','30 cm, 70 cm lors de la floraison','20 à 30 cm, 50 cm en fleur','30 à 75 cm','de 15 cm à 60 cm selon les variétés',
                                                '30 à 50 cm'),
                            'entre 50 et 100 cm': ('60 à 80 cm','40 à 90 cm','50cm, 2,50m avec la hampe florale','40 à 80 cm en tous sens','60 cm','60 cm à 1 m',
                                                '80 cm, hampe florale de 1 m 50','40 à 60 cm',"jusqu'à 70 cm",'30 à 60 cm','70 cm','80 à 100 cm','80 cm',"jusqu'à 90cm pour le feuillage",
                                                'de 50 à 100 cm','de 50 à 70 cm','de 60 à 120 cm','environ 70 cm','75 cm','de 50 à 80 cm','80 à 120 cm','90 cm','environ 60 cm',
                                                'de 50 à 80 cm selon les espèces','50 cm','40 à 50 cm','45 à 70 cm','de 30 à 60 cm','60 cm à 1,50 m','35 à 60 cm',
                                                '50 à 100 cm','40 à 80 cm','60 cm en fleur','0,60 à 1 m','70  à 180 cm',"jusqu'à 1 m",'1m','60 à 90 cm','0.30 à 3 m selon les variétés','1 m',
                                                '50 cm à plusieurs mètres','50 à 90 cm','70 à 120 cm','de 60 à 1,5 m',"tiges volubile jusque 0.80m de long voir 2m dans la nature",
                                                "tiges jusquà 1 m",'50 cm à 1m','30 cm, 70 cm lors de la floraison','de 0,50 à 1,20 m','30 à 75 cm','de 15 cm à 60 cm selon les variétés',
                                                'de 60 cm à 1 m selon les variétés',"jusqu'à 1m, éétalement important"),
                            'entre 1 et 2 m': ('1,50 m','1 m 20 à 2 m',"jusqu'à 1 m en pot, 2m en milieu naturel","1 m, plusieurs mètres avec l'inflorescence", '1m, 4m lors de la floraison',
                                            '1m 20','80 cm, hampe florale de 1 m 50','1 à 3 m','de 1 à 1,3 m','de 1 à 1,5 m','1 m à 1 m 30','de 60 à 120 cm','80 à 120 cm',
                                            '1,50m à 2m','1,50 à 3 m','100 cm','60 cm à 1,50 m',"jusqu'à 2m",'70  à 180 cm','150 à 250 cm','1 à 4 m','0.30 à 3 m selon les variétés',
                                            '50 cm à plusieurs mètres','70 à 120 cm','de 1 à 2 m','de 60 à 1,5 m','1 m','1 m 50','1 à 3 m','1,2m, étalement 60 cm',
                                            "tiges jusquà 1 m 20",'tiges grimpante de 1 à 3 m','tiges grimpantes de 1 à 7 m','1 m, 4 m lors de la floraison',"jusqu'à 1,50 m",
                                            'de 0,50 à 1,20 m',"Jusqu'à 2 m","jusqu'à 1,2 m"),
                            'plus de 2 m': ('de 1,50 à 2 m avec ses hampes florales',"jusqu'à 2,50 m",'4,5 m en culture','de 5 à 7m de haut','de 4 m à 10 m selon les variétés', 
                                            'de 10 à 12m de haut',"jusqu'à 6 m, 15 m dans son pays natal",'12 à 15 m','20 à 30 m','10 m','5 m','de 2 à 3m de haut',
                                            '4 m','2 m','4 à 5 m, étalement : 2m','50cm, 2,50m avec la hampe florale',"1 m, plusieurs mètres avec l'inflorescence",'jusque 3 m',
                                            'feuilles : 2 m fleurs : 7 m','feuilles : 2 m, fleurs : 6 à 12 m',"jusqu'à 10 m dans sa région d'origine","jusqu'à 10 m",'de 2 à 5 m',
                                            '1m, 4m lors de la floraison',"5 à 8m",'10 m dans son milieu naturel, 3 m en appartement','10 m dans son milieu naturel',
                                            '3 à 4 m','2 à 3 m','1 à 3 m',"jusqu'à 4 mètres",'6 à 10 m','1,50 à 3 m','2 à 6 m','4 à 10 m',"jusqu'à 16 m dans la nature",
                                             '2 à 3m',"jusqu'à 4m",'150 à 250 cm','1 à 4 m','3 à 4 mètres','de 6 à 10 m, 2 m en bac','de 6 à 12m','de 2 à 8 m de hauteur selon les expèces, croissance assez lente',
                                             '0.30 à 3 m selon les variétés',"jusqu'à 5 m",'50 cm à plusieurs mètres','2 à 3 m en pot, 4 à 8 m en extérieur',"jusqu'à 4 m",
                                             "jusqu'à 2 ou 3m selon les espèces",'6 à 12 m','2 m','20 m','peut dépasser les 10 m',"2 m à la maison, 30 m dans son milieu d'origine",
                                             '40 m','50 m en pleine terre',"jusqu'à 40 m",'2 à 5 m',"jusqu'à 25 m","jusqu'à 15m",'4 à 6 m','2 à 4 m, voire 6 m',"2-3 m. (très vieux sujets jusqu'à 8 m).",
                                             'de 2 à 10 m',"jusquà 30 m",'10 m à lextérieur, 2 m 50 à 4 m maximum en plante dintérieur','4 à 5 m','2 à 3 m','de 15 à 20 m','3 à 6 m',
                                             '1 à 3 m','30 m','12 m','de 10 à 15 m','5 à 8 m','10 à 15 m, exceptionnellement 30 m',"jusquà 20 m","tiges volubiles jusque 2m de long",
                                             'tiges grimpante de 1 à 3 m','tiges grimpantes de 1 à 7 m','1 m, 4 m lors de la floraison','2 à 4 m')
        }
        self.hauteur=  tk.OptionMenu(interro2, self.hauteurvar, *listeOptions)
        self.rusticite=  tk.OptionMenu(interro2, self.rusticitevar, *listeOptions)
        self.exposition=  tk.OptionMenu(interro2, self.expositionvar, *listeOptions)
        self.typesol=  tk.OptionMenu(interro2, self.typesolvar, *listeOptions)
        self.aciditesol=  tk.OptionMenu(interro2, self.aciditesolvar, *listeOptions)
        self.humiditesol=  tk.OptionMenu(interro2, self.humiditesolvar, *listeOptions)
        self.utilisation=  tk.OptionMenu(interro2, self.utilisationvar, *listeOptions)


        liste =  tk.LabelFrame(self, text="liste des plantes trouvées", font= fonttitre, width= 515, height= 620, \
            foreground= "dark slate grey", bg='light grey', bd=3, padx=10, pady=10)
        ydefil=  tk.Scrollbar(liste, orient='vertical')
        ydefil.grid(row=0, column=1, sticky='ns')
        xdefil=  tk.Scrollbar(liste, orient='horizontal')
        xdefil.grid(row=1, column=0, sticky='we')
        self.maListe=  tk.Listbox(liste, listvariable= self.resultvar, selectmode= 'single', exportselection=0, height=30, width=60, \
            xscrollcommand= xdefil.set, yscrollcommand= ydefil.set)
        self.maListe.grid(row=0,column=0, sticky='nsew')
        xdefil['command'] = self.maListe.xview
        ydefil['command'] = self.maListe.yview


        self.detail1 =  tk.LabelFrame(self, text="Detail", font= fonttitre,  width= 1160, height= 920, foreground= "dark slate grey",  bg="white", bd=3)
        self.detail2 =  tk.LabelFrame(self, text="Detail", font= fonttitre,  width= 1160, height= 920, foreground= "dark slate grey",  bg="white", bd=3)
        tk.Label(self.detail1, text="Famille:", justify= 'right').grid(row=4, column=0, sticky='e')
        tk.Label(self.detail1, text="Origine géographique:", justify= 'right').grid(row=6, column=0, sticky='e')
        tk.Label(self.detail1, text="Période de floraison:", justify= 'right').grid(row=7, column=0, sticky='e')
        tk.Label(self.detail1, text="Couleurs des fleurs:", justify= 'right').grid(row=8, column=0, sticky='e')
        tk.Label(self.detail1, text="Type de plante:", justify= 'right').grid(row=9, column=0, sticky='e')
        tk.Label(self.detail1, text="Type de végétation:", justify= 'right').grid(row=10, column=0, sticky='e')
        tk.Label(self.detail1, text="Type de feuillage:", justify= 'right').grid(row=11, column=0, sticky='e')
        tk.Label(self.detail1, text="Hauteur:", justify= 'right').grid(row=12, column=0, sticky='e')
        tk.Label(self.detail1, text="Rusticité:", justify= 'right').grid(row=13, column=0, sticky='e')
        tk.Label(self.detail1, text="Exposition:", justify= 'right').grid(row=14, column=0, sticky='e')
        tk.Label(self.detail1, text="Type de sol:", justify= 'right').grid(row=15, column=0, sticky='e')
        tk.Label(self.detail1, text="Acidité du sol:", justify= 'right').grid(row=16, column=0, sticky='e')
        tk.Label(self.detail1, text="Humidité du sol:", justify= 'right').grid(row=17, column=0, sticky='e')
        tk.Label(self.detail1, text="Utilisation:", justify= 'right').grid(row=18, column=0, sticky='e')
        tk.Label(self.detail1, text="Plantation, rempotage:", justify= 'right').grid(row=19, column=0, sticky='e')
        tk.Label(self.detail1, text="Méthode de multiplication:", justify= 'right').grid(row=20, column=0, sticky='e')
        tk.Label(self.detail1, text="Taille:", justify= 'right').grid(row=21, column=0, sticky='e')
        tk.Label(self.detail1, text="Maladies et ravageurs:", justify= 'right').grid(row=22, column=0, sticky='e')
        tk.Label(self.detail2, text="Description:", justify= 'right').grid(row=3, column=0, sticky='w')

        self.detailsource.append( tk.Label(self.detail1, font= fonttitre, text="ici s'affiche le nom vulgaire de la plante sélectionnée"))
        self.detailsource[0].grid(row=0, column=0, columnspan=2)
        self.detailsource.append( tk.Label(self.detail1, text="ici s'affiche les synonymes de la plante sélectionnée"))
        self.detailsource[1].grid(row=1, column=0, columnspan=2)
        self.detailsource.append( tk.Label(self.detail1, font= fonttitre, text="ici s'affiche le genre et l'espèce de la plante sélectionnée"))
        self.detailsource[2].grid(row=2, column=0, columnspan=2)
        self.detailsource.append( tk.Label(self.detail1, text="ici s'affiche la famille de la plante sélectionnée"))
        self.detailsource[3].grid(row=3, column=0, columnspan=2)
        self.detailsource.append( tk.Label(self.detail1, text="ici s'affiche la description de la famille de la plante sélectionnée", \
             width=120, wraplength=900))
        self.detailsource[4].grid(row=4, column=0, columnspan=2)
        self.detailsource.append( tk.Label(self.detail1, text="ici s'affiche la photo de la plante sélectionnée"))
        self.detailsource[5].grid(row=5, column=0, columnspan=2)
        for i in list(range(6,23)):
            self.detailsource.append( tk.Label(self.detail1, text="ici s'affiche les données de la plante sélectionnée", \
                justify= 'left', width=120, wraplength=900))
            self.detailsource[i].grid(row=i, column=1, sticky='w', padx=10)

        self.detailsource.append( tk.Label(self.detail2, font= fonttitre, text="ici s'affiche le nom vulgaire de la plante sélectionnée"))
        self.detailsource[23].grid(row=0, column=0, columnspan=2)
        self.detailsource.append( tk.Label(self.detail2, text="ici s'affiche les synonymes de la plante sélectionnée"))
        self.detailsource[24].grid(row=1, column=0, columnspan=2)
        self.detailsource.append( tk.Label(self.detail2, font= fonttitre, text="ici s'affiche le genre et l'espèce de la plante sélectionnée"))
        self.detailsource[25].grid(row=2, column=0, columnspan=2)
        self.detailsource.append( tk.Label(self.detail2, text="ici s'affiche les données de la plante sélectionnée", \
                justify= 'left', width=130, height= 45, wraplength=1000))
        self.detailsource[26].grid(row=3, column=1, sticky='w', padx=10)

        bt_planter= tk.Button(self, text="PLANTER !",padx=5, pady=5,bg= "dark slate grey",foreground="white", command= self.planter)

        self.B1= tk.Button(self, text='1', state= tk.DISABLED, command= self.page1)
        self.B2= tk.Button(self, text='2', state= tk.NORMAL, command= self.page2)


        bt1.grid(row=0,column=0, sticky='n')
        bt2.grid(row=0,column=1, sticky='n')
        bt3.grid(row=0,column=2, sticky='n')
        interro1.grid(row=1,column=0, columnspan=3,stick='nw')
        liste.grid(row=2,column=0, columnspan=3, sticky='nw')
        liste.pack_propagate(0)
        self.detail1.grid(row=0,column=3,rowspan=3, columnspan=2, sticky='nW')
        self.detail1.pack_propagate(0)
        self.detail2.grid(row=0,column=3,rowspan=3, columnspan=2, sticky='nW')
        self.detail2.pack_propagate(0)
        self.detail2.grid_remove()
        bt_planter.grid(row=2, column=3, padx=60, sticky='sw')
        self.B1.grid(row=2, column=4, padx= 50, sticky='se' )
        self.B2.grid(row=2, column=4, padx= 20,  sticky='se' )

        # évènement sur maListe
        self.maListe.bind("<ButtonRelease-1>", self.recup_selection)

    def recherche1(self):
        self.recup_selection(event=None)

    def recherche2(self):
        pass

    def recherche3(self):
        pass


    def recup_selection(self, event):
        select_id = self.maListe.curselection()
        if select_id != ():
            maSelection= self.maListe.get(int(select_id[0]))
            id_plante= maSelection[0]

            conn=sql.connect('plantes')
            cur = conn.cursor()
            req="SELECT * FROM especes WHERE id =?;"
            cursor = cur.execute(req, (id_plante,))
            proprietes_especes= cursor.fetchone()
            genreId= proprietes_especes[1]
            req="SELECT * FROM genres WHERE id= ?;"
            cursor = cur.execute(req, (genreId,))
            proprietes_genres= cursor.fetchone()
            famillesId= proprietes_genres[1]
            req="SELECT * FROM familles WHERE id = ?;"
            cursor = cur.execute(req, (famillesId,))
            proprietes_familles=cursor.fetchone()
            self.affiche(proprietes_especes, proprietes_genres, proprietes_familles)

            conn.close()

    def affiche(self, Tb_especes, Tb_genres, Tb_familles):
        self.detailsource[0]['text']= Tb_especes[4]
        self.detailsource[23]['text']= Tb_especes[4]
        if len(Tb_especes[5])>1:
            self.detailsource[1]['text']= "ou " + Tb_especes[5]
            self.detailsource[24]['text']= "ou " + Tb_especes[5]
        self.detailsource[2]['text']= "( "+ Tb_genres[2] + ", " + Tb_especes[2] + " )"
        self.detailsource[25]['text']= "( "+ Tb_genres[2] + ", " + Tb_especes[2] + " )"
        self.detailsource[3]['text']= Tb_familles[1]
        self.detailsource[4]['text']= Tb_familles[2]
        #self.detailsource[5]['image']= Tb_especes[3]
        for i in list(range(6,23)):
            self.detailsource[i]['text']= Tb_especes[i]
        self.detailsource[26]['text']= Tb_especes[23]

    def page1(self):
        self.detail1.grid()
        self.detail2.grid_remove()
        self.B1.config(state= tk.DISABLED)
        self.B2.config(state= tk.NORMAL)

    def page2(self):
        self.detail2.grid()
        self.detail1.grid_remove()
        self.B2.config(state= tk.DISABLED)
        self.B1.config(state= tk.NORMAL)


    def planter(self):
        pass

    def createMenuBar(self):

    #    mb =  Menu(self.master, bg="grey")
    #    self.master['menu']= mb
        self.sm1 =  tk.Menu(self.mb, tearoff=0, bg= 'dark grey')
        self.sm2 =  tk.Menu(self.mb, tearoff=0, bg= 'dark grey')
        self.sm3 =  tk.Menu(self.mb, tearoff=0, bg= 'dark grey')

        self.mb.add_cascade(label = "Classification", menu= self.sm1)
        self.sm1.add_command(label='Familles', command= self.familles)
        self.sm1.add_command(label='Genres', command= self.genres)
        self.sm1.add_command(label='Espèces', command= self.especes)

        self.mb.add_cascade(label = "Recherche", menu= self.sm2)
        self.sm2.add_command(label='Par nom', command= self.rechercheNom)
        self.sm2.add_command(label='Par critères', command= self.criteres)

        self.mb.add_cascade(label = "Mode Terrain", command= self.terrain)

        self.mb.add_cascade(label='Mode Plantation', command= self.plantation)

        self.mb.add_cascade(label='Quitter', command= self.quit)

    def familles(self):
        pass

    def genres(self):
        pass

    def especes(self):
        pass

    def rechercheNom(self):
        pass

    def criteres(self):
        pass

    def terrain(self):
        self.monJardin = Terrain(self)

    def plantation(self):
        pass


    def rechercher(self):
        "commandes sqlite3 dans la base Plantes"

        conn=sql.connect('plantes')
        cur = conn.cursor()
        pattern='%{}%'.format(self.nomvar.get())
        req = "SELECT id, nom_latin, nom_vulgaire FROM ESPECES WHERE nom_latin LIKE :pattern or nom_vulgaire LIKE :pattern or synonymes LIKE :pattern;"
        cursor = cur.execute(req, {'pattern': pattern})
        result=[]
        for row in cursor:
            result.append(row)

        self.resultvar.set( result)

        conn.close()

