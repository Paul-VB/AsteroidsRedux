"""a basic 2d enitity class for use with tkinter. by Paul VandenBroeck. May 2018"""
from PIL import Image, ImageTk
import tkinter
import math
import simpleaudio as sa
import random
import time

import main



#magic numbers/ string literals

defaultSpritePath=main.spritesFolderPath+"/defaultTexture.png"

#ship stuff
shipSpritePath=main.spritesFolderPath+"/ship.png"
shipDamagedSpritePath=main.spritesFolderPath+"/shipDamaged.png"
shipDamagedSoundPath=main.soundClipsFolderPath+"/roblox-death-sound.wav"
shipDamagedInvulerabilityGracePeriodLength=1.5#seconds
shiptHitboxRadius=25.0
shipRotationSpeed=5
defaultNumberOfShipLives=3

#bullet stuff
bulletSpritePath=main.spritesFolderPath+"/bullet.png"
bulletSoundPath=main.soundClipsFolderPath+"/pew.wav"
bulletHitboxRadius=2.5
maxNumberOfBulletsPerShip=4
bulletSpeed=10
bulletTimeToLive=1.5# IN SECONDS, how long the bullet can travel for in open space before it self-deletes

#rockStuff
rockLargeSpritePath=main.spritesFolderPath+"/rockLarge.png"
rockLargeHitboxRadius=100.0
rockLargePointValue=20
rockMediumSpritePath=main.spritesFolderPath+"/rockMedium.png"
rockMediumHitboxRadius=50.0
rockMediumPointValue=50
rockSmallSpritePath=main.spritesFolderPath+"/rockSmall.png"
rockSmallHitboxRadius=25.0
rockSmallPointValue=100
numberOfNewRocksToSpawnOnShatter=2
rockSpeedRange=[0,3]#new rocks spawn with a random speed between these two values 

def updateAllEntities():
    """goes through each instance of entity and runs all the funtions they should do per tick"""
    entityKeys=list(registeredEntities.keys())
    for currKey in entityKeys:
        try:
            currEntity=registeredEntities[currKey]
            currEntity.update()
        except KeyError:
            #this should only be called if an entity is deleted (like if a rock got hit by a bullet)
            continue
            

def deleteAllEntities():
    """deletes every entity. this is used when the game is reset or closed"""
    entityKeys=list(registeredEntities.keys())
    for currKey in entityKeys:
        try:
            currEntity=registeredEntities[currKey]
            currEntity.delete()

        except KeyError:
            #this should only be called if an entity is deleted (like if a rock got hit by a bullet)
            continue

entityCounter=0
registeredEntities={}# a dictionary of all the entities that have been made

