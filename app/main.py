# 2019 COLO SNAKE
# Author: Catherine, Chloe, Licht, Olivia
# ----------------------------------------------------------------------------------------------------------
import json
import os
import random
import bottle
from dfs import DFS,get_distance, createChild
from collections import OrderedDict
import time

from api import ping_response, start_response, move_response, end_response
#------------------------------------------------methods----------------------------------------------

# -----------------------------
# | 0 | 0 | -1 | 0 | 0 | 0 | 0 |
# -----------------------------
# | 0 | 4 | 4 | 4 | 0 | 0 | 0 |
# -----------------------------
# | 0 | -1 | 0 | 0 | 0 | 0 | 0 |
# -----------------------------
# | 4 | 0 | 0 | 0 | 0 | -1 | 0 |
# -----------------------------
# | 4 | 0 | 0 | -1 | 0 | 0 | 0 |
# -----------------------------
# | 4 | 4 | 0 | 0 | 0 | 4 | 0 |
# -----------------------------
# | 0 | -1 | 0 | 0 | 0 | 4 | 4 |
# -----------------------------
# 0: food, 0: safe, 2: position will be reached in 2 steps, 3: in 1 step, 4:dangerous 

def getFoodScore(x, y, board):
    # count =0
    # score = 0
    # if(outOfBoard(x+1, y, board) == False):
    #     score += board[y][x+1]
    #     count += 1
    # if(outOfBoard(x-1, y, board) == False):
    #     score += board[y][x-1]
    #     count += 1
    # if(outOfBoard(x, y+1, board) == False):
    #     score += board[y+1][x]
    #     count += 1
    # if(outOfBoard(x, y-1, board) == False):
    #     score += board[y-1][x]
    #     count += 1

    # if count > 0:
    #     avg = score / count
    #     return avg
    return board[y][x]


def outOfBoard(x, y, board):
    if (x<0 or x>=len(board[0])): return True
    if (y<0 or y>=len(board)): return True
    return False

def setBoard(data, current_pos):
    selfsnake = data['you']
    board_width = data['board']['width']
    board_height = data['board']['height']
    board = [[0 for x in range(board_width)] for y in range(board_height)]

    foodList = {}
    # set food positions
    food = get_food_positions(data)
    for each_food in food:
        y = each_food['y']
        x = each_food['x']
        board[y][x] = 0
        food_pos = (x,y)
        distance = get_distance(current_pos, food_pos)
        foodList[food_pos] = distance

    snakes = data['board']['snakes']
    numSnakes = len(snakes)
    for snake in snakes:
        print ('snake body', snake['body'])
        # set body position
        snake_body = snake['body'][1:]
        for body_frag in snake_body:
            board[body_frag['y']][body_frag['x']] = 4

        # set head position
        snake_head = snake['body'][0]
        board[snake_head['y']][snake_head['x']] = 4

        # reopen tail position (if the snake didnt eat at this step, reopen its tail position)
        # if((snake['health']!=100) and (snake['body'][-1]!=snake['body'][-2])):
        # if((snake['health']!=100): # didnt eat
        if len(snake['body'])>=3: # length>=3
            if snake['body'][-1]!=snake['body'][-2]: # tail not overlap
                snake_tail = snake['body'][-1]
                board[snake_tail['y']][snake_tail['x']] = 0
                print 'reopen tail position with position: ', snake_tail

        # (----------------TODO-------------------)
        # set longer snakes' potential next head positions    
        snake_length = len(snake['body'])
        self_length = len(selfsnake['body'])
        #if (board_width > 10 and board_width < 15 and numSnakes < 5) or (board_width > 15 and numSnakes < 10):
        if((snake['id']!=selfsnake['id']) and (snake_length>=self_length)):
            around_cells_1 = get_around_cells(snake['body'][0], board_width)
            for each_cell_1 in around_cells_1:
                cell = board[each_cell_1['y']][each_cell_1['x']]
                if (cell == 0 or cell == 2):
                    board[each_cell_1['y']][each_cell_1['x']] = 3 # next 1 step
                around_cells_2 = get_around_cells(each_cell_1, board_width)
                for each_cell_2 in around_cells_2:
                    cell =  board[each_cell_2['y']][each_cell_2['x']]
                    if(cell == 0):
                        board[each_cell_2['y']][each_cell_2['x']] = 2 # next 2 step

    foodScores = {}
    for each_food in foodList.keys():
        score = getFoodScore(each_food[0], each_food[1], board)
        foodScores[each_food] = (score, foodList[each_food])

    foodOrderValues = OrderedDict(sorted(foodScores.items(), key=lambda kv: kv[1]))
    
    # print(board)
    print('\n'.join([''.join(['{:4}'.format(item) for item in row]) 
      for row in board]))
    return board, foodOrderValues.keys()

