import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from tkinter.colorchooser import askcolor
import pickle
import os
from dialogue import Dialogue
from PIL import Image, ImageDraw
from configparser import ConfigParser

class FenControle(Dialogue):
    "Fenêtre satellite contenant des contrôles de redimensionnement"

    def habillage(self, cadreconteneur, maVariable=None):

        tk.Label(cadreconteneur,text="Veuillez indiquer les dimensions de votre jardin en mètres").grid(row=0,column=0, padx=10, pady=10, columnspan=2)
        tk.Label(cadreconteneur,text='longueur').grid(row=2,column=0)
        tk.Label(cadreconteneur,text='largeur').grid(row=3,column=0)
        self.saisielongueur=tk.Entry(cadreconteneur)
        self.saisielongueur.grid(row=2,column=1, padx=15)
        self.saisielargeur= tk.Entry(cadreconteneur)
        self.saisielargeur.grid(row=3, column=1, padx=15)
        tk.Label(cadreconteneur,text='nom du jardin').grid(row=4,column=0)
        self.saisienom= tk.Entry(cadreconteneur)
        self.saisienom.grid(row=4,column=1, padx=15)
        tk.Label(cadreconteneur,text="").grid(row=1,column=0)
        return self.saisielongueur

    def apply(self):

        dimX, dimY = int(self.saisielongueur.get()) , int(self.saisielargeur.get()) # en mètres
        self.master.max_width=dimX*50    # en pixels (1 m = 50 px)
        self.master.max_height=dimY*50
        self.master.nom= self.saisienom.get()
        self.master.echelle.set(100)
        self.master.canvas.config(scrollregion=(0,0,self.master.max_width, self.master.max_height))


