import random


def fizzbuzz(number):
    """
    This method return element of #number from Fizz Buzz game.
    """
    number = int(number)
    if number < 1:
        raise ValueError()

    if number % 3 == 0:
        if number % 5 == 0:
            value = 'fizzbuzz'
        else:
            value = 'fizz'
    elif number % 5 == 0:
        value = 'buzz'
    else:
        value = str(number)
    return value

MAX_ROUNDS = 100000

SKILLS_ERRORS_RATE = {
  1: 40,
  2: 20,
  3: 10,
  4: 5
}


def generate_answer_for(player, current_number):
    """
    This method generates answers according to players skills
    Player with skill:
    1 - makes 40 % of mistakes
    2 - 20 %
    3 - 10 %
    4 - 5 %
    Error is defined as best shot - when player says current_number
    without thinking. Still this answer may be correct :)
    """
    element = random.randrange(0, 101)
    if element < 100 - SKILLS_ERRORS_RATE[player.skill]:
        # good answer
        return fizzbuzz(current_number)
    else:
        # try your best and - shoot!
        return str(current_number)