# up, down, left, right cell coordinates of a cell
def get_around_cells(cell, board_width):
    cells = []
    x = cell['x']
    y = cell['y']
    if (y-1>=0): cells.append({'x': x, 'y': y-1}) #up
    if (y+1<=board_width-1): cells.append({'x': x, 'y': y+1}) #down
    if (x+1<=board_width-1): cells.append({'x': x+1, 'y': y}) #right
    if (x-1>=0): cells.append({'x': x-1, 'y': y}) #left
    return cells

# this method will return an array of food positions. 
def get_food_positions(data):
    return data['board']['food'];

# this method will return the next direction e.g. 'up'
def next_direction(data, board, destination, current_pos, health_flag):
    # print 'data:' , data
    print ('turn: ', data['turn'])
    print ('current pos: ', current_pos)
    # direction = data['turn']
    health = data['you']['health']
    direction = 'up'
    next_pos = DFS(current_pos, destination, board, health_flag)
    if(next_pos is None):
        return None
    print ('next pos: ', next_pos)
    if next_pos[0]==current_pos[0]:
        direction = ('up' if next_pos[1]<current_pos[1] else 'down')
    if next_pos[1]==current_pos[1]:
        direction = ('left' if next_pos[0]<current_pos[0] else 'right')

    return direction

def chaseFood(foodList, data, board_, head, tail, flag, health_flag):
    close_food = []
    food_sub_list = foodList
    if (len(foodList)>=4):
        food_sub_list = foodList[0:4]
    for food in food_sub_list:
        direction_head_to_food = next_direction(data, board_, food, head, health_flag)
        if direction_head_to_food is not None: # check there is path from head to food
            # if flag == 1 means the game just start, no need to test path from food to tail
            if (flag == 1) or (next_direction(data, board_, tail, food, health_flag) is not None): # check there is path from food to tail
                # or (get_distance(tail, food) > 225)
                print('There is path from food', food, 'to tail')
                return direction_head_to_food
            else:
            	print('There is no path from food', food, 'to tail')
    return None


def safeCheck(x, y, board):
    #safe = [0, 2, 3]
    if y<0 or y>(len(board)-1):
        return False
    if x<0 or x>(len(board[0])-1):
        return False
    return (board[y][x] != 4)

# (-----------TODO---------------)
def finalChoice(position, board):
    x = position[0]
    y = position[1]
    direction = {}

    if safeCheck(x-1, y, board):
        direction['left'] = board[y][x-1]
    if safeCheck(x+1, y, board):
        direction['right'] = board[y][x+1]
    if safeCheck(x, y-1, board):
        direction['up'] = board[y-1][x]
    if safeCheck(x, y+1, board):
        direction['down'] = board[y+1][x]

    sorted_dic = OrderedDict(sorted(direction.items(), key=lambda kv: kv[1]))
    directions = sorted_dic.keys()
    if len(directions) > 0:
        direction = directions[0]
    else: 
        direction = 'right'
    # no way to go, then whatever
    print("final choice direction:", direction)
    return direction

# def minLength(board_width):
#     if board_width == 7:
#         return 5
#     if board_width == 11:
#         return 10
#     if board_width == 19: 
#         return 15
#     return 5

# def minLength(snakes):
#     num_of_snakes = len(snakes)
#     self_length_index = (num_of_snakes-1)/2


#     return length


# # min health condition that the snake has to find food
# def minHealth(numofsnakes, numoffood, board_width): 
#     # food_per_cell = board_width/numoffood
#     food_per_snake = numoffood/numofsnakes



#------------------------------------------------API calls------------------------------------------------------
@bottle.route('/')
def index():
    return '''
    Battlesnake documentation can be found at
       <a href="https://docs.battlesnake.io">https://docs.battlesnake.io</a>.
    '''

@bottle.route('/static/<path:path>')
def static(path):
    """
    Given a path, return the static file located relative
    to the static folder.

    This can be used to return the snake head URL in an API response.
    """
    return bottle.static_file(path, root='static/')