class Entity:
    """a parent class for most entity types"""
           
    def __init__(self,canvas=None,spritePath=defaultSpritePath,hitboxRadius=0,xPos=0,yPos=0):
        """initalizes this instance of Entity"""
        global entityCounter
        global registeredEntities
        self.ID=entityCounter
        entityCounter+=1
        registeredEntities[self.ID]=self        
        
        #these variables deal with position and motion
        self.xPos=xPos #the x postion of the entity
        self.yPos=yPos #the y position of the entity
        self.xMomentum=0.0
        self.yMomentum=0.0
        self.faceHeading=0.0
        
        self.hitboxRadius=hitboxRadius
        
        #these variabls and other junk deal with drawing the sprite onscreen
        self.spritePath=spritePath#the path to the image that this entity instance will use
        self.spriteImageFile=(Image.open(self.spritePath)) #the image file that we'll manipulate mainly when doing rotations
        self.spriteImage = ImageTk.PhotoImage(self.spriteImageFile.rotate(self.faceHeading,expand=True)) #the thing that tkinter uses as an image to draw on a canvas

        #theres two spriteImage variables because of the weird way that you basically have to reload the image if you want to rotate it. its a weirdity with tkinter
        self.spriteOnCanvas=None #the variable that holds a refrence to the actual drawn-on-screen thingy that's actually on the canvas
        self.canvasIGetDrawnOn=None #the canvas that this instance of the entitiy class will have its sprite drawn on
        self.canvasIGetDrawnOnsWidth=0
        self.canvasIGetDrawnOnsHeight=0
        if (canvas!=None):
            self.setCanvas(canvas)
            
        #these variables deal with motion and rotation due to player interaction
        self.isAcceleratingForward=False

       
    
    def setTexture(self,pathToNewTexture):
        """sets the texute image that this instance of entity will use as a sprite"""
        self.spritePath=pathToNewTexture
        self.spriteImageFile=(Image.open(self.spritePath))
        self.reDraw()
    
    def setCanvas(self,newCanvasIGetDrawnOn):
        """sets the canvas that this entity will have it's sprite drawn upon"""
        self.canvasIGetDrawnOn=newCanvasIGetDrawnOn
        self.spriteOnCanvas=self.canvasIGetDrawnOn.create_image(self.xPos,self.yPos,image=self.spriteImage)
        self.canvasIGetDrawnOnsWidth=float(self.canvasIGetDrawnOn['width'])
        self.canvasIGetDrawnOnsHeight=float(self.canvasIGetDrawnOn['height'])
    
    def setXPos(self,newXPos):
        """updates the x position of this entity"""
        self.xPos=newXPos
    
    def setYPos(self,newYPos):
        """updates the y position of this entity"""
        self.yPos=newYPos
        
    def syncSpriteCoordinates(self):
        """makes the coordinates of the image drawn on the canvas 
        to match the xPos and yPos of the entity."""
        oldSpriteCoords=self.canvasIGetDrawnOn.coords(self.spriteOnCanvas)
        deltaCoords=[self.xPos-oldSpriteCoords[0],self.yPos-oldSpriteCoords[1]]
        self.canvasIGetDrawnOn.move(self.spriteOnCanvas,*deltaCoords)
        
    def startAcceleratingForward(self,event):
        """sets the isAcceleratingForward to True. this function is used with a key press (when the key is pressed DOWN) event"""
        self.isAcceleratingForward=True
        
    def stopAcceleratingForward(self,event):
        """sets the isAcceleratingForward to False. this function is used with a key release event"""
        self.isAcceleratingForward=False
    
    def accelerateForwards(self,movementSpeed=0.1):
        """accelerates the entity forwards based on its current faceHeading"""
        self.xMomentum+=math.sin(self.faceHeading*(math.pi/180))*movementSpeed
        self.yMomentum+=math.cos(self.faceHeading*(math.pi/180))*movementSpeed
        
    def decelerate(self):
        """slows the entity down by a percentage of its current momentum."""
        self.decelerationRate=0.99       
        self.xMomentum=self.xMomentum*self.decelerationRate
        self.yMomentum=self.yMomentum*self.decelerationRate
        
        
    def moveBasedOnCurrentMomentum(self):
        """updates the entity's x and y coordinates based on how far the entity
        moves each game tick due to the entity's momentum"""
        self.xPos-=self.xMomentum
        self.yPos-=self.yMomentum
        self.syncSpriteCoordinates()
        
    def checkCanvasBoundsAndWrap(self):
        """checks to see if the entity is out of the bounds of the canvas"""
        #check along the x axis
        if (self.xPos<0):
            self.setXPos(self.canvasIGetDrawnOnsWidth)
            
        elif (self.xPos>self.canvasIGetDrawnOnsWidth):
            self.setXPos(0)
        #check along the y axis
        if (self.yPos<0):
            self.setYPos(self.canvasIGetDrawnOnsHeight)
            
        elif (self.yPos>self.canvasIGetDrawnOnsHeight):
            self.setYPos(0)
            
    def moveLeft(self,event):
        '''move the entity left''' 
        oldCoords=[self.xPos,self.yPos]
        
        self.xPos= self.xPos-1 #modify the coordiantes
        
        deltaCoords=[self.xPos-oldCoords[0],self.yPos-oldCoords[1]]
        self.canvasIGetDrawnOn.move(self.sprite,*deltaCoords)
        
      
    def moveRight(self,event):
        '''move the entity right'''  
        oldCoords=[self.xPos,self.yPos]
        
        self.xPos= self.xPos+1 #modify the coordiantes
        
        deltaCoords=[self.xPos-oldCoords[0],self.yPos-oldCoords[1]]
        self.canvasIGetDrawnOn.move(self.sprite,*deltaCoords)
        
    
    def moveUp(self,event):
        oldCoords=[self.xPos,self.yPos]
        
        self.yPos= self.yPos-1 #modify the coordiantes
        
        deltaCoords=[self.xPos-oldCoords[0],self.yPos-oldCoords[1]]
        self.canvasIGetDrawnOn.move(self.sprite,*deltaCoords)
        
    def moveDown(self,event):
        """moves the entity down"""
        oldCoords=[self.xPos,self.yPos]
        
        self.yPos= self.yPos+1 #modify the coordiantes
        
        deltaCoords=[self.xPos-oldCoords[0],self.yPos-oldCoords[1]]
        self.canvasIGetDrawnOn.move(self.sprite,*deltaCoords)
        
    def reDraw(self):
        """deletes the current sprite on the canvas and redraws the entity's sprite on the canvas"""
        self.canvasIGetDrawnOn.delete(self.spriteOnCanvas)
        self.spriteImage = ImageTk.PhotoImage(self.spriteImageFile.rotate(self.faceHeading, expand=True))
        self.spriteOnCanvas=self.canvasIGetDrawnOn.create_image(self.xPos,self.yPos,image=self.spriteImage)
    
    def update(self):
        """a function that calls all the fuctions that each entity needs to perform each tick"""
        self.syncSpriteCoordinates()
        self.moveBasedOnCurrentMomentum()
        #self.decelerate()
        self.checkCanvasBoundsAndWrap()

    
    def delete(self):
        """deletes the entity"""
        del registeredEntities[self.ID]
        try:
            self.canvasIGetDrawnOn.delete(self.spriteOnCanvas)

        except tkinter.TclError:
            """this error is thrown if the user closes the game window"""
                
        self.spriteImageFile.close()
        self.spriteImageFile=None
        
        
    def hasCollidedWith(self,otherEntity):
        """this function checks if the circular hitboxes this entity and another entity are colliding
        returns False if the two entities are NOT colliding, returns True if they ARE colliding"""
        distance=math.sqrt((otherEntity.xPos-self.xPos)**2+(otherEntity.yPos-self.yPos)**2)
        return distance < (self.hitboxRadius+otherEntity.hitboxRadius)
        

