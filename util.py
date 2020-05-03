def convert_tier_rank_stars_to_stars_needed(tier, rank, stars):
    if tier == 0:
        return 0
    return (tier-1)*30+(rank-1)*3+(3-stars)


def convert_stars_needed_to_tier_rank_stars(stars_needed):
    if stars_needed == 0:
        return (0, 0, 0)
    if stars_needed == 151:
        return (5, 10, 0)
    else:
        tier = ((stars_needed-1)//30) + 1
        remaining = (stars_needed-1) % 30
        rank = (remaining//3) + 1
        stars = 3 - (remaining % 3)
        return (tier, rank, stars)


def generate_floor_and_next_floor(stars_needed):
    floor = ((stars_needed-1)//15+1)*15
    next_floor = ((stars_needed-1)//15)*15
    return floor, next_floor


def simulate_one_game(win_list, stars_needed, bonus_stars):
    floor, next_floor = generate_floor_and_next_floor(stars_needed)
    stars_list = [stars_needed]
    num_games_list = []
    prev_prev_win, prev_win = None, None
    for win in win_list:
        if win:
            if floor != 15 and prev_win and prev_prev_win:
                stars_needed -= bonus_stars
            stars_needed -= bonus_stars
        else:
            if stars_needed != floor+1:
                stars_needed += 1
        if stars_needed <= next_floor:
            num_games_list.append(len(stars_list))
            if bonus_stars != 1:
                bonus_stars -= 1
            floor, next_floor = generate_floor_and_next_floor(stars_needed)
            if floor == 15:
                bonus_stars = 1
        stars_list.append(stars_needed)
        prev_prev_win = prev_win
        prev_win = win
        if stars_needed == 0:
            break
    return stars_list, num_games_list