@bottle.post('/ping')
def ping():
    """
    A keep-alive endpoint used to prevent cloud application platforms,
    such as Heroku, from sleeping the application instance.
    """
    return ping_response()

@bottle.post('/start')
def start():
    data = bottle.request.json

    """
    TODO: If you intend to have a stateful snake AI,
            initialize your snake state here using the
            request's data if necessary.
    """
    # print(json.dumps(data))

    color = "#ffcccc"
    headType = "silly"
    tailType = "bolt"

    return start_response(color, headType, tailType)


@bottle.post('/move')
def move():
    data = bottle.request.json
    direction = 'up' #initialize a direction

    # draw the board
    start_time = time.time()
    x = data['you']['body'][0]['x']
    y = data['you']['body'][0]['y']
    head = (x,y)
    tail_pos_x = data['you']['body'][-1]['x']
    tail_pos_y = data['you']['body'][-1]['y']
    tail = (tail_pos_x, tail_pos_y)
    board_, foodList = setBoard(data, head)
    

    health = data['you']['health']
    print 'health: ', health

    # num_of_snakes = data['board']['snakes']

    # -----------------------at the beginning of the game, chase food and increase length to xxx according to snake length--------------
    # min_length = minLength(data['board']['width'])
    # if (len(data['you']['body'])<=min_length):

    if (len(data['you']['body'])<=5):
        print "!!=============LENGTH<=5, CHASE FOOD==============!!"
        direction = chaseFood(foodList, data, board_, head, tail, 1, 'A')
        if direction is None:
            direction = finalChoice(head, board_)
        print("--- %s miliseconds ---" % int((time.time() - start_time) * 1000))
        print('next direction: ', direction)
        print('move', move_response(direction))
        return move_response(direction)

    #-----------------------------------------------------------------------------------------------------------------------------------

    if (health == 100):
        direction = None
        if(get_distance(head, tail) > 1):
            print('!!========HEALTH FULL, CHASE TAIL==============!!')
            board_[tail[1]][tail[0]] = 0
            direction = next_direction(data, board_, tail, head, 'B')
        else:
            print('!!=============CHASE FOOD==============!!') 
            direction = chaseFood(foodList, data, board_, head, tail, 0, 'B')
        if direction is None:
            print('!!=========HEALTH FULL, NO PATH TO FOOD, FINAL==============!!')
            direction = finalChoice(head, board_)
        print("--- %s miliseconds ---" % int((time.time() - start_time) * 1000))
        return move_response(direction)

    else:
    # 
    # if num_of_snakes > 4:
    #     if health > 90:
    #         chase tail
    #     else if health < 30:
    #         chase food (by distance)
    #     else: chase food (safe mode)
    # else:
    #     if health > 80:
    #         chase tail
    #     else if len(food)/len(snake) < 1/2 and health < 40:
    #         chase food (by distance)
    #     else:
    #     chase food 
        snakes = data['board']['snakes']
        num_of_snakes = len(snakes)
        if num_of_snakes > 4:
            if health > 90:
                #chase tail
                print('!!==========SNAKES >4, Health>90, CHASE TAIL==============!!') 
                direction = next_direction(data, board_, tail, head, 'B')
                if direction is None:
                    print 'no path to tail'
                    direction = chaseFood(foodList, data, board_, head, tail, 0, 'B') # chase food 
                if direction is None:
                    direction = finalChoice(head, board_)
                print ('next direction: ', direction)
                print("--- %s miliseconds ---" % int((time.time() - start_time) * 1000))
                return move_response(direction)    

            elif health < 30:
                print('!!==========SNAKES >4, Health<30, CHASE FOOD (danger mode)==============!!') 
                #chase food (C)
                direction = chaseFood(foodList, data, board_, head, tail, 0, 'C') # chase food 
                if direction is None:
                    direction = next_direction(data, board_, tail, head, 'C')# chase tail
                if direction is None:
                    direction = finalChoice(head, board_)
                print ('next direction: ', direction)
                print("--- %s miliseconds ---" % int((time.time() - start_time) * 1000))
                return move_response(direction)    

            else:
                print('!!==========SNAKES >4, Health>30 and <=90 CHASE FOOD (safe mode)==============!!') 
                #chase food (B)
                direction = chaseFood(foodList, data, board_, head, tail, 0, 'B') # chase food 
                if direction is None:
                    direction = next_direction(data, board_, tail, head, 'B')# chase tail
                if direction is None:
                    direction = finalChoice(head, board_)
                print ('next direction: ', direction)
                print("--- %s miliseconds ---" % int((time.time() - start_time) * 1000))
                return move_response(direction)  

        else:
            if health > 80:
                #chase tail
                print('!!==========SNAKES <=4, Health>80, CHASE TAIL==============!!') 
                direction = next_direction(data, board_, tail, head, 'B')
                if direction is None:
                    print 'no path to tail'
                    direction = chaseFood(foodList, data, board_, head, tail, 0, 'B') # chase food 
                if direction is None:
                    direction = finalChoice(head, board_)
                print ('next direction: ', direction)
                print("--- %s miliseconds ---" % int((time.time() - start_time) * 1000))
                return move_response(direction) 


            elif (len(data['board']['food'])/num_of_snakes < 1/2) and (health < 40):
                #chase food (C)
                print('!!==========SNAKES <=4, food/snake < 1/2, heath <40, CHASE TAIL(danger mode)==============!!') 
                direction = chaseFood(foodList, data, board_, head, tail, 0, 'C') # chase food 
                if direction is None:
                    direction = next_direction(data, board_, tail, head, 'C')# chase tail
                if direction is None:
                    direction = finalChoice(head, board_)
                print ('next direction: ', direction)
                print("--- %s miliseconds ---" % int((time.time() - start_time) * 1000))
                return move_response(direction)    

            else: 
                #chase food (B)
                ('!!==========SNAKES <=4, CHASE FOOD (safe mode)==============!!') 
                print('!!==========SNAKES >4, Health>30 and <=90 CHASE FOOD (safe mode)==============!!') 
                #chase food (safe mode)
                direction = chaseFood(foodList, data, board_, head, tail, 0, 'B') # chase food 
                if direction is None:
                    direction = next_direction(data, board_, tail, head, 'B')# chase tail
                if direction is None:
                    direction = finalChoice(head, board_)
                print ('next direction: ', direction)
                print("--- %s miliseconds ---" % int((time.time() - start_time) * 1000))
                return move_response(direction) 



    #(---------TODO---------- if eat a food at this step, DFS to tail doesnt work, so chase tail around) 



    # if (health>=90 and health != 100): # chasing the tail 
    #     print('!!==========Health>=70, CHASE TAIL==============!!') 
    #     direction = next_direction(data, board_, tail, head, 'C')
    #     # (------------TODO------------- if there's no path to the tail or tail is dangerous)
    #     if direction is None:
    #         print('!!=============Health>=70, NO PATH TO TAIL OR TAIL DANGEROUS, CHASE FOOD=========!!')
    #         print("health",health)   
    #         direction = chaseFood(foodList, data, board_, head, tail, 0, 'C')
    #     if direction is None:
    #         print('!!=============Health>=70, NO PATH TO TAIL, FINAL==========!!')
    #         direction = finalChoice(head, board_)
    #     print ('next direction: ', direction)
    #     print("--- %s miliseconds ---" % int((time.time() - start_time) * 1000))
    #     return move_response(direction)
    # else:
    #     # chasing the food in sequence
    #     print('!!============Health<70 CHASE FOOD==============!!')
    #     direction = chaseFood(foodList, data, board_, head, tail, 0, 'C')
    #     # no path find for all of the food (----------TODO-----------)   
    #     if direction is None: 
    #     	print('!!=============NO FOOD!! GO TAIL==============!!')
    #     	direction = next_direction(data, board_, tail, head, 'C')
    #     if direction is None:
    #         print('!!=============NO FOOD!! NO TO TAIL, FINAL==============!!')
    #         direction = finalChoice(head, board_)
    #     print ('next direction: ', direction)
    #     print('move', move_response(direction))
    #     print("--- %s miliseconds ---" % int((time.time() - start_time) * 1000))
    #     return move_response(direction)


@bottle.post('/end')
def end():
    data = bottle.request.json
    return end_response()

# Expose WSGI app (so gunicorn can find it)
application = bottle.default_app()

if __name__ == '__main__':
    bottle.run(
        application,
        host=os.getenv('IP', '0.0.0.0'),
        port=os.getenv('PORT', '8080'),
        debug=os.getenv('DEBUG', True)
    )