class Ship(Entity):
    """the ship that the player can control, requires the movement keys to be bound in the parent TK root thing"""
    shipDamagedSound = sa.WaveObject.from_wave_file(shipDamagedSoundPath)
    def __init__(self,canvas=0,spritePath=shipSpritePath,hitboxRadius=shiptHitboxRadius,xPos=0,yPos=0):
        """initalizes this instance of Ship"""
        Entity.__init__(self,canvas,spritePath,hitboxRadius,xPos,yPos)
        self.lives=defaultNumberOfShipLives
        self.isInGraceInvulnerability=False
        self.score=0#the number of points this ship has scored
        self.maxBullets=maxNumberOfBulletsPerShip#the maximum number of bullets this ship can shoot at one time
        self.currentBullets=0#the number of bullets currently flying through space that this ship has fired
        self.hasBulletLoaded=True#whether or not the ship has a bullet loaded in its semi-auto gun
        self.isRotatingLeft=False
        self.isRotatingRight=False
        
    def startRotatingLeft(self,event):
        """sets the entity's isRotatingLeft variable to True"""
        self.isRotatingLeft=True
        
    def stopRotatingLeft(self,event):
        """sets the entity's isRotatingLeft variable to False"""
        self.isRotatingLeft=False
        
    def rotateLeft(self):
        """adjusts the faceheading of the entity by the entity's rotation speed"""
        self.faceHeading+=shipRotationSpeed
        self.reDraw()
        
    def startRotatingRight(self,event):
        """sets the entity's isRotatingRight variable to True"""
        self.isRotatingRight=True
        
    def stopRotatingRight(self,event):
        """sets the entity's isRotatingRight variable to False"""
        self.isRotatingRight=False
    
    def rotateRight(self):
        """adjusts the faceheading of the entity by the entity's rotation speed multiplied by -1"""
        self.faceHeading+=-1*shipRotationSpeed
        self.reDraw()
        
    def shootBullet(self,event):
        """spawns a new bullet entity that travels along the ships current faceHeading"""
        if (not self.hasBulletLoaded):
            return
        if (self.currentBullets>=self.maxBullets):
            return
        newBullet=Bullet(self.canvasIGetDrawnOn,entityThatCreatedMe=self,xPos=self.xPos,yPos=self.yPos)
        self.hasBulletLoaded=False#the gun chamber is now empty
        self.currentBullets+=1
        newBullet.faceHeading=self.faceHeading
        newBullet.reDraw()
        newBullet.accelerateForwards(movementSpeed=bulletSpeed)#gives the bullet its inital speed.
        
    def reloadBullet(self,event):
        """this function is to 'reload' the gun after its fired once. 
        its basically to prevent the player from holding down the fire button
        and firing a continuous stream of bullets"""
        self.hasBulletLoaded=True
        
    def update(self):
        """a function that calls all the fuctions that each entity needs to perform each tick"""
        super().update()
        self.decelerate()
        #check for a collisison with all rock types
        self.checkForRockCollisions()
        #when the ship gets hit by a rock, it enters a period of invulnerability. we need to make sure that period ends at the proper time
        self.checkGracePeriodDuration()
        #movement stuff
        if (self.isAcceleratingForward):
            self.accelerateForwards()
        if (self.isRotatingLeft):
            self.rotateLeft()
        if (self.isRotatingRight):
            self.rotateRight()
    
    def checkForRockCollisions(self):
        """checks to see if this ship has collided with any existing rocks. if a collision has occurred, then the number of lives this ship has is reduced by 1
        this function wont be ran if the ships isInvulnerable variable is True """
        if not self.isInGraceInvulnerability:
            rockKeys=list(Rock.registeredRocks.keys())
            for currKey in rockKeys:
                currRock=Rock.registeredRocks[currKey]
                if (self.hasCollidedWith(currRock)):
                    #if the ship hit a rock...
                    currRock.shatter()
                    self.lives-=1
                    Ship.shipDamagedSound.play()
                    self.enableGracePeriod()
                    break
                
    def enableGracePeriod(self):
         """when the ship gets hit by a rock, it loses a life AND gets a grace period of invulnerability for a short time
         this function turns on that grace period"""
         self.isInGraceInvulnerability=True
         self.gracePeriodStartTime=time.time()
         self.setTexture(shipDamagedSpritePath)
    
    def disableGracePeriod(self):
         """disables the invulerability grace period after losing a life"""
         self.isInGraceInvulnerability=False
         self.setTexture(shipSpritePath)
         
    def checkGracePeriodDuration(self):
        """checks if the ship is in the invulerability grace period state and disables the grace period after the proper time has passed"""
        if (not self.isInGraceInvulnerability):
            return
        if (time.time()-self.gracePeriodStartTime > shipDamagedInvulerabilityGracePeriodLength):
            #if the grace period is over...
            self.disableGracePeriod()
        
