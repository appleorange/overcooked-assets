'''
Key Features:
1. player movement and facing direction
- use arrow keys to move the player
- player faces a certain tile to pick up/drop/cook items
2. pickup, holding, and placing items
- press the pickup key [e] when facing an item
- items held by the player are displayed above them
3. serving orders and scoring
- orders are shown on the right side of the screen
- complete orders by placing the correct combination of ingredients on plates 
- score increases for completed orders, decreases for missed or incorrect orders, and high score is tracked
- game is over when time's up or when your score drops below 0
4. ingredient and plate rendering
- ingredients are drawn on plates in position based on how many there are
- stored 'cut_' and 'cook_' ingredients to display the correct image
5. fire extinguisher feature
- use the [e] key to activate the fire extinguisher
- use it if you leave the cooked item on the stove for too long and it burns
- observe fire being cleared in kitchen if present
6. washing dishes
- interact with the sink to wash plates by pressing [e]
- plates must be washed every 2 orders otherwise you cannot get new plates

features are described more detailed in the instructions page (press [i])
'''

'''
Grading Shortcuts:
- press 1: fill player inventory with a ready to serve plate
- press 2: place a cut ingredient on the stove and start cooking
- press 3: burn an ingredient instantly to show the fire extinguisher
- press 4: make the sink dirty to show cleaning feature
- press 5: spawn a new order instantly
'''

from cmu_graphics import *
import random

