from tkinter import *

# ****************************************************************
# ce module définit une classe, celle d'une fenêtre de dialogue  *
# ****************************************************************
class Dialogue (Toplevel) :
    # le constructeur    
    # # ###############
    def __init__ (self, conteneur, titre = None, centrer= False, offx=350, offy=400, source=None) :
        # associer la fenête de dialogue et son conteneur        
        Toplevel.__init__(self, conteneur, source=None)
        self.protocol("WM_DELETE_WINDOW", self.annuler)
        self.transient(conteneur)   # Le dialogue apparait au dessus de son conteneur        
        self.resizable(width =0, height =0)    # => empêche le redimensionnement
        
        if titre:
            self.title(titre)   #   title() est hérité de Toplevel

        # conteneur = fenêtre qui ouvre le Dialogue
        self.conteneur = conteneur
        self.source= []
        if source:
            self.source.extend(source)
        self.resultat= None

        cadre = Frame(self)
        self.initial_focus = self.habillage(cadre, self.source)
        cadre.pack(padx=10, pady=10)

        focusDefaut =self.boiteBoutons()    # créer la boite bouton

        self.grab_set()     # rendre la fenêtre modale

        # cas où on n'a pas surchargé la fonction habillage()
        if not self.initial_focus :
            self.initial_focus = focusDefaut # bouton OK
            
        if centrer :            
            # centrer la fenêtre de dialogue            
            self.update_idletasks() # nécessaire pour winfo_width()            
            wh = self.winfo_width()            
            ht = self.winfo_height()            
            swh= self.winfo_screenwidth()
            sht= self.winfo_screenheight()            
            xtl=(swh-wh) // 2            
            ytl=(sht - ht) // 2            
            self.geometry('+'+str(xtl)+'+'+str(ytl))
        else:            
            # afficher la fenêtre de dialogue par rapport au conteneur            
            self.geometry ("+"+str(conteneur.winfo_rootx()+offx)+"+"+str(conteneur.winfo_rooty()+offy))        
            
        # porter le focus sur le cadre ou la fenêtre d'entrée        
        self.initial_focus.focus_set ()        
        
        # boucle locale de la fenêtre de dialogue        
        self.wait_window (self)

    # construire
    def habillage (self, master, source) :
        pass    # méthode qui doit être surchargée


    # définition de la boîte à boutons    
    # # ################################
    def boiteBoutons (self) :        
        boite = LabelFrame (self, text="Valider")        
        w1 = Button (boite, text = "O.K.", width = 10, command = self.ok, default = ACTIVE)
        w1.pack (side=LEFT, padx = 5, pady = 5)        
        w2 = Button (boite, text = "Annuler", width = 10,command = self.annuler)        
        w2.pack (side=LEFT, padx = 5, pady = 5)        
        self.bind("<Return>", self.ok)        
        self.bind("<Escape>", self.annuler)        
        boite.pack ()
        return w1
        
    def ok (self, evenement = None) :        
        self.initial_focus.focus_set()        
        
        # effacement avant de supprimer (pour le rendu)        
        self.withdraw () 
        
        # nécessaire si dans apply() on utilise des éléments qui doivent être visibles pour fournir des données   
        self.update_idletasks()        
        self.apply()        
        self.annuler()

    def annuler (self, evenement = None) :        
        self.conteneur.focus_set()        
        self.destroy()
        
    def apply (self) :
        pass    # méthode qui doit être surchargée   