class Bullet(Entity):
    """the bullets that the ship shoots"""
    bulletCounter=0
    registeredBullets={}# a dictionary of all the BULLETS that have been made     
    bulletSound = sa.WaveObject.from_wave_file(bulletSoundPath)
    def __init__(self,canvas=0,spritePath=bulletSpritePath,hitboxRadius=bulletHitboxRadius,xPos=0,yPos=0,entityThatCreatedMe=None):
        """initalizes this instance of Bullet"""
        Entity.__init__(self,canvas,spritePath,xPos=xPos,yPos=yPos)
        self.creationTime=time.time()#a time stamp for exactly when the bullet was spawned, this is used in preventing the bullet from traveling forever
        self.entityThatCreatedMe=entityThatCreatedMe#a refrence back to the ship that fired this bullet
        #registering this bullet in a big list o' bullets
        self.bulletID=Bullet.bulletCounter
        Bullet.bulletCounter+=1
        Bullet.registeredBullets[self.bulletID]=self
        Bullet.bulletSound.play()
    
    def delete(self):
        """deletes the bullet"""
        super().delete()
        self.entityThatCreatedMe.currentBullets-=1
        del Bullet.registeredBullets[self.bulletID]
    
    def checkTimeToLive(self):
        """checks if the bullet has lived for longer than the max time specified by timeToLive variable"""
        if (time.time()-self.creationTime > bulletTimeToLive):
            #if this is true, the bullet has lived too long
            self.delete()
    
    def update(self):
        """a function that calls all the fuctions that each entity needs to perform each tick (overloaded from parent)"""
        super().update()
        self.checkTimeToLive()
        
    def deleteAllBullets(self):
        """deletes every entity. this is used when the game is reset"""
        bulletKeys=list(Bullet.registeredBullets.keys())
        for currKey in bulletKeys:
            try:
                currBullet=Bullet.registeredBullets[currKey]
                currBullet.delete()
            except KeyError:
                #this should only be called if an entity is deleted (like if a rock got hit by a bullet)
                continue
        
