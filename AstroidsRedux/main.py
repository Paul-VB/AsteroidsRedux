from tkinter import *
import entity
import time
import simpleaudio as sa
import random



##this junk here is for pyinstaller, not needed to compile the game, just a little thing to make the game into 1 single portable exe file
import sys
import os
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)





    
appFont="Comic Sans MS"
assetsFolderPath=resource_path("assets")
spritesFolderPath=assetsFolderPath+"/sprites"
soundClipsFolderPath=assetsFolderPath+"/sounds"
backgroundMusicFilePath=soundClipsFolderPath+"/SMASH MOUTH - ALL STAR - SHITTYFLUTED.wav"


class app:
    def __init__(self):
        '''initializes a tk window and app'''
        self.currentGameLevel=0
        self.root = Tk()#initialize blank window
        self.root.title("Asteroids by Paul_VB")
        self.root.geometry('1024x850')#set the size of the window
        self.gameplayCanvas=Canvas(bg="purple")#make the game area background a certain color
        self.gameplayCanvas.config(width=1024, height=768)
        self.playBgMusic=True#whether or not the background music should play
        '''this is commented out, but not deleted so in the future if i ever have to work with tkinter i'll have some examples with buttons on hand
        #logically you doint need a lambda here cuz a function is already defined but muh boilerplate and syntax so screw you
        blueButton=Button(root, text="click me to make the canvas blue", command=lambda: self.makeCanvasBlue()) 
        blueButton.pack()
        redButton=Button(root, text="click me to make the canvas red", command=lambda: self.makeCanvasRed())
        redButton.pack()'''
        #settung up the ship and the score/ship lives counter display
        self.scoreLabel=Label(self.root,font=(appFont,20), text="")
        self.scoreLabel.pack()
        self.root.bind("r",self.newGame)
        self.gameplayCanvas.pack()
        self.newGame(event=None)
        
    def spawnRocks(self,numberOfRocks,fractionOfBoardNotToSpawnIn=1/3):
        """spawns some LargeRocks randomnly around the gamePlayCanvas. 
        the number of rocks spawned is specified by numberOfRocks.
        the rocks will be spawned around the outer bits of the canvas
        the amount of 'outer bits' is controled by fractionOfBoardNotToSpawnIn"""
        while (numberOfRocks>0):
            #first pick an X and Y cordinate that are NOT in the centerish area of the canvas
            
            x=random.randint(0,int(self.gameplayCanvas['width']))
            while (x>int(self.gameplayCanvas['width'])*fractionOfBoardNotToSpawnIn and x<int(self.gameplayCanvas['width'])*(1-fractionOfBoardNotToSpawnIn)):
                x=random.randint(0,int(self.gameplayCanvas['width']))
            
            y=random.randint(0,int(self.gameplayCanvas['height']))
            while (y>int(self.gameplayCanvas['height'])*fractionOfBoardNotToSpawnIn and y<int(self.gameplayCanvas['height'])*(1-fractionOfBoardNotToSpawnIn)):
                y=random.randint(0,int(self.gameplayCanvas['height']))
            
            #now spawn in the rock with the X and Y we generated    
            entity.Rock(canvas=self.gameplayCanvas,xPos=x,yPos=y)
            numberOfRocks-=1
            
    def newGame(self,event):
        """resets the game back to the starting conditions"""
        self.currentGameLevel=0
        entity.deleteAllEntities()
        self.gameplayCanvas.delete("all")
        self.ship=entity.Ship(canvas=self.gameplayCanvas)
        self.ship.setXPos(float(self.gameplayCanvas['width'])/2)
        self.ship.setYPos(float(self.gameplayCanvas['height'])/2)
        self.root.bind("<KeyPress-a>",self.ship.startRotatingLeft)
        self.root.bind("<KeyRelease-a>",self.ship.stopRotatingLeft)
        self.root.bind("<KeyPress-d>",self.ship.startRotatingRight)
        self.root.bind("<KeyRelease-d>",self.ship.stopRotatingRight)
        self.root.bind("<KeyPress-w>",self.ship.startAcceleratingForward)
        self.root.bind("<KeyRelease-w>",self.ship.stopAcceleratingForward)
        self.root.bind("<KeyPress-space>",self.ship.shootBullet)
        self.root.bind("<KeyRelease-space>",self.ship.reloadBullet)
        
    def nextLevel(self):
        """starts the next level of the game"""
        self.currentGameLevel+=1
        
        #move the ship back to the center
        self.ship.setXPos(float(self.gameplayCanvas['width'])/2)
        self.ship.setYPos(float(self.gameplayCanvas['height'])/2)
        self.ship.xMomentum=0
        self.ship.yMomentum=0
        
        newLevelText=self.gameplayCanvas.create_text(float(self.gameplayCanvas['width'])/2,float(self.gameplayCanvas['height'])/2,fill="white",font=(appFont,50),text=("Level "+str(self.currentGameLevel)))
        self.root.update()
        time.sleep(1)
        self.gameplayCanvas.delete(newLevelText)
        self.spawnRocks(self.currentGameLevel)
            
            
        
    def makeCanvasBlue(self):
        """makes the background of the canvas blue"""
        gameplayCanvas=self.gameplayCanvas
        gameplayCanvas.configure(background='blue')
        
        print("blue?")

    def makeCanvasRed(self):
        """makes the background of the canvas red"""
        gameplayCanvas=self.gameplayCanvas
        gameplayCanvas.configure(background='red')
        print("RED?")
    
    def updateLabels(self):
        """updates the label containing the number of lives left and the player's score"""
        self.scoreLabel.config(text="Ship Lives: "+str(self.ship.lives)+" | Score: "+str(self.ship.score)+" | Level: "+str(self.currentGameLevel))
            
    def shutdownApp(self):
        """shuts down the app and stops playing the background music"""
        entity.deleteAllEntities()
        sa.stop_all()

        
    def run(self):
        """runs the game"""
        if self.playBgMusic==True:
            bgmusic=sa.WaveObject.from_wave_file(backgroundMusicFilePath)
            bgmusicPlayObj=bgmusic.play()
        isGameOver=False
        while True:
            #check if the bg music is still playing
            if self.playBgMusic==True:
                if not bgmusicPlayObj.is_playing():
                    bgmusicPlayObj=bgmusic.play()

            try:
                self.updateLabels()
                self.root.update()
                isGameOver=0>=self.ship.lives
                if not isGameOver:
                    entity.updateAllEntities()
                else:
                    #game over
                    self.gameplayCanvas.create_text(float(self.gameplayCanvas['width'])/2,float(self.gameplayCanvas['height'])/2,fill="white",font=(appFont,40),text="Game Over, Your score was: "+str(self.ship.score)+"\nPress the 'R' key to play again")
                    
                time.sleep((1000/60)/1000)#wow okay so i just did this the shitty way


            except TclError:
                """this error is thrown if the user closes the game window"""
                print("game window closed, shutting down")
                self.shutdownApp()
                print("game shutdown successful!")
                break
                        #check for next level
            if (len(entity.Rock.registeredRocks)==0):
                #if there are no rocks on the gameplay canvas...
                self.nextLevel()
    
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)       

def main():
    a=app()
    a.run()
if __name__ == "__main__": main()
