import tkinter as tk
import os.path
from configparser import ConfigParser

class MainJardin(tk.Frame):
    """classe contenaire"""

    def __init__(self, root):  
        super().__init__(root)
        root.title("Mon jardin")
        self.pack(fill=tk.BOTH)
        self.createMenuBar()
        self.demarrage()

    def createMenuBar(self):

        self.mb =  tk.Menu(root, bg="grey")
        root.config(menu= self.mb)
        
    """ embranchement vers les 2 modules principaux
    - dessin du jardin --> module terrain
    - gestion du jardin --> module gestion

    selon le contenu du fichier MonJardin.ini
    """

    def demarrage(self):
        config = ConfigParser()
        if os.path.exists("./monJardin.ini"):
            config.read("./monJardin.ini")
            if config.get('Last', 'module') == 'terrain':
                from terrain import Terrain
                self.monTerrain = Terrain(root,self.mb, config.get('Module', 'terrain'))
            elif config.get('Last', 'module') == 'planter':
                from planter import Planter
                self.monJardin = Planter(root,self.mb,config.get('Module', 'planter'))
            elif config.get('Last', 'module') == 'gestion':
                from gestion import Gestion
                self.monJardin = Gestion(root, self.mb, config.get('Module', 'gestion'))
                
        else:   # si première ouverture du programme
            from terrain import Terrain
            self.monJardin = Terrain(root, self.mb, None)


# boucle principale
if __name__ == "__main__":
    root= tk.Tk()
    monApp = MainJardin(root)
    root.mainloop()
    root.destroy()