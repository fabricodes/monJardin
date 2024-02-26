import tkinter as tk
from tkinter import ttk
import sqlite3 as sql
import tkinter.font as tkFont
from tkinter import Frame, Misc, simpledialog
from tkinter import messagebox
import pickle
import os, sys
from PIL import ImageTk, Image, ImageDraw
from configparser import ConfigParser
from functools import partial
from plante import Plante


class Planter( tk.Frame):
    """Fenêtre d'Application principale"""
    plantes=[]
    def __init__(self, master=None, mb=None, fichier=None):
        tk.Frame.__init__(self)
        self.master=master
        self.master.title("Les plantes de mon jardin")
        # self.master.geometry("1920x1080")
        self.mb= mb
        self.pack()
        self.createMenuBar()

    # Variables d'instance
        self.view_height=900
        self.view_width=1540
        self.max_height= 3000
        self.max_width= 4000
        self.zoom0 = 1
        self.zoom1 = 1
        self.ico = (0,0)
        self.icon_item=None
        self.active = None
        self.buttons= []
        self.mesPlantes={}  # dictionnaire des plantes plantées
        self.plantes= []    # liste des objets Plante
    
    
    # Les Widgets
        self.cnv =  tk.Canvas(self, bg='white', width= self.view_width, height= self.view_height, scrollregion= (0 ,0,self.max_height, self.max_width))
        self.defily =  tk.Scrollbar(self, orient='vertical', bg= 'dark slate gray', command=self.cnv.yview)
        self.defilx =  tk.Scrollbar(self, orient='horizontal', bg='dark slate gray', command=self.cnv.xview)
        self.bandeau =  tk.Frame(self, bg='dark grey', bd= 2, height= self.view_height)
        self.etat =  tk.Frame(self, bg='grey', pady=5, bd=2, relief= tk.GROOVE)
        self.mesure =  tk.Label(self.etat, text="mesure = ", bg="grey")
        
        
        # constituer la base des icons des types de plantes
        self.fileimages={}
        dossiers= os.listdir('images/Plantes')
        for dossier in dossiers:
            self.fileimages[dossier]=os.listdir("images/Plantes/" + dossier)
        
        self.listimages=[] # liste des images au format tkPhotoimage pour une catégorie
        self.photoimages={} # structure: { non de la catégorie : [ listimages]}
        for categorie, fname in self.fileimages.items():
            for i in range(len(fname)):
                self.listimages.append(tk.PhotoImage(file='images/Plantes/' + categorie + '/' + fname[i]))
            self.photoimages[categorie]=self.listimages
            self.listimages=[]
        Plante.photoimages = self.photoimages
        i=0        
        self.frm_categorie=[] # liste des frames de type
        for categorie, plantes  in self.photoimages.items():
            self.frm_categorie.append(tk.LabelFrame(self.bandeau, text=categorie, bd=2))
            self.frm_categorie[-1].pack(anchor=tk.W,padx=5, pady=5)
            
            for j,img_plante in enumerate(plantes):
                self.buttons.append(tk.Button(self.frm_categorie[-1],
                          image=img_plante,
                          bd=4,
                          relief= tk.FLAT,
                          command=  lambda categorie= categorie, j=j, i=i:  self.select_ico(categorie, j, i)
                          ))
                self.buttons[-1].grid(row=(j//3), column= j%3)                   
                i+=1
        
        self.cnv.grid(row=0, column=0)
        self.defily.grid(row=0, column=1, sticky= tk.NS)
        self.defilx.grid(row=1, column=0, stick=tk.EW)
        self.bandeau.grid(row=0, column=2)
        self.etat.grid(row=2, column=0, columnspan=2)
        self.mesure.pack()

        self.cnv['xscrollcommand'] = self.defilx.set
        self.cnv['yscrollcommand'] = self.defily.set

        # récupérer l'image de fond du jardin
        config= ConfigParser()
        config.read("./monJardin.ini")
        if config.get('Module', 'gestion'):
            path = config.get('Module', 'gestion')
                
        image1 = Image.open(path)
        self.Jardin = ImageTk.PhotoImage(image1)
        h = self.Jardin.height()
        w= self.Jardin.width()
        centre= (w//2, h//2)
        self.cnv.create_image(centre, image=self.Jardin)
        
        # récupérer 'mesPlantes' le dictionnaire picklelisé des plantes déjà plantées
        try:
            config.read("./monJardin.ini")
            if config.get('Module', 'planter'):
                path = config.get('Module', 'planter')
                with open(path,'rb') as fl:
                    self.mesPlantes= pickle.load(fl)
                    self.affichePlantes()
        except IOError:
           pass
                  
        
        self.cnv.bind("<Double-Button-1>", self.planter)
        self.cnv.bind("<Button-1>", self.duplique)

        
    def createMenuBar(self):
        self.sm1 = tk.Menu(self.mb, tearoff=0, bg= 'dark grey')
        self.sm2 = tk.Menu(self.mb, tearoff=0, bg = 'dark grey')
        
        self.mb.add_cascade(label = "Fichier", menu= self.sm1)
        self.sm1.add_command(label='Ouvrir', command= self.ouvrir)
        self.sm1.add_command(label='Enregistrer', command= "")
        self.sm1.add_command(label='Quitter', command= self.quitter)
               
        self.mb.add_cascade(label= "Gérer", menu= self.sm2)
        self.sm2.add_command(label= 'Modifier terrain', command= self.terrain)
        self.sm2.add_command(label='classification', command= self.classification)
        
        self.master.config(menu=self.mb)    
        
        
    def select_ico(self, categorie, j, idx):
        self.ico= (categorie, j)
        # basculer l'icon sélectionnée en SUNKEN et ramener la précédente en FLAT
        if self.active is not None:
            self.buttons[self.active].configure(relief= tk.FLAT)
        self.buttons[idx].configure(relief=tk.SUNKEN)    
        self.active = idx

        
    def affichePlantes(self):
        """crée les objets plantes déjà plantées et affiche leur icon sur le canevas"""
        Plante.mesPlantes = self.mesPlantes
        for coord, maPlante in self.mesPlantes.items():
            Planter.plantes.append(Plante(self.cnv, coord, maPlante, ico= None ))

    def planter(self, event):
        """crée un nouvel objet plante suite Double-click et affiche son icon sur le canevas"""
        if self.ico != (0,0):
            coord= (event.x, event.y)
            Planter.plantes.append(Plante(self.cnv, coord, None, ico= self.ico ))
        self.mesPlantes= Plante.mesPlantes
        
    def duplique(self, event):
        if Plante.doublon:
            coord= event.x, event.y
            self.ico= Plante.maPlante_ref['ico']
            Planter.plantes.append(Plante(self.cnv, coord, Plante.maPlante_ref, ico= self.ico ))
            
    
    def ouvrir(self,event):
        pass
    
    
    def terrain(self):
        self.mb =  tk.Menu(self.master, bg="grey")
        self.master.config(menu= self.mb)
        self.pack_forget()
        from terrain import Terrain
        from configparser import ConfigParser
        config = ConfigParser()
        config.read("./monJardin.ini")
        self.monJardin = Terrain(self.master, self.mb, config.get('Module', 'terrain'))
    
    def classification(self):
        self.mb =  tk.Menu(self.master, bg="grey")
        self.master.config(menu= self.mb)
        self.pack_forget()
        from gestion import Gestion
        self.monJardin = Gestion(self.master, self.mb)
         
    def glisse(self, event):
        pass

    
    def delete_item(self, event):
        pass
    
    def ctrl_glisse(self,event):
        pass
    
    def ok(self,event):
        pass
    
    def esc(self, event):
        pass
        
    def quitter(self):
        sys.exit()
