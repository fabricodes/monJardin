import sqlite3 as sql
import tkinter as tk
from dialogue import Dialogue



class categorie_dialogue(Dialogue):
    "Fenêtre satellite contenant des contrôles de redimensionnement"

    def habillage(self, cadreconteneur, source):

         Label(cadreconteneur,text='id = ').grid(row=0,column=0, sticky='e')
         Label(cadreconteneur,text= repr(source[0])).grid(row=0,column=1,sticky='w')
         Label(cadreconteneur,text='hauteur = ').grid(row=1,column=1, sticky='e')
         Label(cadreconteneur,text=source[1]).grid(row=1,column=2,sticky='w')
         Label(cadreconteneur,text='hauteur_cat (en cm : (x, y,..) = ').grid(row=2,column=1, sticky='e')
        self.saisieCategorie= Entry(cadreconteneur)
        self.saisieCategorie.grid(row=2,column=2, sticky='w')
        return self.saisieCategorie

    def apply(self):
        self.resultat= self.saisieCategorie.get()

class App( Frame):
    def __init__(self, master=None):
         Frame.__init__(self)
        self.master.title("ajouter et renseigner une autre colonne")
        self.master.geometry("500x150")
        self.grid()


        self.conn=sql.connect('plantes')
        self.cur = self.conn.cursor()
        curseur= self.cur.execute('SELECT COUNT(id) FROM especes;')
        self.nb= curseur.fetchone()[0]

        self.action()

    def action(self):    
        for phrase in self.generateur_de_phrases():
            id, texte = phrase[0], phrase[1]
            resultat=self.analyse(texte)
            nombres=resultat[0]
            unites=resultat[1]
            if len(nombres) != len(unites):
                categorie= self.nouvelle_interro(id)
            else:
                categorie=[]
                for i in list(range(len(nombres))):
                    if unites[i]  in ['m', 'metre', 'metres', 'mètre', 'mètres']:
                        nombres[i]=float(nombres[i])*100
                    else:
                        nombres[i]= float(nombres[i])

                    if nombres[i] > 250:
                        categorie.append('5')
                    elif nombres[i]>150:
                        categorie.append('4')
                    elif nombres[i]>75:
                        categorie.append('3')
                    elif nombres[i]>30:
                        categorie.append('2')
                    else:
                        categorie.append('1')
                cat= set(','.join(categorie))
                cat.discard(',')

                self.enregistre_categorie(id, cat)


    def generateur_de_phrases(self):
        " passage en revue du champ hauteur"
        i=1
        while  i <= self.nb:
            curseur= self.cur.execute('SELECT id, hauteur FROM especes WHERE id= {};'.format(i))
            i += 1
            phrase= curseur.fetchone()
            yield phrase

    def corriger(self,text):
        "éclate les mots anormalement accolés"
        self.sousmots=[]

        def ipartage(mot):         
            if not mot.isnumeric() and not mot.isalpha():
                i=1
                while i<len(mot):
                    if mot[:i].isnumeric() or mot[:i].isalpha():
                        i+=1
                    else: 
                        break
                if i==1:
                    self.sousmots.append(mot[:i])
                    if len(mot)-i>0:
                        ipartage(mot[i:])
                else:
                    self.sousmots.append(mot[:i-1])
                    if len(mot)-i+2>1:
                        ipartage(mot[i-1:])
                    else:
                        self.sousmots.append(mot[i-1:])

            else:
                self.sousmots.append(mot)

        def combine():
            i=1
            while i< len(self.sousmots)-1:  # convertit x m y en float x.y m
                try:
                    if self.sousmots[i-1].isnumeric() and self.sousmots[i] in ['cm', 'm', 'centimetre','centimètre','centimètres', 'metre','mètre', 'mètres'] and \
                    self.sousmots[i+1].isnumeric():
                        mot1= self.sousmots[i-1] +'.'+ self.sousmots[i+1]
                        self.sousmots[i-1]= float(mot1)
                        self.sousmots.pop(i+1)
                except: pass
                i+=1
            i=1
            while i< len(self.sousmots)-1:  # convertit x,y en float x.y
                try:
                    if self.sousmots[i-1].isnumeric() and self.sousmots[i] in ['.', ','] and self.sousmots[i+1].isnumeric():
                        mot1= self.sousmots[i-1] + '.' + self.sousmots[i+1]
                        self.sousmots[i-1]= float(mot1)
                        self.sousmots.pop(i)
                        self.sousmots.pop(i)
                except: pass
                i+=1
            i=0
            while i< len(self.sousmots):    # convertit en float
                try:
                    mot1= float(self.sousmots[i])
                    self.sousmots[i]= mot1
                except: pass
                i+=1
            i=1
            while i<len(self.sousmots): # convertit un en 1.0 si avant à ou une unité
                if self.sousmots[i-1]=="un" and (self.sousmots[i]=='à' or self.sousmots[i] in \
                    ['cm', 'm', 'centimetre','centimetres','centimètre','centimètres', 'metre','mètre', 'metres','mètres']) :
                    mot1= 1.0
                    self.sousmots[i-1]= mot1
                i+=1
            i=1
            while i<len(self.sousmots): # convertit plusieurs ou quelques en 3.0
                if (self.sousmots[i-1]=="plusieurs" or self.sousmots[i-1]== 'quelques') and self.sousmots[i] in \
                    ['cm', 'm', 'centimetre','centimetres','centimètre','centimètres', 'metre','mètre', 'metres','mètres'] :
                    mot1= 3.0
                    self.sousmots[i-1]= mot1
                i+=1
            i=1
            while i<len(self.sousmots): # convertit douzaine de en 12.0
                if self.sousmots[i-1]=="douzaine" and self.sousmots[i] == 'de' :
                    mot1= 12.0
                    self.sousmots[i-1]= mot1
                i+=1
            i=1
            while i<len(self.sousmots): # convertit le mètre en 0.9 et 1.1 m
                if self.sousmots[i-1]=="le" and self.sousmots[i] in ['cm', 'm', 'centimetre','centimetres','centimètre','centimètres', 'metre','mètre', 'metres','mètres'] :
                    mot1= 0.9
                    mot2= 'à'
                    mot3= 1.1
                    self.sousmots[i-1]= mot1
                    self.sousmots.insert(i, mot2)
                    self.sousmots.insert(i+1, mot3)
                i+=1
            i=1
            while i<len(self.sousmots): # retrouve les unités manquantes
                if type(self.sousmots[i-1])==float and \
                    self.sousmots[i] not in ['cm', 'm', 'centimetre','centimetres','centimètre','centimètres', 'metre','mètre', 'metres','mètres'] :
                    index= i
                    j=i+1
                    max= i+len(self.sousmots)-index
                    while j< max:
                        if self.sousmots[j] in ['cm', 'm', 'centimetre','centimetres','centimètre','centimètres', 'metre','mètre', 'metres','mètres'] and \
                            type(self.sousmots[j-1])==float :
                            self.sousmots.insert(index,self.sousmots[j])
                            break
                        j+=1
                i+=1       

        for mot in text:
            ipartage(mot)

        combine() 
    

        return self.sousmots
                            

    def analyse(self, text):
        mots= text.split()
        mots= self.corriger(mots)
        nombres=[]
        unites=[]  
       
        for mot in mots:
            if type(mot)==float:
                nombres.append(mot)
            elif mot in ['cm', 'm', 'centimetre','centimetres','centimètre','centimètres', 'metre','metres','mètre', 'mètres']:
                unites.append(mot)
              
        return (nombres, unites)                        


    def nouvelle_interro(self,i):
        req='SELECT id, hauteur FROM especes WHERE id={};'.format(i)
        curseur=self.cur.execute(req)
        source= list(curseur.fetchone())
        monDialog= categorie_dialogue(self, source=source)
        req= "UPDATE especes SET hauteur_cat = {} where id = {};".format(repr(monDialog.resultat), i)
        curseur=self.cur.execute(req)
        self.conn.commit()
         

    def enregistre_categorie(self, id, cat):

        req= "UPDATE especes SET hauteur_cat = {} where id = {};".format(repr(','.join(cat))  , id)
        curseur=self.cur.execute(req)
        self.conn.commit()

    def suite(self):
        categorie = self.saisie.get().split(',')
        id= self.idbase.get()
        self.enregistre_categorie(id, set(categorie))
        self.saisie.set('')
        self.idbase.set('')
        self.hauteur_base.configure(text= '' )
        self.action()

#---------------Programme principal------------------------------
if __name__ == '__main__':
    myapp = App()
    myapp.mainloop()
    myapp.destroy()
