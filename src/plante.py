import tkinter as tk
from tkinter import ttk, filedialog
from PIL import Image, ImageTk
from datetime import datetime
from configparser import ConfigParser
import sqlite3 as sql
import os
import pickle

class Plante():
    doublon = False
    maPlante_ref= {}
    mesPlantes= {}
    
    def __init__(self, cnv, coord, maPlante, ico):
        self.cnv= cnv
        self.ico= ico
        self.coord= coord
        self.maPlante= maPlante
        self.bulleinfo= True
        self.demarre_deplacement =True
        self.suite_deplacement= False

        
        if self.maPlante:    # pour les plantes déjà créées
            self.ico=self.maPlante['ico']
            img= Plante.photoimages[self.ico[0]][self.ico[1]]
            self.icon_item=self.cnv.create_image(self.coord, image=img)
        else:   # pour une nouvelle plante à créer
            self.maPlante={}
            img= Plante.photoimages[self.ico[0]][self.ico[1]]
            self.icon_item= self.cnv.create_image(self.coord, image= img)
            self.maPlante=self.form_plante()

    # déclenche une popup
        self.popup()
        self.cnv.tag_bind(self.icon_item,'<Enter>',self.infobulle)
        self.cnv.tag_bind(self.icon_item,'<Button-3>',self.do_popup)
        self.cnv.tag_bind(self.icon_item,'<B1-Motion>', self.deplacePlante)
        self.cnv.tag_bind(self.icon_item,'<ButtonRelease-1>', self.finDeplacement)
        
        if Plante.doublon: # doit sauvegarder un doublon
            self.mesPlantes[self.coord]= self.maPlante
            self.sauve_mesPlantes()
            Plante.doublon = False

    def popup(self):
        self.popup_menu = tk.Menu(self.cnv, tearoff = 0)
        self.popup_menu.add_command(label= "Modifier/détail", command = self.afficheDetail)
        self.popup_menu.add_command(label= "Dupliquer", command= self.dupliquer)
        self.popup_menu.add_command(label= "Supprimer", command= self.supprime)
    
    def do_popup(self, event):
        self.bulle.withdraw()
        try:
            self.popup_menu.tk_popup(event.x, event.y+50, 0)
        finally:
            self.popup_menu.grab_release()
    
    
    def getcoord(self):
        '''récupération des coordonnées de la plante
        ce qui permet d'identifier la plante dans le dictionnaire'''
        list_of_key= list(Plante.mesPlantes.keys())
        list_of_value= list(Plante.mesPlantes.values())
        return list_of_key[list_of_value.index(self.maPlante)]
        
    def afficheDetail(self,event=None):
        '''affiche la plante en détail'''
        self.form_plante()

    
    def deplacePlante(self, event):
        if self.demarre_deplacement and not self.suite_deplacement:
            self.old_coord= self.getcoord()
            self.suite_deplacement= True
        if self.suite_deplacement and not self.demarre_deplacement:
            self.cnv.moveto(self.icon_item, event.x, event.y)
        self.demarre_deplacement= False
        
    def finDeplacement(self, event):
        if not self.demarre_deplacement:
            coord= event.x, event.y
            del Plante.mesPlantes[self.old_coord]
            Plante.mesPlantes[coord]= self.maPlante
            self.sauve_mesPlantes()
            self.demarre_deplacement=True
        
    def dupliquer(self, event=None):
        old_coord= self.getcoord()
        Plante.maPlante_ref= Plante.mesPlantes[old_coord]
        Plante.doublon=True
            
    def do_duplication(self, coord):
        self.ico= Plante.maPlante_ref['ico']
        img= self.photoimages[self.ico[0]][self.ico[1]]
        self.icon_item=self.cnv.create_image(coord, image=img)
        Plante.mesPlantes[coord]= Plante.maPlante_ref
        self.sauve_mesPlantes()
        Plante.doublon=False  

    def supprime(self, event=None):
        self.cnv.delete(self.icon_item)
        coord = self.getcoord()
        del Plante.mesPlantes[coord]
        self.sauve_mesPlantes()
        
        
    def infobulle(self, event):
        '''affiche une infobulle sur les noms commun et latin et la famille de la plante'''
        if self.bulleinfo:
            self.bulleinfo=False
            self.bulle= tk.Toplevel(bd=1, bg='lightgoldenrod1')
            self.bulle.withdraw()
            self.bulle.overrideredirect(1)
            datePlantation=self.maPlante['date']
            nomcommun= self.maPlante['nom_commun']
            nomlatin= self.maPlante['nom_latin']
            famille= self.maPlante['famille'][1:-1]
            date_plantation= ttk.Label(self.bulle, text=f"date de plantation = {datePlantation}", background='lightgoldenrod1')
            date_plantation.pack(anchor=tk.NW)
            nom_commun= ttk.Label(self.bulle, text=f"nom commun = {nomcommun}",background='lightgoldenrod1')
            nom_commun.pack(anchor=tk.W)
            nom_latin= ttk.Label(self.bulle, text= f"Nom latin = {nomlatin}",background='lightgoldenrod1')
            nom_latin.pack(anchor=tk.W)
            famille= ttk.Label(self.bulle, text= f"Famille = {famille}",background='lightgoldenrod1')
            famille.pack(anchor=tk.SW)
            self.bulle.update_idletasks()
            self.bulle.tipwidth = nom_commun.winfo_reqwidth()
            self.bulle.tipheight = nom_commun.winfo_reqheight()
            self.bulle.update_idletasks()    
            posX = event.x
            posY = event.y+32
            if posX + self.bulle.tipwidth > self.cnv.winfo_screenwidth()/2 - 50:
                posX = posX-self.bulle.tipwidth
            if posY + self.bulle.tipheight > self.cnv.winfo_screenheight() - 50:
                posY = posY+100-self.bulle.tipheight
            self.bulle.geometry('+%d+%d'%(posX,posY))
            self.bulle.deiconify()
            self.delai()
  
    def delai(self):
        self.bulle.after(2000,self.efface)
        
    def efface(self):
        self.bulle.withdraw()
        self.bulleinfo=True
        
    def form_plante(self):
        self.Form_plante= tk.Toplevel()
        self.Form_plante.geometry('460x940')
        self.Form_plante.title("Formulaire d'une plante")
        self.Form_plante.wait_visibility()
        self.Form_plante.grab_set()
        # self.form_plante.transient(self.icon_item)
        
        # les variable _var() du formulaire
        self.date_var= tk.StringVar()
        self.nomlatin_var= tk.StringVar()
        self.nomcommun_var= tk.StringVar()
        self.variete_var= tk.StringVar()
        self.famille_var=tk.StringVar()
        self.photo1_file= ""
        self.photo2_file= ""
        self.categorie_var= tk.StringVar()
        self.port_var= tk.StringVar()
        self.feuillage_text=""
        self.floraison_var=tk.StringVar()
        self.couleur_var=tk.StringVar()
        self.fruit_var=tk.StringVar()
        self.croissance_var=tk.StringVar()
        self.hauteur_var=tk.IntVar()
        self.mutiplication_var=tk.StringVar()
        self.sol_var=tk.StringVar()
        self.acidite_var=tk.StringVar()
        self.humidite_var=tk.StringVar()
        self.exposition_var=tk.StringVar()
        self.rusticite_var=tk.IntVar()
        self.origine_var=tk.StringVar()
        self.entretien_texte=""
        self.maladie_texte=""
        self.utilisation_texte=""
        
        if self.maPlante:
            self.date_var.set(self.maPlante['date'])
            self.nomlatin_var.set(self.maPlante['nom_latin'])
            self.nomcommun_var.set(self.maPlante['nom_commun'])
            self.variete_var.set(self.maPlante['variété'])
            self.famille_var.set(self.maPlante['famille'])
            self.photo1_file=self.maPlante['photo1']
            self.photo2_file=self.maPlante['photo2']
            self.categorie_var.set(self.maPlante['catégorie'])
            self.port_var.set(self.maPlante['port'])
            self.feuillage_texte=self.maPlante['feuillage']
            self.floraison_var.set(self.maPlante['floraison'])
            self.couleur_var.set(self.maPlante['couleur'])
            self.fruit_var.set(self.maPlante['fruit'])
            self.croissance_var.set(self.maPlante['croissance'])
            self.hauteur_var.set(self.maPlante['hauteur'])
            self.mutiplication_var.set(self.maPlante['multiplication'])
            self.sol_var.set(self.maPlante['sol'])
            self.acidite_var.set(self.maPlante['acidité'])
            self.humidite_var.set(self.maPlante['humidité'])
            self.exposition_var.set(self.maPlante['exposition'])
            self.rusticite_var.set(self.maPlante['rusticité'])
            self.origine_var.set(self.maPlante['origine'])
            self.entretien_texte=self.maPlante['entretien']
            self.maladie_texte=self.maPlante['maladie']
            self.utilisation_texte=self.maPlante['utilisation']
        else:
            self.date_var.set(datetime.today().strftime("%d/%m/%Y"))
            self.nomlatin_var.set("nom Latin et synonymes")
            self.nomcommun_var.set("Plusieurs noms communs sont possibles")
            self.variete_var.set("Nom de la variété")
            self.floraison_var.set("Période habituelle, couleur, attire ou repousse d'autres insectes...")
            self.fruit_var.set("description et précisions s'ils sont comestibles, toxiques ou allergisants")
            self.croissance_var.set("vitesse de croissance en une année")
            self.sol_var.set("pauvre/riche, humifère/bruyère/de jardin/argileux/sable/grave")
            self.entretien_texte="ce qu'il faut faire à quel moment et comment y procéder"
            self.maladie_texte="maladies cryptogamiques, insectes hôtes, les ravageurs(aleurodes, escargots, limaces, pucerons...), les animaux nuisibles..."
            self.utilisation_texte="propiétés santé, modes d'utilisation"
            
            try:          
                combostyle = ttk.Style()
                combostyle.theme_create('combostyle', parent='alt',
                                settings = {'TCombobox':
                                            {'configure':
                                                {'selectbackground': 'grey',
                                                'fieldbackground': 'white',
                                                'background': 'grey'
                                                }}}
                                )
                combostyle.theme_use('combostyle')
            except:
                pass
                             
        
        self.fiche0= tk.Frame(self.Form_plante, borderwidth=5, padx=5, pady=5)
        self.fiche0.place(x=5)        
        self.fiche1= tk.Frame(self.Form_plante, borderwidth=5, padx=5, pady=5)
        self.fiche1.place(x=5, y=30)
        self.fiche2= tk.Frame(self.Form_plante, borderwidth=5, padx=5, pady=5)
        self.fiche2.place(x=5, y=250)
        self.fiche3= tk.Frame(self.Form_plante, borderwidth=5, padx=5, pady=5)
        self.fiche3.place(x=5, y= 470)
        self.fiche4= tk.Frame(self.Form_plante, borderwidth=5, padx=5, pady=5)
        self.frm_boutons= tk.Frame(self.Form_plante, borderwidth=5, padx=5, pady=5)
        self.frm_boutons.place(x=5, y = 860)
        
        ttk.Label(self.fiche0,text="date de la plantation").pack(padx=5, side=tk.LEFT)
        datePlantation_entry=ttk.Entry(self.fiche0,textvariable=self.date_var, width=30)
        datePlantation_entry.pack(side= tk.LEFT)
        
        ttk.Label(self.fiche1,text="Nom latin").pack(padx=5, fill=tk.X)
        nomlatin_cb=ttk.Combobox(self.fiche1,textvariable=self.nomlatin_var, width=50)
        nomlatin_cb['values']= self.getlatin()
        nomlatin_cb['state']='readonly'
        nomlatin_cb.bind('<<ComboboxSelected>>', self.nomlatin_selected)
        nomlatin_cb.pack(padx= 5, pady=(0,10), fill=tk.X)
        
        ttk.Label(self.fiche1, text='nom commun (ou vulgaire ou vernaculaire)').pack(padx=5, fill=tk.X)
        nomcommun_entry=ttk.Entry(self.fiche1, textvariable=self.nomcommun_var, width=50)
        nomcommun_entry.pack(padx=5, pady=(0,10), fill=tk.X)
        
        ttk.Label(self.fiche1, text='nom de la variété').pack(padx=5, fill=tk.X)
        variete_entry=ttk.Entry(self.fiche1, textvariable=self.variete_var, width=50)
        variete_entry.pack(padx=5, pady=(0,10), fill=tk.X)
        
        ttk.Label(self.fiche1, text='Famille').pack(padx=5, fill=tk.X)
        famille_entry=ttk.Entry(self.fiche1, textvariable=self.famille_var, width=50)
        famille_entry.pack(padx=5, pady=(0,10), fill=tk.X)
        
        if self.photo1_file=="":
            self.img1= Image.open("photos/Sans titre.png")
        else:
            self.img1= Image.open(self.photo1_file)
        self.image1= ImageTk.PhotoImage(self.img1.resize((190,190)))
        self.photo1_img= tk.Button(self.fiche2, image= self.image1, command=self.quelPhoto1)
        self.photo1_img.grid(column=0, row=1, padx=10, pady=10)
        
        if self.photo2_file=="":
            self.img2= Image.open("photos/Sans titre.png")
        else:
            self.img2=Image.open(self.photo2_file)
        self.image2= ImageTk.PhotoImage(self.img2.resize((190,190)))
        self.photo2_img= tk.Button(self.fiche2, image= self.image2, command= self.quelPhoto2)
        self.photo2_img.grid(column=1, row=1, padx=10, pady=10 )
        
        ttk.Label(self.fiche3, text='Catégorie').pack(padx=5, fill=tk.X)
        categorie_cb=ttk.Combobox(self.fiche3, textvariable=self.categorie_var, width=50)
        categorie_cb['value']= ['vivace', 'annuel', 'bisannuelle', 'herbacée', 'aquatique', 'rhizome', 'bulbe', 'arbre', 'arbuste', 'succulente']
        categorie_cb['state']='readonly'
        categorie_cb.pack(padx=5, pady=(0,10), fill=tk.X)
        
        ttk.Label(self.fiche3, text='Port').pack(padx= 5, fill=tk.X)
        port_cb=ttk.Combobox(self.fiche3, textvariable=self.port_var, width=50)
        port_cb['values']=['érigé', 'rampant', 'grimpant', 'buissonnant']
        port_cb['state']= 'readonly'
        port_cb.pack(padx=5, pady=(0,10), fill=tk.X)
        
        ttk.Label(self.fiche3, text='Feuillage').pack(padx=5, fill=tk.X)
        self.feuillage_text=tk.Text(self.fiche3, height=2, width=50)
        self.feuillage_text.pack(padx=5, pady=(0,10), fill=tk.X)
        
        ttk.Label(self.fiche3, text='Floraison').pack(padx=5, fill=tk.X)
        floraison_entry=ttk.Entry(self.fiche3, textvariable=self.floraison_var, width=50)
        floraison_entry.pack(padx=5, pady=(0,10), fill=tk.X)
        
        ttk.Label(self.fiche3,text='Fruits').pack(padx=5, fill=tk.X)
        fruit_entry=ttk.Entry(self.fiche3, textvariable=self.fruit_var, width=50)
        fruit_entry.pack(padx=5, pady=(0,10), fill=tk.X)
        
        ttk.Label(self.fiche3, text='Croissance').pack(padx=5, fill=tk.X)
        croissance_entry=ttk.Entry(self.fiche3, textvariable= self.croissance_var, width=50)
        croissance_entry.pack(padx=5, pady=(0,10), fill=tk.X)
        
        ttk.Label(self.fiche3, text="hauteur adulte en m").pack(padx=5, fill=tk.X)
        hauteur_entry=ttk.Entry(self.fiche3,textvariable=self.hauteur_var, width=50,)
        hauteur_entry.pack(padx=5,pady=(0,10), fill=tk.X)
        
        ttk.Label(self.fiche4, text="Multiplication").pack(padx=5, fill=tk.X)
        multiplication_cb=ttk.Combobox(self.fiche4, textvariable=self.mutiplication_var, width=50)
        multiplication_cb['values']=['semis','marcotage','bouturage','division']
        multiplication_cb.pack(padx=5, pady=(0,10), fill=tk.X)
        
        ttk.Label(self.fiche4, text='Sol').pack(padx=5, fill=tk.X)
        sol_entry=ttk.Entry(self.fiche4, textvariable=self.sol_var, width=50)
        sol_entry.pack(padx=5, pady=(0,10), fill=tk.X)

        ttk.Label(self.fiche4, text='Humidité').pack(padx=5, fill=tk.X)
        humidite_cb=ttk.Combobox(self.fiche4, textvariable=self.humidite_var, width=50)
        humidite_cb['values']=["les pieds dans l'eau","a besoin d'humidité",'normal','pas trop humide', 'sec']
        humidite_cb.pack(padx=5, pady=(0,10), fill=tk.X)
        
        ttk.Label(self.fiche4, text="Acidité").pack(padx=5, fill=tk.X)
        acidite_cb=ttk.Combobox(self.fiche4, textvariable=self.acidite_var,  width=50)
        acidite_cb['values']=['acide','neutre à légèrement acide','neutre','neutre à légèrement basic', 'basique']
        acidite_cb.pack(padx=5, pady=(0,10), fill=tk.X)
                
        ttk.Label(self.fiche4, text= 'Exposition').pack(padx=5, fill=tk.X)
        exposition_cb=ttk.Combobox(self.fiche4, textvariable=self.exposition_var,  width=50)
        exposition_cb['values']=['lumière vive', 'soleil', 'mi-ombre', 'ombre']
        exposition_cb.pack(padx=5, pady=(0,10), fill=tk.X)
        
        ttk.Label(self.fiche4, text='rusticité: résistance au froid').pack(padx=5, fill=tk.X)
        rusticite_entry=ttk.Entry(self.fiche4, textvariable=self.rusticite_var,  width=50)
        rusticite_entry.pack(padx=5, pady=(0,10), fill=tk.X)
        
        ttk.Label(self.fiche4, text="Origine géographique").pack(padx=5, fill=tk.X)
        origine_entry=ttk.Entry(self.fiche4, textvariable=self.origine_var, width=50)
        origine_entry.pack(padx=5, pady=(0,10), fill=tk.X)
        
        ttk.Label(self.fiche4, text="Entretien").pack(padx=5, fill=tk.X)
        self.entretien_text=tk.Text(self.fiche4, height=3, width=50)
        self.entretien_text.pack(padx=5, pady=(0,10), fill=tk.X)
        self.entretien_text.insert('1.0', self.entretien_texte)
        
        ttk.Label(self.fiche4, text="Maladies et ravageurs").pack(padx=5, fill=tk.X)
        self.maladie_text=tk.Text(self.fiche4, height= 3, width=50)
        self.maladie_text.pack(padx=5, pady=(0,10), fill=tk.X)
        self.maladie_text.insert('1.0',self.maladie_texte)
        
        ttk.Label(self.fiche4, text="Propriétés et utilisation").pack(padx=5, fill=tk.X)
        self.utilisation_text= tk.Text(self.fiche4, height=3, width=50)
        self.utilisation_text.pack(padx=5, pady=(0,10), fill=tk.X)
        self.utilisation_text.insert('1.0', self.utilisation_texte)
        
        self.btn_arriere=tk.Button(self.frm_boutons,
                   text="<",
                   command=self.arriere)
        self.btn_arriere.pack(padx=20, pady=10, side=tk.LEFT)
        self.btn_page1=tk.Button(self.frm_boutons,
                  text="1",
                  command=self.arriere)
        self.btn_page1.pack(padx=20, pady=10, side=tk.LEFT)
        self.btn_page2=tk.Button(self.frm_boutons,
                  text="2",
                  command=self.avant)
        self.btn_page2.pack(padx=20, pady=10, side=tk.LEFT)
        self.btn_avant=tk.Button(self.frm_boutons,
                   text=">",
                   command=self.avant)
        self.btn_avant.pack(padx=20, pady=10, side=tk.LEFT)
        self.btn_enregistrer=tk.Button(self.frm_boutons,
                   text='Enregistrer',
                   command=self.enregistrer)
        self.btn_enregistrer.pack(padx= 5,pady=10, side= tk.LEFT ,expand=True)

    def enregistrer(self):
        """enregistre le dictionnaire du formulaire en objet pickle 'mesPlantes_picklefile'
        le disctionnaire self.mesPlantes = {self.coord: maPlante}
        maPlante est le dictionnaire des propriétés d'une plante
        """
        plante={}
        plante['ico']=self.ico
        plante['date']=self.date_var.get()
        plante['nom_latin']=self.nomlatin_var.get()
        plante['nom_commun']=self.nomcommun_var.get()
        plante['variété']= self.variete_var.get()
        plante['famille']=self.famille_var.get()
        plante['photo1']=self.photo1_file
        plante['photo2']=self.photo2_file
        plante['catégorie']=self.categorie_var.get()
        plante['port']=self.port_var.get()
        plante['feuillage']=self.feuillage_text.get('1.0','end')
        plante['floraison']=self.floraison_var.get()
        plante['couleur']=self.couleur_var.get()
        plante['fruit']=self.fruit_var.get()
        plante['croissance']=self.croissance_var.get()
        plante['hauteur']=self.hauteur_var.get()
        plante['multiplication']=self.mutiplication_var.get()
        plante['sol']=self.sol_var.get()
        plante['acidité']=self.acidite_var.get()
        plante['humidité']=self.humidite_var.get()
        plante['exposition']=self.exposition_var.get()
        plante['rusticité']=self.rusticite_var.get()
        plante['origine']=self.origine_var.get()
        plante['entretien']=self.entretien_text.get('1.0','end')
        plante['maladie']=self.maladie_text.get('1.0','end')
        plante['utilisation']=self.utilisation_text.get('1.0','end')
        self.mesPlantes[self.coord]= plante
        self.maPlante = plante
        Plante.maPlante_ref= plante
        self.Form_plante.grab_release()
        self.Form_plante.withdraw()
        self.sauve_mesPlantes()
      
    def sauve_mesPlantes(self):
        # sauvegarde pickle du dictionnaire des plantes plantées
        config = ConfigParser()
        if os.path.exists("./monJardin.ini"):
            config.read("./monJardin.ini")
            if config.get('Last', 'module') == 'terrain': # pas encore de sauvegarde des plantes
                options = {
                    'initialdir': './save',
                    'title': 'Nom du fichier de sauvegarde',
                    'filetypes': (("pkl files", "*.pkl"),),
                    'initialfile': "mesPlantes.pkl"
                }
                path= filedialog.asksaveasfilename(**options)
                with open(path, "wb") as f:
                    pickle.dump(Plante.mesPlantes, f)
                # mise à jour de monJardin.ini
                config.set("Last","module", "planter")  
                config.set("Module", "planter", path)
                with open("./monJardin.ini",'w') as configfile:
                    config.write(configfile)          
            elif config.get('Last', 'module') == 'planter':
                path= config.get('Module', 'planter')
                with open(path, "wb") as f:
                    pickle.dump(Plante.mesPlantes, f)
        
        else:   # le créer s'il n'existe pas
            config = ConfigParser()
            config["Last"]={"module" : "terrain"}
            config["Module"]={"terrain" : "", "planter" : "", "gestion" :""}
            with open("./monJardin.ini", 'w') as f:
                config.write(f)

    
    def quelPhoto1(self):
        self.photo1_file=filedialog.askopenfilename(
            initialdir="./photos", 
            title="Sélectionner la photo", 
            filetypes=(("png", "*.png"), ("webp", "*.webp"), ("jpeg", "*.jpg"), ("all files", "*.*")))
        self.img1= Image.open(self.photo1_file)
        self.image1= ImageTk.PhotoImage(self.img1.resize((190,190)))
        self.photo1_img.configure (image= self.image1)
        self.photo1_img.image = self.image1
        
        
    def quelPhoto2(self):
        self.photo2_file=filedialog.askopenfilename(
            initialdir="./photos", 
            title="Sélectionner la photo", 
            filetypes=( ("png", "*.png"), ("webp", "*.webp"), ("jpeg", "*.jpg"), ("all files", "*.*")))
        self.img2= Image.open(self.photo2_file)
        self.image2= ImageTk.PhotoImage(self.img2.resize((190,190)))
        self.photo2_img.configure (image= self.image2)
        self.photo2_img.image = self.image2
    
    def arriere(self):
        self.fiche4.place_forget()
        self.fiche2.place(x=5, y= 250)
        self.fiche3.place(x=5, y=470)
        self.btn_page2.configure(fg= 'black')
        self.btn_page1.configure(fg= 'red')
    
    def avant(self):
        self.fiche2.place_forget()
        self.fiche3.place_forget()
        self.fiche4.place(x=5, y= 250)
        self.btn_page2.configure(fg= 'red')
        self.btn_page1.configure(fg= 'black')

    def getlatin(self):
        conn=sql.connect('plantes')
        cur = conn.cursor()
        req="SELECT nom_latin FROM especes;"
        cursor = cur.execute(req)
        list_nomlatin= []
        for nomlatin in cursor:
            strnomlatin = nomlatin[0]
            list_nomlatin.append(strnomlatin)
        conn.close()
        list_nomlatin.sort()
        
        return list_nomlatin
        
    def nomlatin_selected(self, event):
        choix= self.nomlatin_var.get()
        conn=sql.connect('plantes')
        cur = conn.cursor()
        cursor = cur.execute("SELECT id_genre, nom_vulgaire FROM especes WHERE nom_latin = ?", (choix,))
        res= cursor.fetchone()
        id_genre= res[0]
        nom_vulgaire = res[1]
        self.nomcommun_var.set(nom_vulgaire)
        
        cur= conn.cursor()
        cursor= cur.execute("SELECT id_famille FROM genres WHERE id = ?", (id_genre,))
        id_famille= cursor.fetchone()
        
        cur= conn.cursor()
        cursor= cur.execute("SELECT nom FROM familles WHERE id= ?", id_famille)
        nomfamille= ','.join(cursor.fetchone())
        
        self.famille_var.set(nomfamille)
        
        conn.close()
        