class Terrain( tk.Frame):
    """Notre fenêtre principale.
    Tous les widgets sont stockés comme attribut de cette fenêtre."""

    def __init__(self, master=None, mb=None, fichier=None):
        tk.Frame.__init__(self)
        self.master = master
        self.master.title("Mon Jardin")
        self.pack()
        self.mb=mb
        self.fichier= fichier
        self.createMenuBar()

            # variables d'instances
        self.x1, self.y1, self.x2, self.y2 = 10, 190, 190, 10
        self.coul = ['#EE1313', '#400B0B', '#21CA0E', '#686666', '#DDDCA8' ,'#3D5CD0', '#000000']
        self.rbshape =  tk.IntVar()
        self.ckbtrait = tk.IntVar()
        self.ckbcouleur= tk.IntVar()
        self.spinepais= tk.IntVar()
        self.zoom0 = 1
        self.zoom1 = 1
        self.mode= 0     # le bouton de dessin sélectionné, par defaut = la flèche
        self.listeFormeId= []    # liste des formes sélectionné
        self.forme_raise=None    # la forme le plus élevée dans la liste
        self.forme_statut=None # 0 premier click pour tracer une forme.
                                # 1 forme en cours de traçage,
                                # 2 forme terminée d'être tracé
                                # 4 forme en cours de modification
        self.control_flag= False
        self.xy_old=[None, None]
        self.position=None
        self.polygone=[]
        self.pts_i=0
        self.view_height=900
        self.view_width=1377
        self.max_height= 3000
        self.max_width= 4000
        self.dict_formes= {}
        self.nom= "monJardin"



        # les différents widget de l'interface

        self.bandeau =  tk.Frame(self, bg='dark grey', bd= 2)
        self.canvas =  tk.Canvas(self, bg='white', width= self.view_width, height= self.view_height, scrollregion= (0 ,0,self.max_height, self.max_width))
        self.defily =  tk.Scrollbar(self, orient='vertical', bg= 'dark slate gray', command=self.canvas.yview)
        self.defilx =  tk.Scrollbar(self, orient='horizontal', bg='dark slate gray', command=self.canvas.xview)
        self.etat =  tk.Frame(self, bg='grey', pady=5, bd=2, relief= tk.GROOVE)
        self.mesure =  tk.Label(self.etat, text="mesure = ", bg="grey")
        
        self.bandeau.grid(row=0, column=0)
        self.canvas.grid(row=0, column=1)
        self.defily.grid(row=0, column=2, sticky= tk.NS)
        self.defilx.grid(row=1, column=1, stick=tk.EW)
        self.etat.grid(row=2, column=0, columnspan=2)
        self.mesure.pack()

        self.canvas['xscrollcommand'] = self.defilx.set
        self.canvas['yscrollcommand'] = self.defily.set

        self.canvas.bind("<Button-1>", self.click)
        self.canvas.bind("Double-Button-1>", self.ok)
        self.canvas.bind("<ButtonRelease>", self.relache)
        self.canvas.bind("<B1-Motion>" , self.glisse)
        self.canvas.bind("<Control-B1-Motion>" , self.ctrl_glisse)
        self.canvas.bind("<Motion>", self.survole)
        self.bind_all("<KeyPress-Delete>", self.delete_item)
        self.bind_all("<KeyPress-Return>", self.ok)
        self.bind_all("<KeyPress-Escape>", self.esc)

        self.frm_select = tk.LabelFrame(self.bandeau, text="Mode Sélection", bd=2)
        self.frm_dessin = tk.LabelFrame(self.bandeau, text="Mode dessin", bd=2)
        self.frm_prop = tk.LabelFrame(self.bandeau, bd=2)
        self.frm_grillescale = tk.LabelFrame(self.bandeau, bd=2)
        self.frm_bouton = tk.Frame(self.bandeau, bd=0)
        
        self.img=[]
        image=  tk.PhotoImage(file="images/fleche.gif")
        self.img.append(image)
        tk.Radiobutton(self.frm_select, image=self.img[0],variable=self.rbshape, indicatoron=0, borderwidth= 5, value= 0, command=self.commande).grid(row=0, column= 0, padx= 109, pady= 5)
        
        for i in list(range(1,5)):
            image= tk.PhotoImage(file="images/forme" + str(i) + ".png")
            self.img.append(image)
            bou= tk.Radiobutton(self.frm_dessin, image= self.img[i],variable=self.rbshape, indicatoron=0, borderwidth= 5, value=i, command= self.commande)
            r= ((i-1)//2)*2
            if i % 2 == 0:
                bou.grid(padx= 5, pady= 5, row= r, column=1)
            else:
                bou.grid(padx= 5, pady= 5, row= r, column=0)

        tk.Label(self.frm_dessin, text="Click-glissé").grid(row= 1, column=0, padx=8, pady=5 )
        tk.Label(self.frm_dessin, text="Click-glissé" +chr(10) + "CTRL-Click-glissé" + chr(10)+  "pour un carré").grid(row= 1, column=1, padx=8, pady=5)
        tk.Label(self.frm_dessin, text="Click-glissé" +chr(10) + "CTRL-Click-glissé" + chr(10)+ "pour un cercle").grid(row= 3, column=0, padx=8, pady=5)
        tk.Label(self.frm_dessin, text="n-click + [RETURN]").grid(row= 3, column=1, padx=8, pady=5)
        
        self.img_trait= tk.PhotoImage(file="images/trait.png")
        tk.Checkbutton(self.frm_prop, image=self.img_trait, variable=self.ckbtrait, borderwidth= 5,  command= self.commande).grid(row=0, column= 0, padx= 5, pady= 5)
        self.img_rempli= tk.PhotoImage(file="images/remplissage.png")
        tk.Checkbutton(self.frm_prop, image=self.img_rempli, variable=self.ckbcouleur, borderwidth= 5, command= self.commande).grid(row=0, column= 1, padx= 5, pady= 5)
        tk.Spinbox(self.frm_prop, textvariable= self.spinepais, from_=1.0, to=10.0, width= 5 ).grid(row=1, column=0, padx=8, pady=5)
        self.bt_couleur= tk.Button(self.frm_prop, height=1, width=2, bd=2, command= self.quellecouleur)
        self.bt_couleur.grid(row=1, column=1, padx=5, pady=5)
        tk.Label(self.frm_prop, text="Cliquer pour \nchoix couleur", width=17).grid(row=2, column= 1, padx=10, pady=5)
        
        self.img_grille=  tk.PhotoImage(file="images/grille.gif")
        tk.Button(self.frm_grillescale, image= self.img_grille, command= self.grille).grid(row=0, column=0, padx= 5, pady= 5)
        tk.Label(self.frm_grillescale,text="Grille", width=14).grid(row=1, column=0)
        tk.Label(self.frm_grillescale,text="Zoom (%)").grid(row=0, column=1, padx=5, sticky=tk.S)
        self.echelle= tk.Scale(self.frm_grillescale, orient='horizontal', bg="grey", fg="blue",font=('Helvetica', '8'), variable= self.zoom1, length=140, width=10, sliderlength=20, showvalue=0, from_ = 0, to = 300, tickinterval=100, command= self.scale)
        self.echelle.set(100)
        self.echelle.grid(row=1, column=1, padx= 10, pady= 10)
                
        self.frm_select.grid(row=0, column=0)
        self.frm_dessin.grid(row=1, column=0)
        self.frm_prop.grid(row=2, column=0)
        self.frm_grillescale.grid(row=4, column=0)
        self.frm_bouton.grid(row=5,column=0)
        
        tk.Button(self.frm_bouton, text="Enregistrer \nterrain", command="self.saveTerrain").grid(row=0, column=0, padx=14, pady=10)
        tk.Button(self.frm_bouton, text="Convertir .png", command="self.convertir").grid(row=0, column=1, padx=14, pady=10)
    
        
        if self.fichier and os.path.exists(self.fichier):
        # ouvre et dessine le fichier .mjd s'il existe
            self.afficheDernierTerrain(self.fichier)
        else:
            self.nouveau()
        
    def quellecouleur(self):
            colors = askcolor( color= self.bt_couleur["bg"], title= "Couleur de remplissage")
            self.bt_couleur ["bg"]= colors[1]
            
    def afficheDernierTerrain(self,fichier):

        try:
            with open(fichier, 'rb') as f:
                self.dict_formes = pickle.load(f)
        except Exception:
            reponse = messagebox.showerror("Erreur fichier","l'ouverture ou la lecture du fichier provoque une erreur")

        self.redraw_formes()

    def createMenuBar(self):

        self.sm1 = tk.Menu(self.mb, tearoff=0, bg= 'dark grey')
        self.sm2 = tk.Menu(self.mb, tearoff=0, bg = 'dark grey')
        
        self.mb.add_cascade(label = "Fichier", menu= self.sm1)
        self.sm1.add_command(label='Nouveau', command= self.nouveau)
        self.sm1.add_command(label='Ouvrir', command= self.ouvrir)
        self.sm1.add_command(label='Enregistrer', command= self.saveTerrain)
        self.sm1.add_command(label='PNG Convertion', command= self.convertir)
        self.sm1.add_command(label='Quitter', command= self.quit)
               
        self.mb.add_cascade(label= "Gérer", menu= self.sm2)
        self.sm2.add_command(label= 'Planter', command= self.planter)
        self.sm2.add_command(label='classification', command= self.classification)
        
        self.master.config(menu=self.mb)


    # commandes menu
    def classification(self):
        self.mb =  tk.Menu(self.master, bg="grey")
        self.master.config(menu= self.mb)
        self.pack_forget()
        from gestion import Gestion
        self.monJardin = Gestion(self.master, self.mb)
        
    def planter(self):
        self.mb =  tk.Menu(self.master, bg="grey")
        self.master.config(menu= self.mb)
        self.pack_forget()
        from planter import Planter
        self.monJardin = Planter(self.master, self.mb)

    def nouveau(self):
        """    effacer le canvas,
        ouvrir une fenetre pour demander la dimension du canvas et son nom"""

        self.clear_formes()

        self.fen2 = FenControle(self)
        self.master.title(self.nom)

    def ouvrir(self):

        """ efface toutes les formes s'il y en a,
            ouvre le fichier .mjd choisi,
            dessine les formes définis dans ce fichier """

        all_formes=self.canvas.find_all()

        for forme_id in all_formes:
            self.canvas.delete(forme_id)

        options = {
                    'initialdir': './save',
                    'title': 'Choisir un fichier',
                    'filetypes': (("fichiers .mjd", "*.mjd"),)
        }
        name_file = filedialog.askopenfilename(**options)
        try:
            with open(name_file, 'rb') as f:
                self.dict_formes = pickle.load(f)
        except Exception:
            reponse = messagebox.showerror("Erreur fichier","l'ouverture ou la lecture du fichier provoque une erreur")

        self.redraw_formes()

    def saveTerrain(self):
        """ sauvegarde pickle d'un dictionnaire des paramètres de chacun des formes """
        self.push_dict_formes()
        config = ConfigParser()
        path=""
        if os.path.exists("./monJardin.ini"):
            config.read("./monJardin.ini")
            if config.get('Last', 'module') == 'terrain':
                path= config.get('Module', 'terrain')               
                if path:
                    with open(path, "wb") as f:
                        pickle.dump(self.dict_formes, f, 4)
                else:
                    options = {
                    'initialdir': './save',
                    'title': 'Nom du fichier de sauvegarde',
                    'filetypes': (("monJardin .mjd", "*.mjd"),)
                    }
                    terrain= filedialog.askopenfilename(**options)
                    with open(terrain, "wb") as f:
                        pickle.dump(self.dict_formes, f, 4)
            else:
                options = {
                    'initialdir': './save',
                    'title': 'Nom du fichier de sauvegarde',
                    'filetypes': (("monJardin .mjd", "*.mjd"),)
                }
                terrain= filedialog.askopenfilename(**options)
                with open(terrain, "wb") as f:
                    pickle.dump(self.dict_formes, f, 4)
            # mettre à jour monJardin.ini
            config = ConfigParser()
            config.read("./monJardin.ini")
            config.set("Last","module", "terrain")  
            config.set("Module", "terrain", terrain)
            with open("./monJardin.ini",'w') as configfile:
                config.write(configfile)          
        else:   # le créer s'il n'existe pas
            config = ConfigParser()
            config["Last"]={"module" : "terrain"}
            config["Module"]={"terrain" : "", "planter" : "", "gestion" :""}
            with open("./monJardin.ini", 'w') as f:
                config.write(f)

    def convertir(self):
        """enregistre une image .png du canevas grace à pillow"""
        """ recharge en mémoire pillow les formes"""
        pillow_image = Image.new("RGB", (4000, 3000), 'white')
        forme_id=ImageDraw.Draw(pillow_image)
        zoom0 = self.dict_formes['zoom0']
        zoom1 = self.dict_formes['zoom1']
        i=0
        for value in self.dict_formes.values():
            if i >1:
                coords=tuple(map(lambda x : x / zoom0 * zoom1, value[0] ))
                options= value[1]
                try:
                    tag= options.get('tags')
                    largeur= options.get('width')
                    h= options.get('fill').lstrip('#')
                    remplissage = tuple(int(h[i:i+2],16) for i in (0, 2, 4))
                    
                    if tag[0]== "rectangle":
                        forme_id.rectangle(coords,width=largeur, fill= remplissage, outline='black')                        
                    elif tag[0]== "polygone":
                        forme_id.polygon(coords,width=largeur, fill= remplissage, outline='black')                       
                    elif tag[0]== "ovale":
                        forme_id.ellipse(coords,width=largeur, fill= remplissage, outline='black')
                    elif tag[0]== "ligne":
                        forme_id.line(coords,width=largeur, fill= remplissage, outline='black')
                    elif tag[0]== "grille":
                        forme_id.line(coords, width=largeur, fill= remplissage, outline='black')
                except Exception:
                    pass
                
            i+=1
        config= ConfigParser()
        if os.path.exists("./monJardin.ini"):
            config.read("./monJardin.ini")
            path= config.get('Module', 'gestion')               
            if path:
                with open(path, "wb") as f:
                    pillow_image.save(path, 'png')
            else:
                options = {
                'initialdir': './save',
                'title': 'Nom du fichier de sauvegarde',
                'filetypes': (("png files", "*.png"),),
                'initialfile': "monJardin.png"
                }
                path= filedialog.asksaveasfilename(**options)
                with open(path, "wb") as f:
                    pillow_image.save(path, 'png')
                # mettre à jour monJardin.ini
                config = ConfigParser()
                config.read("./monJardin.ini")
                config.set("Last","module", "gestion")  
                config.set("Module", "gestion", path)
                with open("./monJardin.ini",'w') as configfile:
                    config.write(configfile)          
        else:   # le créer s'il n'existe pas
            options = {
            'initialdir': './save',
            'title': 'Nom du fichier de sauvegarde',
            'filetypes': (("png files", "*.png"),),
            'initialfile': "monJardin.png"
            }
            path= filedialog.asksaveasfilename(**options)
            head, tail= os.path.split(path)
            f= os.path.splitext(tail)
            config = ConfigParser()
            config_string='''
            [Last]
                module = terrain
            [Module]
                terrain = ''' + head + f[0] + ".mjd" + '''
                planter = ""
                gestion = path
            '''
            with open("./monJardin.ini", 'w') as f:
                config_string.write(f)
            pillow_image.save(path, 'png')
    
    def commande(self):
        self.mode= self.rbshape.get()
        # 0 = Sélection
        # 1 = Ligne
        # 2 = Rectangle/Carré
        # 3 = Oval/Cercle 
        # 4 = Polygone

    def push_dict_formes(self):
        self.dict_formes={}
        self.dict_formes['zoom0']=self.zoom0
        self.dict_formes['zoom1']=self.zoom1
        all_formes=self.canvas.find_all()
        for i in all_formes:
            formes={}
            coords= self.canvas.coords(i)
            formes['tags']= self.canvas.gettags(i)
            formes['width']= 2
            formes['fill']= self.canvas.itemcget(i,'fill')
            self.dict_formes[i]= (coords, formes)


    def scale(self,event):
        self.zoom1 = self.echelle.get() / 100
        if self.zoom1 == 0: self.zoom1 = 0.01
        self.push_dict_formes()
        self.clear_formes()
        self.max_width= self.max_width / self.zoom0 * self.zoom1
        self.max_height=self.max_height /self.zoom0 * self.zoom1
        self.canvas.config(scrollregion=(0,0,self.max_width,self.max_height))
        self.redraw_formes()
        self.zoom0= self.zoom1

    def clear_formes(self):
        "efface tous les items"
        all_formes=self.canvas.find_all()
        for forme_id in all_formes:
            self.canvas.delete(forme_id)

    def redraw_formes(self):
        """Redessine toutes les formes de dict_formes en tenant compte du zoom"""
        zoom0 = self.dict_formes['zoom0']
        zoom1 = self.dict_formes['zoom1']
        
        i=0
        for value in self.dict_formes.values():
            if i>1 : # pour sauter les 2 premières entrées zoom
                coords = value[0]
                options= value[1]
                tag= options.get('tags')[0]
                if tag in ("rectangle", "polygone", "ovale", "ligne", "grille"):
                    coords_scaled = [coord / zoom0 * zoom1 for coord in coords]
                    try:
                        if tag == "rectangle":
                            forme_id= self.canvas.create_rectangle(*coords_scaled,**options)
                        elif tag == "polygone":
                            forme_id= self.canvas.create_polygon(*coords_scaled,**options)
                        elif tag == "ovale":
                            forme_id= self.canvas.create_oval(*coords_scaled,**options)
                        elif tag == "ligne" or tag == "grille":
                            forme_id= self.canvas.create_line(*coords_scaled,**options)
                    except Exception as e:
                        print(f"Erreur lors de la création de la forme {tag}: {e}")
            i+=1
        
    def grille(self):
        if not self.grid_flag:
            for l in list(range(0, int(self.max_height), int(50 * self.zoom0))) :
                grid_id= self.canvas.create_line(0,l, self.max_width, l, fill='black')
                self.canvas.addtag_withtag("grille", grid_id)
            for c in list(range(0, int(self.max_width), int(50 * self.zoom0))):
                grid_id= self.canvas.create_line(c,0,c,self.max_height, fill='black')
                self.canvas.addtag_withtag("grille", grid_id)
            self.grid_flag= True
        else:
            self.canvas.delete("grille")
            self.grid_flag=False

    # ---définition des fonctions gestionnaires d'évènements : ---
    
    def esc(self,event):
         # stop dessin d'une forme
        if self.mode == 1:
            self.canvas.delete("pt")
            self.canvas.delete("lin")
        if self.mode == 2:
            self.canvas.delete("pt")
            self.canvas.delete("rect")
        if self.mode == 3:
            self.canvas.delete("pt")
            self.canvas.delete("oval")
        if self.mode == 4 :
            self.canvas.delete("line")
            self.canvas.delete("lin")
            self.canvas.delete("pt")
            self.polygone=[]

    def survole(self, event):
        """ indique les coordonnées du cursor dans la barre d'état """

        self.mesure['text']= "Cordonnées du Curseur - x et y : {0} X {1}".format(self.canvas.canvasx(event.x), self.canvas.canvasy(event.y))

        if self.mode==0:
            self.listeFormeId=self.canvas.find_overlapping(self.canvas.canvasx(event.x)-1,self.canvas.canvasy(event.y)-1, \
                                                          self.canvas.canvasx(event.x)+1, self.canvas.canvasy(event.y)+1)
            if len(self.listeFormeId)>0:
                coords= self.canvas.coords(self.listeFormeId[len(self.listeFormeId)-1])
                listags= self.canvas.gettags(self.listeFormeId[len(self.listeFormeId)-1])
                if listags[0] == "rectangle":
                    try:
                        if self.canvas.canvasx(event.x) in [coords[0]-1, coords[0], coords[0]+1, coords[2]-1, coords[2], coords[2]+1]:
                            self.config(cursor="sb_h_double_arrow")
                        elif self.canvas.canvasy(event.y) in [coords[1]-1, coords[1], coords[1]+1, coords[3]-1, coords[3], coords[3]+1]:
                            self.config(cursor="sb_v_double_arrow")
                        else:
                            self.config(cursor="hand1")
                    except Exception:
                        pass
                elif listags[0] == "polygone" or listags[0] == "line":
                    try:
                        for i in list(range(0,len(coords), 2)) :
                            pts=(coords[i], coords[i+1])
                            if self.canvas.canvasx(event.x) in list(range(int(pts[0])-3 , int(pts[0])+4)) and \
                                self.canvas.canvasy(event.y) in list(range(int(pts[1])-3, int(pts[1])+4)):
                                self.config(cursor="cross")
                                break
                            else:
                                self.config(cursor="hand1")
                    except Exception:
                        pass
                elif listags[0] == "ovale":
                    a= (coords[2] - coords[0]) / 2  # demi grand axe
                    b= (coords[3] - coords[1]) / 2  # demi petit axe
                    u= coords[0] + a  # coordonné x du centre de l'ellipse
                    v= coords[1] + b  # coordonné y du centre de l'ellipse
                    limite= False
                    for x in [self.canvas.canvasx(event.x)-1, self.canvas.canvasx(event.x), self.canvas.canvasx(event.x)+1]:
                        for y in [self.canvas.canvasy(event.y)-1, self.canvas.canvasy(event.y), self.canvas.canvasy(event.y)+1]:
                            if (((x - u)**2) / (a**2)) + (((y - v)**2) / (b**2)) > 0.9 and \
                               (((x - u)**2) / (a**2)) + (((y - v)**2) / (b**2)) < 1.1 :  # équation de l'ellipse
                                limite= True
                                break
                    if limite :
                        self.config(cursor= "cross_reverse")
                    else:
                        self.config(cursor="hand1")

            else:
                self.config(cursor="arrow")
        else:   # mode dessin: traçage d'un polygone
            if self.forme_statut == 0:
                    self.x2= self.canvas.canvasx(event.x)
                    self.y2= self.canvas.canvasy(event.y)
                    self.drawPolygone()


    def glisse(self, event):
        """Déplacement d'une forme ou d'un de ses bords
        ou Dessin provisoire d'une forme """

        if self.mode == 0 : # si mode sélection
            if self["cursor"]=='hand1':
                self.canvas.move(self.forme_raise,self.canvas.canvasx(event.x)-self.xy_old[0], self.canvas.canvasy(event.y)-self.xy_old[1])
                self.xy_old[0]= self.canvas.canvasx(event.x)
                self.xy_old[1]= self.canvas.canvasy(event.y)
            elif self["cursor"]=='sb_h_double_arrow' or self["cursor"]=='sb_v_double_arrow':
                self.forme_statut= 3
                if  self.position=="gauche":
                    self.x1= self.canvas.canvasx(event.x)
                elif self.position== "droit":
                    self.x2= self.canvas.canvasx(event.x)
                elif self.position == "haut":
                    self.y1= self.canvas.canvasy(event.y)
                elif self.position == "bas":
                    self.y2= self.canvas.canvasy(event.y)
                self.drawRec()  
            elif self["cursor"]=='cross': # pointe d'un polygone ou d'une ligne
                coords= self.canvas.coords(self.forme_raise)
                coords.pop(self.pts_i)   # retrait de la coordonnée à changer
                coords.pop(self.pts_i)
                coords.insert(self.pts_i, self.canvas.canvasy(event.y))    # insertion de la nouvelle coordonnée
                coords.insert(self.pts_i, self.canvas.canvasx(event.x))
                if len(coords)>4 :  # polygone
                    polygone_id=self.canvas.create_polygon(coords,width=2, fill=self.canvas.itemcget(self.forme_raise, 'fill'))
                    self.canvas.addtag_withtag("polygone",polygone_id)
                else :  # ligne
                    polygone_id= self.canvas.create_line(coords, width=4, fill=self.canvas.itemcget(self.forme_raise, 'fill'))
                    self.canvas.addtag_withtag("ligne", polygone_id)
                self.canvas.delete(self.forme_raise)
                self.forme_raise= polygone_id
            elif self["cursor"]=="cross_reverse":
                coords= self.canvas.coords(self.forme_raise)
                self.x1, self.y1, self.x2, self.y2 = coords
                dx= self.canvas.canvasx(event.x) - self.xy_old[0]
                dy= self.canvas.canvasy(event.y) - self.xy_old[1]
                self.x2 = self.x2 + dx
                self.y2 = self.y2 + dy
                self.xy_old[0]= self.canvas.canvasx(event.x)
                self.xy_old[1]= self.canvas.canvasy(event.y)
                self.forme_statut = 3
                self.drawOval()

        else:   # mode dessin
            if self.control_flag==False:
                if self.forme_statut==0: # forme en cours de dessin
                    self.x2= self.canvas.canvasx(event.x)
                    self.y2= self.canvas.canvasy(event.y)
                    if self.mode== 1:   # ligne intermédiaire                
                        self.drawLigne()
                    if self.mode== 2:   # rectangle intermédiaire         
                        self.drawRec()       
                    if self.mode== 3:   # ovale intermédiaire         
                        self.drawOval()                 

    def ctrl_glisse(self, event):
        "Dessin provisoire d'un carré ou d'un cercle durant le CTRL-glissé"
        self.control_flag= True
        self.x2= self.canvas.canvasx(event.x)
        self.y2= self.y1 + (self.x2 - self.x1)
        if self.mode ==2 : # si mode dessin est un rectangle
            self.forme_statut= 0
            self.drawRec()
        if self.mode== 3:   # ovale intermédiaire         
            self.forme_statut= 0
            self.drawOval()                 

    def relache(self,event):
        """ permet de finir une forme ou mettre en place les pointes d'un polygone lors de son dessin """
        self.x2= self.canvas.canvasx(event.x)
        self.y2= self.canvas.canvasy(event.y)
        if self.mode==1:# fin d'une ligne
            self.forme_statut= 1
            self.drawLigne()
        if self.mode==2:# fin d'un rectangle 
            if self.control_flag==True:
                self.y2 = self.y1 + (self.x2 - self.x1)
            self.forme_statut= 1
            self.drawRec()
        if self.mode==3:# fin d'un ovale 
            if self.control_flag==True:
                self.y2 = self.y1 + (self.x2 - self.x1)
            self.forme_statut= 1
            self.drawOval()
        if self.mode==4:     # angle d'un polygone
            self.polygone.append((self.x1,self.y1))
            self.forme_statut=0     
 
    def click(self,event):
        """click pour sélectionner une forme et/ou pour la déplacer en mode sélection"""
        if self.mode == 0: # si le bouton sélection est enfoncé
            self.listeFormeId=self.canvas.find_overlapping(self.canvas.canvasx(event.x)-1,self.canvas.canvasy(event.y)-1, \
                self.canvas.canvasx(event.x)+1, self.canvas.canvasy(event.y)+1)  # on récupère la forme la plus élevée sous le click
            if len(self.listeFormeId)>0:
                if len(self.canvas.find_all()) >1:
                    self.canvas.tag_raise(self.listeFormeId[len(self.listeFormeId)-1])   # on élève la forme la plus haute de la liste des formes

                self.forme_raise= self.listeFormeId[len(self.listeFormeId)-1]
                coords= self.canvas.coords(self.forme_raise)
                listags= self.canvas.gettags(self.forme_raise)

                if self["cursor"] == "hand1":
                    self.xy_old[0]= self.canvas.canvasx(event.x)
                    self.xy_old[1]= self.canvas.canvasy(event.y)
                else:
                    if listags[0]=="rectangle":
                        self.x1, self.y1, self.x2, self.y2 =coords[0], coords[1], coords[2], coords[3]
                        if self.canvas.canvasx(event.x) in [coords[0]-1, coords[0], coords[0]+1, coords[2]-1, coords[2], coords[2]+1]:
                            #self.config(cursor="sb_h_double_arrow")
                            if self.canvas.canvasx(event.x) in [coords[0]-1, coords[0], coords[0]+1]:
                                self.position="gauche"
                            else:
                                self.position="droit"
                            self.forme_statut= 3  # modifier un coté
                        elif self.canvas.canvasy(event.y) in [coords[1]-1, coords[1], coords[1]+1, coords[3]-1, coords[3], coords[3]+1]:
                            #self.config(cursor="sb_v_double_arrow")
                            if self.canvas.canvasy(event.y) in [coords[1]-1, coords[1], coords[1]+1]:
                                self.position="haut"
                            else:
                                self.position="bas"
                            self.forme_statut = 3 # modifier un coté

                    elif listags[0]=="polygone" or listags[0] == "ligne":
                        self.pts_i=-1
                        for i in list(range(0,len(coords), 2)) :
                            pts=(coords[i], coords[i+1])
                            if self.canvas.canvasx(event.x) in list(range(int(pts[0])-3 , int(pts[0])+4)) and \
                                self.canvas.canvasy(event.y) in list(range(int(pts[1])-3, int(pts[1])+4)):
                                #self.config(cursor="cross")
                                self.pts_i=i
                                break

                    elif listags[0] == "ovale":
                        self.xy_old[0]= self.canvas.canvasx(event.x)
                        self.xy_old[1]= self.canvas.canvasy(event.y)
            else:
                self.config(cursor="arrow")
                
        else: # début d'une forme
            self.forme_statut=0
            self.x1= self.canvas.canvasx(event.x)
            self.y1= self.canvas.canvasy(event.y)
            pts1= (self.x1-3, self.y1-3, self.x1+3, self.y1+3)
            line_id=self.canvas.create_line(pts1, width=2)
            self.canvas.addtag_withtag("pt", line_id)
            pts2= (self.x1+3,self.y1-3, self.x1-3,self.y1+3)
            line_id=self.canvas.create_line(pts2, width=2)
            self.canvas.addtag_withtag("pt", line_id)
            
    def ok(self, event):
        """met fin au dessin d'un polygone"""
        if self.mode ==4:
            if len(self.polygone)== 2:   # tracé d'une ligne
                self.drawLigne()
            if len(self.polygone)> 2: 
                self.forme_statut=1 
                self.drawPolygone()# tracé d'un polygone en bouclant sur le premier point
 

    def drawRec(self):
        "Tracé d'un rectangle dans le canevas"
        trait=0
        couleur=None
        if self.ckbtrait.get()== 1:
            trait = self.spinepais.get()
        if self.ckbcouleur.get()== 1:
            couleur = self.bt_couleur["bg"]
        coords=self.x1,self.y1,self.x2,self.y2
        if self.forme_statut == 0 :  # rectangle en cours de traçage
            self.canvas.delete("rect")
            rectangle_id=self.canvas.create_rectangle(coords,width=2,dash=(4,4))
            self.canvas.addtag_withtag("rect", rectangle_id)
        if self.forme_statut == 1 :  # traçage du rectangle définitif
            self.canvas.delete("pt")
            self.canvas.delete("rect")
            rectangle_id=self.canvas.create_rectangle(coords,width=trait,fill=couleur)
            self.canvas.addtag_withtag("rectangle", rectangle_id)
            self.forme_raise= rectangle_id
            self.control_flag=False
        if self.forme_statut == 3 : # modifier l'un des cotés
            rectangle_id=self.canvas.create_rectangle(coords, width=self.canvas.itemcget(self.forme_raise, 'width'), fill=self.canvas.itemcget(self.forme_raise, 'fill'))
            self.canvas.addtag_withtag("rectangle", rectangle_id)
            self.canvas.delete(self.forme_raise)
            self.forme_raise= rectangle_id

    def drawOval(self):
        "Tracé d'un ovale dans le canevas"
        trait=0
        couleur=None
        if self.ckbtrait.get()== 1:
            trait = self.spinepais.get()
        if self.ckbcouleur.get()== 1:
            couleur = self.bt_couleur["bg"]
        coords=self.x1,self.y1,self.x2,self.y2
        if self.forme_statut == 0 :  # ovale en cours de traçage
            self.canvas.delete("oval")
            ovale_id=self.canvas.create_oval(coords,width=2,dash=(4,4))
            self.canvas.addtag_withtag("oval", ovale_id)
        if self.forme_statut == 1 :  # traçage de l'ovale définitif
            self.canvas.delete("pt")
            self.canvas.delete("oval")
            ovale_id=self.canvas.create_oval(coords,width=trait,fill=couleur)
            self.canvas.addtag_withtag("ovale", ovale_id)
            self.forme_raise= ovale_id
            self.control_flag=False
        if self.forme_statut == 3 : # modifier la grandeur de l'oval
            oval_id=self.canvas.create_oval(coords, width=self.canvas.itemcget(self.forme_raise, 'width'), fill=self.canvas.itemcget(self.forme_raise, 'fill'))
            self.canvas.addtag_withtag("ovale", oval_id)
            self.canvas.delete(self.forme_raise)
            self.forme_raise= oval_id
            
    def drawPolygone(self):
        "Tracé des lignes intermédiaires  puis tracé du polygone lorsque bouclage"
        if self.forme_statut== 0: # ligne intermédiaire du polygone
            coords=self.polygone[-1][0], self.polygone[-1][1], self.x2,self.y2
            line_id=self.canvas.create_line(coords, width=2,dash=(4,4))
            self.canvas.addtag_withtag("line", line_id)
            self.canvas.delete(line_id - 1)
        if self.forme_statut == 1 :   # bouclage du polygone et traçage définitif
            polygone_id=self.canvas.create_polygon(self.polygone,width=self.spinepais.get(), fill=self.bt_couleur["bg"] )
            self.canvas.addtag_withtag("polygone",polygone_id)
            self.canvas.delete("line")
            self.canvas.delete("lin")
            self.canvas.delete("pt")
            self.forme_raise= polygone_id
            self.polygone=[]

    def drawLigne(self):
        coords=self.x1,self.y1,self.x2,self.y2
        if self.forme_statut==0: # ligne intermédiaire
            self.canvas.delete("lin")
            ligne_id=self.canvas.create_line(coords,width=2,dash=(4,4))
            self.canvas.addtag_withtag("lin", ligne_id)
        else:   # ligne définitive
            self.canvas.delete("pt")
            self.canvas.delete("lin")
            ligne_id=self.canvas.create_line(coords,width=self.spinepais.get(),fill=self.bt_couleur["bg"])
            self.canvas.addtag_withtag("line", ligne_id)
            self.forme_raise= ligne_id


    def delete_item(self, event):
        try:
            self.canvas.delete(self.forme_raise)
        except Exception:
            pass