class Rock(Entity):
    """the class for the rocks that you shoot at"""
    rockCounter=0
    registeredRocks={}# a dictionary of all the ROCKS that have been made
    def __init__(self,canvas,xPos=0,yPos=0,size=2):
        """initalizes this instance of Rock"""
        self.size=size#this denotes if the rock is small(0) medium(1) or large(2)
        if self.size==2:
            #large rock
            self.spritePath=rockLargeSpritePath
            self.hitboxRadius=rockLargeHitboxRadius
            self.pointValue=rockLargePointValue
        elif self.size==1:
            #medium
            self.spritePath=rockMediumSpritePath
            self.hitboxRadius=rockMediumHitboxRadius
            self.pointValue=rockMediumPointValue
        elif self.size==0:
            #small
            self.spritePath=rockSmallSpritePath
            self.hitboxRadius=rockSmallHitboxRadius
            self.pointValue=rockSmallPointValue
        Entity.__init__(self,canvas,self.spritePath,self.hitboxRadius,xPos,yPos)#call parent constructior
        self.faceHeading=random.randint(0,360)#pick a random direction to start with
        self.accelerateForwards(movementSpeed=random.uniform(*rockSpeedRange))
        #register this rock in a big old list o' rocks
        self.rockID=Rock.rockCounter
        Rock.rockCounter+=1
        Rock.registeredRocks[self.rockID]=self
        self.reDraw()
        
    def update(self):
        """a function that calls all the fuctions that each entity needs to perform each tick (overloaded from parent)"""
        super().update()
        bulletKeys=list(Bullet.registeredBullets.keys())
        for currKey in bulletKeys:
            currBullet=Bullet.registeredBullets[currKey]
            if (self.hasCollidedWith(currBullet)):
                currBullet.delete()
                currBullet.entityThatCreatedMe.score+=self.pointValue
                self.shatter()
                break
            
    def delete(self):
        """deletes the rock"""
        super().delete()
        del Rock.registeredRocks[self.rockID]
    
    def shatter(self):
        """deletes the current instance of rock."""
        self.delete()
        if self.size==0:
            #if this rock is a small rock, then dont spawn any new rocks when its shattered
            return
        numberOfRocksLeftToSpawn=numberOfNewRocksToSpawnOnShatter
        while (numberOfRocksLeftToSpawn>0):
            Rock(canvas=self.canvasIGetDrawnOn,xPos=self.xPos,yPos=self.yPos,size=self.size-1)
            numberOfRocksLeftToSpawn-=1