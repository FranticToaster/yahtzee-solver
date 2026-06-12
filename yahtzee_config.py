#some basic rule/variation configs

#the index[i] will give the i-th category's constant score (None if non-constant score)
constScoreCategories: list[None | int] = [
    None,
    None,
    None,
    None,
    None,
    None,
    30,
    40,
    None,
    None,
    25,
    None,
    None, #special, based on Yahtzee Bonus rule
]

yahtzeeBonus = False


#loaded die config
#first element is weight for 1, second element is weight for 2 etc
dieWeights = [6, 5, 4, 3, 2, 1]
dieWeightsSum = sum(dieWeights)