#classes
class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.holding = None #player inventory, what it's holding
        self.facing = 'down'
    
    def move(self, direction, app, speed):
        #moves player in direction if tile not blocked
        
        tileSize = app.tileSize
        kitchen = app.kitchen
        px, py = self.x, self.y
        
        newX, newY = self.x, self.y
        
        if direction == 'up':
            self.facing = 'up'
            newX, newY = px, py-speed
        elif direction == 'down':
            self.facing = 'down'
            newX, newY = px, py + speed
        elif direction == 'left':
            self.facing = 'left'
            newX, newY = px-speed, py
        elif direction == 'right':
            self.facing = 'right'
            newX, newY = px + speed, py
        
        print(f'moving {direction} to ({newX}, {newY})')
            
        #collision check
        col = int(newX // tileSize)
        row = int(newY//tileSize)
        
        if 0 <= row < len(kitchen) and 0 <= col < len(kitchen[0]):
            if kitchen[row][col] not in app.blockedTiles:
                self.x = newX
                self.y = newY
                
            

#title screen + mvc framework + modes
def onAppStart(app):
    app.mode = 'title' #starts on title screen
    app.width = 800
    app.height = 600
    
    app.timeLimit = 100
    app.timeRemaining = app.timeLimit
    app.highScore = 0
    
    app.keysHeld = set()
    app.facing = 'down'
    
    #tiles that the player cannot collide into
    app.blockedTiles = {'plate_crate', 'tomato','cheese', 'onion', 'lettuce', 'buns', 'wall', 'counter', 'stove', 'sink', 'serve', 'extinguisher', 'cut'}
    app.cuttable = {'tomato', 'onion', 'lettuce', 'cheese'}
    app.cookable = {'cut_onion', 'cut_cheese'}
    app.itemsOnGround = {} #{(row, col): 'cut_tomato',...}
    app.fires = set() #tiles currently on fire
    
    app.isCutting = False
    app.cutProgress = 0
    app.cutTarget = None
    app.cutPosition = None
    
    app.isCooking = False
    app.cookProgress = 0
    app.cookTarget = None
    app.cookPosition = None
    
    #helps track when to wash sink
    app.ordersServed = 0
    app.sinkDirty = False
    
    app.isCleaningSink = False
    app.cleanProgress = 0
    app.cleanTarget = None

    app.images = {
        'tomato': 'https://github.com/appleorange/overcooked-assets/blob/main/tomato.png?raw=true', 
        'onion': 'https://github.com/appleorange/overcooked-assets/blob/main/ONION.png?raw=true',
        'buns': 'https://github.com/appleorange/overcooked-assets/blob/main/buns.png?raw=true',
        'cheese': 'https://github.com/appleorange/overcooked-assets/blob/main/cheese.png?raw=true',
        'lettuce': 'https://github.com/appleorange/overcooked-assets/blob/main/lettuce.png?raw=true',
        'floor': 'https://github.com/appleorange/overcooked-assets/blob/main/floor.png?raw=true',
        'sink': 'https://github.com/appleorange/overcooked-assets/blob/main/sink.png?raw=true',
        'wall': 'https://github.com/appleorange/overcooked-assets/blob/main/wall.png?raw=true',
        'extinguisher': 'https://github.com/appleorange/overcooked-assets/blob/main/extinguisher.png?raw=true',
        'stove': 'https://github.com/appleorange/overcooked-assets/blob/main/stove.png?raw=true',
        'cut': 'https://github.com/appleorange/overcooked-assets/blob/main/cuttingboard.png?raw=true',
        'counter': 'https://github.com/appleorange/overcooked-assets/blob/main/counter.png?raw=true',
        'serve': 'https://github.com/appleorange/overcooked-assets/blob/main/serve.png?raw=true',
        'appKnife': 'https://github.com/appleorange/overcooked-assets/blob/main/appKnife.png?raw=true',
        'cook_onion': 'https://github.com/appleorange/overcooked-assets/blob/main/cooked_onion.png?raw=true',
        'fire': 'https://github.com/appleorange/overcooked-assets/blob/main/fire.png?raw=true',
        'cook_cheese': 'https://github.com/appleorange/overcooked-assets/blob/main/cooked_cheese.png?raw=true',
        'plate_crate': 'https://github.com/appleorange/overcooked-assets/blob/main/plate.png?raw=true',
        'plate_empty': 'https://github.com/appleorange/overcooked-assets/blob/main/plate.png?raw=true',
        'player': 'https://github.com/appleorange/overcooked-assets/blob/main/character.png?raw=true',
        'dirty_sink': 'https://github.com/appleorange/overcooked-assets/blob/main/image-removebg-preview.png?raw=true'
        }
    
    # app.renderedItemImages = {} #stores snapshot of drawn items (with knife overlay for cut items)
    
    initGame(app)
    
'''    
def getIngredientImage(app, item):
    if item in app.cutIngredients:
        return app.cutIngredients[item]
    return app.ingredients[item]
''' 
    
def getItemImage(app, itemName): #returns action done + base name cut_tomato
    base = itemName
    base = base.replace('cut_', '')
    base = base.replace('cook_', '')
    return app.images[base]
    
def initGame(app):
    app.tileSize = 70
    
    app.score = 0
    app.scoreFlash = False
    app.scoreFlashTimer = 0
    app.scoreFlashDuration = 15
    
    app.orders = []
    app.orderInterval = 300
    app.orderTimer = 0
    app.maxOrders = 2
    
    app.serveTimers = {}
    
    #map of kitchen layout using strings
    app.kitchen = [
        ['wall', 'wall', 'wall', 'wall', 'wall', 'wall'],
        ['tomato', 'extinguisher', 'serve', 'stove', 'sink', 'wall'],
        ['floor', 'floor', 'floor', 'floor', 'floor', 'wall'],
        ['floor', 'cut', 'counter', 'plate_crate', 'cut', 'wall'],
        ['floor', 'floor', 'floor', 'floor', 'buns', 'wall'],
        ['cheese', 'lettuce', 'onion', 'floor', 'floor', 'wall']
        ]
    app.player = Player(2*app.tileSize + 30, 2*app.tileSize + 30) 
    app.orders.append(generateOrder(app))
    
    app.secondCounter = 0
    app.timeRemaining = app.timeLimit
    
def generateOrder(app):
    ingredientsPool = ['tomato', 'cheese', 'lettuce', 'onion', 'buns']
    numIngredients = random.randint(2, 5)
    ingredients = random.sample(ingredientsPool, numIngredients)
    
    finalIngredients = []
    for ing in ingredients:
        if ing == 'tomato' or ing == 'lettuce':
            finalIngredients.append('cut_' + ing)
        elif ing == 'onion' or ing == 'cheese':
            finalIngredients.append('cook_' + ing)
        else:
            finalIngredients.append(ing)
    order = {'ingredients': finalIngredients, 'timer': 1000, 'position': len(app.orders)}
    return order
    
def getTileAt(app, x, y):
    tileSize = app.tileSize
    col = x // tileSize
    row = y // tileSize
    
    if row < 0 or row >= len(app.kitchen):
        return None
    if col < 0 or col >= len(app.kitchen[0]):
        return None
    return app.kitchen[row][col]
    
#returns tile directly in front of player to see which direction player is facing for picking up/dropping items
def getTileInFront(app):
    tileSize = app.tileSize
    row = int(app.player.y//tileSize)
    col = int(app.player.x //tileSize)
    
    app.facing = app.player.facing
    
    if app.facing == 'up':
        row -= 1
    elif app.facing == 'down':
        row += 1
    elif app.facing == 'left':
        col -=1
    elif app.facing == 'right':
        col +=1
        
    if 0 <= row < len(app.kitchen) and 0 <= col < len(app.kitchen[0]):
        return (row, col)
    return None
    
#returns the correct image key for the item
def getDrawImage(app, item):
    if item.startswith('plate_with_'):
        ingredients = item[11:].split('_and_')
        return ('plate_empty', ingredients)
    
    if item.startswith("cook_"):
        base = item.replace('cook_', '')
        return app.images['cook_' + base]
        
    if item.startswith('burnt_'):
        base = item.replace('burnt_', '')
        return app.images['cook_' + base]
    
    base = item.replace('cut_', '')
    return app.images[base]
    
#draw kitchen
def drawKitchen(app):
    tileSize = app.tileSize
    for r in range(len(app.kitchen)):
        for c in range(len(app.kitchen[0])):
            tile = app.kitchen[r][c]
            x = c*tileSize
            y = r*tileSize
            
            if tile == 'wall':
                drawImage(app.images['wall'], x, y, width = tileSize, height = tileSize)
            elif tile == 'extinguisher':
                drawImage(app.images['extinguisher'], x, y, width = tileSize, height = tileSize)
            elif tile == 'counter':
                drawImage(app.images['counter'], x, y, width = tileSize, height = tileSize)
            elif tile == 'tomato':
                drawImage(app.images['tomato'], x, y, width = tileSize, height = tileSize)
            elif tile == 'buns':
                drawImage(app.images['buns'], x, y, width = tileSize, height = tileSize)
            elif tile == 'cheese':
                drawImage(app.images['cheese'], x, y, width = tileSize, height = tileSize)
            elif tile == 'lettuce':
                drawImage(app.images['lettuce'], x, y, width = tileSize, height = tileSize)
            elif tile == 'onion':
                drawImage(app.images['onion'], x, y, width = tileSize, height = tileSize)
            elif tile == 'cut':
                drawImage(app.images['cut'], x, y, width = tileSize, height = tileSize)
            elif tile == 'stove':
                drawImage(app.images['stove'], x, y, width = tileSize, height = tileSize)
            elif tile == 'sink':
                drawImage(app.images['sink'], x, y, width = tileSize, height = tileSize)
                if app.sinkDirty:
                    drawImage(app.images['dirty_sink'], x, y, width = tileSize, height = tileSize)
            elif tile == "serve":
                drawImage(app.images['serve'], x, y, width = tileSize, height = tileSize)
            elif tile == 'floor':
                drawImage(app.images['floor'], x, y, width = tileSize, height = tileSize)
            elif tile == 'plate_crate':
                drawImage(app.images['plate_crate'], x, y, width = tileSize, height = tileSize)
    
    #draws every item lying on ground, if item is plated with multiple ingredients, draws the plate with ingredients
    for (r, c), item in app.itemsOnGround.items():
        tileSize = app.tileSize
        imgSize = int(tileSize*0.6)
        
        x = c*app.tileSize + (tileSize-imgSize)//2
        y = r*app.tileSize + (tileSize-imgSize)//2
        
        drawResult = getDrawImage(app, item)
        
        if isinstance(drawResult, tuple):
            plateImgKey, ingredientList = drawResult
            plateImg = app.images[plateImgKey]
            
            plateSize = imgSize*1.35
            plateX = c*tileSize+(tileSize - plateSize)/2
            plateY = r*tileSize+(tileSize-plateSize)/2
            
            drawImage(plateImg, plateX, plateY, width = plateSize, height = plateSize)
            
            padding = plateSize*0.2
            spacing = (plateSize - 2*padding)/max(len(ingredientList), 1)
            
            positions = []
            n = len(ingredientList)
            plateCenterX = plateX + plateSize/2
            plateCenterY = plateY + plateSize/2
            offset = plateSize * 0.3
            
            if n >= 1:
                positions.append((plateCenterX, plateCenterY))
            if n>= 2:
                positions[0] = (plateCenterX - offset, plateCenterY)
                positions.append((plateCenterX + offset, plateCenterY))
            if n >= 3:
                positions[0] = (plateCenterX - offset, plateCenterY-offset)
                positions[1] = (plateCenterX + offset, plateCenterY-offset)
                positions.append((plateCenterX - offset, plateCenterY + offset))
            if n >= 4:
                positions.append((plateCenterX + offset, plateCenterY + offset))
            if n>= 5:
                positions.append((plateCenterX, plateCenterY + offset*1.5))
            for i, ingKey in enumerate(ingredientList):
                if i >= len(positions):
                    foodX = plateCenterX
                    foodY = plateCenterY - offset + i*10
                else:
                    foodX, foodY = positions[i]
                    
                lookupKey = ingKey
                if ingKey.startswith('cut_') or ingKey.startswith('cook_'):
                    lookupKey = ingKey.split('_', 1)[1]
                ingImg = app.images[lookupKey]
                    
                foodSize = plateSize*0.35
                drawImage(ingImg, foodX - foodSize/2, foodY-foodSize/2, width = foodSize, height = foodSize)
        else:
            drawImage(drawResult, x, y, width = imgSize, height=imgSize)
        
        if item.startswith('burnt_'):
            fireSize = int(tileSize*0.35)
            fireX = x + (imgSize-fireSize)//2
            fireY = y + (imgSize-fireSize)//2
            drawImage(app.images['fire'], fireX, fireY, width = fireSize, height=fireSize)
            
        
        if item.startswith('cut_'):
            knifeSize = int(tileSize * 0.35)
            knifeX = x + imgSize - knifeSize//2
            knifeY = y -knifeSize//4
            drawImage(app.images['appKnife'], knifeX, knifeY, width = knifeSize, height = knifeSize)
            
        if (r, c) in app.fires:
            fireSize = int(tileSize*0.7)
            fireX = x + (tileSize-fireSize)//2
            fireY = y+(tileSize-fireSize)//2
            drawImage(app.images['fire'], fireX, fireY, width = fireSize, height = fireSize)

#modes
def redrawAll(app):
    if app.mode == 'title':
        drawTitleScreen(app)
    elif app.mode == 'instructions':
        drawInstructions(app)
    elif app.mode == 'game':
        drawGame(app)
    elif app.mode == 'gameOver':
        drawGameOver(app)
    elif app.mode == 'timeUp':
        drawTimeUp(app)
        
def onKeyPress(app, key):
    if app.mode == 'title':
        titleKeyPressed(app, key)
    elif app.mode == 'instructions':
        instructionsKeyPressed(app, key)
    elif app.mode == 'game':
        gameKeyPressed(app, key)
    elif app.mode == 'gameOver':
        if key == 'r':
            initGame(app)
            app.mode = 'game'
    elif app.mode == 'timeUp' and key == 'h':
        app.mode = 'title'
        initGame(app)

def onKeyHold(app, keys):
    for key in keys:
        app.keysHeld.add(key)

def onKeyRelease(app, key):
    if key in app.keysHeld:
        app.keysHeld.remove(key)
        
'''
        
def movePlayer(app, key, speed):
    tileSize = app.tileSize
    px, py = app.player.x, app.player.y
    
    if key == 'up': 
        app.facing = 'up'
        newX, newY = px, py-speed
    elif key == 'down': 
        app.facing = 'down'
        newX, newY = px, py+speed
    elif key == 'left': 
        app.facing = 'left'
        newX, newY = px-speed, py
    elif key == 'right':
        app.facing = 'right'
        newX, newY = px+speed, py
    else:
        return
        
    #collisionCheck
    tile = getTileAt(app, newX, newY)
    if tile is not None and tile not in app.blockedTiles:
        app.player.x = newX
        app.player.y = newY
'''    

def onStep(app):
    speed = 5
    
    if app.mode =='game':
        app.secondCounter += 1
        if app.secondCounter >= app.stepsPerSecond:
            app.timeRemaining -= 1
            app.secondCounter = 0
            if app.timeRemaining <= 0:
                if app.score > app.highScore:
                    app.highScore = app.score
                app.mode = 'timeUp'
                return
    
    app.orderTimer += 1
    if app.orderTimer >= app.orderInterval and len(app.orders) < app.maxOrders:
        newOrder = generateOrder(app)
        app.orders.append(newOrder)
        app.orderTimer = 0
        
        
    removeOrders = []
    for order in app.orders:
        order['timer'] -= 0.5
        if order['timer'] <= 0:
            removeOrders.append(order)
            app.score -= 1
            
    for order in removeOrders:
        app.orders.remove(order)
    
    if app.isCutting:
        app.cutProgress += 1
        if app.cutProgress >= 10:
            finishCutting(app)
        return

    if app.isCooking:
        row, col = app.cookPosition
        if (row, col) not in app.itemsOnGround:
            app.isCooking = False
            app.cookProgress = 0
            app.cookTarget = None
            app.cookPosition = None
        else:
            app.cookProgress += 1
            if app.cookProgress == 10:
                finishCooking(app)
            elif app.cookProgress >= 40:
                burnFood(app)
        return
    
    if app.isCleaningSink:
        app.cleanProgress += 1
        if app.cleanProgress >= 20:
            row, col = app.cleanTarget
            app.sinkDirty = False
            app.isCleaningSink = False
            app.cleanTarget = None
            app.cleanProgress = 0
        return
    
    if app.score < 0: #lose if u have negative points
        app.mode = 'gameOver'
        return
    
    for key in app.keysHeld:
        app.player.move(key, app, speed)
        
    
    #countdown timers that track when a served dish should disappear and give points
    removeList = []
    for pos in app.serveTimers:
        app.serveTimers[pos] -= 1
        if app.serveTimers[pos] <= 0:
            app.score += 1
            app.scoreFlash = True
            app.scoreFlashTimer = app.scoreFlashDuration
            if pos in app.itemsOnGround:
                del app.itemsOnGround[pos]
            removeList.append(pos)
        
        for pos in removeList:
            del app.serveTimers[pos]
            
    if app.scoreFlash:
        app.scoreFlashTimer -= 1
        if app.scoreFlashTimer <= 0:
            app.scoreFlash = False
        
#title screen
def drawTitleScreen(app):
    drawRect(0, 0, app.width, app.height, fill = 'peachpuff')
    drawLabel("112 COOKOUT!", app.width/2, 150, size = 40, bold=True)
    drawLabel('Press SPACE to start', app.width/2, 300, size=25)
    drawLabel('Press I for instructions', app.width/2, 350, size=25)
    drawLabel(f'High Score: {app.highScore}', app.width/2, 400, size = 25)
    
def titleKeyPressed(app, key):
    if key == 'space':
        app.mode = 'game'
    elif key == 'i':
        app.mode = 'instructions'

#instructions
def drawInstructions(app):
    drawRect(0, 0, app.width, app.height, fill = 'lightyellow')
    drawLabel("Instructions", app.width/2, 40, size = 35, bold=True)
    instructionLines = [
        '1. Move your player using the arrow keys.',
        '2. Stand in front of an item and press [E] to pick up, drop, cut, cook, or clean the sink.',
        '3. Onions and cheese must be cut and cooked before plating.',
        '4. Tomatoes and lettuce only need to be cut; cooking them do nothing.',
        '5. You can only drop items on the floor, cutting board, stove, counter, or serving tray.',
        '6. You can only hold one item at a time.',
        '7. Place ready ingredients on a plate before serving.',
        '8. Only plate items that are fully prepared (cut/cooked as needed).',
        '9. Buns can be used without preparation.',
        '10. If cut onions or cheese are left on the stove too long, they will burn. Use the extinguisher to remove the fire and remake the item.',
        '11. Orders appear on the right side of the screen. You can plate items in any order.',
        '12. Serving the wrong order or missing the order time limit costs 1 point.',
        '13. Serving the correct order on time earns 2 points.',
        '14. A max of 2 orders can be active at a time.',
        '15. If your score drops below 0, the game is over.',
        '16. After every 2 served orders, the sink becomes dirty. Clean it before getting new plates.',
        '17. Complete as many orders as you can in 100 seconds!'
        ]
        
    yStart = 80
    lineHeight = 25
    for i, line in enumerate(instructionLines):
        drawLabel(line, 50, yStart + i*lineHeight, size = 18, align = 'left')

    drawLabel("Press B to go back", app.width/2, app.height-30, size = 20, bold = True)
        
def instructionsKeyPressed(app, key):
    if key == 'b':
        app.mode = 'title'
        
#game
def drawGame(app):
    if app.scoreFlash:
        size = 25
        color = 'gold'
    else:
        size = 25
        color = 'black'
    drawLabel(f"Score: {app.score}", app.width - 80, 30, size = size, bold = True, fill = color)
    
    #draw timer
    minutes = int(app.timeRemaining//60)
    seconds = int(app.timeRemaining %60)
    timeStr = f'{minutes:02}:{seconds:02}'
    drawLabel(f'Time Remaining: {timeStr}', app.width-270, 400, size = 18)
    
    #draworders
    
    xStart = app.width - 350
    yStart = 90
    orderHeight = 60
    
    drawLabel("Orders", xStart+30, 60, size = 25, bold = True)
    
    #draws orders
    for i, order in enumerate(app.orders):
        y = yStart + i*orderHeight
        ingredients = order['ingredients']
        
        drawRect(xStart-10, y-10, 260, 60, fill = 'lightgray')
        
        imgSize = 40
        spacing = 10
        for j, ing in enumerate(ingredients):
            ingImg = getDrawImage(app, ing)
            if isinstance(ingImg, tuple):
                ingImg = app.images[ingImg[0]]
            drawImage(ingImg, xStart + j*(imgSize + spacing), y, width = imgSize, height=imgSize)
            
            if ing.startswith('cut_'):
                knifeSize = int(imgSize*0.4)
                knifeX = xStart + j*(imgSize + spacing) + imgSize - knifeSize - 2
                knifeY = y + 2
                drawImage(app.images['appKnife'], knifeX, knifeY, width = knifeSize, height = knifeSize)

        timerWidth = 100
        timerRatio = order['timer']/1000
        drawRect(xStart, y + 35, timerWidth, 10, fill = 'gray')
        drawRect(xStart, y + 35, timerWidth*timerRatio, 10, fill = 'green')
    
    drawKitchen(app)
    playerSize = 80
    drawImage(app.images['player'], app.player.x - playerSize/2, app.player.y-playerSize/2, width = playerSize, height = playerSize)
    
    #draws what player is holding
    if app.player.holding is not None:
        item = app.player.holding
        
        drawResult = getDrawImage(app, item)
        px = app.player.x-20
        py = app.player.y-60
        size = 40
        
        if isinstance(drawResult, tuple):
            plateImgKey, ingredientList = drawResult
            plateImg = app.images[plateImgKey]
            
            plateSize = 40
            plateX = px
            plateY = py
            
            drawImage(plateImg, plateX, plateY, width = plateSize, height = plateSize)
            
            n = len(ingredientList)
            plateCenterX = plateX + plateSize/2
            plateCenterY = plateY + plateSize/2
            offset = plateSize * 0.3
            
            positions = []
            if n >= 1:
                positions.append((plateCenterX, plateCenterY))
            if n>= 2:
                positions[0] = (plateCenterX - offset, plateCenterY)
                positions.append((plateCenterX + offset, plateCenterY))
            if n >= 3:
                positions[0] = (plateCenterX - offset, plateCenterY-offset)
                positions[1] = (plateCenterX + offset, plateCenterY-offset)
                positions.append((plateCenterX - offset, plateCenterY + offset))
            if n >= 4:
                positions.append((plateCenterX + offset, plateCenterY + offset))
            if n>= 5:
                positions.append((plateCenterX, plateCenterY + offset*1.5))
                
            #draws each ingredient on top of a plate the player is holding
            for i, ingKey in enumerate(ingredientList):
                if i >= len(positions):
                    foodX = plateCenterX
                    foodY = plateCenterY - offset + i*10
                else:
                    foodX, foodY = positions[i]
                
                lookupKey = ingKey
                if ingKey.startswith('cut_') or ingKey.startswith('cook_'):
                    lookupKey = ingKey.split('_', 1)[1]
                ingImg = app.images[lookupKey]
                
                foodSize = plateSize*0.35
                drawImage(ingImg, foodX - foodSize/2, foodY-foodSize/2, width = foodSize, height = foodSize)
        else:
            drawImage(drawResult, px, py, width = size, height=size)
        
        if item.startswith('burnt_'):
            drawImage(app.images['fire'], app.player.x-10, app.player.y-80, width = 35, height=35)
        
        if item.startswith('cut_'):
            drawImage(app.images['appKnife'], app.player.x + 10, app.player.y-70, width = 25, height = 25)
        
    if app.cutProgress > 0:
        drawRect(app.player.x-30, app.player.y+30, 60, 10, fill = 'gray')
        drawRect(app.player.x-30, app.player.y+30, 6*app.cutProgress, 10, fill = 'green')
        
    if app.isCooking and app.cookProgress > 0:
        drawRect(app.player.x-30, app.player.y+45, 60, 10, fill = 'gray')
        progressWidth = min(6*app.cookProgress, 60)
        drawRect(app.player.x-30, app.player.y+45, progressWidth, 10, fill = 'orange')
        
    if app.isCleaningSink and app.cleanProgress > 0:
        row, col = app.cleanTarget
        tileSize = app.tileSize
        x = col*tileSize
        y = row*tileSize + tileSize #draw below sink tile?
        drawRect(x, y, tileSize, 10, fill = 'gray')
        progressWidth = min(app.cleanProgress/20 * tileSize, tileSize)
        drawRect(x, y, progressWidth, 10, fill = 'blue')
    
    drawLabel("Press T to return to Title Screen", app.width/2, app.height-20, size = 18)
    drawLabel("Press R to reset the game", app.width/2, app.height-40, size = 18)
    
def gameKeyPressed(app, key):
    if key == 't': app.mode = 'title'
    if key == 'e':
        interact(app)
    if key == 'r':
        initGame(app)
        return
    
    #grading shortcuts
    if key == '1':
        app.player.holding = 'plate_with_cut_onion_and_cook_cheese'
    if key == '2':
        row, col = 1, 3
        app.itemsOnGround[(row, col)] = 'cut_onion'
        app.player.holding = None
        app.isCooking = True
        app.cookProgress = 0
        app.cookTarget = 'cut_onion'
        app.cookPosition = (row, col)
        if (row, col) in app.fires:
            app.fires.remove((row, col))
    if key == '3':
        row, col = 1, 3
        app.itemsOnGround[(row, col)] = 'burnt_onion'
        app.fires.add((row, col))
    if key == '4':
        app.sinkDirty = True
    if key == '5':
        app.orders.append(generateOrder(app))
    
        
#game over screen
def drawGameOver(app):
    drawRect(0, 0, app.width, app.height, fill = 'black')
    drawLabel('GAME OVER', app.width/2, app.height/2-40, size = 50, fill = 'red', bold = True)
    drawLabel("You ran out of points!", app.width/2, app.height/2 + 10, size = 30, fill = 'white')
    drawLabel("Press R to restart", app.width/2, app.height/2 + 60, size = 25, fill='white')
    
#time up screen
def drawTimeUp(app):
    drawRect(0, 0, app.width, app.height, fill = 'lightSlateGray')
    drawLabel("TIME'S UP!", app.width/2, app.height/2 - 50, size = 50, fill = 'steelBlue', bold = True)
    drawLabel(f"Your Score: {app.score}", app.width/2, app.height/2, size = 30, fill = 'white')
    drawLabel(f"High Score: {app.highScore}", app.width/2, app.height/2 + 50, size = 30, fill = 'white')
    drawLabel("Press H to return home", app.width/2, app.height/2 + 100, size = 30, fill = 'white')
    
    
def interact(app):
    pos = getTileInFront(app)
    if pos is None:
        return
    
    row, col = pos
    tile = app.kitchen[row][col]
    
    #clean sink
    if tile == 'sink' and app.sinkDirty and not app.isCleaningSink:
        app.isCleaningSink = True
        app.cleanProgress = 0
        app.cleanTarget = (row, col)
        #app.sinkDirty = False
        return
    
    pickupTiles = {'tomato', 'cheese', 'lettuce', 'buns', 'onion', 'extinguisher', 'plate_crate'}
    
    #cutting items
    if tile == 'cut' and app.player.holding in app.cuttable:
        app.isCutting = True
        app.cutProgress = 0
        app.cutTarget = app.player.holding
        app.cutPosition = (row, col)
        print(f'cutting {app.player.holding} at {pos}')
        return
    
    if tile == 'stove' and app.player.holding in app.cookable:
        held = app.player.holding
        
        app.itemsOnGround[(row, col)] = app.player.holding
        app.player.holding = None
        
        app.isCooking = True
        app.cookProgress = 0
        app.cookTarget = held
        app.cookPosition = (row, col)
        print(f'cooking {held} at {pos}')
        return
    
    #serving
    if tile == 'serve' and app.player.holding is not None:
        if app.player.holding.startswith('plate_with_'):
            servedIngredients = app.player.holding[11:].split('_and_')
            servedSet = set(servedIngredients)
            
            correctOrder = None
            for order in app.orders:
                orderSet = set(order['ingredients'])
                if servedSet == orderSet:
                    correctOrder = order
                    print(f'served {app.player.holding} at {pos}')
                    break
                
            if correctOrder:
                app.score += 2
                app.orders.remove(correctOrder)
                app.scoreFlash = True
                app.scoreFlashTimer = app.scoreFlashDuration
                
                #track orders served for dirty sink
                app.ordersServed += 1
                if app.ordersServed % 2 == 0: #sink gets dirty every 2 orders
                    app.sinkDirty = True
            else:
                app.score -= 1
            
            app.player.holding = None
            return

    
    #extinguish fire
    if pos in app.fires and app.player.holding == 'extinguisher':
        app.fires.remove(pos)
        if pos in app.itemsOnGround:
            del app.itemsOnGround[pos]
        app.player.holding = None
        return
    
    #pickup from crate
    if not app.isCutting and app.player.holding is None and tile in pickupTiles:
        if tile == 'plate_crate':
            if app.sinkDirty:
                return
            app.player.holding = 'plate_empty'
        else:
            app.player.holding = tile
        return
    
    #pickup from ground
    if not app.isCutting and app.player.holding is None:
        if pos in app.itemsOnGround:
            app.player.holding = app.itemsOnGround[pos]
            del app.itemsOnGround[pos]
            return
        
    #plate food on empty plate
    pos = getTileInFront(app)
    if pos in app.itemsOnGround and app.player.holding is not None:
        itemOnPlate = app.itemsOnGround[pos]
        ingredient = app.player.holding
        base = ingredient
        
        if itemOnPlate.startswith('plate_with_'):
            existing = itemOnPlate[11:].split('_and_')
            existing.append(base)
            app.itemsOnGround[pos] = 'plate_with_' + '_and_'.join(existing)
            app.player.holding = None
            return
        elif itemOnPlate == 'plate_empty':
            app.itemsOnGround[pos] = 'plate_with_' + base
            app.player.holding = None
            return
    
    #drop item on ground
    dropable = {'floor', 'counter', 'cut', 'serve', 'stove'}
    if not app.isCutting and app.player.holding is not None and tile in dropable:
            app.itemsOnGround[pos] = app.player.holding
            app.player.holding = None
            return
     
def finishCutting(app):
    ingredient = app.cutTarget
    row, col = app.cutPosition
     
    if (row, col) in app.itemsOnGround:
        del app.itemsOnGround[(row, col)]
    
    cutName = 'cut_' + ingredient
    app.itemsOnGround[(row, col)] = cutName
    
    app.player.holding = None
    
    app.isCutting = False
    app.cutTarget = None
    app.cutPosition = None
    app.cutProgress = 0
    
def finishCooking(app):
    ingredient = app.cookTarget.replace('cut_', '')
    row, col = app.cookPosition
    
    if (row, col) in app.itemsOnGround:
        del app.itemsOnGround[(row, col)]
    
    cookedName = 'cook_' + ingredient
    app.itemsOnGround[(row, col)] = cookedName
    print(f'cooked {cookedName} at {row, col}')
    
def burnFood(app):
    ingredient = app.cookTarget.replace('cut_', '')
    row, col = app.cookPosition
    
    if (row, col) in app.itemsOnGround:
        del app.itemsOnGround[(row, col)]
    
    burntName = 'burnt_' + ingredient
    app.itemsOnGround[(row, col)] = burntName
    
    app.fires.add((row, col))
    
    print(f'burnt {burntName} at {row, col}, fires: {app.fires}')

    app.isCooking = False
    app.cookProgress = 0
    app.cookTarget = None
    app.cookPosition = None
    
def main():
    runApp()

main()
